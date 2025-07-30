from __future__ import annotations

import boto3
import logging
import requests
from abc import ABC, abstractmethod
from botocore.exceptions import ClientError
from pycognito.aws_srp import AWSSRP
from requests.exceptions import HTTPError

from .config import CartaConfig
from ..exceptions import *
from .profile import Profile

logger = logging.getLogger(__name__)


__all__ = ["CartaAgent"]


# region AUTHENTICATION AGENT
class AuthenticationAgent(ABC):
    # These should be overloaded in derived classes.
    HOST_DEV: str | None=None
    HOST_PROD: str | None=None

    def __init__(
        self,
        *,
        profile: str | None=None,
        username: str | None=None,
        password: str | None=None,
        token: str | None=None,
        environment: str | None,
        host: str | None=None,
    ):
        """
        Either a username/password or a token must be provided.

        Parameters
        ----------
        profile : str | Profile
            User profile to use for authentication. Default: None.
        username : str
            Carta username. Default: None
        password : str
            Carta password. Default: None
        token : str
            If provided, token supercedes username/password. Default: None.
        environment : str
            Resolves to either HOST_PROD, if "production", or HOST_DEV,
            otherwise. Defaults to None.
        host : str
            Host to use for authentication. Overrides environment. Recover
            default hosts by setting host to None. Defaults to None.
        """
        logger.debug(f"Creating AuthenticationAgent.")
        if host:
            self.HOST_PROD = str(host)
            self.HOST_DEV = str(host)
            logger.debug(f"Using host: {self.HOST_PROD}")
        else:
            self.HOST_PROD = self.__class__.HOST_PROD
            self.HOST_DEV = self.__class__.HOST_DEV
            logger.debug(f"Using default hosts.")
        self._profile = Profile(
            username=str(username) if username else None,
            password=str(password) if password else None,
            token=str(token) if token else None,
            environment=str(environment) if environment else None,
        )
        self._session: requests.Session = requests.Session()
        if profile:
            logger.debug("Authenticating with user profile.")
            self.authenticate(profile=profile)
        elif token:
            logger.debug("Authenticating with token.")
            self.token = token
        elif username and password:
            logger.debug("Authenticating with username/password.")
            self.authenticate(username=username, password=password)

# region Abstract Methods
    @abstractmethod
    def is_authenticated(self) -> bool:
        raise NotImplementedError("is_authenticated has not been implemented.")  # pragma: no cover
    
    @abstractmethod
    def _profile_authentication(self, *, profile: str | Profile) -> None:
        """
        Performs profile-based authentication.

        Parameters
        ----------
        profile : str | Profile
            Profile to authenticate with.

        Returns
        -------
        None
        """
        cls = type(self)
        if isinstance(profile, str):
            # This will raise a ProfileNotFound exception if the profile does
            # not exist.
            self._profile = CartaConfig().get_profile(profile)
        else:  # pragma: no cover
            self._profile = profile
        try:
            if not self.is_authenticated():
                raise AuthenticationError("Profile authentication failed.")
        except:
            logger.debug("Authenticating from profile username/password.")
            self._password_authentication(
                username=self._profile.username,
                password=self._profile.password)
        else:
            logger.debug("Authenticated from profile token.")
    
    @abstractmethod
    def _password_authentication(self, *, username: str, password: str) -> None:
        """
        Performs username/password-based authentication.

        Parameters
        ----------
        username : str
            Carta user name.
        password : str
            Carta password.

        Returns
        -------
        None
        """
        raise NotImplementedError("Password authentication has not been implemented.")  # pragma: no cover

    @abstractmethod
    def reset_password(self) -> None:  # pragma: no cover
        """
        Resets the user's password.

        Returns
        -------
        None
        """
        NotImplementedError("Password reset has not been implemented.")
# endregion
    
# region Authentication API    
    @property
    def environment(self) -> str | None:
        return self._profile.environment
    @environment.setter
    def environment(self, value: str) -> None:
        self._profile.environment = str(value)

    @property
    def host(self) -> str | None:
        return self.HOST_PROD if self._profile.is_production() else self.HOST_DEV
    @host.setter
    def host(self, value: str | None) -> None:
        if value:
            self.HOST_PROD = str(value)
            self.HOST_DEV = str(value)
            logger.debug(f"Using host: {self.HOST_PROD}")
        else:
            self.HOST_PROD = self.__class__.HOST_PROD
            self.HOST_DEV = self.__class__.HOST_DEV
            logger.debug(f"Using default hosts.")

    @property
    def url(self) -> str | None:  # pragma: no cover
        DeprecationWarning("`AuthenticationAgent.url` has been deprecated in "
                           "favor of `AuthenticationAgent.host`.")
        return self.host
    @url.setter
    def url(self, value: str | None) -> None:  # pragma: no cover
        DeprecationWarning("`AuthenticationAgent.url` has been deprecated in "
                           "favor of `AuthenticationAgent.host`.")
        self.host = value

    @property
    def token(self) -> str | None:
        return self._profile.token
    @token.setter
    def token(self, value: None | str) -> None:
        if value is None:
            self._session.headers.pop("Authorization", None)
            self._profile.invalidate_token()
        else:
            self._profile.set_token(str(value))
            self._session.headers.update({"Authorization": f"Bearer {self.token}"})

    @property
    def username(self) -> str | None:
        return self._profile.username
    @username.setter
    def username(self, value: str) -> None:  # pragma: no cover
        AttributeError("'username' set during username/password authentication.")

    @property
    def password(self) -> str | None:
        return self._profile.password
    
    @password.setter
    def password(self, value: str) -> None:  # pragma: no cover
        AttributeError("'password' set during username/password authentication.")

    def is_authenticated(self) -> bool:
        return self.agent.get("user/authenticated")

    def authenticate(
        self,
        *,
        profile: Profile | None=None,
        username: str | None=None,
        password: str | None=None,
    ) -> None:
        """
        Authenticates the user either using a profile or username/password.
        If both are provided, profile is used preferentially.

        Parameters
        ----------
        profile : Profile | str
            Profile to authenticate with.
        username : str
            Carta user name.
        password : str
            Carta password.

        Returns
        -------
        None
        """
        if profile is not None:
            self._profile_authentication(profile=profile)
        elif username is not None and password is not None:
            self._password_authentication(username=username, password=password)
        else:  # pragma: no cover
            raise ValueError("Either a profile or username/password must be provided.")
# endregion

# region Requests API
    def _get_url(self, endpoint: str) -> str:
        if not self.host:
            raise ValueError("Base URL has not been provided.")  # pragma: no cover
        url = str(self.host).strip("/") + "/" + str(endpoint).strip("/")
        logger.debug(f"URL: {url}")
        return url
    
    @staticmethod
    def authorization_optional(func):
        """
        Adds an "authorize" named keyword/option to the decorated function. If
        True (default) then the Authorization header will be included in the
        request. If False, the Authorization header will be removed before the
        request is made, but will be restored afterwards.

        This also standardizes the response to a HTTP request.

        Parameters
        ----------
        func : function
            Function to decorate.

        Returns
        -------
        function
            Decorated function.
        """
        def wrapped(self, *args, authorize: bool=True, **kwargs):
            if not authorize:
                token = self._session.headers.pop("Authorization", None)
                try:
                    logger.debug(f"Calling {func.__name__}({args}, {kwargs})")
                    response = func(self, *args, **kwargs)
                finally:
                    if token:
                        self._session.headers["Authorization"] = token
            else:
                logger.debug(f"Calling {func.__name__}({args}, {kwargs})")
                if "Authorization" not in self._session.headers:
                    raise AuthenticationError("Authentication required.")
                response = func(self, *args, **kwargs)

            if response.status_code == 400:  # pragma: no cover
                # TODO update this with more information should Carta API be updated
                logger.error(f"Bad request: {response.reason}")
                raise InvalidParameterException()

            if response.status_code == 403:  # pragma: no cover
                logger.error(f"Forbidden: {response.reason}")
                raise PermissionDeniedException()

            if response.status_code == 500:  # pragma: no cover
                logger.error(f"Server error: {response.reason}")
                raise CartaServerException()

            # Something else bad happened, raise it to the surface rather than letting it fester
            response.raise_for_status()
            return response
        return wrapped
    
    @authorization_optional
    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        logger.debug(f"Calling request {method!r}.")
        return self._session.request(str(method), self._get_url(endpoint), **kwargs)
    
    @authorization_optional
    def head(self, endpoint: str, **kwargs) -> requests.Response:
        logger.debug(f"Calling 'head'.")
        return self._session.head(self._get_url(endpoint), **kwargs)
    
    @authorization_optional
    def get(self, endpoint: str, *, params=None, **kwargs) -> requests.Response:
        logger.debug(f"Calling 'get' with params: {params}.")
        return self._session.get(self._get_url(endpoint), params=params, **kwargs)
    
    @authorization_optional
    def post(self, endpoint: str, *, data=None, json=None, **kwargs) -> requests.Response:
        logger.debug(f"Calling 'post' with " \
                     f"data: {'Y' if data else 'N'}, " \
                     f"json: {'Y' if json else 'N'}.")
        return self._session.post(self._get_url(endpoint),
                                   data=data, json=json, **kwargs)
    
    @authorization_optional
    def put(self, endpoint: str, *, data=None, **kwargs) -> requests.Response:
        logger.debug(f"Calling 'put' with data: {'Y' if data else 'N'}.")
        return self._session.put(self._get_url(endpoint), data=data, **kwargs)
    
    @authorization_optional
    def patch(self, endpoint: str, *, data=None, **kwargs) -> requests.Response:
        logger.debug(f"Calling 'patch' with data: {'Y' if data else 'N'}.")
        return self._session.patch(self._get_url(endpoint), data=data, **kwargs)
    
    @authorization_optional
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        logger.debug(f"Calling 'delete'.")
        return self._session.delete(self._get_url(endpoint), **kwargs)
# endregion
# endregion

# region COGNITO AGENT
class CognitoAgent(AuthenticationAgent):
    """
    The CognitoAgent serves as the base for authentication against a Cognito
    user pool. However, this class is not intended to be used directly. Instead,
    derive from this class and set the HOST_PROD and HOST_DEV class variables
    in the derived class.
    """
    def __init__(
        self,
        *,
        profile: str | Profile | None=None,
        username: str | None=None,
        password: str | None=None,
        token: str | None=None,
        environment: str | None=None,
        host: str | None=None,
    ):
        # These must be established before calling the super class constructor
        # because the base class will authenticate if credentials are provided.
        self._auth_resources: dict = dict()
        self._aws_session: boto3.Session = boto3.Session()
        super().__init__(
            profile=profile,
            username=username, password=password,
            token=token,
            environment=environment,
            host=host,)

    def _get_auth(self) -> dict:
        """
        Returns the Cognito user pool information.

        Returns
        -------
        dict
        """
        if self.host and self._auth_resources.get("domain") == self.host:  # pragma: no cover
            return self._auth_resources
        logger.debug("Retrieving cognito pool information.")
        response = self.get("auth", authorize=False)
        response.raise_for_status()
        self._auth_resources = response.json()
        self._auth_resources["domain"] = self.host
        return self._auth_resources

    def _profile_authentication(self, *, profile: str | Profile) -> None:
        """
        Authenticates using information stored in a profile.

        Parameters
        ----------
        profile : str | Profile
            Authentication information.

        Returns
        -------
        None
        """
        super()._profile_authentication(profile=profile)
        profile = self._profile
        if profile.aws_profile:
            self._aws_session = boto3.Session(profile_name=profile.aws_profile)

    def _password_authentication(self, *, username: str, password: str) -> str:
        """
        Performs username/password-based authentication.

        Parameters
        ----------
        username : str
            Carta user name.
        password : str
            Carta password.

        Returns
        -------
        None
        """
        user_pool = self._get_auth()
        logger.debug(f"Cognito User Pool Info: {user_pool}")
        logger.debug(f"Username: {username}")
        logger.debug(f"Password: ***{password[-2:]}")
        pool_id = user_pool["userPoolId"]
        region = user_pool["region"]
        client_id = user_pool["userPoolWebClientId"]

        client = self._aws_session.client("cognito-idp", region_name=region)
        aws = AWSSRP(username=username,
                     password=password,
                     pool_id=pool_id,
                     client_id=client_id,
                     client=client)
        try:
            tokens = aws.authenticate_user()
        except ClientError:
            raise BadCredentialsException()

        self._profile.username = str(username)
        self._profile.password = str(password)
        self.token = str(tokens['AuthenticationResult']['IdToken'])

    def reset_user_password(self, username: str):
        if username and self.is_authenticated():
            auth = self._get_auth()
            cognito = self._aws_session.client("cognito-idp")
            user_details = cognito.admin_get_user(
                UserPoolId=auth['userPoolId'], Username=username)
            if user_details['UserStatus'] == "FORCE_CHANGE_PASSWORD":
                cognito.admin_create_user(
                    UserPoolId=auth['userPoolId'],
                    Username=username,
                    MessageAction='RESEND')
            else:
                cognito.admin_reset_user_password(
                    UserPoolId=auth['userPoolId'],
                    Username=username)
    
    def reset_password(self):
        return self.reset_user_password(self.username)
# endregion

# region CARTA AGENT
class CartaAgent(CognitoAgent):
    HOST_DEV = "https://api.sandbox.carta.contextualize.us.com"
    HOST_PROD = "https://api.carta.contextualize.us.com"

    def __init__(
        self,
        *,
        profile: str | Profile | None=None,
        username: str | None=None,
        password: str | None=None,
        token: str | None=None,
        environment: str | None=None,
        host: str | None=None,
    ):
        super().__init__(
            profile=profile,
            username=username, password=password,
            token=token,
            environment=environment,
            host=host,)
    
    def is_authenticated(self) -> bool:
        try:
            response = self.get("user/authenticated")
            response.raise_for_status()
            return response.json()
        except BadCredentialsException as e:
            return False
        except HTTPError as e:
            if e.response.status_code == 401:
                return False
            raise
        except:
            raise
# endregion
