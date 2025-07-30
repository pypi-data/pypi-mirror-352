import os
import logging
import sevenbridges as sbg
from dotenv import load_dotenv
from getpass import getpass
from pycarta.admin import get_secret


logger = logging.getLogger(__name__)


SBG_CARTA_SECRET_NAME = "sbg/credentials"

class SbgLoginManager:
    """
    Manages the login functionality for Seven Bridges (SBG) and handles
    cases where login information might be missing or incorrect.
    """

    def __init__(self, *,
                 profile: str | None=None,
                 api: str | sbg.Api |None=None,
                 interactive: bool=False):
        self.api = None
        self._profile = None
        self.login(profile=profile, api=api, interactive=interactive)
    
    @property
    def profile(self) -> str:
        return self._profile
    
    @profile.setter
    def profile(self, value: str) -> None:
        raise NotImplementedError(f"Profile cannot be set directly but is set during login.")
    
    def is_authenticated(self) -> bool:
        return self.api is not None

    def login(self, *,
              profile: str | None=None,
              api: str | sbg.Api | None=None,
              interactive: bool=False) -> bool:
        """
        Attempte to authenticate based on specific profile or API key.
        TBW: order discussed.

        Parameters
        ----------
        profile : str | None
            The profile name to use for login

        api : str | sbg.Api | None
            The API token or 'sbg.API' instance

        Returns
        -------
        bool
            True if authentication was successful, otherwise false
        """
        # 1. Has a profile or api key already been specified?
        if api:
            return self._api_login(api)
        elif profile:
            # this is going to attempt to pull the profile from carta secret
            # then check carta profile for profile name
            # if present, login with carta profile (try, except)
            if not self._carta_secret_login(profile):
                # if not present, attempt to login using sbg profile
                self._sbg_profile_login(profile)
        else:
            # check for env vars (api = sbg.Api())
            if self._env_login():
                return True
            # attempt to pull profile from Carta Secret, login using default
            if self._carta_secret_login(profile="default"):
                return True
            # attempt to login using sbg default
            if self._sbg_profile_login(profile="default"):
                return True
            # if interactive, prompt the user
            if interactive:
                self._interactive_login()
                return True
            return False

    def _api_login(self, api: str | sbg.Api) -> bool:
        """ Authenticate using a provided API token or an `sbg.API` instance. """
        if isinstance(api, str):
            try:
                # if api is a string, treat it as a token and create an sbg.Api instance
                self.api = sbg.Api(token=api)
                return True
            except sbg.errors.SbgError as e:
                logger.debug(f"Failed to authenticate with provided API token: {e}")
                return False
        elif isinstance(api, sbg.Api):
            # If `api` is already an sbg.Api instance, use it directly
            self.api = api
            return True
        # If the input was neither a string nor an sbg.Api instance, fail to authenticate
        logger.debug("Invalid API token provided for authentication.")
        return False

    def _carta_secret_login(self, profile:str) -> bool:
        """ Attempt login using a stored API key as a secret in Carta. """
        try:
            token = get_secret(SBG_CARTA_SECRET_NAME(profile))
        except Exception as e:
            logger.debug(f"Failed to retrieve SBG token for {profile!r}.")
            return False
        else:
            try:
                self.api = sbg.Api(token=token)
                logger.info(f"Authenticated with Carta-stored API key for profile '{profile}'.")
                return True
            except sbg.errors.SbgError as e:
                logger.debug(f"Failed to authenticate with Seven Bridges using stored Carta secret.")
                return False

    def _sbg_profile_login(self, profile:str) -> bool:
        """ Attempt login using an SBG profile from $HOME/.sevenbridges/credentials. """
        try:
            config = sbg.Config(profile=profile)
            self.api = sbg.Api(config=config)
            logger.info(f"Authenticated using SBG profile '{profile}'.")
            return True
        except sbg.errors.SbgError as e:
            logger.debug(f"Failed to authenticate with SBG profile '{profile}': {e}")
            return False

    def _env_login(self) -> bool:
        """Attempt login using an API key from environment variables or .env file."""
        # Load environment variables from .env file if it exists
        # Check multiple potential .env file locations
        for env_path in (
            ".env",
            os.path.expanduser("~/.env"),
            os.path.expanduser("~/.sevenbridges/dotenv"),
            os.path.expanduser("~/.carta/sevenbridges_dotenv"),
        ):
            if os.path.exists(env_path):
                load_dotenv(env_path, override=False)
                logger.info(f"Loaded environment variables from {env_path!r}")

        # Look for API keys in environment variables
        api_key = os.getenv("SBG_API_KEY") or os.getenv("SB_AUTH_TOKEN")
        api_endpoint = os.getenv("SBG_API_ENDPOINT", "https://api.sbgenomics.com/v2/")  # Default endpoint

        if api_key:
            try:
                self.api = sbg.Api(url=api_endpoint, token=api_key)
                logger.info("Authenticated using API key from environment variables.")
                return True
            except sbg.errors.SbgError as e:
                logger.debug(f"Failed to authenticate with environment API key: {e}")
                return False

        logger.debug("No valid API key found in environment variables.")
        return False

    def _interactive_login(self) -> bool:
        """Prompt the user for credentials interactively."""
        api_key = getpass("Please enter your SBG API token: ").strip()
        if not api_key:
            logger.debug("No API token provided.")
            return False

        try:
            self.api = sbg.Api(token=api_key)
            logger.info("Successfully authenticated interactively with user-provided API token.")
            return True
        except sbg.errors.SbgError as e:
            logger.debug(f"Failed to authenticate with user-provided API token: {e}")
            return False

if __name__ == "__main__":
    # Current order of operations:
    # 1. Seven Bridges API (string or sbg.Api object)
    # 2. Carta secret (user-specified profile)
    # 3. Seven Bridges profile (user-specified profile name)
    # 4. Environment variables
    # 5. Carta secret (default profile)
    # 6. Seven Bridges profile (default profile)
    # 7. Interactive (optional)
    manager = SbgLoginManager() # This is going to become part of the PycartaContext

