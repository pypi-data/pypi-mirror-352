import os
import ssl
import socket
from aiomqtt import MqttError, MqttCodeError


class PyCartaMQTTError(Exception):
    """Base exception for all PyCarta MQTT errors."""
    pass


class ConfigurationError(PyCartaMQTTError):
    """Raised when the MQTT client configuration is invalid."""
    pass


class UnsupportedQoSError(ConfigurationError):
    """Raised when the broker does not support the requested QoS level."""

    def __init__(self, qos: int, broker: str, message: str | None = None):
        if message is None:
            message = (
                f"Broker {broker!r} does not support QoS {qos}. "
                "Please use QoS 0 or 1."
            )
        super().__init__(message)
        self.qos = qos
        self.broker = broker


class AckTimeoutError(PyCartaMQTTError):
    """Raised when a PUBACK or SUBACK is not received within the expected time."""

    def __init__(self,
                 ack_type: str,
                 qos: int,
                 timeout: float,
                 topic: str,
                 message: str | None = None):
        if message is None:
            action = "publish" if ack_type.upper() == "PUBACK" else "subscribe"
            message = (
                f"Timed out waiting for the broker’s {ack_type} (QoS {qos}) "
                f"after {timeout} seconds on topic {topic}. "
                "This typically means your client isn’t authorized to "
                f"{action} this topic (check that your TLS certificate has the necessary permissions)."
            )
        super().__init__(message)
        self.ack_type = ack_type
        self.qos = qos
        self.timeout = timeout
        self.topic = topic


# TLS credential validation errors
class CredentialValidationError(ConfigurationError):
    """Base for all credential-validation failures."""
    pass


class MissingCredentialsError(CredentialValidationError):
    """Raised when CA, client cert, or key is missing."""

    def __init__(self):
        super().__init__(
            "TLS is enabled but CA certificate, client certificate, or private key is missing."
        )


class CertificateFileNotFoundError(CredentialValidationError):
    """Raised when one of the cert/key files cannot be found on disk."""

    def __init__(self, path: str, label: str):
        super().__init__(f"{label} file not found at '{path}'. Please verify the path.")


class CertificateMismatchError(CredentialValidationError):
    """Raised when the client cert and key do not form a valid pair."""

    def __init__(self, message: str | None = None):
        super().__init__(
            message or "Client certificate and private key do not match. Please use matching files."
        )


class TLSSetupError(CredentialValidationError):
    """Raised when Paho’s tls_set() fails unexpectedly."""
    def __init__(self, message: str = None):
        super().__init__(
            message
            or "Unexpected TLS setup failure. Please verify your certificates."
        )


class CertificateNotAuthorizedError(CredentialValidationError):
    """Raised when the broker refuses TLS handshake with given certs."""

    def __init__(self, host: str, port: int):
        super().__init__(f"Certificate is valid but not authorized or not required for broker {host}:{port}.")


def validate_tls_credentials(
    ca: str | None,
    cert: str | None,
    key: str | None,
    host: str,
    port: int
) -> None:
    """
    1) Verify presence of ca, cert, key.
    2) Verify each file exists.
    3) Verify cert/key match.
    4) Perform a real TLS handshake to check authorization.
    """
    # presence
    if not (ca and cert and key):
        raise MissingCredentialsError()

    # existence
    for path, label in [(ca, "CA certificate"), (cert, "Client certificate"), (key, "Client private key")]:
        if not os.path.exists(path):
            raise CertificateFileNotFoundError(path, label)

    # match
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_cert_chain(certfile=cert, keyfile=key)
    except ssl.SSLError as e:
        raise CertificateMismatchError() from e

    # handshake
    vctx = ssl.create_default_context(cafile=ca)
    vctx.check_hostname = False
    vctx.load_cert_chain(certfile=cert, keyfile=key)
    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            with vctx.wrap_socket(sock, server_hostname=host):
                pass
    except ssl.SSLError as e:
        # Handshake issues (e.g. broker refusal)
        raise CertificateNotAuthorizedError(host, port) from e


# Connection validation errors
class HostResolutionError(ConfigurationError):
    """Raised when the broker hostname cannot be resolved."""
    def __init__(self, host: str):
        super().__init__(f"Unable to resolve broker hostname '{host}'. Please verify the address.")
        self.host = host


class InvalidPortError(ConfigurationError):
    """Raised when the port is not a valid integer."""
    def __init__(self, port):
        super().__init__(f"Port value '{port}' is not an integer. Please specify a valid integer port.")
        self.port = port


class PortOutOfRangeError(ConfigurationError):
    """Raised when the port is out of the 0–65535 range."""
    def __init__(self, port: int):
        super().__init__(f"Port '{port}' is out of range [0, 65535]. Please specify a valid port.")
        self.port = port


class BrokerConnectionError(ConfigurationError):
    """Raised when a plain TCP connection to the broker fails."""
    def __init__(self, host: str, port: int):
        super().__init__(f"Unable to connect to '{host}:{port}'. Port may be closed or inaccessible.")
        self.host = host
        self.port = port


class ConnectionTimeoutError(ConfigurationError):
    """Raised when waiting for the broker’s CONNACK times out."""
    def __init__(self, timeout: float):
        super().__init__(
            f"Timed out waiting for the broker’s CONNACK after {timeout} seconds. "
            "Connection may be hanging due to TLS auth issues or network problems."
        )
        self.timeout = timeout


def validate_connection(
    host: str,
    port: int,
    credentials=None,
    timeout: float = 3
) -> None:
    """
    Perform all pre-connection checks:
      1) Hostname resolution
      2) Port type and range
      3) Plain-TCP connection
      4) Optional TLS credential validation
    """
    # 1) hostname
    try:
        socket.gethostbyname(host)
    except socket.gaierror as e:
        raise HostResolutionError(host) from e
    # 2) port
    if not isinstance(port, int):
        raise InvalidPortError(port)
    if not (0 <= port <= 65535):
        raise PortOutOfRangeError(port)
    # 3) TCP
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
    except OSError as e:
        raise BrokerConnectionError(host, port) from e
    # 4) TLS
    if credentials and getattr(credentials, "_content", None) is not None:
        credentials.validate(host, port)
