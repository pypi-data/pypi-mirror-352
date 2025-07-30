import os
import asyncio
import json
import logging
import pytest
import requests
import time
from contextlib import contextmanager
from pprint import pformat
from pycarta.admin.service import utilize_service
from pycarta.services import service
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class Calculation(BaseModel):
    lhs: float
    rhs: float

    def __call__(self) -> float:
        return self.lhs + self.rhs
    

@contextmanager
def start_service():
    from threading import Event, Thread

    async def worker(flag):
        task = asyncio.create_task(service.connect())
        while not flag.is_set():
            await asyncio.sleep(0.1)
        task.cancel()

    flag = Event(); flag.clear()
    thread = Thread(target=asyncio.run, args=(worker(flag),))
    thread.start()
    flag.wait(timeout=5)  # Give the service time to start

    try:
        yield
    finally:
        flag.set()
        thread.join()


def test_create_service():
    namespace = "test"
    name = "delme"

    @service(namespace=namespace, service=name).get()
    def foo():
        """
        Foo Summary

        Returns
        -------
        str

            Simple message.
        """
        return "Hello from 'foo'"

    @service(namespace=namespace, service=name).get()
    def add(*, lhs: float, rhs: float) -> float:
        """
        Adds two numbers together.

        Parameters
        ----------
        lhs (float) : Left operand.

        rhs (float) : Right operand.
        
        Returns
        -------
        float
        """
        logger.debug(f"Calling add(lhs={lhs} ({type(lhs)}), {rhs} ({type(rhs)}))")
        return lhs + rhs

    @service(namespace=namespace, service=name).post()
    def calc(payload: Calculation) -> float:
        f"""
        Constructs then calls a `Calculation` object from the
        contents of the request body.

        body
        ----
        {pformat(Calculation.model_json_schema())}

        Returns
        -------
        float
        """
        return payload()
    
    try:
        with start_service():
            try:
                svc = utilize_service(namespace=namespace, service=name)
                
                submit = svc.get("foo"); submit.raise_for_status()
                time.sleep(3)
                result = svc.get(params=submit.json())
                assert json.loads(result.json()["response"]) == "Hello from 'foo'"

                submit = svc.get("add", params={"lhs": 1, "rhs": 2}); submit.raise_for_status()
                time.sleep(3)
                result = svc.get(params=submit.json())
                assert json.loads(result.json()["response"]) == 3

                submit = svc.post("calc", json={"lhs": 1, "rhs": 2}); submit.raise_for_status()
                time.sleep(3)
                result = svc.get(params=submit.json())
                assert json.loads(result.json()["response"]) == 3

            except requests.HTTPError as e:
                # pytest.fail(f"{e.response.status_code}: {e.response.text}")
                raise RuntimeError(f"{e.response.status_code}: {e.response.text}")
            except Exception as e:
                logger.error(f"Submit: {submit.json()}")
                logger.error(f"Result: {result.json()}")
                raise
            #     pytest.fail(str(e))
    finally:
        service.cleanup(force=True)

