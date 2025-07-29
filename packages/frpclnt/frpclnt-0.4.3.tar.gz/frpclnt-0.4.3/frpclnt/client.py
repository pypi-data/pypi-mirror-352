import asyncio
import logging

import aiohttp
import inspect
from typing import Any, Dict, Optional, Callable


class AsyncRestClient:
    """Универсальный клиент для работы с REST API и WebSocket."""

    def __init__(self, address: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30):
        self.address = address.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    async def request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = f"{self.address}/{endpoint.lstrip('/')}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(method, url, timeout=self.timeout, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    async def __call__(self, method: str, endpoint: str, **kwargs) -> Any:
        return await self.request(method, endpoint, **kwargs)

    async def websocket(self, endpoint: str,
                        params: Optional[Dict[str, Any]] = None,
                        callback: Callable = None,
                        callback_context: Any = None) -> None:

        url = f"{self.address}/{endpoint.lstrip('/')}"
        retry_delay = 1
        max_delay = 60

        while True:
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.ws_connect(url, timeout=self.timeout, heartbeat=30) as ws:
                        if params:
                            await ws.send_json(params)

                        retry_delay = 1  # Сброс задержки после успешного подключения

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = msg.json()
                                if callback:
                                    if inspect.iscoroutinefunction(callback):
                                        if callback_context is not None:
                                            await callback(callback_context, data)
                                        else:
                                            await callback(data)
                                    else:
                                        if callback_context is not None:
                                            callback(callback_context, data)
                                        else:
                                            callback(data)

                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                raise Exception(f"WebSocket error: {msg.data}")

                            elif msg.type in (aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                                self.logger.warning(f"WebSocket connection closed, reconnecting...")
                                break

            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                self.logger.warning(f"WebSocket connection error: {e}, reconnect in {retry_delay}s")
            except Exception as e:
                self.logger.error(f"Unexpected WebSocket error: {e}")

            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)
