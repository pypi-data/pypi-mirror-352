from datetime import datetime


class AuthenticationError(Exception):  # pragma: no cover
    pass


class CartaException(Exception):  # pragma: no cover
    def __init__(self, message="Carta has experienced an error"):
        self.message = message


class BadCredentialsException(CartaException):  # pragma: no cover
    pass


class PermissionDeniedException(CartaException):  # pragma: no cover
    pass


class InvalidParameterException(CartaException):  # pragma: no cover
    def __init__(self, message="Parameter is invalid, or action cannot be completed."):
        super().__init__(message)


class UserCreationFailedException(InvalidParameterException):  # pragma: no cover
    def __init__(self):
        super().__init__("Failed to create user. Either the request parameters are invalid, or the username is already"
                         "taken.")


class CartaServerException(CartaException):  # pragma: no cover
    def __init__(self):
        self.happened = datetime.utcnow()
        super().__init__(f"Fatal server error occurred at {self.happened.isoformat()}. Please contact Carta "
                         f"system administrator.")

class ProfileNotFoundException(Exception):  # pragma: no cover
    pass
