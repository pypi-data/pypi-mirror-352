# http_client.py

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union

import aiohttp
from aiohttp import ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError, ClientResponseError
from bs4 import BeautifulSoup


class RequestRateLimiter:
    def __init__(self, calls_per_second: float = 2.0):
        self.calls_per_second = calls_per_second
        self.last_call_time = 0.0

    async def acquire(self):
        now = time.time()
        time_since_last_call = now - self.last_call_time
        if time_since_last_call < 1.0 / self.calls_per_second:
            await asyncio.sleep(
                1.0 / self.calls_per_second - time_since_last_call
            )
        self.last_call_time = time.time()


class HttpClient:
    BASE_URL = "https://servis.mgm.gov.tr/web/"
    BASE_WEBSITE_URL = "https://www.mgm.gov.tr/"
    HEADERS = {"Origin": BASE_WEBSITE_URL}

    def __init__(
        self,
        timeout: int = 60,
        max_retries: int = 3,
        calls_per_second: float = 2.0,
        max_connections: int = 100,
        ssl_verify: bool = True,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RequestRateLimiter(calls_per_second)
        self._session: Optional[aiohttp.ClientSession] = None
        self.connector = TCPConnector(
            limit=max_connections,
            ssl=ssl_verify,
            force_close=False,
            enable_cleanup_closed=True,
        )
        self.timeout_obj = ClientTimeout(
            total=timeout,
            connect=10,
            sock_read=30,
            sock_connect=10,
        )

    async def __aenter__(self) -> "HttpClient":
        self._session = aiohttp.ClientSession(
            headers=self.HEADERS,
            connector=self.connector,
            timeout=self.timeout_obj,
            trust_env=True,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()

    async def _request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        response_type: str = "json",
        retry_count: int = 0,
    ) -> Union[Dict[str, Any], BeautifulSoup, None]:
        """Internal method to make HTTP requests with retry logic."""
        if not self._session:
            raise RuntimeError(
                "Session is not initialized. Use 'async with HttpClient()'."
            )

        await self.rate_limiter.acquire()

        try:
            async with self._session.get(url, params=params) as response:
                response.raise_for_status()

                if response_type == "json":
                    return await response.json(content_type="application/json")
                elif response_type == "html":
                    return BeautifulSoup(await response.text(), "html.parser")
                elif response_type == "image":
                    return await response.read()
                else:
                    raise ValueError(
                        f"Unsupported response_type: {response_type}"
                    )

        except (ClientError, ClientResponseError) as e:
            if retry_count < self.max_retries:
                wait_time = 2**retry_count  # Exponential backoff
                print(
                    f"Request failed: {e}. Retrying in {wait_time} seconds..."
                )
                await asyncio.sleep(wait_time)
                return await self._request(
                    url, params, response_type, retry_count + 1
                )
            print(
                f"Error fetching {url} after {self.max_retries} retries: {e}"
            )
            return None
        except asyncio.TimeoutError:
            print(f"Timeout: {url}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching {url}: {e}")
            return None

    async def request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        response_type: str = None,
    ) -> Union[Dict[str, Any], BeautifulSoup, None]:
        """Genel bir GET isteği yapar ve belirtilen formatta yanıt döner."""
        return await self._request(url, params, response_type)

    async def get_json(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """JSON formatında veri çeker."""
        return await self.request(
            f"{self.BASE_URL}{endpoint}",
            params,
            response_type="json",
        )

    async def get_html(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[BeautifulSoup]:
        """HTML formatında veri çeker."""
        return await self.request(
            f"{self.BASE_WEBSITE_URL}{endpoint}",
            params,
            response_type="html",
        )

    async def get_jpeg(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        """JPEG formatında veri çeker."""
        return await self.request(
            f"{self.BASE_WEBSITE_URL}{endpoint}",
            params,
            response_type="image",
        )
