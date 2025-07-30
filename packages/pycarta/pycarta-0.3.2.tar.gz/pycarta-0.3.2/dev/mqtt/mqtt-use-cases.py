import asyncio
from random import randint
from pprint import pprint
from pycarta.mqtt.connection import MqttError
from pycarta.mqtt.publisher import PublishBase as publisher
from pycarta.mqtt.subscriber import SubscribeBase as subscriber
from pycarta.mqtt.credentials import TLSCredentials

PORT = 8883
CREDENTIALS = TLSCredentials(
    ca_cert="ca-cert.pem",
    cert="client.crt",
    key="client.key",
)
OPTS = {
    "host": "localhost",
    "port": PORT,
    "credentials": CREDENTIALS,
    "qos": 1,
}

@publisher(topic="test", **OPTS)
@publisher(topic="test2", **OPTS)
def sync_pub():
    return f"Hello from sync_pub: {randint(1, 100):03d}."

@publisher(topic="test", **OPTS)
async def async_pub():
    await asyncio.sleep(1)
    return f"Hello from async_pub: {randint(1, 100):03d}."

@subscriber(topic="test", **OPTS)
def sync_sub(msg):
    return f"Received {msg!s} from sync_sub."


@subscriber(topic="test", **OPTS)
async def async_sub(msg):
    return f"Received {msg!s} from async_sub."

@subscriber(topic="test", **OPTS)
async def async_add(msg):
    msg = msg.decode() if isinstance(msg, bytes) else msg
    a, b = [float(x.strip()) for x in msg.split(",")]
    return a + b

@subscriber(topic="test", **OPTS)
async def async_mul(msg):
    msg = msg.decode() if isinstance(msg, bytes) else msg
    a, b = [float(x.strip()) for x in msg.split(",")]
    return a * b


@subscriber(topic="test", **OPTS)
def sync_sub_with_stop(msg):
    message = msg.decode() if isinstance(msg, bytes) else msg
    if message == "STOP":
        print("Stopping sync subscriber.")
        raise StopIteration()
    return message

@subscriber(topic="test", **OPTS)
async def async_sub_with_stop(msg):
    message = msg.decode() if isinstance(msg, bytes) else msg
    if message == "STOP":
        print("Stopping async subscriber.")
        raise StopAsyncIteration()
    return message


if __name__ == "__main__":
    # The following tests assume you are running a mosquitto
    # server locally.

    print("Start a local mosquitto server: mosquitto -c broker.cfg")
    print(f"Publisher: mosquitto_pub --cafile ca-cert.pem --cert client.crt --key client.key -h localhost -p {PORT} -t test -m MESSAGE")
    print(f"Subscriber: mosquitto_sub --cafile ca-cert.pem --cert client.crt --key client.key -h localhost -p {PORT} -t test")

    # # ##### publishers ##### #
    # # Start `mosquitto_sub -t test` separately (or equivalent)
    # _ = input("Synchronous publisher (single). Press [enter] to continue...")
    # sync_pub()  # "Hello from sync_pub." should appear in subscriber window.

    
    # _ = input("Async publisher (single). Press [enter] to continue...")
    # asyncio.run(async_pub())  # "Hello from async_pub." should appear.
    # # asyncio.create_task(async_pub())  # "Hello from async_pub." should appear.

    
    # # publish is blocking, so this should take approximately 3 seconds.
    # _ = input("Async publisher (three, gather). Press [enter] to continue...")
    # async def gather_pub():
    #     return await asyncio.gather(async_pub(),
    #                                 async_pub(),
    #                                 async_pub())  # "Hello from async_pub." should appear 3 times.
    # asyncio.run(gather_pub())

    
    # # ##### subscribers ##### #
    # # In the following, "SEND <msg>" sends a message through
    # # `mosquitto_pub -t test <msg>`.

    
    # _ = input("Sync subscriber (single). Press [enter] to continue...")
    # print(sync_sub())  # Exits after receiving 1 message.
    # # SEND <msg>
    # # "Received <msg> from sync_sub." printed to stdout.

    
    # _ = input("Async subscriber (three, sequential). Send comma-separated number pairs. Press [enter] to continue...")
    # print(f"type(async_sub): {type(async_sub)}")
    # print(asyncio.run(async_sub()))  # Exits after receiving message 1
    # print(asyncio.run(async_add()))  # Exits after receiving message 2
    # print(asyncio.run(async_mul()))  # Exits after receiving message 3
    # # SEND <msg>
    # # "Received <msg> from async_sub." printed to stdout.
    # # SEND <msg>
    # # "Received <msg> from async_sub." printed to stdout.
    # # SEND <msg>
    # # "Received <msg> from async_sub." printed to stdout.
    

    # _ = input("Async subscriber (three, gather). Send comma-separated number pairs. Press [enter] to continue...")
    # # QUESTION: Does this make sense, or should this be effectively
    # # the same as the example above?
    # # ANSWER: This does not make sense and should be almost the same as the example
    # # above. Why? Because the logic to running multiple instances on the same
    # # input only makes sense in a very narrow set of conditions -- and all of
    # # have alternate solutions, such as the cooperative use of threading and async.
    # # The only significant difference between this and the previous is that this
    # # approach will wait for three messages to be received before returning the
    # # results. This is not the same as the previous approach, which will return
    # # the results as soon as they are received.
    # async def async_sub_gather():
    #     return await asyncio.gather(async_sub(),
    #                                 async_add(),
    #                                 async_mul())  # Exits after receiving 3 message
    # print(asyncio.run(async_sub_gather()))
    # # SEND <msg>
    # # SEND <msg>
    # # SEND <msg>
    # # ["Received <msg> from async_sub.", "Received <msg> from async_sub.", "Received <msg> from async_sub."] printed to stdout.
    

    # _ = input("Async subscribe (timeout 15 sec). Press [enter] to continue...")
    # # Example of a process that will run for XX seconds before
    # # proceeding.
    # async def timeout():
    #     async with asyncio.timeout(15):
    #         return [msg async for msg in async_sub]
    # arr = asyncio.run(timeout())
    # print("\n".join(arr))
    # # SEND A
    # # SEND B
    # # SEND C
    # # SEND D
    # # After XX seconds, the following lines are printed to the stdout.
    # # A
    # # B
    # # C
    # # D

    # # This doesn't do what I intended: process a workflow. Why? Because the
    # # Timeout exception is not handled by the individual futures, but by
    # # gather, so gather does not exit gracefully.
    # # _ = input("Async subscribe (workflow). Publish comma separated pairs of numbers. Press [enter] to continue...")
    # # async def workflow(timeout: float=15):
    # #     async def make_list():
    # #         return [msg async for msg in async_sub]
    # #     async def add():
    # #         return [result async for result in async_add]
    # #     async def mul():
    # #         return [result async for result in async_mul]

    # #     try:
    # #         async with asyncio.timeout(timeout):
    # #             return await asyncio.gather(
    # #                 make_list(),
    # #                 add(),
    # #                 mul(),
    # #             )
    # #     except TimeoutError:
    # #         print("Timeout reached.")
    # #         pass

    # # result = asyncio.run(workflow(15))
    # # pprint(result)


    # # _ = input("Async subscriber (ctrl-c to stop). Press [enter] to continue...")
    # # # Example of a process that will run forever, until stopped
    # # # manually subscriber-side.
    # # async def run_forever():
    # #     return [msg async for msg in async_sub]
    # # arr = asyncio.run(run_forever())
    # # print("\n".join(arr))
    # # # SEND A
    # # # SEND B
    # # # SEND ...
    # # # When you type ctrl-c, the following are printed to stdout.
    # # # A
    # # # B
    # # # ...

    # # Modified version of the use case above
    # _ = input("Async subscriber (ctrl-c to stop). Press [enter] to continue...")
    # async def run_forever():
    #     arr = []
    #     try:
    #         async for msg in async_sub:
    #             arr.append(msg)
    #     except (KeyboardInterrupt, asyncio.CancelledError):
    #         # When ctrl+c is pressed, catch the exception and return what we've collected.
    #         return arr
    #     return arr

    # # Then run it like:
    # arr = asyncio.run(run_forever())
    # print("\n".join(arr))
    # # # SEND A
    # # # SEND B
    # # # SEND ...
    # # # When you type ctrl-c, the following are printed to stdout.
    # # # A
    # # # B
    # # # ...


    # _ = input("Sync subscriber (send STOP to stop). Press [enter] to continue...")
    # # Example of a process that will run until STOP is received.
    # # (More generally, a predefined message that the function is
    # # looking for.)
    # arr = [m for m in sync_sub_with_stop]
    # print("\n".join(arr))
    # # SEND A
    # # SEND B
    # # SEND STOP
    # # The following is printed to the stdout
    # # A
    # # B

    
    # _ = input("Async subscriber (send STOP to stop). Press [enter] to continue...")
    # # Example of a process that will run until STOP is received.
    # # (More generally, STOP is a predefined message that the function
    # # is looking for.)
    # async def with_stop():
    #     return [m async for m in async_sub_with_stop]
        
    # arr = asyncio.run(with_stop())
    # print("\n".join(arr))
    # # SEND A
    # # SEND B
    # # SEND STOP
    # # The following is printed to the stdout
    # # A
    # # B

    # Test reconnect
    print("Test reconnect.")
    print("1. Start the subscriber (you will be prompted momentarily).")
    print("2. Publish some values.")
    print("3. Stop the broker. This will disconnect the subscriber.")
    print("4. Restart the mosquitto broker: mosquitto -c broker.cfg (subscriber automatically reconnects).")
    print("5. Publish additional values.")
    print("6. Publish STOP.")
    _ = input("Sync subscriber (send STOP to stop). Press [enter] to continue...")
    # Example of a process that will run until STOP is received.
    # (More generally, a predefined message that the function is
    # looking for.)
    # arr = [m for m in sync_sub_with_stop]
    # print("\n".join(arr))

    async def call_async_sub():
        return [msg async for msg in async_sub_with_stop]
    arr = asyncio.run(call_async_sub())
    print("\n".join(arr))

    # IS THIS SUFFICIENT? DO WE NEED ANOTHER OPTION THAT
    # STARTS COLLECTING AT "START" AND STOPS COLLECTING
    # AT "STOP"?

    # # my_application.py
    # import pycarta as pc

    # @pc.subscribe(...)
    # async def monitor(msg):
    #     if "token" in msg:
    #         print("Found token.")

    # task1 = asyncio.create_task(anext(monitor))
    # task2 = asyncio.create_task(async_add)
    # task3 ...

    # result = await async_add()
    # # Do something with the result.

    # async for result in async_add:
    #     # Do something with the result.