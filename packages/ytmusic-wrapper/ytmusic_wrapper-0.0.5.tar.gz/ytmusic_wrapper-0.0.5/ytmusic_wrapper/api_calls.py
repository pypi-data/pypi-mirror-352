"""Provides the `APICalls` class for interacting with the Youtube Music API. It includes methods for controlling playback, adjusting volume, and retrieving song information."""
from __future__ import annotations

import json
import logging
from typing import Any, TypedDict

from asyncio import timeout
from aiohttp import ContentTypeError

from .http_calls import HTTPCalls

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class SongInfo(TypedDict):
    """A TypedDict representing information about a song."""

    title: str
    artist: str
    views: int
    uploadDate: str
    imageSrc: str
    isPaused: bool
    songDuration: int
    elapsedSeconds: int
    url: str
    album: str
    videoId: str
    playlistId: str
    mediaType: str


class QueueInfo(TypedDict):
    """A TypedDict representing information about a queue."""

    items: list[Any]
    autoPlaying: bool


class APICalls:
    """A class to handle API calls for controlling and retrieving information from a music service.

    Attributes:
        access_token (str): The access token for authentication.
        http_calls (HTTPCalls): An instance of HTTPCalls to make HTTP requests.

    """

    def __init__(self, http_calls: HTTPCalls, access_token: str | None) -> None:
        """Initialize the APICalls class with an access token and HTTPCalls instance.

        Args:
            access_token (str): The access token for authentication.
            http_calls (HTTPCalls): An instance of HTTPCalls to make HTTP requests.

        """
        self.http_calls = http_calls
        self.access_token = access_token

    async def get_status(self) -> bool:
        """Send a request to get the current status.

        Returns:
            bool: True if it is available and ready, False otherwise.

        """
        try:
            # Timeout after 2 seconds if the request takes too long
            async with timeout(2.0):
                response = await self.http_calls.get_call(
                    "/api/v1/song", self.access_token, True
                )
        except Exception as e:  # noqa: BLE001
            logger.debug(
                "Failed to get status from the Youtube Music API Server: %s", e
            )
            return False
        if response is None:
            logger.debug("Failed to get status from the Youtube Music API Server")
            return False
        try:
            responseJSON = await response.json()
        except (json.JSONDecodeError, ContentTypeError) as e:
            logger.debug(
                "Failed to decode JSON response from the Youtube Music API Server: %s, JSON Response: %s",
                e,
                await response.text(),
            )
            return False
        if "title" not in responseJSON:
            logger.debug(
                "Title not found in response from the Youtube Music API Server: %s",
                responseJSON,
            )
            return False
        logger.debug(
            "Successfully got status from the Youtube Music API Server: %s",
            responseJSON["title"],
        )
        return True

    async def previous(self):
        """Send a request to play the previous song."""
        await self.http_calls.post_call("/api/v1/previous", self.access_token)

    async def next(self):
        """Send a request to play the next song."""
        await self.http_calls.post_call("/api/v1/next", self.access_token)

    async def play(self):
        """Send a request to play the current song."""
        await self.http_calls.post_call("/api/v1/play", self.access_token)

    async def pause(self):
        """Send a request to pause the current song."""
        await self.http_calls.post_call("/api/v1/pause", self.access_token)

    async def set_volume(self, volume: int):
        """Send a request to set the volume to the specified level, level should be between 0 and 100."""
        body = json.loads('{"volume": ' + str(volume) + "}")
        await self.http_calls.post_call("/api/v1/volume", self.access_token, body)

    async def get_volume(self) -> int:
        """Send a request to get the current volume level."""
        response = await self.http_calls.get_call("/api/v1/volume", self.access_token)
        if response is None:
            raise ConnectionError(
                "Failed to get volume from the Youtube Music API Server"
            )
        responseJSON = await response.json()
        return responseJSON["state"]

    async def get_song(self) -> SongInfo:
        """Send a request to get the current song information."""
        respone = await self.http_calls.get_call("/api/v1/song", self.access_token)
        if respone is None:
            raise ConnectionError(
                "Failed to get song from the Youtube Music API Server"
            )
        return await respone.json()

    async def get_queue(self) -> QueueInfo:
        """Send a request  to get the current queue."""
        respone = await self.http_calls.get_call("/api/v1/queue", self.access_token)
        if respone is None:
            raise ConnectionError(
                "Failed to get song from the Youtube Music API Server"
            )
        return await respone.json()

    async def toggle_mute(self):
        """Send a request to toggle the mute state."""
        await self.http_calls.post_call("/api/v1/toggle-mute", self.access_token)

    async def toggle_play_pause(self):
        """Send a request to toggle play/pause state."""
        await self.http_calls.post_call("/api/v1/toggle-play", self.access_token)

    async def get_shuffle(self) -> bool | None:
        """Send a request to get the current shuffle state."""
        respone = await self.http_calls.get_call("/api/v1/shuffle", self.access_token)
        if respone is None:
            raise ConnectionError(
                "Failed to get song from the Youtube Music API Server"
            )
        responseJSON = await respone.json()
        if "state" in responseJSON:
            return bool(responseJSON["state"])
        logger.error(
            "Shuffle state not found in response, Response JSON: %s", responseJSON
        )
        return None

    async def set_shuffle(self):
        """Send a request to shuffle the queue."""
        await self.http_calls.post_call("/api/v1/shuffle", self.access_token)

    async def clear_queue(self):
        """Send a request to clear the current queue."""
        await self.http_calls.delete_call("/api/v1/queue", self.access_token)

    async def seek(self, position: float):
        """Send a request to clear the current queue."""
        body = json.loads('{"seconds": ' + str(int(position)) + "}")
        await self.http_calls.post_call("/api/v1/seek-to", self.access_token, body)
