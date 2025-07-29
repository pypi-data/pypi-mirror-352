import aiohttp
from typing import TypeVar, Type
from .common import BASE_URL
from .common.base import BaseRequest

T = TypeVar("T", bound=BaseRequest)


class WarframeMarketClient:
    """Client for interacting with Warframe Market API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.response = None

    async def get(self, request_class: Type[T], slug="", **kwargs) -> T:
        """Perform a GET request using the specified request class.

        Args:
            request_class: The request class that defines the endpoint and response type
            slug: Optional slug to append to the endpoint URL
            **kwargs: Additional query parameters to include in the request

        Returns:
            The parsed API response
        """
        endpoint = request_class._get_endpoint(slug=slug, **kwargs)
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error {response.status}: {await response.text()}")
                data = await response.text()
                return request_class._decode(data)

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit async context manager."""
        pass
