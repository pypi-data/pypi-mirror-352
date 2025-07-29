"""Package for the Youtube Music API Wrapper.

Initializes this module for the HTTP calls and obtains the access token for the Youtube Music API Server.
"""
from __future__ import annotations

import aiohttp

from .api_calls import APICalls
from .http_calls import HTTPCalls


class ytmusic_wrapper:
    """Initialize the Main function for the HTTP calls and obtain the access token.

    Returns an instance of APICalls, on which the Music Controller functions can be called.
    """

    api_calls: APICalls
    is_online: bool = False

    def __init__(self, host: str, port: int) -> None:
        """Create an instance of APICalls with the given host and port."""
        session = aiohttp.ClientSession()
        http_calls = HTTPCalls(host, port, session)
        self.api_calls = APICalls(http_calls, None)

    async def async_setup(self) -> None:
        """Initialize the HTTPCalls class with host, port, and websession."""

        response = await self.api_calls.http_calls.post_call(
            "/auth/HomeAssistantMusicController"
        )
        if response is None:
            await self.async_close()
            raise ConnectionError("Failed to connect to the Youtube Music API Server")
        self.is_online = True
        response_json = await response.json()
        access_token = response_json["accessToken"]
        self.api_calls.access_token = access_token

    async def async_close(self) -> None:
        """Close the aiohttp session."""
        if self.api_calls.http_calls.websession.closed is False:
            await self.api_calls.http_calls.websession.close()
