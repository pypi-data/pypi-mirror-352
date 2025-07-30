"""
Services are defined through a FastAPI interface, but communication to or from
the local system must occur through a third party mediator, such as a
websockets API, as exposed by Carta Service Manager.

This module defines proxies that are used to forward content into a service.
This proxy listens for incoming content and, therefore, should be async.
"""

from __future__ import annotations

import os

import asyncio
import json
import logging
import requests
import websockets
from abc import ABC, abstractmethod
from ..auth.agent import CartaAgent
from pprint import pformat
from pydantic import BaseModel, Field
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())


# region Models
class HttpRequest(BaseModel):
    headers: dict[str, Any]
    path: str
    method: str = Field(alias="httpMethod")
    # params: None | dict[str, Any] = Field(None, alias="queryStringParameters")
    params: None | dict[str, Any] = Field(None, alias="params")
    body: None | Any=None

    def authorization(self) -> str:
        try:
            return self.headers.get("Authorization", self.headers.get("X_CARTA_TOKEN", "")).split(" ")[1]
        except IndexError:
            return None

    def json(self):
        try:
            return json.loads(self.body)
        except:
            return self.body


class HttpResponse(BaseModel):
    status_code: int
    reason: str
    headers: dict[str, Any]
    body: None | Any=None
# endregion


# region Proxy ABCs
class Proxy(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    async def handler(self, request: Any):
        raise NotImplementedError("Proxy subclasses must define 'handler'.")

    @abstractmethod
    async def listen(self):
        raise NotImplementedError("Proxy subclasses must define 'listen'.")
    

class WebsocketProxy(Proxy):
    def __init__(
        self,
        uri: str,
        *args,
        redirect: str,
        **kwds,
    ):
        from websockets.asyncio.client import connect
        # self.client = websockets.connect(uri, *args, **kwds)  # websockets.client.connect is deprecated. Delete on cleanup.
        self.client = connect(uri, *args, **kwds)
        self.redirect: str = redirect.strip("/")

    async def listen(self):
        retry_count = 0
        max_retries = 5
        async for connection in self.client:
            while True:
                message = await connection.recv()
                logger.info(f"Received message from websockets: {pformat(json.loads(message))}.")
                if json.loads(message).get("message") == "Internal server error":
                    # Send failed. Attempt to resubmit the last message
                    retry_count += 1
                    if retry_count > max_retries:
                        logger.info("Max retries reached. Exiting.")
                        break
                    else:
                        logger.info(f"Send failed. Retry {retry_count}.")
                        logger.info(f"Resubmitting {pformat(response)}")
                        await connection.send(json.dumps(response))
                else:
                    # Process the message
                    response = await self.handler(message)
                    await connection.send(json.dumps(response))
                    logger.info(f"Sent response to websockets: {pformat(response)}")

# end region


# region Carta Service Manager
class CartaServiceManagerProxy(WebsocketProxy):
    class IncomingEvent(BaseModel):
        task_id: str = Field(alias="taskId")
        event: HttpRequest

        @classmethod
        def parse_request(cls, event: str | dict[str, Any]):
            try:
                event = json.loads(event)
            except:
                logger.info(f"Could not parse event: {event}")
                event = event
            logger.info(f"Received event into Carta Service Manager proxy: {pformat(event)}")
            taskId = event["taskId"]
            headers = event["event"]["headers"]
            event_ = {
                "headers": dict(),
                "httpMethod": event["event"]["httpMethod"],
                "path": event["event"]["path"],
                "params": event["event"].get(
                    # Coming from a python requests object.
                    "params",
                    event["event"].get(
                        # Coming from an AWS API Gateway object.
                        "queryStringParameters",
                        None)),
                "body": event["event"].get("body", None),
            }
            if "Authorization" in headers or "X_CARTA_TOKEN" in headers:
                event_["headers"]["Authorization"] = headers.get("Authorization", headers.get("X_CARTA_TOKEN"))
            logger.debug(f"Event: {pformat(event_)}")
            return cls(**{
                "taskId": taskId,
                "event": HttpRequest(**event_),
            })

    class OutgoingEvent(BaseModel):
        task_id: str = Field(alias="taskId")
        event: HttpResponse

        @classmethod
        def parse_response(cls, response: requests.Response, *, task_id: str):
            try:
                body = json.dumps(response.json())
            except:
                body = response.text
            return cls(**{
                "taskId": task_id,
                "event": HttpResponse(**{
                    "status_code": response.status_code,
                    "reason": response.reason,
                    "headers": dict(response.headers),
                    "body": body
                }),
            })

    def __init__(
        self,
        uri: str,
        namespace: str,
        service: str,
        *args,
        redirect: str,
        agent: None | CartaAgent=None,
        **kwds,
    ):
        """
        Redirects events/messages received from Carta Service Manager
        Websockets API to the FastAPI spun up for the local service handler.
        This is typically 'http://localhost:{port}'.

        Parameters
        ----------
        uri : str
            URI of the Carta Service Manager websockets API.
        namespace : str
            The namespace of the Carta service.
        service : str
            The name of the Carta service.
        redirect : str
            URL to which incoming messages are redirected. This is typically
            'http://localhost:<port>' where <port> is the port number that the
            service is listening on.
        agent : CartaAgent (optional)
            If specified, the websockets connection is established with this
            agent. If not, then the global agent is used.

        *args, **kwds
            All other arguments are keywords are passed through to establish
            the websockets connection.
        """
        if agent is None:
            from pycarta import get_agent
            agent = get_agent()
        self.agent: CartaAgent = agent
        self.namespace: str = str(namespace)
        self.service: str = str(service)
        kwds["additional_headers"] = kwds.get("additional_headers", dict())
        kwds["additional_headers"].setdefault("Authorization", f"Bearer {self.agent.token}")
        uri = f"{uri.strip('/')}?namespace={namespace}&service={service}"
        super().__init__(uri, *args, redirect=redirect, **kwds)

    async def handler(self, payload: str | dict[str, Any]) -> dict:
        request = CartaServiceManagerProxy.IncomingEvent.parse_request(payload)
        url = f"{self.redirect.strip('/')}/{request.event.path.strip('/')}"
        logger.info(f"Calling proxied HTTP ({url}).")
        # try:
        #     response = requests.request(
        #         request.event.method,
        #         url,
        #         headers=request.event.headers,
        #         params=request.event.params or None,
        #         json=request.event.json(),
        #     )
        #     response.raise_for_status()
        #     logger.info(f"Successful response from proxied HTTP ({url}).")
        # except requests.HTTPError as e:
        #     logger.error(f"Failed response from proxied HTTP ({e}).")
        #     logger.info(f"Payload: {payload}")
        #     logger.info(f"Status code: {e.response.status_code}")
        #     logger.info(f"Reason: {e.response.reason}")
        #     # logger.info(f"Headers: {pformat(e.response.headers)}")
        #     logger.info(f"Body: {e.response.text}")
        #     # logger.info(f"Request: {pformat(request.model_dump(by_alias=True))}")
        #     raise e
        # except: # requests.HTTPError as e:
        #     from pprint import pformat
        #     logger.error(f"Failed response from proxied HTTP ({url}).")
        #     logger.info(f"Request: {pformat(request.model_dump(by_alias=True))}")
        #     raise
        response = requests.request(
            request.event.method,
            url,
            headers=request.event.headers,
            params=request.event.params or None,
            json=request.event.json(),
        )
        logger.info(f"Completed proxied HTTP ({url}).")
        return CartaServiceManagerProxy.OutgoingEvent.parse_response(
            response,
            task_id=request.task_id,
        ).model_dump(by_alias=True)
# end region
