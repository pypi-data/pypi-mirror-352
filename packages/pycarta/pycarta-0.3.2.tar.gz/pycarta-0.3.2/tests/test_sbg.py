import filecmp
import logging
import pytest
import shutil
from petname import generate
from pycarta.sbg import (
    SbgFile,
    SbgDirectory,
    SbgLoginManager,
    ExecutableApp,
    ExecutableProject,
)
from pycarta.sbg.project import (
    canonicalize_name,
    title,
)
import os

logger = logging.getLogger(__name__)


@pytest.fixture
def local_file(tmp_path):
    return tmp_path / f"pytest-{generate()}.txt"

class TestSbgLoginManager:
    @pytest.fixture(autouse=True)
    def reset_environment(self, tmp_path):
        """ Reset the environment by unsetting environment variables and backing up .env files and credentials. """
        # Backup and unset environment variables
        env_vars = [
            "SBG_API_KEY",
            "SB_AUTH_TOKEN",
            "SBG_API_ENDPOINT",
            "CARTA_API_TOKEN",
        ]
        backups = {var: os.environ.pop(var, None) for var in env_vars}

        # Backup and remove .env and credentials files
        backup_files = []
        config = None
        for src in (
            ".env",
            os.path.expanduser("~/.env"),
            os.path.expanduser("~/.sevenbridges/credentials"),
        ):
            if os.path.exists(src):
                if src.endswith("credentials"):
                    logger.debug(f"Reading profiles from {src!r}.")
                    from configparser import ConfigParser
                    config = ConfigParser()
                    config.read(src)
                dest = tmp_path / (os.path.basename(src) + ".bkp")
                shutil.move(src, dest)
                logger.debug(f"Backed up {src!r} to {dest!r}.")
                backup_files.append((src, dest))
        
        yield {"env": backups, "config": config}

        # Restore environment variables
        for var, value in backups.items():
            if value is not None:
                logger.debug(f"Restoring {var!r} to {value[:5]!r}.")
                os.environ[var] = value

        # Restore backup files
        for src, dest in backup_files:
            logger.debug(f"Restoring {src!r} from {dest!r}.")
            shutil.move(dest, src)

    def test_carta_default(self):
        """ Test authentication using Carta secret for the default profile. """
        manager = SbgLoginManager()
        assert not manager.is_authenticated(), "No credentials should exist, so a user should not be authenticated."

    def test_local_default(self, reset_environment):
        """ Test SBG default profile authentication using $HOME/.sevenbridges/credentials. """
        credentials_path = os.path.expanduser("~/.sevenbridges/credentials")
        config = reset_environment["config"]
        env = reset_environment["env"]
        key = env.get("SBG_API_KEY", env.get("SB_AUTH_TOKEN", None))
        if config:
            logger.info("Using credentials from profile.")
            section = config.sections()[0]
            with open(credentials_path, "w") as f:
                config.write(f)
        elif key:
            logger.info("Using credentials from environment variables.")
            section = "default"
            with open(credentials_path, "w") as f:
                f.write(
                    "[default]\n"
                    "api_endpoint = https://api.sbgenomics.com/v2/\n"
                    f"auth_token = {key}\n"
                )
        else:
            raise ValueError("No credentials found to test.")
        manager = SbgLoginManager(profile=section)
        assert manager.is_authenticated(), "Failed to authenticate using the local default profile."

    def test_invalid_profile_name(self):
        """ Test authentication using a named Carta secret profile. """
        # raise an exception because 1. there is no secret or 2. there is a secret, but no profile with that name
        manager = SbgLoginManager()
        result = manager.login(profile="test_named")
        assert not result, "Authentication should fail for non-existent Carta profile but did not."

    def test_local_named(self, reset_environment):
        credentials_path = os.path.expanduser("~/.sevenbridges/credentials")
        config = reset_environment["config"]
        env = reset_environment["env"]
        key = env.get("SBG_API_KEY", env.get("SB_AUTH_TOKEN", None))
        section = "test_named"
        if config:
            logger.info("Using credentials from profile.")
            tmp = config.sections()[0]
            with open(credentials_path, "w") as f:
                f.write(
                    f"[{section}]\n"
                    f"api_endpoint = {config[tmp]['api_endpoint']}\n"
                    f"auth_token = {config[tmp]['auth_token']}\n"
                )
        elif key:
            logger.info("Using credentials from environment variables.")
            with open(credentials_path, "w") as f:
                f.write(
                    f"[{section}]\n"
                    "api_endpoint = https://api.sbgenomics.com/v2/\n"
                    f"auth_token = {key}\n"
                )
        else:
            raise ValueError("No credentials found to test.")
        manager = SbgLoginManager(profile=section)
        assert manager.is_authenticated(), "Failed to authenticate using the local named profile."

    def test_env_var(self, reset_environment):
        """ Test authentication using environment variables. """
        config = reset_environment["config"]
        env = reset_environment["env"]
        key = env.get("SBG_API_KEY", env.get("SB_AUTH_TOKEN", None))
        if config:
            logger.info("Using credentials from profile.")
            os.environ["SBG_API_KEY"] = config["default"]["auth_token"]
        elif key:
            logger.info("Using credentials from environment variables.")
            os.environ["SBG_API_KEY"] = key
        os.environ["SBG_API_ENDPOINT"] = "https://api.sbgenomics.com/v2/"
        manager = SbgLoginManager()
        result = manager.login()
        assert result, "Failed to authenticate using environment variables."

    @pytest.mark.skip(reason="GUI tests are not implemented.")
    def test_prompt_gui(self):
        """ Test GUI prompt for API token. """
        pass

    def test_prompt_console(self):
        # use conftest.py
        pass
        

# region SbgFile
# @pytest.mark.skip("Skipped to reduce API calls.")
class TestSbgFile:
    def test_local(self, local_file):
        # Initialize with local file
        fobj = SbgFile(str(local_file))
        # File name
        assert fobj.local == str(local_file)
        # Local file I/O
        contents = "Hello, World!"
        with fobj.open("w") as fh:
            fh.write(contents)
        with open(str(local_file), "r") as fh:
            assert fh.read() == contents
        # No remote file
        assert fobj.remote is None
        # Lazy file setting
        fobj = SbgFile()
        fobj.local = str(local_file)
        # File name
        assert fobj.local == str(local_file)
        # Local file I/O
        contents = "Hello, World!"
        with fobj.open("w") as fh:
            fh.write(contents)
        with open(str(local_file), "r") as fh:
            assert fh.read() == contents
        # No remote file
        assert fobj.remote is None

    def test_upload_download(self, local_file, sbg_api, sbg_project):
        api = sbg_api
        project = sbg_project
        # Upload a file
        contents = "Hello, World!"
        with open(local_file, "wb") as fh:
            fh.write(contents.encode())
        up = SbgFile(str(local_file))
        up.upload(str(local_file),
                  project=project,
                  file_name=local_file.name,
                  overwrite=True,
                  api=api,)
        # Download the file
        down = SbgFile(name=local_file.name,
                       project=project,
                       api=api,)
        down.download(overwrite=True)
        with open(local_file.name, "rb") as fh:
            assert fh.read() == contents.encode()
        # Clean up
        os.remove(local_file.name)
        try:
            up.delete()
        except:
            pass

    def test_push_pull(self, local_file, sbg_api, sbg_project):
        api = sbg_api
        project = sbg_project
        # Initialize with local file
        contents = b"Hello, World!"
        with SbgFile().push(file_name=local_file.name,
                            project=project,
                            overwrite=True,
                            api=api) as fh:
            fh.write(contents)
        down = SbgFile(name=local_file.name,
                       project=project,
                       api=api)
        with down.pull() as fh:
            assert fh.read() == contents
        # cleanup
        try:
            down.delete()
        except:
            pass
# end region


# region SbgDirectory
class dircmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """
    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(self.left,
                                 self.right,
                                 self.common_files,
                                 shallow=False)
        self.same_files, self.diff_files, self.funny_files = fcomp

    def __bool__(self):
        if (self.left_only or self.right_only or self.diff_files or self.funny_files):
            return False
        for subdir in self.common_dirs:
            if not dircmp(os.path.join(self.left, subdir),
                          os.path.join(self.right, subdir)):
                return False
        return True


class TestSbgDirectory:
    @pytest.fixture()
    def srcdir(self):
        from tempfile import TemporaryDirectory
        folder = TemporaryDirectory()
        yield folder
        folder.cleanup()

    @pytest.fixture()
    def destdir(self):
        from tempfile import TemporaryDirectory
        folder = TemporaryDirectory()
        yield folder
        folder.cleanup()

    def populate_directory_fwd(self, dirname):
        # Create a file that will be uploaded for use in the app.
        content = "Hello, World!"
        with open(os.path.join(dirname, "hello.txt"), "w") as fh:
            fh.write(content)
        os.mkdir(os.path.join(dirname, "subdir"))
        content = "Goodbye, World!"
        with open(os.path.join(dirname, "subdir", "goodbye.txt"), "w") as fh:
            fh.write(content)

    def populate_directory_rev(self, dirname):
        # Create a file that will be uploaded for use in the app.
        content = "Goodbye, World!"
        with open(os.path.join(dirname, "goodbye.txt"), "w") as fh:
            fh.write(content)
        os.mkdir(os.path.join(dirname, "subdir"))
        content = "Hello, World!"
        with open(os.path.join(dirname, "subdir", "hello.txt"), "w") as fh:
            fh.write(content)
    
    def test_upload_download_same(self, sbg_api, sbg_project, srcdir, destdir):
        self.populate_directory_fwd(srcdir.name)
        self.populate_directory_fwd(destdir.name)
        api = sbg_api
        project = sbg_project
        folder = SbgDirectory(srcdir.name)
        folder.upload(project=project, api=api)
        folder.download(destdir.name)
        try:
            assert bool(dircmp(srcdir.name, destdir.name)), \
                f"FAILED: Downloaded directory does not match uploaded directory."
        finally:
            # Cleanup
            folder.delete()
        
    def test_upload_download_differ(self, sbg_api, sbg_project, srcdir, destdir):
        self.populate_directory_fwd(srcdir.name)
        self.populate_directory_rev(destdir.name)
        api = sbg_api
        project = sbg_project
        folder = SbgDirectory(srcdir.name)
        folder.upload(project=project, api=api)
        folder.download(destdir.name)
        try:
            assert not bool(dircmp(srcdir.name, destdir.name)), \
                f"FAILED: Downloaded directory matches uploaded directory."
        finally:
            # Cleanup
            folder.delete()
# end region


# region Executable App/Project
class TestProjectUtils:
    def test_canonicalize_name(self):
        assert canonicalize_name("Hello World") == 'Hello_World'
        assert canonicalize_name("Hello-World") == 'Hello_World'
        assert canonicalize_name("Hello, World") == 'Hello_World'
        assert canonicalize_name("Hello World!") == 'Hello_World_'

    def test_title(self):
        assert title("hello_world") == 'Hello World'
        assert title("hello-world") == 'Hello World'
        assert title("hello, world") == 'Hello World'    


class TestExecutableAppProject:
    # @pytest.mark.skip("Skipping ExecutableApp test.")
    def test_executable_app(self, local_file, sbg_app):
        # Create a file that will be uploaded for use in the app.
        content = "Hello, World!"
        with open(local_file, "w") as fh:
            fh.write(content)
        # Create the App and run it.
        app = ExecutableApp(sbg_app, cleanup=True)
        outputs, _ = app(input=str(local_file))
        # Check the output
        try:
            with outputs["output"].open("r") as fh:
                assert fh.read() == content
        except Exception as e:
            raise type(e)(f"outputs: {outputs}")
        finally:
            # Clean up
            os.remove(outputs["output"].local)
            try:
                outputs["output"].remote.delete()
            except:
                pass

    def test_executable_project(self, sbg_api, sbg_project):
        project = ExecutableProject(project=sbg_project,
                                    cleanup=True,
                                    overwrite_local=True,
                                    overwrite_remote=True,
                                    api=sbg_api,)
        # What apps are expected?
        proj = sbg_api.projects.query(name=sbg_project)[0]
        apps = sbg_api.apps.query(project=proj)
        app_names = [canonicalize_name(app.name) for app in apps]
        # Create executable apps from the project
        for name in app_names:
            assert hasattr(project, canonicalize_name(name))
# end region
