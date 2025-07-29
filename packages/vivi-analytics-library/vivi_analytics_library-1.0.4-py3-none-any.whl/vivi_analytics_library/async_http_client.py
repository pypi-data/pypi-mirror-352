import aiohttp

import logging
from typing import Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HttpResponse(BaseModel):
    """Model for HTTP response."""

    success: bool
    status: int
    headers: dict
    content: Any

    class config:
        from_attributes = True


async def get_async(
    url: str,
    accessToken: str = None,  # type: ignore
    verifySSL: bool = True,
    params: dict = None,  # type: ignore
    headers: dict = None,  # type: ignore
) -> HttpResponse:
    """Send an asynchronous GET request."""
    logger.debug(f"get_async: URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            if not headers:
                headers = {
                    "Accept": "application/json",
                }

            if accessToken:
                headers["Authorization"] = f"Bearer {accessToken}"

            async with session.get(
                url, headers=headers, params=params, ssl=verifySSL
            ) as response:

                http_response = HttpResponse(
                    success=response.status in range(200, 300),
                    status=response.status,
                    headers=dict(response.headers),
                    content=await response.json() if response.content_type == "application/json" else await response.text(),
                )

                return http_response
    except aiohttp.ClientResponseError as e:
        logger.error(f"async get failed with status code {e.status}. {e}")
        raise
    except Exception as e:
        logger.error(f"async get failed with exception {e}")
        raise


async def post_async(
    url: str,
    accessToken: str = None,  # type: ignore
    verifySSL: bool = True,
    params: dict = None,  # type: ignore
    data: Any = None,  # type: ignore
    json: Any = None,  # type: ignore
    headers: dict = None,  # type: ignore
) -> HttpResponse:
    """Send an asynchronous POST request."""
    try:
        if json and data:
            raise ValueError("Cannot specify both 'json' and 'data' parameters.")

        logger.debug(f"post_async: URL: {url}")

        async with aiohttp.ClientSession() as session:
            if not headers:
                headers = {
                    "Accept": "application/json",
                }

            if accessToken:
                headers["Authorization"] = f"Bearer {accessToken}"

            async with session.post(
                url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                ssl=verifySSL,
            ) as response:

                http_response = HttpResponse(
                    success=response.status in range(200, 300),
                    status=response.status,
                    headers=dict(response.headers),
                    content=await response.json() if response.content_type == "application/json" else await response.text(),
                )

                return http_response
    except aiohttp.ClientResponseError as e:
        logger.error(f"async post failed with status code {e.status}. {e}")
        raise
    except Exception as e:
        logger.error(f"async post failed with exception {e}")
        raise
