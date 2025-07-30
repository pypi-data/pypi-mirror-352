import os
import logging
import queue
import zipfile
import io
import ssl
from abc import ABC, abstractmethod
from ..admin import FileInformation, list_files, get_file
from ..auth import CartaAgent
from .connection import SyncClient, AsyncClient
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from .exceptions import TLSSetupError, validate_tls_credentials

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("DEBUG_LEVEL", "INFO"))


file_t = str | Path


class Credentials(ABC):
    
    class Local:
        def __init__(self, scope: "Credentials"):
            self.scope = scope

        def read(self, path: file_t) -> "Credentials":
            if isinstance(path, str):
                path = Path(path)
            self.scope.path = path
            with open(path, "rb") as ifs:
                self.scope._content = ifs.read()
            return self.scope

        def write(self, path: file_t | None=None, *, overwrite: bool=False) -> "Credentials":
            path = path or self.scope.path
            if isinstance(path, str):
                path = Path(path)
            if overwrite or not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "wb") as ofs:
                    ofs.write(self.scope._content)
            return self.scope
        
    class Carta:
        def __init__(self, scope: "Credentials", *, agent: CartaAgent | None=None):
            if agent is None:
                from pycarta import get_agent
                agent = get_agent()
            self.agent = agent
            self.scope = scope

        def find(self, path: file_t) -> list[FileInformation]:
            if isinstance(path, str):
                path = Path(path)
            self.scope.path = path
            parent = str(path.parent)
            return [
                f for f in list_files(source="Carta", path=parent)
                if f.path.startswith(parent) and f.name == path.name
            ]

        def read(self, path: file_t) -> "Credentials":
            if isinstance(path, str):
                path = Path(path)
            try:
                first, *others = self.find(path)
                if len(others):
                    logger.error(f"Found multiple matching credential files '{path}'")
                    raise ValueError(f"Found multiple matching credential files '{path}'")
            except ValueError:
                logger.error(f"Could not find credential file '{path}'")
                raise FileNotFoundError(f"Could not find credential file '{path}'")
            try:
                # response = self.agent.get(f"files/Carta/file/{first.id}")
                # response.raise_for_status()
                # logger.info(f"Download success: {path}")
                # self.scope._content = response.content
                self.scope._content = get_file("Carta", first.id)
            # except requests.HTTPError as e:
            except Exception as e:
                logger.error(f"Download failed: {path} ({e})", exc_info=True)
                raise e
            else:
                return self.scope

        def write(self, path: file_t | None=None, *, overwrite: bool=False) -> "Credentials":
            path = path or self.scope.path
            if isinstance(path, str):
                path = Path(path)
            kwargs = {
                # "files": {"file": (str(path.name), self.scope._content, "application/octet-stream")},
                "files": {"file": (str(path), self.scope._content, "application/octet-stream")},
            }
            try:
                first, *others = self.find(path)
                if len(others):
                    logger.error(f"Found multiple matching credential files '{path}'")
                    raise ValueError(f"Found multiple matching credential files '{path}'")
                if overwrite:
                    logger.warning(f"Overwriting existing credential file '{path}'")
                    url = f"files/Carta/file/{first.id}"
                    uploader = self.agent.patch
                else:
                    logger.info(f"Skipping (already exists): {path}")
                    return self.scope
            except ValueError:
                kwargs["params"] = {"path": "/"}  # str(path.parent)}
                url = "files/Carta"
                uploader = self.agent.post
            try:
                response = uploader(url, **kwargs)
                response.raise_for_status()
                logger.info(f"Upload success: {path}")
            except:
                from pprint import pformat
                logger.error(f"Upload failed: {path}", exc_info=True)
                logger.error(f"URL: {url}")
                logger.error(f"Data: {pformat(kwargs)}")
                raise
            return self.scope

    def __init__(self):
        # self.path: Path | None = None
        self._connection: "Connection" | None = None
        self.carta = Credentials.Carta(self)
        self.local = Credentials.Local(self)
        self._content: bytes | None = None

    @abstractmethod
    def __enter__(self):
        if self._content is None:
            raise RuntimeError("No content to write.")
    
    @abstractmethod
    def __exit__(self, *exc):
        raise NotImplementedError()
    
    @abstractmethod
    def authenticate(self, client: SyncClient | AsyncClient) -> SyncClient | AsyncClient:
        raise NotImplementedError()
    

class TemporaryCredentials(Credentials):
    def __init__(self):
        super().__init__()
        self._queue: queue.Queue = queue.Queue()

    def __enter__(self):
        # This creates a temporary directory for each context
        Credentials.__enter__(self)
        tempdir = TemporaryDirectory()
        self._queue.put(tempdir)
        with open(tempdir.name, "wb") as ofs:
            ofs.write(self._content)
        return tempdir

    def __exit__(self, *exc):
        self._queue.get().cleanup()
    

class ZippedCredentials(TemporaryCredentials):
    def __init__(self):
        super().__init__()

    def __enter__(self):
        # This creates a temporary directory for each context
        # to ensure the temporary directory is cleaned up after
        # use.
        tempdir = TemporaryDirectory()
        self._queue.put(tempdir)
        try:
            buffer = io.BytesIO(self._content)
            with zipfile.ZipFile(buffer, "r") as zf:
                zf.extractall(tempdir.name)
        except:
            self._queue.get()
            raise
        return tempdir
    
    def __exit__(self, *exc):
        self._queue.get().cleanup()

    
class TLSCredentials(ZippedCredentials):
    def __init__(self,
                 ca_cert: file_t | None=None,
                 cert: file_t | None=None,
                 key: file_t | None=None,):
        """
        TLS Certificates establish a bilateral authentication mechanism
        between the MQTT broker and the client. Three files are necessary
        to establish a secure connection:

            ca: A Certificate Authority file (.pem or .crt)
            cert: A certificate file (.pem or .crt)
            key: A private key file (.pem)

        These may be set through the constructor, by separate calls to
        eponymously named properties, through a zip archive stored locally
        or on Carta, or inferred from a file.

        Examples
        --------

            aclient = AsyncClient("localhost", 1883)
            client = SyncClient(CallbackAPIVersion.VERSION2)

            # 1. Multiple files are stored as a zip file, rather than as separate files.
            # 2. Files are stored based on a label or tag.

            # TLS Authentication from local files
            credentials = TLSCredentials().identify_certificates("srcdir/")
            credentials.authenticate(client)  # Authenticates a synchronous client.
            credentials.authenticate(aclient)  # Authenticates an async client.
            credentials.carta.write("/mqtt/aimpf.zip")  # Writes credentials to Carta

            # TLS Authentication from carta
            credentials = TLSCredentials().carta.read("mqtt/aimpf.zip")
            credentials.authenticate(client)
            credentials.local.write("destdir/aimpf_local.zip")  # Writes credentials to a folder.

            # TLS Authentication from specific files
            credentials = TLSCredentials()
            credentials.ca = "ca.crt"
            credentials.cert = "client.crt"
            credentials.key = "key.pem"
            credentials.authenticate(client)
            credentials.carta.write("/mqtt/contextualize.zip")
            # or equivalently
            credentials = TLSCredentials(ca_cert="ca.crt",
                                        cert="client.crt",
                                        key="key.pem")
            credentials.authenticate(client)
            credentials.carta.write("/mqtt/contextualize.zip")
        """
        super().__init__()
        self._ca: str | None = None
        self._cert: str | None = None
        self._key: str | None = None
        self._lock = Lock()
        if ca_cert:
            self.ca = str(ca_cert)
        if cert:
            self.cert = str(cert)
        if key:
            self.key = str(key)

    def validate(self, host: str, port: int) -> None:
        """
        Unpack ZIP if present, identify cert files, then call validate_tls_credentials
        exactly once (while the temp files still exist), and finally restore state.
        """
        # stash old attributes so we can restore them afterwards
        old = (self._ca, self._cert, self._key)

        if self._content is not None:
            # ZIP‐mode
            try:
                with self as tmp:
                    # 1) unpack → tmp.name
                    # 2) identify_ca,cert,key in that temp folder
                    self.identify_certificates(tmp.name, recursive=True)
                    ca, cert, key = self.ca, self.cert, self._key

                    # 3) validate *inside* the with (files still exist)
                    validate_tls_credentials(ca, cert, key, host, port)

            finally:
                # 4) restore your original attributes immediately
                self._ca, self._cert, self._key = old

        else:
            # manual‐mode: just run validate once on whatever was set by the user
            validate_tls_credentials(self.ca, self.cert, self._key, host, port)

    def _set_tls(self, client: SyncClient) -> None:
        """
        Hand off the already-validated cert/key to paho.Client.tls_set().
        Any SSLError here would be a true anomaly, but we catch it
        and re-raise as TLSSetupError for consistency.
        """
        try:
            client.tls_set(
                ca_certs=self.ca,
                certfile=self.cert,
                keyfile=self._key,
            )
        except ssl.SSLError as e:
            raise TLSSetupError() from e

    # Helper Functions
    def _read_cert(self, path: file_t) -> x509.Certificate:
        if isinstance(path, str):
            path = Path(path)
        with open(path, "rb") as ifs:
            content = ifs.read()
        try:
            return x509.load_pem_x509_certificate(content)
        except:
            logger.debug(f"{path!s} is not a valid certificate.")
            raise

    def _update(self) -> None:
        """
        Update the TLS certificate contents. Subsequent writes will
        write these contents.

        Note: Use `self.local.write(...)` or `self.carta.write(...)` to
        persist the content locally or on carta, respectively.
        """
        if not self.has_certs():
            raise RuntimeError("No certificates to update.")
        with BytesIO() as buffer:
            with zipfile.ZipFile(buffer, "w") as zf:
                for path in [self._ca, self._cert, self._key]:
                    zf.write(path, Path(path).name)
            self._content = buffer.getvalue()

    # ##### API ###### #
    # Properties
    @property
    def ca(self) -> str | None:
        return self._ca
    
    @ca.setter
    def ca(self, path: str | Path) -> None:
        try:
            cert = self._read_cert(path)
            # Check if certificate is for a Certificate Authority
            basic = cert.extensions.get_extension_for_class(x509.BasicConstraints)
            if not basic.value.ca:
                raise ValueError(f"{path!s} is not a Certificate Authority file.")
        except Exception as e:
            # logger.error(str(e))
            raise
        else:
            logger.debug(f"Certificate Authority file: {path!s}")
            self._ca = str(path)
            if self.has_certs():
                self._update()

    @property
    def cert(self) -> str | None:
        return self._cert
    
    @cert.setter
    def cert(self, path: str | Path) -> None:
        try:
            cert = self._read_cert(path)
            # Check if certificate is for a Certificate Authority
            basic = cert.extensions.get_extension_for_class(x509.BasicConstraints)
            if basic.value.ca:
                raise ValueError(f"{path!s} is a Certificate Authority file.")
        except x509.ExtensionNotFound:
            logger.debug(f"{path!s} does not contain a BasicConstraints extension: assuming certificate.")
            pass
        except Exception as e:
            # logger.error(str(e))
            raise
        logger.debug(f"Certificate file: {path!s}")
        self._cert = str(path)
        if self.has_certs():
            self._update()

    @property
    def key(self) -> str | None:
        return self._key
    
    @key.setter
    def key(self, path: str | Path) -> None:
        self.set_key(path, password=None)

    def set_key(self, path: str | Path, *, password: str | None=None) -> None:
        if isinstance(path, str):
            path = Path(path)
        try:
            with open(path, "rb") as ifs:
                serialization.load_pem_private_key(
                    ifs.read(),
                    password=password.encode() if password else None
                )
        except:
            # logger.debug(f"{path!s} is not a valid key file.")
            raise
        else:
            logger.debug(f"Key file: {path!s}")
            self._key = str(path)
            if self.has_certs():
                self._update()

    # Interface
    def authenticate(self, client: SyncClient | AsyncClient) -> SyncClient | AsyncClient:
        """
        Authorize the client to connect to the broker.

        Parameters
        ----------
        client : SyncClient | AsyncClient
            The client to authorize.

        Returns
        -------
        SyncClient | AsyncClient
            The authorized client.
        """
        if isinstance(client, SyncClient):
            # 1) pull the real host/port out of our Connection.kwargs
            host = self._connection.kwargs["host"]
            port = self._connection.kwargs["port"]

            # 2) run *all* of your checks
            self.validate(host, port)

            # 3) now hand off to Paho for TLS
            if self._content is not None:
                # ZIP mode: unpack once, identify & set
                with self as tmp:
                    self.identify_certificates(tmp.name, recursive=True)
                    self._set_tls(client)
            else:
                # manual‐mode: your setters already populated ca/cert/key
                self._set_tls(client)
            # only do the ZIP‐mode unpack/validate once
            self._content = None
            return client
        elif isinstance(client, AsyncClient):
            # delegate to sync branch (which now handles both cases correctly)
            _ = self.authenticate(client._client)
            return client
        else:
            raise ValueError(f"Unknown client type: {type(client)}")

    # Extensions
    def has_certs(self) -> bool:
        return self.ca and self.cert and self.key

    def identify_certificates(self, folder: str | Path, *, password: str | None=None, recursive: bool=False) -> "TLSCredentials":
        """
        Identify the certificate, key, and CA filenames in the given folder.
        This operation is greedy, taking the first key, server, and certificate
        authority files found.

        Parameters
        ----------
        folder : str | Path
            The folder to be searched.

        password : Optional[str]
            The key file's password, if required. Default: None.
        
        recursive : Optional[bool]
            Whether to search a directory recursively. Default: False.

        Returns
        -------
        None
            Updates ca, cert, and key member variables with the filenames.
        """
        if isinstance(folder, str):
            folder = Path(folder)
        for filename in folder.iterdir():
            logger.debug(f"Processing {filename!s}")
            if filename.is_dir():
                # Skip the macOS metadata folder (and any hidden dirs)
                if filename.name == "__MACOSX" or filename.name.startswith("."):
                    continue
                if recursive:
                    try:
                        self.identify_certificates(filename, password=password, recursive=recursive)
                    except FileNotFoundError:
                        # no certs down that branch? ignore and keep looking
                        continue
                    # if the recursive call found everything, stop here
                    if self.has_certs():
                        break
                else:
                    continue
            # Skip ZIP files
            # TODO: ZIP files that contain certificates are read by the x509
            # library, but that is not necessary given the current structure.
            # ZIP could replace certificate files: ZIP is x509 readable? Y.
            # Then delete key, ca, and cert files and load ZIP.
            if filename.suffix == ".zip":
                continue
            # Check for key
            if self.key is None:
                try:
                    self.set_key(filename, password=password)
                except:
                    pass
            # Check certificates
            if self.ca is None:
                try:
                    self.ca = filename
                except:
                    pass
            if self.cert is None:
                try:
                    self.cert = filename
                except:
                    pass
            # All files found
            if self.has_certs():
                logger.debug(f"Found all certificate files in {folder!s}")
                self._update()
                break
        else:
            raise FileNotFoundError(f"Could not identify certificate files in {folder!s}")
        return self

    def unset_certs(self) -> None:
        self._ca = None
        self._cert = None
        self._key = None
