import os
import logging
import sevenbridges as sbg
from contextlib import contextmanager
from sevenbridges.transfer.download import Download as SbgDownload
from sevenbridges.transfer.upload import Upload as SbgUpload
from tempfile import NamedTemporaryFile
from typing import Any, Optional, Union


logger = logging.getLogger(__name__)


class SbgFile:
    def __init__(self,
                 path: None | str =None,
                 *,
                 name: None | str=None,
                 project: None | str | sbg.Project=None,
                 api: None | sbg.Api=None,
                 file: None | sbg.File=None,
    ):
        """
        Object to manage a file that may exist on a local or remote system.

        Parameters
        ----------
        path : str 
            Local file name. Default: None (local file name will be constructed
            from the remote file name).
        name : str
            Exact file name on the remote server. Default: None.
        project : str | sevenbridges.Project
            Project name or object. Default: None.
        api : sevenbridges.Api
            API object. Default: None.
        file : sevenbridges.File
            File object. Default: None.

        Examples
        --------
        >>> api = sbg.Api()
        >>> filename = "_5_cmd.out"
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     name=filename,
        ...     project=project,
        ...     api=api,
        ... )
        >>> assert True

        Alternatively, an SbgFile can be created directly from a
        sevenbridges.File object.
        """
        logger.debug(f"SbgFile(path={path}, name={name}, project={project}, api={api}, "
                     f"file={file})")
        self._remote: None | sbg.File=None
        self._local: None | str = path
        if name and project:
            self._api = api or sbg.Api()
            self._remote = self._api.files.query(
                project=project,
                names=[name],
            )[0]
        else:
            self._remote = file

    @property
    def local(self) -> None | str:
        """
        Returns the local file path as a string.
        
        Examples
        --------
        >>> api = sbg.Api()
        >>> filename = "_5_cmd.out"
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     name=filename,
        ...     project=project,
        ...     api=api,
        ... )
        >>> assert file.local == filename
        """
        return self._local or getattr(self._remote, "name", None)
    
    @local.setter
    def local(self, value: str):
        """
        Sets the local file path from a string or Path.

        Examples
        --------
        >>> api = sbg.Api()
        >>> filename = "_5_cmd.out"
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     name=filename,
        ...     project=project,
        ...     api=api,
        ... )
        >>> file.local = "myfile.ext"
        >>> assert file.local == "myfile.ext"
        """
        self._local = value

    @property
    def remote(self) -> None | sbg.File:
        """
        Returns the remote file object.
        """
        return self._remote
    
    @remote.setter
    def remote(self, value: sbg.File):
        """Sets the remote file object."""
        self._remote = value
    
    @contextmanager
    def open(self, mode='r'):
        """
        Context manager to operate on the local file.

        Parameters
        ----------
        mode : str
            File open mode.

        Yields
        ------
        resource : file

        Examples
        --------
        >>> file = SbgFile(
        ...     path="hello.txt"
        ... )
        >>> with file.open("w") as f:
        ...     f.write("Hello, World!")
        13
        >>> with file.open("r") as f:
        ...     print(f.read())
        Hello, World!
        """
        if self.local is None:
            raise ValueError("No local path set.")
        resource = open(self.local, mode)
        try:
            yield resource
        finally:
            resource.close()

    @contextmanager
    def pull(self, path: None | str=None, cleanup: bool=False, **download_opts):
        """
        Context manager to download the remote file for local work.

        Parameters
        ----------
        path : str | Path
            Local file path. If not provided, a temporary file is created.
            Note that, by default, the content of this file will be overwritten.

        cleanup : bool
            Whether to remove the file into which the content was pulled. This
            is only material if a `path` is specified; temporary files are
            always removed.

        download_opts : dict
            Download options (see ``File.download``).

        Yields
        ------
        resource : file

        Examples
        --------
        >>> api = sbg.Api()
        >>> filename = "_1_hello.txt"
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     name=filename,
        ...     project=project,
        ...     api=api,
        ... )
        >>> with file.pull("tempfile", cleanup=True) as f:
        ...     print(f.read().strip())
        b'Hello, Chen.'
        """
        download_opts.setdefault("wait", True)
        # with open(path, "w+b") if path else NamedTemporaryFile("w+b", delete=False) as f:
        #     logger.info(f"Pulling file {self.remote} into {path or f.name}")
        #     self.download(path=f.name, **download_opts)
        #     f.seek(0)
        #     logger.info(f"Contents: {f.read()}")
        #     yield f
        if path:
            self.download(path=path, **download_opts)
            resource = open(path, "r+b")
        else:
            resource = NamedTemporaryFile("w+b", delete=False)
            self.download(path=resource.name, **download_opts)
            resource.close()
            resource = open(resource.name, "r+b")
        # resource = open(path, "w+b") if path else NamedTemporaryFile("w+b", delete=False)
        # self.download(path=resource.name, **download_opts)
        # resource.close()
        try:
            # resource = open(resource.name, "r+b")
            yield resource
        finally:
            resource.close()
            if cleanup or not path:
                # delete temporary file
                os.remove(resource.name)

    @contextmanager
    def push(self,
             mode="r+b",
             path: None | str=None,
             **upload_opts
    ):
        """
        Context manager to open and edit a local file which is then pushed to
        the remote upon exiting the context. If a path is provided in the upload


        Parameters
        ----------
        mode : str
            File open mode. Default is ``r+b``.

        path : str | Path
            Local file path. If not provided, a temporary file is created.

        project : str
            Project name. Default: None.

        upload_opts : dict
            Upload options (see ``File.upload``).

        Yields
        ------
        resource : file

        Examples
        --------
        >>> api = sbg.Api()
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     path="hello.txt",
        ...     api=api,
        ... )
        >>> with file.push(mode="w+b", project=project, overwrite=True) as f:
        ...     f.write(b"Hello, World!")
        13
        >>> with file.pull() as f:
        ...     print("Remote contents for", file.remote.name)
        ...     assert f.read() == b"Hello, World!"
        Remote contents for hello.txt
        """
        dest = os.path.basename(path) if path else self.local
        upload_opts.setdefault("wait", True)
        upload_opts.setdefault("file_name", dest)
        resource = open(path, mode) if path else NamedTemporaryFile("w+b")
        try:
            yield resource
            resource.seek(0)
            self.upload(path=resource.name, **upload_opts)
        finally:
            resource.close()

    # # proxy methods to the remote file object
    # def __getattr__(self, name):
    #     attr = getattr(self, name)
    #     if attr is None:
    #         if self._remote is None:
    #             raise ValueError("No file set.")
    #         return getattr(self._remote, name)

    def download(self, *args, **kwds) -> SbgDownload:
        """
        Download the remote file to the local path.

        Parameters
        ----------
        path : str | Path
            Local file path. By default this is ``File.local``.

        retry : int
            Number of times to retry the download.

        timeout : int
            Timeout in seconds.

        chunk_size : int
            Chunk size in bytes.

        wait : bool
            Wait for the download to complete. If False, it is the
            responsibility of the caller to manage the download, e.g.

            ```
            download.start() # to start the download
            download.pause() # to pause the download
            download.resume() # to resume the download
            download.stop() # to stop the download
            download.wait() # to wait for the download to complete
            ```
        
        overwrite : bool
            Overwrite the local file if it exists.

        Returns
        -------
        downloader : sevenbridges.transfer.download.Download

        Examples
        --------
        >>> api = sbg.Api()
        >>> filename = "_8_hello-world.txt"
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     name=filename,
        ...     project=project,
        ...     api=api,
        ... )
        >>> file.download()
        >>> with file.pull() as remote:
        ...     remote_content = remote.read()
        ...     with file.open("rb") as local:
        ...         local_content = local.read()
        ...         assert remote_content == local_content, f"{remote_content[:15]} != {local_content[:15]}"
        """
        if self._remote is None:
            raise ValueError("No file set.")
        opts = {k:v for k,v in zip(["path",
                                    "retry",
                                    "timeout",
                                    "chunk_size",
                                    "wait",
                                    "overwrite",],
                                    args)}
        opts.update(kwds)
        opts.setdefault("path", self.local)
        opts.setdefault("wait", True)
        opts.setdefault("overwrite", True)
        logger.info(f"Downloading to {opts['path']}: download({opts})")
        # TODO: This deletes the file before replacing the contents because of an apparent bug in SBG (sbg.File.download()).
        # Overwrite does not work on Windows. Confirmed on sevenbridges-python==2.11.0.
        if os.path.exists(opts["path"] and opts["overwrite"]):
            os.remove(opts["path"])
            logger.debug(f"Deleted {opts['path']}.")
        return self._remote.download(**opts)

    def upload(self, *args, update: bool=True, **kwds) -> SbgUpload:
        """
        Upload the local file to the remote path.

        Parameters
        ----------
        path : str | Path
            Local file path. By default this is ``File.local``.

        project : str
            Remote project name.
        
        parent : str
            Remote parent folder.

        file_name : str
            Remote file name. Default: Same as local.

        overwrite : bool
            Overwrite the remote file if it exists.

        retry : int
            Number of retries if an error occurs during upload.

        timeout : float
            HTTP request timeout.

        part_size : int
            Part size in bytes.

        wait : bool
            Wait for the upload to complete. If False, it is the
            responsibility of the caller to manage the upload, e.g.

            ```
            upload.start() # to start the upload
            upload.pause() # to pause the upload
            upload.resume() # to resume the upload
            upload.stop() # to stop the upload
            upload.wait() # to wait for the upload to complete
            ```
        api : sevenbridges.Api
            API object. Default: None. If not provided, the default API
            object is used.

        Returns
        -------
        upload : sevenbridges.transfer.upload.Upload

        Examples
        --------
        >>> api = sbg.Api()
        >>> project = "contextualize/sandbox-branden"
        >>> file = SbgFile(
        ...     path="hello.txt",
        ...     api=api,
        ... )
        >>> with file.open("w") as f:
        ...     f.write("Hello, World!")
        13
        >>> file.upload(project=project, update=True, overwrite=True)
        <Upload: status=COMPLETED>
        >>> with file.pull() as remote:
        ...     lhs = remote.read()
        ...     with file.open("rb") as local:
        ...         rhs = local.read()
        ...         assert lhs == rhs, f"{lhs[:15]} != {rhs[:15]}"
        """
        opts = {k:v for k,v in zip(["path",
                                    "project",
                                    "parent",
                                    "file_name",
                                    "overwrite",
                                    "retry",
                                    "timeout",
                                    "part_size",
                                    "wait",
                                    "api",],
                                    args)}
        opts.update(kwds)
        opts.setdefault("path", self.local)
        opts.setdefault("wait", True)
        logger.debug(f"Uploading from {opts['path']}: upload({opts})")
        uploader = self.remote or opts.get("api", sbg.Api()).files
        upload = uploader.upload(**opts)
        # update the remote file object
        if opts["wait"] and update:
            self._remote = upload.result()
        return upload


class CwlType:
    def __init__(self,
        *,
        id: None | str=None,
        type: None | str | list | dict=None,
        **kwds
    ):
        """
        Class for defining python protocols (types) from CWL types.

        Parameters
        ----------
        id : None | str
            Identifier, i.e., the variable name.

        type : None | str | list | dict
            CWL type.
        """
        self.id = id
        self.cwl_type = type
        for k, v in kwds.items():
            setattr(self, k, v)

    def __str__(self):
        """
        String representation of the CWL type.

        Returns
        -------
        str
        
        Examples
        --------
        >>> str(CwlType(id="foo", type="string"))
        'foo: str'
        >>> str(CwlType(id="foo", type="string?"))
        'foo: typing.Optional[str]'
        >>> str(CwlType(id="foo", type={"type": "array", "items": "string"}))
        'foo: list[str]'
        """
        type_ = self.type(self.cwl_type)
        if hasattr(type_, "__origin__"):
            return f"{self.id}: {type_}"
        else:
            return f"{self.id}: {type_.__name__}"
       
    def optional(self,
        cwl_type: None | str | list | dict=None,
        *,
        recurse: bool=False
    ) -> bool:
        """
        Check if a CWL type is optional.

        Parameters
        ----------
        cwl_type : None | str | list | dict
            CWL type. By default this returns whether the type of the instance
            is optional.

        recurse : bool
            Recursively check if the arguments to generics are optional.
            Default: False.

        Returns
        -------
        bool

            Returns True if the type is optional.

        Examples
        --------
        >>> CwlType().optional("string")
        False
        >>> CwlType().optional("string?")
        True
        >>> CwlType().optional({"type": "array", "items": "string"})
        False
        >>> CwlType().optional({"type": "array?", "items": "string"})
        True
        >>> CwlType().optional({"type": "array", "items": "string?"})
        False
        >>> CwlType().optional({"type": "array", "items": "string?"}, recurse=True)
        True
        """
        def _optional(type_):
            # Helper function for recursion.
            try:
                # Optiona[...] === Union[type | None], meaning all optional parameters
                # will have an __args__ parameter.
                types_ = type_.__args__
            except AttributeError:
                # If missing, this parameter cannot be optional.
                return False
            except:
                raise
            else:
                if type(None) in types_:
                    return True
                if recurse:
                    return any([_optional(t) for t in types_])
                else:
                    return False
        return _optional(self.type(cwl_type))
    
    def type(self, cwl_type: None | str | list | dict=None) -> type:
        """
        This returns a python type from a CWL type.

        Parameters
        ----------
        cwl_type : None | str | list | dict
            CWL type. By default this returns the type of the instance.

        Returns
        -------
        type

        Examples
        --------
        >>> CwlType().type("string")
        <class 'str'>
        >>> CwlType().type("boolean")
        <class 'bool'>
        >>> CwlType().type("int")
        <class 'int'>
        >>> CwlType().type("long")
        <class 'int'>
        >>> CwlType().type("float")
        <class 'float'>
        >>> CwlType().type("double")
        <class 'float'>
        >>> CwlType().type("null")
        <class 'NoneType'>
        >>> CwlType().type("record")
        <class 'dict'>
        >>> CwlType().type("File")
        <class '__main__.SbgFile'>
        >>> CwlType().type({"type": "array", "items": "string"})
        list[str]
        >>> CwlType().type({"type": "enum", "symbols": ["A", "B", "C"]})
        typing.Any
        """
        _TYPES = {
            "string": str,
            "boolean": bool,
            "int": int,
            "long": int,
            "float": float,
            "double": float,
            "null": type(None),
            "record": dict,
            "File": SbgFile
        }

        cwl_type = cwl_type or self.cwl_type
        if cwl_type is None:
            raise ValueError("No type provided.")

        if isinstance(cwl_type, str):
            # named type
            optional = cwl_type.endswith("?")
            return Optional[_TYPES[cwl_type.strip("?")]] if optional else _TYPES[cwl_type]
        elif isinstance(cwl_type, list):
            # list of possible values
            return Union[tuple(self.type(v) for v in cwl_type)]
        elif isinstance(cwl_type, dict):
            # complex types (array or enum)
            container_ = cwl_type["type"]
            optional = container_.endswith("?")
            type_ = {
                "array": lambda: list[self.type(cwl_type["items"])],
                "enum": lambda: Any
            }[container_.strip("?")]()
            return Optional[type_] if optional else type_
        elif cwl_type is None:
            # null type
            return _TYPES["null"]
        else:
            raise TypeError(f"Invalid type description: {cwl_type}")
    
    def check(self, val: Any, cwl_type: None | str | list | dict=None) -> bool:
        """
        Checks whether the value comports with a CWL type.

        Parameters
        ----------
        val : Any
            Value to check.

        cwl_type : None | str | list | dict
            CWL type. Default: The type from this instance.

        Returns
        -------
        bool
            True if the value comports with this CwlType, False otherwise.

        Examples
        --------
        >>> CwlType().check(1.0, "float")
        True
        >>> CwlType().check("1.0", "float")
        False
        >>> CwlType().check(None, "float?")
        True
        >>> CwlType().check([1.0, None], {"type": "array", "items": "float?"})
        True
        >>> CwlType().check([1.0, None], {"type": "array", "items": ["float", "int"]})
        False
        >>> CwlType().check([1.0, -1], {"type": "array", "items": ["float", "int"]})
        True
        >>> CwlType().check("A", {"type": "enum", "symbols": ["A", "B", "C"]})
        True
        >>> CwlType().check("D", {"type": "enum", "symbols": ["A", "B", "C"]})
        False
        """
        type_ = self.type(cwl_type)
        try:
            return isinstance(val, type_)
        except TypeError:
            if hasattr(type_, "__origin__"):
                # list: check item type
                return (isinstance(val, type_.__origin__) and
                        all(self.check(v, cwl_type["items"]) for v in val))
            else:
                # enum
                return val in cwl_type["symbols"]


if __name__ == "__main__":
    import os
    import sys
    import configparser
    import doctest

    # logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')

    if "SB_AUTH_TOKEN" not in os.environ or "SB_API_ENDPOINT" not in os.environ:
        try:
            # try to read the credentials from the credentials file
            parser = configparser.ConfigParser()
            parser.read(f"{os.environ['HOME']}/.sevenbridges/credentials")
            os.environ["SB_AUTH_TOKEN"] = parser.get("default", "auth_token")
            os.environ["SB_API_ENDPOINT"] = parser.get("default", "api_endpoint")
        except:
            print("Please set SB_AUTH_TOKEN and SB_API_ENDPOINT to continue.")
            sys.exit(1)

    print("Running doctests...")
    doctest.testmod()
    print("Done.")
