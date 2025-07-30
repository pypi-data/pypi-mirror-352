import os
import asyncio
import inspect
import logging
import ssl
import paho.mqtt.client as mqtt
from threading import Event
from uuid import uuid4
from .client import AsyncClient, SyncClient, MqttError
from .credentials import TLSCredentials
from .exceptions import validate_connection, ConnectionTimeoutError

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class ClientGenerator:
    """
    ClientGenerator establishes a common API for creating either
    a synchronous MQTT client (paho.mqtt.client.Client) or an
    asynchronous client (aiomqtt.client.Client).

    An appropriate client is created depending on the context in
    which the client operates, e.g.

    .. code: python

        with ClientGenerator() as client:
            # Produces a synchronous client
            client.connect(host="localhost", port=1883)
            client.publish(...)

        async with ClientGenerator(host="localhost", port=1883) as client:
            # Produces an asynchronous client
            client.publish(...)
    """
    def __init__(self, credentials: TLSCredentials | None=None, **kwargs):
        self.kwargs = kwargs
        self.credentials = credentials
        self.kwargs.setdefault("client_id", str(uuid4()))
        self.kwargs.setdefault("callback_api_version", mqtt.CallbackAPIVersion.VERSION2)

    def __enter__(self) -> SyncClient:
        logger.debug("Entering ClientGenerator context.")
        kwargs = {k:v for k,v in self.kwargs.items()
                  if k in inspect.signature(SyncClient).parameters}
        client = SyncClient(**kwargs)
        if self.credentials:
            client = self.credentials.authenticate(client)
        logger.debug("ClientGenerator context setup complete.")
        return client

    def __exit__(self, *exc):
        logger.debug("Exited ClientGenerator context.")

    async def __aenter__(self) -> AsyncClient:
        logger.debug("Entering async ClientGenerator context.")
        kwargs = {k:v for k,v in self.kwargs.items()
                  if k in inspect.signature(AsyncClient).parameters}
        client = AsyncClient(**kwargs)
        if self.credentials:
            client = self.credentials.authenticate(client)
        logger.debug("Async ClientGenerator context setup complete.")
        return client

    async def __aexit__(self, *exc):
        logger.debug("Exited async ClientGenerator context.")


class Connection:
    """
    Connection establishes a common API for connecting to an MQTT broker.
    When a Connection context is established, the context returns a connected
    client, either synchronous or asynchronous depending on the context, that
    handles reconnects and disconnects.

    .. code: python

        with Connection() as client:
            # Returns a connected, synchronous client.
            client.publish(...)

        async with Connection() as client:
            # Returns a connected, asynchronous client.
            client.publish(...)
    """
    # def __init__(self, gen: ClientGenerator | None=None, **kwargs):
    def __init__(self, host: str="localhost", port: int=1883, *,
                 credentials: TLSCredentials | None=None,
                 **kwargs):
        # self.client_generator: ClientGenerator = gen or ClientGenerator()
        self.kwargs = kwargs.copy()
        self.kwargs["host"] = host
        self.kwargs["port"] = port
        self.credentials = credentials
        if self.credentials is not None:
            self.credentials._connection = self
        self.client_generator: ClientGenerator = ClientGenerator(credentials, **self.kwargs)
        self.client: AsyncClient | SyncClient | None = None
        self.event: Event = Event()
        self.callbacks = {
            "on_connect": self.on_connect,
            "on_disconnect": self.on_disconnect,
        }

    def __enter__(self) -> SyncClient:
        logger.debug("Entering Connection context.")
        validate_connection(
            host=self.kwargs["host"],
            port=self.kwargs["port"],
            credentials=self.credentials,
            timeout=3
        )

        if not self.client:
            # Reuse the client
            self.client = self.client_generator.__enter__()
        for k,v in self.callbacks.items():
            logger.debug(f"Registering {k} callback: {v}")
            setattr(self.client, k, v)
        try:
            self.event.clear()
            wait = 1
            while True:
                try:
                    self.client.connect(**self.kwargs)
                    self.client.loop_stop()
                    self.client.loop_start()
                    logger.debug("Waiting to establish connection (with timeout)…")
                    if not self.event.wait(timeout=3):
                        raise ConnectionTimeoutError(3)
                except ConnectionRefusedError:
                    logger.debug(f"Broker unavailable. Retry in {wait} seconds.")
                    self.event.wait(wait)
                    wait = min(2*wait, 120)
                except:
                    raise
                else:
                    logger.debug("Connection established.")
                    break
        except KeyboardInterrupt:
            logger.debug("Attempt to connect cancelled.")
            raise
        except Exception as e:
            logger.error(f"Failed to connect {self.client} with {self.kwargs}: {e}")
            raise
        logger.debug("Connection context setup complete.")
        return self.client

    def __exit__(self, *exc):
        self.client.disconnect()
        self.client.loop_stop()
        self.client_generator.__exit__()
        logger.debug("Exited Connection context.")

    async def __aenter__(self) -> AsyncClient:
        logger.debug("Entering async Connection context.")
        validate_connection(
            host=self.kwargs["host"],
            port=self.kwargs["port"],
            credentials=self.credentials,
            timeout=3
        )
        # Aiomqtt Client combines client and connection.
        kwargs = {**self.client_generator.kwargs, **self.kwargs}
        # Handle API inconsistency between Paho Client and Aiomqtt Client.
        kwargs["hostname"] = kwargs.pop("host")
        self.client_generator.kwargs.update(kwargs)
        # Generate and connect client.
        if self.client is None:
            self.client = await self.client_generator.__aenter__()
        else:
            await self.__aexit__(None, None, None)
            logger.debug("Reentered async Connection context.")
        wait = 1
        while True:
            try:
                await self.client.__aenter__()
            except (ConnectionRefusedError, MqttError):
                logger.info(f"Broker not available. Attempting to reconnect in {wait} seconds.")
                await asyncio.sleep(wait)
                wait = min(2*wait, 120)
            except KeyboardInterrupt as e:
                logger.debug("Attempt to connect cancelled.")
                await self.client.__aexit__(type(e), e, None)
                raise
            except Exception as e:
                logger.error(f"An unexpected error occured while connecting ({e}). Aborting.")
                await self.client.__aexit__(type(e), e, None)
                raise
            else:
                logger.debug(f"Connected to {kwargs['hostname']}:{kwargs['port']}")
                break
        logger.debug("Async Connection context complete.")
        return self.client

    async def __aexit__(self, *exc):
        client = self.client
        try:
            await client.__aexit__(*exc)
        except MqttError:
            # Try to gracefully disconnect from the broker
            rc = client._client.disconnect()
            if rc == mqtt.MQTT_ERR_SUCCESS:
                # Wait for acknowledgement
                await client._wait_for(client._disconnected, timeout=None)
                # Reset `_connected` if it's still in completed state after disconnecting
                if client._connected.done():
                    client._connected = asyncio.Future()
            else:
                logger.warning(
                    "Could not gracefully disconnect: %d. Forcing disconnection.", rc
                )
            # Force disconnection if we cannot gracefully disconnect
            if not client._disconnected.done():
                client._disconnected.set_result(None)
            # Release the reusability lock
            if client._lock.locked():
                client._lock.release()
        await self.client_generator.__aexit__(*exc)
        logger.debug("Exited async Connection context.")

    def on_connect(self, client, userdata, connect_flags, reason_code, properties):
        logger.debug("Starting connection loop.")
        self.event.set()

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        # logger.debug("Stopping connection loop.")
        # client.loop_stop()
        pass
