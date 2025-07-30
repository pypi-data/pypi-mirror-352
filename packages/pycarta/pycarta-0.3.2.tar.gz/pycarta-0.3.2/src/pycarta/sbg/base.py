import os
import logging
import sevenbridges as sbg
from collections import deque
from contextlib import contextmanager
from pathlib import Path
from sevenbridges.errors import BadRequest  # Raised when an attempt is made to delete a non-empty directory
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
                 parent : None | str | sbg.File=None,
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
        parent : str | sevenbridges.File
            Parent directory. Default: None.
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
        if name:
            api = api or sbg.Api()
            self._api = api
            if project and parent:
                raise ValueError("Must provide either project or parent, not both.")
            elif project:
                project = api.projects.query(name=project)[0] if isinstance(project, str) else project
                self._remote = api.files.query(
                    project=project,
                    names=[name],
                )[0]
            elif parent:
                parent = api.files.query(parent=parent)[0] if isinstance(parent, str) else parent
                self._remote = api.files.query(
                    parent=parent,
                    names=[name],
                )[0]
            else:
                raise ValueError("Must provide either project or parent.")
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
        if self.local is None:  # pragma: no cover
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
        if path:
            self.download(path=path, **download_opts)
            resource = open(path, "r+b")
        else:
            resource = NamedTemporaryFile("w+b", delete=False)
            self.download(path=resource.name, **download_opts)
            resource.close()
            resource = open(resource.name, "r+b")
        try:
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
        # TODO: This deletes the file before replacing the contents because of
        # an apparent bug in SBG (sbg.File.download()). Overwrite does not work
        # on Windows. Confirmed on sevenbridges-python==2.11.0.
        if os.path.exists(opts["path"] and opts["overwrite"]):
            try:
                os.remove(opts["path"])
                logger.debug(f"Deleted {opts['path']}.")
            except FileNotFoundError:
                # If path is a temporary file in linux, the file is created
                # but may not be placed in the node table, so the file, though
                # it exists, cannot be removed and raises a FileNotFoundError.
                pass
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
        # Values needed from opt
        api = opts.get("api", getattr(self.remote, "_API", None))
        project = opts.pop("project", None)
        parent = opts.pop("parent", None)
        if not api:
            raise ValueError("No API object provided to `upload`.")
        if project and parent:
            raise ValueError("Cannot specify both project and parent.")
        elif project:
            if isinstance(project, str):
                project_ = project.split("/")[-1]
                try:
                    project = api.projects.query(name=project_)[0]
                except IndexError:
                    raise ValueError(f"Project {project!r} not found.")
            opts["project"] = project
        elif parent:
            if isinstance(parent, str):
                try:
                    parent = api.files.query(names=[parent])[0]
                except IndexError:
                    raise ValueError(f"Parent folder {parent!r} not found.")
            opts["parent"] = parent
            if not parent.is_folder():
                raise ValueError(f"Parent folder {parent.name!r} is not a directory.")
        uploader = self.remote or api.files
        upload = uploader.upload(**opts)
        # update the remote file object
        if opts["wait"] and update:
            self._remote = upload.result()
        return upload

    def delete(self) -> None:
        """
        Delete the remote file.

        Returns
        -------
        None
        """
        if self.remote:
            self.remote.delete()
            self._remote = None


class SbgDirectory(SbgFile):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        if self.local and os.path.exists(self.local) and not os.path.isdir(self.local):
            raise ValueError(f"Local file {self.local!r} is not a directory.")
        if self.remote and not self.remote.is_folder():
            raise ValueError(f"Remote file {self.remote!r} is not a directory.")
        
    @SbgFile.local.setter
    def local(self, value: str) -> None:
        if value and not os.path.isdir(value):
            raise ValueError(f"{value!r} is not a directory.")
        self._local = value

    @SbgFile.remote.setter
    def remote(self, value: SbgFile) -> None:
        if value and not value.is_folder():
            raise ValueError(f"{value.name!r} is not a directory.")
        self._remote = value

    def open(self, *args, **kwds):
        raise NotImplementedError("Directories cannot be opened like files.")
    
    def pull(self, *args, **kwds):
        raise NotImplementedError("Directories cannot be pulled like files.")
    
    def push(self, *args, **kwds):
        raise NotImplementedError("Directories cannot be pushed like files.")
    
    def download(self, *args, **kwds):
        """
        Downloads the contents of the remote directory.

        Parameters
        ----------
        path : str | Path
            Local directory path. By default this is ``local``.

        retry : int
            Number of times to retry each download.

        timeout : int
            Timeout in seconds.

        chunk_size : int
            Chunk size in bytes.

        wait : bool
            Wait for the download to complete. Default: True. If False,
            it is the responsibility of the caller to manage the download,
            e.g.

            ```
            download.start() # to start the download
            download.pause() # to pause the download
            download.resume() # to resume the download
            download.stop() # to stop the download
            download.wait() # to wait for the download to complete
            ```
        
        overwrite : bool
            Overwrite local files if they exist. Default: True

        recurse : bool
            Recursively download files in subdirectories. Default: False.

        Returns
        -------
        downloaders : list[sevenbridges.transfer.download.Download]
        """
        opts = {k:v for k,v in zip(["path",
                                    "retry",
                                    "timeout",
                                    "chunk_size",
                                    "wait",
                                    "overwrite",
                                    "recurse",],
                                    args)}
        opts.update(kwds)
        path = Path(opts.pop("path", self.local))
        wait = opts.get("wait", True) # Wait for all downloads before returning
        recurse = opts.get("recurse", False)
        opts.setdefault("wait", False) # Don't wait for each file, we'll download asynchronously
        opts.setdefault("overwrite", True)
        logger.info(f"Downloading to {path}: download({opts})")
        # Make the current directory
        path.mkdir(parents=True, exist_ok=True)
        # Get a list of the files to download
        entries = self._remote.list_files()
        files = [f for f in entries if not f.is_folder()]
        dirs = [d for d in entries if d.is_folder()]
        # Download the files
        kwargs = {k:opts[k] for k in opts
              if k in ["retry", "timeout", "chunk_size", "wait", "overwrite"]}
        downloads = [f.download(str(path / f.name), **kwargs) for f in files]
        # Download the subdirectories
        if recurse:
            opts["wait"] = False  # Don't wait for these directories before
            for d in dirs:
                subdir = SbgDirectory(
                    name=d.name,
                    parent = self.remote,
                    api=self.remote._api,
                )
                downloads.extend(subdir.download(str(path / d.name), **opts))
        # Wait for downloads to finish
        if wait:
            for download in downloads:
                logger.debug(f"Downloading {download.path!r}")
                download.start()
            for download in downloads:
                logger.debug(f"Waiting for {download.path!r}")
                download.wait()
        self.local = str(path)
        return downloads
    
    def upload(self, *args, **kwds) -> SbgUpload:
        """
        Upload the local directories to the remote path.

        Parameters
        ----------
        path : str | Path
            Local file path. By default this is ``File.local``.

        project : str | Project
            Remote project name. If parent is not provided, this is required
            and the folder will be uploaded to the project home directory.
        
        parent : str | sevenbridges.File
            Remote parent folder. If provided, this takes precedence over the
            project.

        directory_name : str
            Remote directory name. Default: Same as local.

        overwrite : bool
            Overwrite remote files, if they exist. Default: True

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

            Default: True
        api : sevenbridges.Api
            API object. Default: None. If not provided, the default API
            object is used.

        exists_ok : bool
            If True, do not raise an error if the directory already exists.
            Default: True.

        Returns
        -------
        uploaders : list[sevenbridges.transfer.upload.Upload]
        """
        opts = {k:v for k,v in zip(["path",
                                    "project",
                                    "parent",
                                    "directory_name",
                                    "overwrite",
                                    "retry",
                                    "timeout",
                                    "part_size",
                                    "wait",
                                    "api",
                                    "exists_ok"],
                                    args)}
        opts.update(kwds)
        opts.setdefault("overwrite", True)
        opts.setdefault("wait", True) # Wait for all uploads before returning
        from pprint import pformat
        logger.debug(f"Upload Parameters: {pformat(opts)}")

        # Method parameters needed for this iteration.
        path = Path(opts.pop("path", self.local)); logger.debug(f"Path: {path}")
        folder_name = opts.pop("directory_name", path.name); logger.debug(f"Remote folder: {folder_name}")
        parent = opts.pop("parent", None); logger.debug(f"Parent: {parent}")
        project = opts.pop("project", getattr(self.remote, "project", None)); logger.debug(f"Project: {project}")
        wait = opts.get("wait", True); logger.debug(f"Wait: {wait}")  # Wait for all uploads before returning
        exists_ok = opts.get("exists_ok", True); logger.debug(f"Exists OK: {exists_ok}")
        api = opts.get("api", getattr(self.remote, "api", None)); logger.debug(f"API: {api}")

        # Parameter checks
        if not path.is_dir():
            logger.error(f"{path!r} is not a directory.")
            raise ValueError(f"{path!r} is not a directory.")
        if api is None:
            logger.error("No API object provided to `upload`.")
            raise ValueError("No API object provided to `upload`.")

        # Convert project string into project object
        if isinstance(project, str):
            logger.debug(f"Retrieving project {project!r}.")
            project_ = project.split("/")[-1] # project name, excluding enterprise
            try:
                project = api.projects.query(name=project_)[0]
            except IndexError:
                raise IOError(f"Project {project!r} not found.")
        # Convert the parent string into a parent object
        if isinstance(parent, str):
            logger.debug(f"Retrieving parent {parent!r}.")
            parent = api.files.query(names=[parent], project=project)[0]
        
        # Make the current directory
        try:
            if parent:
                # Parent and project are mutually exclusive. Parent takes precedence.
                parent = api.files.create_folder(folder_name, parent=parent)
            else:
                parent = api.files.create_folder(folder_name, project=project)
        except sbg.errors.Conflict as e:
            # If the folder exists, get the folder object.
            logger.info(f"Folder {folder_name!r} already exists.")
            if not exists_ok:
                raise e
            if parent:
                parent = api.files.query(names=[folder_name], parent=parent)[0]
            else:
                parent = api.files.query(names=[folder_name], project=project)[0]

        # Prep options for each file/nested folder.
        _ = opts.pop("project", None) # After creating the first folder, ...
        opts["parent"] = parent  # ... a parent will always be provided.
        opts["wait"] = False # Don't wait for each file, we'll upload asynchronously

        # List of files/directories to upload
        entries = list(path.iterdir())
        files = [f for f in entries if f.is_file()]
        dirs = [d for d in entries if d.is_dir()]
        # Upload files
        kwargs = {k:opts[k] for k in opts
                  if k in ["project",
                           "parent",
                           "file_name",
                           "overwrite",
                           "retry",
                           "timeout",
                           "part_size",
                           "wait",
                           "api"]}
        uploaders = [
            api.files.upload(str(f), file_name=f.name, **kwargs)
            for f in files]
        # Upload subdirectories
        for dir in dirs:
            uploaders.extend(self.upload(str(dir), **opts))

        # Start uploads, if requested
        if wait:
            for upload in uploaders:
                logger.debug(
                    f"Uploading {upload.file_name}: upload({opts})")
                upload.start()
            for upload in uploaders:
                upload.wait()
                logger.debug(f"Upload of {upload.file_name} finished.")
        
        # The first called is the last to exit
        self.remote = parent
        return uploaders

    def delete(self):
        """
        Delete the remote directory.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        remote = self.remote
        api = remote._API
        logger.info(f"Deleting {remote.name!r} ({remote.id})")
        job = api.async_jobs.file_bulk_delete(files=[{"file": remote.id}])
        job.get_result() # wait for the job to finish
        self.remote = None


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
            "File": SbgFile,
            "Directory": type(None)  # TODO: handle directories
        }

        cwl_type = cwl_type or self.cwl_type
        if cwl_type is None:
            raise ValueError("No type provided.")
        
        if isinstance(cwl_type, str):
            # named type
            # check if optional (endswith ?) and array (endswith [])
            cwl_type_ = cwl_type
            optional = cwl_type_.endswith("?"); cwl_type_ = cwl_type_.strip("?")
            is_list = cwl_type_.endswith("[]"); cwl_type_ = cwl_type_.strip("[]")
            type_ = list[_TYPES[cwl_type_]] if is_list else _TYPES[cwl_type_]
            return Optional[type_] if optional else type_
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
