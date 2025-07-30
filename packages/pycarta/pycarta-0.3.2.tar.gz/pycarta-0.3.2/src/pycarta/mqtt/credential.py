import logging
import os
from typing import Optional, Dict
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
import tempfile
import paho.mqtt.client as paho

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from ..admin.file import list_files, get_file

logger = logging.getLogger(__name__)

MQTT_DIR = "/mqtt_credentials"


class CertificateFileType(Enum):
    """
    Enumerated certificate file types. Similar to dict keys, but with better type checking.
    """

    BROKER_ADDRESS = "broker_address.pem"
    CERTIFICATE = "certificate.pem"
    PRIVATE_KEY = "private_key.pem"
    CA_CERTIFICATE = "ca_certificate.pem"

    @classmethod
    def get_filename(cls, file_type: str) -> str:
        """
        Get the filename for a certificate file type.

        Parameters
        ----------
        file_type : str
            The type of file (e.g., 'broker_address', 'certificate', etc.).

        Returns
        -------
        str
            The corresponding filename (e.g., 'broker_address.pem').

        Raises
        ------
        ValueError
            If the file_type is not recognized.
        """
        try:
            return cls[file_type.upper()].value
        except KeyError:
            raise ValueError(f"{file_type!r} is not a recognized certificate file type.")


class BaseMqttAuthenticator(ABC):
    """
    Abstract base class for an MQTT credential agent. Provides a method to create a paho-mqtt.Client 
    with relevant authentication.

    Subclasses must implement the `client` method.
    """

    @abstractmethod
    def client(self, client_id: Optional[str] = None, clean_session: bool = True, **kwargs) -> paho.Client:
        """
        Return a paho.Client configured for TLS or other authentication.

        Parameters
        ----------
        client_id : str, optional
            The MQTT client ID.
        clean_session : bool, optional
            Whether to use a clean session.
        **kwargs
            Additional keyword arguments passed to the paho.Client constructor.

        Returns
        -------
        paho.mqtt.client.Client
            A configured paho MQTT client.
        """
        raise NotImplementedError()


class BilateralCredentialAuthenticator(BaseMqttAuthenticator):
    """
    A concrete authenticator that uses CA certificate, private key, and client certificate 
    to configure a paho.Client with TLS.

    NOTE: It writes the certificate contents into a **temporary directory** 
    (one per authenticator). That directory is automatically cleaned up 
    when this object is **garbage-collected** or deleted.

    For example usage:
    
        # Approach #1: Using local file paths
        auth = BilateralCredentialAuthenticator.from_cert_files(
            ca_cert='/path/to/ca.pem',
            cert='/path/to/client_cert.pem',
            key='/path/to/client_key.pem'
        )
        mqtt_client = auth.client(client_id='myClient')
        mqtt_client.connect('mybroker', 8883)
        ...

    Or:
        # Approach #2: Using a folder that already has the 3 PEM files
        auth = BilateralCredentialAuthenticator.from_folder('/path/to/folder')

    Or:
        # Approach #3: Using Carta credentials (tag-based)
        auth = BilateralCredentialAuthenticator.from_carta(tag='my-latest-credentials')
    """

    def __init__(self, ca_cert: str, key: str, cert: str):
        """
        Parameters
        ----------
        ca_cert : str
            CA certificate (PEM-encoded).
        key : str
            Private key (PEM-encoded).
        cert : str
            Client certificate (PEM-encoded).
        """
        # NOTE: This creates a named temporary directory for the CA/cert/key files.
        self._tempdir = tempfile.TemporaryDirectory()
        self._dir_path = Path(self._tempdir.name)

        self._ca_cert_path = self._dir_path / "ca_cert.pem"
        self._key_path = self._dir_path / "client_key.pem"
        self._cert_path = self._dir_path / "client_cert.pem"

        self._write_file(self._ca_cert_path, ca_cert)
        self._write_file(self._key_path, key)
        self._write_file(self._cert_path, cert)

    def __del__(self):
        # NOTE: The destructor calls _tempdir.cleanup(), removing 
        #       the temporary folder and its files automatically.
        self._tempdir.cleanup()

    def _write_file(self, path: Path, content: str):
        """
        Writes the given content into the specified file path.

        Parameters
        ----------
        path : Path
            The file path where content is to be written.
        content : str
            The string content to write.
        """
        with open(path, "w") as f:
            f.write(content)

    @property
    def ca_cert_path(self) -> str:
        """
        Returns
        -------
        str
            The path to the CA certificate file.
        """
        return str(self._ca_cert_path)

    @property
    def key_path(self) -> str:
        """
        Returns
        -------
        str
            The path to the private key file.
        """
        return str(self._key_path)

    @property
    def cert_path(self) -> str:
        """
        Returns
        -------
        str
            The path to the client certificate file.
        """
        return str(self._cert_path)

    def client(self, client_id: Optional[str] = None, clean_session: bool = True, **kwargs) -> paho.Client:
        """
        Return a paho.Client configured for TLS using the ephemeral files.

        Parameters
        ----------
        client_id : str, optional
            The MQTT client ID.
        clean_session : bool, optional
            Whether to use a clean session.
        **kwargs
            Additional keyword arguments for the paho.Client constructor.

        Returns
        -------
        paho.mqtt.client.Client
            A configured paho MQTT client with TLS set.
        """
        mqtt_client = paho.Client(client_id=client_id, clean_session=clean_session, **kwargs)
        mqtt_client.tls_set(
            ca_certs=self.ca_cert_path,
            certfile=self.cert_path,
            keyfile=self.key_path
        )
        return mqtt_client

    # Method 1
    @classmethod
    def from_cert_files(cls, ca_cert: str, cert: str, key: str) -> "BilateralCredentialAuthenticator":
        """
        Create a BilateralCredentialAuthenticator by reading three PEM files from disk.

        Parameters
        ----------
        ca_cert : str
            Path to the CA certificate file.
        cert : str
            Path to the client certificate file.
        key : str
            Path to the private key file.
        """
        with open(ca_cert, "r", encoding="utf-8") as f_ca, \
             open(cert, "r", encoding="utf-8") as f_cert, \
             open(key, "r", encoding="utf-8") as f_key:
            ca_text = f_ca.read()
            cert_text = f_cert.read()
            key_text = f_key.read()

        return cls(ca_cert=ca_text, cert=cert_text, key=key_text)

    # Method 2
    @classmethod
    def from_folder(cls, folder_path: str) -> "BilateralCredentialAuthenticator":
        """
        Auto-detect CA certificate, client certificate, and private key from a folder 
        and build a BilateralCredentialAuthenticator.

        Returns
        -------
        BilateralCredentialAuthenticator
            An authenticator whose ephemeral files point to the discovered certs.
        """
        ca_text, cert_text, key_text = _load_credentials_from_folder(folder_path)
        return cls(ca_cert=ca_text, cert=cert_text, key=key_text)

    # Method 3
    @classmethod
    def from_carta(cls, tag: Optional[str] = None, *, agent: Optional[object] = None) -> "BilateralCredentialAuthenticator":
        """
        Create a BilateralCredentialAuthenticator by retrieving credentials from Carta. 
        This loads CA certificate, client certificate, and private key from the specified `tag`.

        Parameters
        ----------
        tag : str, optional
            Which subdirectory or 'tag' to find the cert files under in Carta.
        agent : object, optional
            The HTTP agent to use for retrieving. If None, uses default get_agent().

        Raises
        ------
        ValueError
            If the needed files aren't found or are incomplete.

        Returns
        -------
        BilateralCredentialAuthenticator
        """
        if not agent:
            from pycarta import get_agent
            agent = get_agent()

        manager = CredentialManager(agent=agent)

        def find_and_download(file_type: str) -> str:
            file_id = manager.find_file_id(file_type, tag)
            if not file_id:
                raise ValueError(f"Could not find file_type='{file_type}' in tag='{tag}'.")
            file_bytes = get_file("Carta", file_id, agent=agent)
            return file_bytes.decode("utf-8") if file_bytes else ""

        ca_text = find_and_download("ca_certificate")
        cert_text = find_and_download("certificate")
        key_text = find_and_download("private_key")

        if not (ca_text and cert_text and key_text):
            raise ValueError(f"Incomplete Carta credentials in tag '{tag}'. Missing one or more PEM files.")

        return cls(ca_cert=ca_text, cert=cert_text, key=key_text)
        

class CredentialManager:
    """
    Manages MQTT credentials including upload, download, delete, and list operations.

    Parameters
    ----------
    agent : Optional[object]
        The agent handling HTTP requests. If None, uses get_agent().
    mqtt_dir : str, optional
        The directory path for MQTT credentials, by default "/mqtt_credentials".
    """

    def __init__(self, agent: Optional[object] = None, mqtt_dir: str = MQTT_DIR):
        """
        Initializes the CredentialManager.

        Parameters
        ----------
        agent : object, optional
            The HTTP agent to use. If None, get_agent() is called.
        mqtt_dir : str, optional
            The directory where credential files are stored, by default "/mqtt_credentials".

        Raises
        ------
        ValueError
            If no agent can be obtained.
        """
        from pycarta import get_agent
        self.agent = agent or get_agent()
        if not self.agent:
            raise ValueError("No agent available. An agent must be provided or retrieved via get_agent().")

        self.mqtt_dir = mqtt_dir
        logger.debug(f"CredentialManager created with agent host={getattr(self.agent, 'host', 'Unknown')}")

    def upload_file(self, file_type: str, content: str, tag: Optional[str] = None, overwrite: bool = False) -> bool:
        """
        Upload or update a credential file.

        Parameters
        ----------
        file_type : str
            The type of file, must be one of the following: 'BROKER_ADDRESS', 'CERTIFICATE', 'PRIVATE_KEY', and 'CA_CERTIFICATE'.
        content : str
            The content of the file.
        tag : str, optional
            The tag to store under, by default None.
        overwrite : bool, optional
            Whether to overwrite the existing file, by default False.

        Returns
        -------
        bool
            True if the upload was successful, False otherwise.
        """
        if not self.agent:
            logger.error("Agent is not initialized. Cannot proceed with file upload.")
            return False

        try:
            filename = CertificateFileType.get_filename(file_type)
        except ValueError as e:
            logger.error(e)
            return False

        tag_dir = f"{self.mqtt_dir}/{tag}" if tag else self.mqtt_dir
        file_path = f"{tag_dir}/{filename}"
        file_id = self.find_file_id(file_type, tag)

        if file_id and not overwrite:
            logger.warning(f"{file_type} already exists under tag '{tag}'. Skipping upload.")
            return False

        url = f"/files/Carta/file/{file_id}" if file_id else f"/files/Carta"
        files = {"file": (file_path, content.encode("utf-8"), "application/octet-stream")}
        data = {"path": tag_dir}

        try:
            if file_id:
                response = self.agent.patch(url, files=files)
            else:
                response = self.agent.post(url, files=files, data=data)
            response.raise_for_status()
            logger.info(f"{'Updated' if file_id else 'Uploaded'} {file_type} successfully to {tag_dir}.")
            return True
        except Exception as e:
            logger.error(f"Failed to {'update' if file_id else 'upload'} {file_type}: {e}", exc_info=True)
            return False

    def download_file(self, file_type: str, tag: Optional[str] = None) -> Optional[str]:
        """
        Download a credential file.

        Parameters
        ----------
        file_type : str
            The type of file, must be one of the following:'BROKER_ADDRESS', 'CERTIFICATE', 'PRIVATE_KEY', and 'CA_CERTIFICATE'.
        tag : str, optional
            The tag to download from, by default None.

        Returns
        -------
        str or None
            The file content if successful, otherwise None.
        """
        if not self.agent:
            logger.error("Agent is not initialized. Cannot proceed with file download.")
            return None

        try:
            filename = CertificateFileType.get_filename(file_type)
        except ValueError as e:
            logger.error(e)
            return None

        file_id = self.find_file_id(file_type, tag)
        if not file_id:
            logger.warning(f"{file_type} not found on the server under tag '{tag}'.")
            return None

        try:
            url = f"/files/Carta/file/{file_id}"
            response = self.agent.get(url)
            response.raise_for_status()
            logger.info(f"Downloaded {file_type} successfully from tag '{tag}' (ID: {file_id}).")
            return response.text
        except Exception as e:
            logger.error(f"Failed to download {file_type} for tag '{tag}': {e}", exc_info=True)
            return None

    def find_file_id(self, file_type: str, tag: Optional[str] = None) -> Optional[str]:
        """
        Find a file ID by file type under a specific tag directory.

        Parameters
        ----------
        file_type : str
            The type of file, must be one of the following:'BROKER_ADDRESS', 'CERTIFICATE', 'PRIVATE_KEY', and 'CA_CERTIFICATE'.
        tag : str, optional
            The tag to search under, by default None.

        Returns
        -------
        str or None
            The file ID if found, otherwise None.
        """
        if not self.agent:
            logger.error("Agent is not initialized. Cannot proceed with file ID lookup.")
            return None

        try:
            filename = CertificateFileType.get_filename(file_type)
        except ValueError as e:
            logger.error(e)
            return None

        directory = f"{self.mqtt_dir}/{tag}" if tag else self.mqtt_dir
        try:
            files = list_files(source="Carta", path=directory)
            for f in files:
                if f.name == filename and f.path.startswith(directory):
                    return f.id
            logger.debug(f"{file_type} not found under tag '{tag}'.")
            return None
        except Exception as e:
            logger.error(f"Failed to list files for {file_type} in {directory}: {e}", exc_info=True)
            return None

    def delete_file(self, file_type: str, tag: Optional[str] = None) -> bool:
        """
        Delete a credential file.

        Parameters
        ----------
        file_type : str
            The type of file, must be one of the following:'BROKER_ADDRESS', 'CERTIFICATE', 'PRIVATE_KEY', and 'CA_CERTIFICATE'.
        tag : str, optional
            The tag to delete from, by default None.

        Returns
        -------
        bool
            True if the file was deleted, False otherwise.
        """
        try:
            filename = CertificateFileType.get_filename(file_type)
        except ValueError as e:
            logger.error(e)
            return False

        file_id = self.find_file_id(file_type, tag)
        if not file_id:
            logger.debug(f"{file_type} not found, no need to delete for tag '{tag}'.")
            return False

        try:
            self.agent.delete(f"/files/Carta/file/{file_id}")
            logger.info(f"Deleted {file_type} successfully from tag '{tag}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {file_type} for tag '{tag}': {e}", exc_info=True)
            return False

    def list_credentials(self, tag: Optional[str] = None) -> Optional[Dict[str, Dict[str, str]]]:
        """
        List all available MQTT credential files on the server for a specific tag.

        Parameters
        ----------
        tag : str, optional
            The tag to list credentials from, by default None.

        Returns
        -------
        dict of str to dict of str, or None
            A dictionary of credential info if successful, or None on failure.
        """
        if not self.agent:
            logger.error("Agent is not initialized. Cannot proceed with listing credentials.")
            return None

        directory = f"{self.mqtt_dir}/{tag}" if tag else self.mqtt_dir
        try:
            files = list_files(source="Carta", path=directory)
            credentials = {}
            for file_type in CertificateFileType:
                for f in files:
                    if f.name == file_type.value:
                        credentials[file_type.name.lower()] = {
                            "id": f.id,
                            "name": f.name,
                            "path": f.path
                        }
            logger.info(f"Available credentials for tag '{tag}': {credentials}")
            return credentials
        except Exception as e:
            logger.error(f"Failed to list available credentials for tag '{tag}': {e}", exc_info=True)
            return None


def upload_mqtt_credentials(credentials: Optional[Dict[str, str]] = None,
                            file_paths: Optional[Dict[str, str]] = None,
                            tag: Optional[str] = None,
                            overwrite: bool = False) -> bool:
    """
    Upload MQTT credentials from strings or file paths, not both.

    Parameters
    ----------
    credentials : dict of str to str, optional
        A dictionary of file types and their contents.
    file_paths : dict of str to str, optional
        A dictionary of file types and their file paths.
    tag : str, optional
        The tag (subdirectory) to store files under.
    overwrite : bool, optional
        Whether to overwrite existing files, by default False.

    Returns
    -------
    bool
        True if all credentials were successfully uploaded, False otherwise.
    """
    if (credentials and file_paths) or (not credentials and not file_paths):
        logger.error("Provide either 'credentials' or 'file_paths', but not both or neither.")
        return False

    manager = CredentialManager()
    success = True

    # Upload credentials provided as strings
    if credentials:
        for file_type, content in credentials.items():
            if not manager.upload_file(file_type, content, tag, overwrite):
                logger.error(f"Failed to upload {file_type} for tag '{tag}'.")
                success = False

    # Upload credentials from file paths
    if file_paths:
        for file_type, file_path in file_paths.items():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if not manager.upload_file(file_type, content, tag, overwrite):
                        logger.warning(f"Skipped uploading {file_type} from {file_path} to tag {tag}.")
                        success = False
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
                success = False
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
                success = False

    if success:
        logger.info(f"Successfully uploaded all MQTT credentials to tag '{tag}'.")
    return success

def retrieve_mqtt_credentials(tag: Optional[str] = None,
                              file_paths: Optional[Dict[str, str]] = None) -> Optional[Dict[str, str]]:
    """
    Retrieve MQTT credentials from a specified tag, optionally saving them to files.

    Parameters
    ----------
    tag : str, optional
        The tag (subdirectory) to retrieve from.
    file_paths : dict of str to str, optional
        A mapping of file types to paths to save the retrieved credentials.

    Returns
    -------
    dict of str to str or None
        A dictionary of file types to file contents if successful, else None.
    """
    manager = CredentialManager()
    credentials = {}
    for file_type in CertificateFileType:
        content = manager.download_file(file_type.name.lower(), tag)
        if content is None:
            logger.error(f"Failed to retrieve {file_type.name.lower()} for tag '{tag}'.")
            return None
        credentials[file_type.name.lower()] = content

        # Save to file if file paths are provided
        if file_paths and file_type.name.lower() in file_paths:
            file_path = file_paths[file_type.name.lower()]
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Saved {file_type.name.lower()} to {file_path} for tag '{tag}'.")
            except Exception as e:
                logger.error(f"Error saving {file_type.name.lower()} to {file_path}: {e}", exc_info=True)
                return None

    logger.info(f"Successfully retrieved MQTT credentials for tag '{tag}'.")
    return credentials

def update_mqtt_credentials(updates: Dict[str, Optional[str]] = None,
                            file_paths: Dict[str, Optional[str]] = None,
                            tag: Optional[str] = None) -> bool:
    """
    Update MQTT credentials under a specific tag using new string contents or file paths.

    Parameters
    ----------
    updates : dict of str to str, optional
        A dictionary of file types to updated string contents.
    file_paths : dict of str to str, optional
        A dictionary of file types to file paths containing new contents.
    tag : str, optional
        The tag (subdirectory) to update.

    Returns
    -------
    bool
        True if all updates were successful, False otherwise.
    """
    manager = CredentialManager()
    success = True

    if updates:
        for file_type, content in updates.items():
            if content is not None:
                if not manager.upload_file(file_type, content, tag, overwrite=True):
                    logger.error(f"Failed to update {file_type} with string for tag '{tag}'.")
                    success = False

    if file_paths:
        for file_type, fp in file_paths.items():
            try:
                with open(fp, 'r') as f:
                    content = f.read()
                    if not manager.upload_file(file_type, content, tag, overwrite=True):
                        logger.error(f"Failed to update {file_type} from file for tag '{tag}'.")
                        success = False
            except Exception as e:
                logger.error(f"Error reading file {fp}: {e}", exc_info=True)
                success = False

    return success

def delete_mqtt_credentials(tag: Optional[str] = None) -> bool:
    """
    Delete all MQTT credentials under a specific tag.

    Parameters
    ----------
    tag : str, optional
        The tag (subdirectory) to delete from.

    Returns
    -------
    bool
        True if all credentials were successfully deleted, False otherwise.
    """
    manager = CredentialManager()
    success = True
    for file_type in CertificateFileType:
        if not manager.delete_file(file_type.name.lower(), tag):
            logger.error(f"Failed to delete {file_type.name.lower()} for tag '{tag}'.")
            success = False
    if success:
        logger.info(f"Successfully deleted all MQTT credentials for tag '{tag}'.")
    return success

def list_mqtt_credentials(tag: Optional[str] = None) -> Optional[Dict[str, Dict[str, str]]]:
    """
    List all MQTT credential files on the server for a specific tag.

    Parameters
    ----------
    tag : str, optional
        The tag (subdirectory) to list credentials from.

    Returns
    -------
    dict of str to dict of str, or None
        A mapping of file type to credential metadata, or None if listing failed.
    """
    manager = CredentialManager()
    try:
        credentials = manager.list_credentials(tag)
        if credentials:
            logger.info(f"Available credentials for tag '{tag}': {credentials}")
        return credentials
    except Exception as e:
        logger.error(f"Failed to list available credentials for tag '{tag}': {e}", exc_info=True)
        return None

def _load_credentials_from_folder(folder_path: str, *, password: Optional[str] = None):
    """
    Auto-detect CA certificate, client certificate, and private key from a folder by parsing each file's PEM contents with `cryptography`.

    Parameters
    ----------
    folder_path : str
        The filesystem path to a folder containing (at least) three PEM files: CA cert, client cert, private key.
    password : str, optional
        An optional password for the private key. Defaults to None, meaning no password is assumed. If your private key is encrypted with a passphrase, provide it here.

    Returns
    -------
    (ca_cert_text, client_cert_text, private_key_text) : tuple of str
        The discovered contents of the CA certificate, client certificate, and private key.

    Raises
    ------
    ValueError
        If it fails to find exactly one of each piece or cannot parse the file, or if the user passes a wrong password for an encrypted key.
    """
    ca_cert_text: Optional[str] = None
    client_cert_text: Optional[str] = None
    private_key_text: Optional[str] = None

    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    logger.info("Files found in %r: %s", folder_path, files)

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if not content:
            logger.debug("Skipping empty file: %s", file_path)
            continue

        logger.debug("Examining file: %s", file_path)

        # Attempt to parse a private key (possibly password-protected)
        try:
            serialization.load_pem_private_key(
                content.encode('utf-8'),
                password=password.encode('utf-8') if password else None
            )
            logger.info("Identified private key in %s", file_path)
            private_key_text = content
            continue
        except ValueError:
            pass

        # Attempt to parse a certificate
        try:
            cert_obj = x509.load_pem_x509_certificate(content.encode('utf-8'))
            try:
                basic_constraints = cert_obj.extensions.get_extension_for_class(x509.BasicConstraints)
                if basic_constraints.value.ca:
                    logger.info("Identified CA certificate in %s", file_path)
                    ca_cert_text = content
                else:
                    logger.info("Identified client certificate in %s", file_path)
                    client_cert_text = content
            except x509.ExtensionNotFound:
                logger.info("No BasicConstraints; treating as client cert: %s", file_path)
                client_cert_text = content
        except ValueError:
            logger.debug("Not a valid private key or X.509 cert: %s", file_path)

    missing = []
    if not private_key_text:
        missing.append("private key")
    if not client_cert_text:
        missing.append("client certificate")
    if not ca_cert_text:
        missing.append("CA certificate")

    if missing:
        raise ValueError(
            f"Could not identify {', '.join(missing)} in folder: {folder_path}"
        )

    logger.info(
        "Successfully identified CA cert, client cert, and private key in folder '%s'.",
        folder_path
    )
    return ca_cert_text, client_cert_text, private_key_text
