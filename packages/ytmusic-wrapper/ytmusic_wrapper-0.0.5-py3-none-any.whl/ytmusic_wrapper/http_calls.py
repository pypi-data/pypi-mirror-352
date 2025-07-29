"""Provides a class `HTTPCalls` to handle asynchronous HTTP GET and POST requests to the Youtube Music API Server using the `aiohttp` library.

Methods:
    __init__: Initializes with host, port, and websession.
    get_call: Sends an async GET request.
    post_call: Sends an async POST request.

"""
from __future__ import annotations
import logging

from aiohttp import ClientError, ClientSession, ClientResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class HTTPCalls:
    """Class to handle HTTP calls to the Youtube Music API Server."""

    def __init__(self, host: str, port: int, websession: ClientSession) -> None:
        """Initialize the HTTPCalls class with host, port, and websession."""
        self.host = host
        self.port = port
        self.websession = websession

    async def get_call(
        self,
        endpoint: str,
        access_token: str | None = None,
        raise_for_status: bool = False,
    ) -> ClientResponse | None:
        """Send an asynchronous GET request to the specified endpoint."""
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {}
        try:
            response = await self.websession.get(
                "http://" + self.host + ":" + str(self.port) + endpoint, headers=headers
            )
        except ClientError as e:
            if raise_for_status:
                raise
            logger.warning("HTTP GET against %s request failed: %s", endpoint, e)
            return None

        if 200 <= response.status < 300:
            logger.debug("Successfully sent GET request")
            return response
        logger.error(
            "Error occurred: Status %s for GET call to %s", response.status, endpoint
        )
        return None

    async def post_call(
        self,
        endpoint: str,
        access_token: str | None = None,
        body: str | None = None,
        raise_for_status: bool = False,
    ) -> ClientResponse | None:
        """Send an asynchronous POST request to the specified endpoint."""
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {}
        try:
            response = await self.websession.post(
                "http://" + self.host + ":" + str(self.port) + endpoint,
                headers=headers,
                json=body,
            )
        except ClientError as e:
            if raise_for_status:
                raise
            logger.warning("HTTP POST against %s request failed: %s", endpoint, e)
            return None
        if 200 <= response.status < 300:
            logger.debug("Successfully sent POST request")
            return response
        logger.error(
            "Error occurred: Status %s for POST call to %s", response.status, endpoint
        )
        return None

    async def delete_call(
        self,
        endpoint: str,
        access_token: str | None = None,
        raise_for_status: bool = False,
    ) -> ClientResponse | None:
        """Send an asynchronous DELETE request to the specified endpoint."""
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {}
        try:
            response = await self.websession.delete(
                "http://" + self.host + ":" + str(self.port) + endpoint,
                headers=headers,
            )
        except ClientError as e:
            if raise_for_status:
                raise
            logger.warning("HTTP DELETE against %s request failed: %s", endpoint, e)
            return None
        if 200 <= response.status < 300:
            logger.debug("Successfully sent DELETE request")
            return response
        logger.error(
            "Error occurred: Status %s for DELETE call to %s", response.status, endpoint
        )
        return None
