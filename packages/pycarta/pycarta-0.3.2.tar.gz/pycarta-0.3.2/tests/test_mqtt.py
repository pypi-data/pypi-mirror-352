import asyncio
import asyncio.timeouts
import logging
import pytest
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager
from queue import Queue
from pycarta.mqtt import publish, subscribe, timeout
from pycarta.mqtt.formatter import Formatter
from pycarta.mqtt.credentials import TLSCredentials

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@pytest.fixture(scope="module", autouse=True)
def local_broker():
    """
    Fixture to set up and tear down the MQTT broker for testing.
    """
    # Setup: Start the MQTT broker
    def start_broker(start_event, stop_event):
        logger.info("Starting MQTT broker.")
        command = [shutil.which("mosquitto"), "-c", "data/broker.cfg"]
        try:
            process = subprocess.Popen(command)
        except:
            msg = "Failed to start MQTT broker. 'mosquitto' MQTT server must be in your path."
            logger.error(msg)
            raise RuntimeError(msg)
        logger.info("Started MQTT broker.")
        start_event.set()
        stop_event.wait()
        logger.info("Stopping MQTT broker.")
        process.terminate()
        process.wait()

    start_event = threading.Event(); start_event.clear()
    stop_event = threading.Event(); stop_event.clear()
    logger.info("Creating MQTT broker thread.")
    thread = threading.Thread(target=start_broker, args=(start_event, stop_event,))
    # thread.daemon = True
    logger.info("Starting MQTT broker thread.")
    thread.start()
    start_event.wait()

    # Yield control to the test case
    logger.info("Yielding control to the test case.")
    yield

    # Teardown: Stop the MQTT broker
    logger.info("Tearing down MQTT broker.")
    stop_event.set()
    thread.join()


@pytest.fixture(scope="module")
def credentials():
    return TLSCredentials().local.read("data/credentials.zip")
    # return TLSCredentials(ca_cert="data/ca-cert.pem", cert="data/client.crt", key="data/client.key")


@pytest.fixture(scope="module")
def mosquitto_org_credentials():
    credentials = TLSCredentials()
    credentials.ca = "data/mosquitto.org.crt"
    return credentials


@contextmanager
def mqtt_publisher(message: str, *,
                   topic: str,
                   host: str="localhost", port: int=8883,
                   delay: float=2.0):
    command = [
        shutil.which("mosquitto_pub"),
        "-h", host,
        "-p", str(port),
        "-t", f"{topic}",
        "-m", f"'{message}'"]
    if host == "localhost" and port == 8883:
        command.extend([
            "--cafile", "data/ca-cert.pem",
            "--cert", "data/client.crt",
            "--key", "data/client.key",
        ])
    if host == "test.mosquitto.org" and port == 8883:
        command.extend([
            "--cafile", "data/mosquitto.org.crt",
        ])
    
    def run():
        while True:
            process = subprocess.run(command, capture_output=True)
            logger.info(f"MQTT publisher complete with return code: {process.returncode}")
            if process.returncode != 0:
                logger.error(f"MQTT publisher stderr: {process.stderr.decode('utf-8')}")
            time.sleep(delay)
            if event.is_set():
                break
    
    logger.info(f"Running MQTT publisher: '" + " ".join(command) + "'")
    event = threading.Event(); event.clear()
    try:
        thread = threading.Thread(target=run)
        thread.start()
        yield
    finally:
        event.set()
        if thread.is_alive():
            thread.join()


@contextmanager
def mqtt_subscriber(topic, *,
                    host: str="localhost",
                    port: int=8883,
):
    stop_queue = threading.Event(); stop_queue.clear()

    command = [
        shutil.which("mosquitto_sub"),
        "-h", host,
        "-p", str(port),
        "-t", f"{topic}"
    ]
    if host == "localhost" and port == 8883:
        command.extend([
            "--cafile", "data/ca-cert.pem",
            "--cert", "data/client.crt",
            "--key", "data/client.key",
        ])
    if host == "test.mosquitto.org" and port == 8883:
        command.extend([
            "--cafile", "data/mosquitto.org.crt",
        ])

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,
                               bufsize=1,)
    
    def enqueue_output(pipe, q):
        for line in iter(pipe.readline, ''):
            q.put(Formatter().unpack(line))
            if stop_queue.is_set():
                break
        pipe.close()

    queue = Queue()
    thread = threading.Thread(target=enqueue_output, args=(process.stdout, queue))
    thread.start()

    # Publish messages until the subscriber connects
    with mqtt_publisher("Wake up!", topic=topic, host=host, port=port, delay=0.5):
        _ = queue.get()
    while queue.qsize():
        _ = queue.get()

    try:
        yield queue
    finally:
        logger.info("Stopping MQTT subscriber.")
        process.terminate()
        process.wait()
        stop_queue.set()
        thread.join()


@pytest.mark.asyncio
async def test_subscribe(credentials, mosquitto_org_credentials):
    logger.info("Entered test_subscribe")
    topic = "pycarta-mqtt-test"

    def clean_message(m):
        return str(m.decode() if isinstance(m, bytes) else m).strip("'").strip('"')

    # local
    logger.info("<<<<< LOCAL >>>>>")

    @subscribe(topic=topic, host="localhost", port=8883, credentials=credentials)
    def sync_subscribe(msg):
        return msg

    @subscribe(topic=topic, host="localhost", port=8883, credentials=credentials)
    async def async_subscribe(msg):
        return msg
    
    with mqtt_publisher("Hello, sync!", topic=topic):
        logger.info("sync_subscribe: single")
        msg = clean_message(sync_subscribe())
        assert msg == "Hello, sync!"

    with mqtt_publisher("Hello, sync!", topic=topic):
        logger.info("sync_subscribe: iterator")
        with timeout(5):
            arr = [x for x in sync_subscribe]
        arr = [x == "Hello, sync!" for x in map(clean_message, arr)]
        assert all(arr)

    with mqtt_publisher("Hello, async!", topic=topic):
        logger.info("async_subscribe: single")
        msg = clean_message(await async_subscribe())
        assert msg == "Hello, async!"

    with mqtt_publisher("Hello, async!", topic=topic):
        logger.info("async_subscribe: iterator")
        async def run():
            return [x async for x in async_subscribe]
        async with asyncio.timeout(5):
            arr = await run()
        arr = [x == "Hello, async!" for x in map(clean_message, arr)]
        assert all(arr)

    # remote host (host="test.mosquitto.org")
    logger.info("<<<<< REMOTE >>>>>")

    @subscribe(topic=topic, host="test.mosquitto.org", port=8883, credentials=mosquitto_org_credentials)
    def sync_subscribe(msg):
        return msg

    @subscribe(topic=topic, host="test.mosquitto.org", port=8883, credentials=mosquitto_org_credentials)
    async def async_subscribe(msg):
        return msg
    

    with mqtt_publisher("Hello, sync!", topic=topic, host="test.mosquitto.org"):
        logger.info("sync_subscribe: single")
        msg = clean_message(sync_subscribe())
        assert msg == "Hello, sync!"

    with mqtt_publisher("Hello, sync!", topic=topic, host="test.mosquitto.org"):
        logger.info("sync_subscribe: iterator")
        with timeout(5):
            arr = [x for x in sync_subscribe]
        arr = [x == "Hello, sync!" for x in map(clean_message, arr)]
        assert all(arr)

    with mqtt_publisher("Hello, async!", topic=topic, host="test.mosquitto.org"):
        logger.info("async_subscribe: single")
        msg = clean_message(await async_subscribe())
        assert msg == "Hello, async!"

    with mqtt_publisher("Hello, async!", topic=topic, host="test.mosquitto.org"):
        logger.info("async_subscribe: iterator")
        async def run():
            return [x async for x in async_subscribe]
        async with asyncio.timeout(5):
            arr = await run()
        arr = [x == "Hello, async!" for x in map(clean_message, arr)]
        assert all(arr)


@pytest.mark.asyncio
async def test_publish(credentials, mosquitto_org_credentials):
    """
    Test the synchronous publish function.
    """
    logger.info("Entered test_publish")
    topic = "pycarta/mqtt/test"

    # local
    logger.info("<<<<< LOCAL >>>>>")

    @publish(topic=topic, host="localhost", port=8883, credentials=credentials)
    def sync_publish(msg):
        return msg
    
    @publish(topic=topic, host="localhost", port=8883, credentials=credentials)
    async def async_publish(msg):
        await asyncio.sleep(5)
        return msg
    
    with mqtt_subscriber(topic) as queue:

        # test synchronous publisher
        sync_publish("Hello, sync!")
        assert queue.get().strip() == "Hello, sync!"
        logger.info("sync_publish() passed.")

        # test asynchronous publisher
        await async_publish("Hello, async!")
        assert queue.get().strip() == "Hello, async!"
        logger.info("async_publish() passed.")

        # test multiple, simultaneous asynchronous publishers
        try:
            async with asyncio.timeout(10):
                _ = await asyncio.gather(
                    async_publish("Hello, async 1!"),
                    async_publish("Hello, async 2!"),
                    async_publish("Hello, async 3!"),
                )
            logger.info("gather(async_publish(), ...) passed.")
            # _ = [queue.get() for _ in range(3)]
        except asyncio.TimeoutError:
            assert False, "TimeoutError: async_publish() did not run in parallel."

    # remote: test.mosquitto.org
    logger.info("<<<<< REMOTE >>>>>")

    @publish(topic=topic, host="test.mosquitto.org", port=8883, credentials=mosquitto_org_credentials)
    def sync_publish(msg):
        return msg
    
    @publish(topic=topic, host="test.mosquitto.org", port=8883, credentials=mosquitto_org_credentials)
    async def async_publish(msg):
        await asyncio.sleep(5)
        return msg
    
    with mqtt_subscriber(topic, host="test.mosquitto.org") as queue:

        # test synchronous publisher
        sync_publish("Hello, sync!")
        assert queue.get().strip() == "Hello, sync!"
        logger.info("sync_publish() passed.")

        # test asynchronous publisher
        await async_publish("Hello, async!")
        assert queue.get().strip() == "Hello, async!"
        logger.info("async_publish() passed.")

        # test multiple, simultaneous asynchronous publishers
        try:
            async with asyncio.timeout(10):
                _ = await asyncio.gather(
                    async_publish("Hello, async 1!"),
                    async_publish("Hello, async 2!"),
                    async_publish("Hello, async 3!"),
                )
            logger.info("gather(async_publish(), ...) passed.")
            # _ = [queue.get() for _ in range(3)]
        except asyncio.TimeoutError:
            assert False, "TimeoutError: async_publish() did not run in parallel."
