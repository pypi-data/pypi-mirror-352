import logging
import re
import sevenbridges as sbg
from collections import deque
from inflection import camelize
try:
    # When this file is moved into src/
    from .base import CwlType, SbgFile
except ImportError:
    # For testing/prototyping
    from base import CwlType, SbgFile


LOGGER = logging.getLogger(__name__)


def canonicalize_name(name: str) -> str:
    """
    Creates a valid python name from a string

    Convert a string to a canonical name by replacing non-word characters with underscores.
    If the string starts with a digit, an underscore is prepended to the string.

    Parameters
    ----------
    name: str
        The string to convert to a canonical name.

    Returns
    -------
    str
        The canonical name

    Examples
    --------
    >>> canonicalize_name("Hello World")
    'Hello_World'
    >>> canonicalize_name("Hello-World")
    'Hello_World'
    >>> canonicalize_name("Hello, World")
    'Hello_World'
    >>> canonicalize_name("Hello World!")
    'Hello_World_'
    """
    res = re.sub(r'\W', '_', name)
    res = ("_" + res) if re.match(r'^\d', res) else res
    return re.sub(r'_+', '_', res)


def title(label: str) -> str:
    """
    Creates a title from a string

    Convert a string to a title by converting non-word characters to spaces
    and capitalizing the first letter of each word.

    Parameters
    ----------
    label: str
        The string to convert to a title.

    Returns
    -------
    str
        The title
    
    Examples
    --------
    >>> title("hello_world")
    'Hello World'
    >>> title("hello-world")
    'Hello World'
    >>> title("hello, world")
    'Hello World'
    """
    import re
    res = re.sub(r'[^A-Za-z0-9]', ' ', label).strip().title()
    res = re.sub(r'\s+', ' ', res)
    return res


def generator():
    """
    Generator that returns None forever. This is used in combination with
    tqdm to create a progress bar for a process that will take an
    indeterminate amount of time.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Examples
    --------
    >>> import time
    >>> import tqdm
    >>> count = 5
    >>> for _ in tqdm.tqdm(generator()):
    ...     time.sleep(1)
    ...     count -= 1
    ...     if count == 0:
    ...         break
    """
    while True:
        yield


class ExecutableApp:
    def __init__(self,
        app: sbg.App,
        *,
        cleanup: bool=False,
        polling_freq: float=10.0,
        overwrite_local: bool=True,
        overwrite_remote: bool=True,
        strict: bool=True,
        api: sbg.Api | None=None,
    ):
        """
        Parameters
        ----------
        app: sbg.App
            The Seven Bridges App/Workflow to be converted into a function.
        cleanup: bool
            Whether to delete files generated on the remote server
            after they have been downloaded. Default: False
        polling_freq: float
            The frequency at which to poll the app for completion.
            Default: 10.0 seconds. Minimum: 3.0 seconds.
        overwrite_local: bool
            Whether to overwrite local files if they already exist.
            Default: True
        overwrite_remote : bool
            Whether to overwrite remote files if they already exist.
            Default: True.
        strict : bool
            If True (default), unknown arguments to the function will cause
            an error. If False, unknown arguments will be ignored.
        api : sbg.Api
            The Seven Bridges API to use. If not provided, the API will be
            inferred from the project.
        """
        self.app: sbg.App = app
        self.cleanup: bool = cleanup
        self.overwrite_local: bool = overwrite_local
        self.overwrite_remote: bool = overwrite_remote
        self.strict: bool = strict
        self.api = api or app._API
        self._polling_freq: float = polling_freq or 10.0
        # self.polling_freq = polling_freq or 10.0
        self.__func = self._generate_func()

    @property
    def polling_freq(self) -> float:
        return self._polling_freq

    # @polling_freq.setter
    # def polling_freq(self, value: float) -> None:
    #     if value < 3.0:
    #         LOGGER.info("Minimum polling frequency: 3.0 sec")
    #     self._polling_freq = max(value, 3.0)

    def __call__(self, **kwds) -> tuple:
        return self.__func(**kwds)

    def _generate_docstring(self) -> str:
        """
        Generates a docstring for the app from the Seven Bridges
        App content.

        Returns
        -------
        str
            The docstring for the app.
        """
        app = self.app
        inputs = [CwlType(**desc) for desc in app.raw.get("inputs", [])]
        outputs = [CwlType(**desc) for desc in app.raw.get("outputs", [])]
        # Grab documentation provided by the SB App developer.
        doc = f"""
        {title(app.raw.get('label', 'Unnamed'))}
        {app.raw.get('doc', '')}
        """
        # add inputs docs
        doc += f"""
        Parameters
        ----------
        """
        for input_ in inputs:
            doc += f"""
            {str(input_)}
                {getattr(input_, "label", "No description provided")}. {getattr(input_, "doc", "")}
            """
        doc += "\n"
        # add outputs docs
        doc += f"""
        Returns
        -------
        ({", ".join([str(output_) for output_ in outputs])}, task)
            Outputs from the task (dict) and the sevenbridges.Task that
            was executed.
        """
        return doc
    
    def _generate_func(self):
        """
        Wraps Seven Bridges Apps to simplify their use with local code.

        Notes
        -----

        Inputs are provided as keyword arguments. Seven Bridges API calls are strongly
        typed, so all input types are checked before calling the task.

        If any input files are required, those should be specified as a string, which
        is assumed to be the local file path, or a ``SbgFile`` object. Files will be
        uploaded to Seven Bridges prior to execution.
        """
        import time
        from datetime import datetime
        from tqdm import tqdm

        # local references to relevant variables.
        app = self.app
        cleanup = self.cleanup
        polling_freq = self.polling_freq
        name = canonicalize_name(app.name)
        inputs = {desc["id"]: CwlType(**desc) for desc in app.raw.get("inputs", [])}
        # outputs = {desc["id"]: CwlType(**desc) for desc in app.raw.get("outputs", [])}
        # build the function
        def func(**kwds) -> tuple:
            # No docstring: that is produced by _generate_docstring
            # check function call
            inputs_required = {type_.id for type_ in inputs.values() if not type_.optional()}
            inputs_optional = {type_.id for type_ in inputs.values() if type_.optional()}
            inputs_provided = set(kwds.keys())
            # check for missing required inputs
            missing = inputs_required - inputs_provided
            unknown = inputs_provided - inputs_required - inputs_optional
            if missing:
                raise ValueError(f"Missing required inputs: {', '.join(missing)}")
            if unknown and self.strict:
                raise ValueError(f"Unknown inputs: {', '.join(unknown)}")
            # check input types
            for input_ in inputs_provided:
                cwl_type = inputs[input_]
                value = kwds[input_]
                if not cwl_type.check(value):
                    # TODO: Allow use of files already on Seven Bridges.
                    type_ = cwl_type.type()
                    if (isinstance(value, str) and 
                        SbgFile in getattr(type_, "__args__", (type_,))):
                        # Local file that needs to be uploaded specified by filename
                        kwds[input_] = SbgFile(value, api=self.api)
                    else:
                        raise TypeError(f"Input {input_!r}({type(value)}) is not of type {type_}.")
            # upload any files needed by the App
            uploads = deque()
            uploaded = deque()
            for input_ in inputs_provided:
                type_ = inputs[input_]
                value = kwds[input_]
                if isinstance(value, SbgFile):
                    # async upload
                    LOGGER.info(f"Uploading {value.local}.")
                    upload_ = value.upload(
                        project=app.project,
                        overwrite=self.overwrite_remote,
                        wait=False)
                    upload_.start()
                    uploads.append((input_, upload_))
            while uploads:
                # await uploads
                input_, upload_ = uploads.pop()
                upload_.wait()
                kwds[input_] = upload_.result()
                uploaded.append(kwds[input_])
                LOGGER.info(f"Uploaded {kwds[input_].name} ({kwds[input_].id}).")
            # CALL THE FUNCTION
            api = app._API
            task_name = name + "-" + datetime.now().strftime("%Y-%m-%d-%H%M%S")  # No ":" -- Windows doesn't like colons.
            project_name = app.project
            app_name = f"{project_name}/{app.name}"
            try:
                # Create the Seven Bridges task and, because run = True, start the task.
                task = api.tasks.create(
                    name=task_name,
                    project=project_name,
                    app=app_name,
                    inputs=kwds,
                    run=True)
                LOGGER.info(f"Task {task.id} has been submitted. This may take a while.")
                # Track progress
                pbar = tqdm(generator())
                for _ in pbar:
                    pbar.set_description(f"Task {task.id!r}: {task.status}")
                    task.reload()
                    if task.status not in ("QUEUED", "RUNNING"):
                        break
                    time.sleep(polling_freq)
            except sbg.errors.SbgError:
                print(f"Unable to run {name!r}")
                raise
            except:
                # Abort the task on error
                print(f"Aborting task {task.id!r}")
                try:
                    task.abort()
                except:
                    # Abort typically fails because there is no task to abort.
                    # This except makes that assumption because I haven't looked
                    # into all the possible failure modes.
                    pass
                raise
            else:
                # PROCESS THE RESULTS
                outputs = {
                    k: (SbgFile(file=v) if isinstance(v, sbg.File) else v)
                    for k, v in task.outputs.items()
                }
                # task.outputs.values() does not work as expected.
                LOGGER.info(f"Task {task.id} has finished. Any resulting files are being downloaded.")
                files = [v for v in outputs.values() if isinstance(v, SbgFile)]
                downloads = deque()
                for file_ in files:
                    # start all files downloading...
                    LOGGER.debug(f"Downloading to {file_.local}")
                    download = file_.download(overwrite=self.overwrite_local, wait=False)
                    downloads.append(download)
                    download.start()
                while downloads:
                    # await downloads
                    download = downloads.pop()
                    download.wait()
                if cleanup:
                    LOGGER.info("Removing remote files.")
                    for file_ in uploaded:
                        # cleanup remote input files
                        # TODO: If using files already on Seven Bridges, do not delete.
                        LOGGER.debug(f"Deleting {file_.name} ({file_.id}) from Seven Bridges.")
                        file_.delete()
                    for file_ in files:
                        # cleanup remote result files
                        LOGGER.debug(f"Deleting {file_.remote.name} ({file_.remote.id}) from Seven Bridges.")
                        file_.remote.delete()
            return (outputs, task)
        # update the function
        # There may be a few other things to do here to ensure the function
        # is properly documented, but this is a start.
        # func.__module__ = __name__  # This may be useful at implementation.
        func.__name__ = name
        func.__doc__ = self._generate_docstring()
        # finished
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        return func
    

# Example Usage: ExecutableProject(project=project, cleanup=True)
# The goal behind this object is to read information from a Seven Bridges
# project and convert that project and its apps into python objects. The
# project becomes a class and the apps become the member functions in that
# class.
class ExecutableProject:
    # Used to hold the project classes that have been created. (Singleton
    # construction.)
    _PROJECTS = dict()

    def __new__(cls, *,
                project: str | sbg.Project,
                cleanup: bool=False,
                polling_freq: float=10.0,
                overwrite_local: bool=True,
                overwrite_remote: bool=True,
                strict: bool=True,
                api: sbg.Api | None=None,):
        """
        This is the ExecutableProject factory class. It
        generates a class that will contain executable apps
        as methods.

        Why overload __new__? Because __new__ controls object creation
        (versus __init__, which controls object initialization) and
        unlike  typical behavior, this does not create an instance
        of the enclosing class. This creates an instance of the
        project class.
        
        That is, ExecutableProject is a factory.
        """
        if isinstance(project, str):
            # Retrieve the project, if specified by name.
            api = api or sbg.Api()
            project = api.projects.get(id=project)
        name = canonicalize_name(project.name)
        classname = camelize(name)
        if classname in cls._PROJECTS:
            # class has already been constructed for this project
            type_ = cls._PROJECTS[classname]
        else:
            # generate a class for this project
            LOGGER.debug(f"Generating class for {classname}")
            # Project class __init__ function.
            # TODO: I would rather represent this as a string and inject it into the namespace
            # using 'exec'. I tried that but was unsuccessful -- I just couldn't get the syntax
            # right. That would remove the annotation warning that pops up below.
            def init(self, *,
                project: sbg.Project,
                cleanup: bool=False,
                polling_freq: float=10.0,
                overwrite_local: bool=True,
                overwrite_remote: bool=True,
                strict: bool=True,
                api: sbg.Api | None=None,
            ):
                """
                Project classes contain method functions that call Seven
                Bridges Apps. This constructor initializes the project class.

                Parameters
                ----------
                project: sbg.Project
                    The project to be converted into a class.
                cleanup: bool
                    Whether to delete files generated on the remote server
                    after they have been downloaded. Default: False
                overwrite: bool
                    Whether to overwrite local files if they already exist.
                    Default: False
                polling_freq: float
                    The frequency at which to poll the app for completion.
                    Default: 10.0 seconds. Minimum: 3.0 seconds.
                """
                super(type(self), self).__init__()
                self.project: sbg.Project = project
                self.cleanup: bool=cleanup,
                self.polling_freq: float=polling_freq,
                self.overwrite_local: bool=overwrite_local,
                self.overwrite_remote: bool=overwrite_remote,
                self.strict: bool=strict,
                self.api: sbg.Api | None=api or project._API,
            namespace = {"__init__": init}
            for app in project.get_apps():
                LOGGER.debug(f"Creating executable for {app.name}")
                exe = ExecutableApp(app,
                                    cleanup=cleanup,
                                    polling_freq=polling_freq,
                                    overwrite_local=overwrite_local,
                                    overwrite_remote=overwrite_remote,
                                    strict=strict,
                                    api=api,)
                namespace[exe.__name__] = exe
            type_ = type(
                classname,
                (),
                namespace,)
            # Singleton pattern to avoid recreating this class definition
            # every time someone requests this object.
            cls._PROJECTS[classname] = type_
        return type_(project=project,
                     cleanup=cleanup,
                     polling_freq=polling_freq,
                     overwrite_local=overwrite_local,
                     overwrite_remote=overwrite_remote,
                     strict=strict,
                     api=api,)
    @classmethod
    def reset(cls, name: None | str | list[str]=None):
        LOGGER.debug("Resetting executable project definitions.")
        if name is None:
            del cls._PROJECTS
            cls._PROJECTS = dict()
        else:
            for key in [name] if isinstance(name, str) else name:
                if key in cls._PROJECTS:
                    del cls._PROJECTS[key]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
