from __future__ import annotations

import time
from typing import TYPE_CHECKING

import anyio

if TYPE_CHECKING:
    from ._client import AsyncAutoma, Automa


class SyncAPIResource:
    _client: Automa

    def __init__(self, client: Automa) -> None:
        self._client = client

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class AsyncAPIResource:
    _client: AsyncAutoma

    def __init__(self, client: AsyncAutoma) -> None:
        self._client = client

    async def _sleep(self, seconds: float) -> None:
        await anyio.sleep(seconds)
