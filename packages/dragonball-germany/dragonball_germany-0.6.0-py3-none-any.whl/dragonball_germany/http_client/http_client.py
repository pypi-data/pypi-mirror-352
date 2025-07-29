import logging
from typing import Any, Literal

import httpx

from dragonball_germany.logger import get_logger

from .exceptions import Exceptions

logger: logging.Logger = get_logger(name=__name__)


class HttpClient(Exceptions):
    def __init__(
        self,
        timeout: int = 3,
        cookies: dict[str, str] | None = None,
        headers: dict[str, str | int] | None = None,
    ) -> None:
        self.timeout: int = timeout
        self.cookies: dict[str, str] | None = cookies
        self.headers: dict[str, str | int] | None = headers

    def _log(self, msg: str) -> None:
        logger.info(msg=f'[HttpClient] {msg}')

    async def get_request(
        self, url: str, query_params: dict[str, str | int | float] | None = None
    ) -> httpx.Response:
        return await self._send_request(
            url=url, method='GET', query_params=query_params
        )

    async def get_json_request(
        self, url: str, query_params: dict[str, str | int | float] | None = None
    ) -> Any:
        response: httpx.Response = await self.get_request(
            url=url, query_params=query_params
        )
        return self.extract_json(response=response)

    async def post_request(
        self,
        url: str,
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> httpx.Response:
        return await self._send_request(
            url=url, method='POST', json=json, query_params=query_params
        )

    async def post_json_request(
        self,
        url: str,
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> Any:
        response: httpx.Response = await self.post_request(
            url=url, json=json, query_params=query_params
        )
        return self.extract_json(response=response)

    async def put_request(
        self,
        url: str,
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> httpx.Response:
        return await self._send_request(
            url=url, method='PUT', json=json, query_params=query_params
        )

    async def put_json_request(
        self,
        url: str,
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> Any:
        response: httpx.Response = await self.put_request(
            url=url, json=json, query_params=query_params
        )
        return await self.extract_json(response=response)

    async def delete_request(
        self,
        url: str,
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> httpx.Response:
        return await self._send_request(
            url=url, method='DELETE', json=json, query_params=query_params
        )

    async def delete_json_request(
        self,
        url: str,
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> Any:
        response: httpx.Response = await self.delete_request(
            url=url, json=json, query_params=query_params
        )
        return self.extract_json(response=response)

    async def _send_request(
        self,
        url: str,
        method: Literal['GET', 'POST', 'PUT', 'DELETE'],
        json: list[dict[str, Any]] | dict[str, Any] | None = None,
        query_params: dict[str, str | int | float] | None = None,
    ) -> httpx.Response:
        if method == 'GET' and json is not None:
            self._log(msg='Ignoring JSON body for GET request.')
            json = None

        try:
            self._log(msg=f"{method} request to '{url}'")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                return await client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=query_params,  # pyright: ignore
                    headers=self.headers,  # pyright: ignore
                    cookies=self.cookies,  # pyright: ignore
                    follow_redirects=False,
                )
        except httpx.ConnectError as e:
            self._log(msg=f'ConnectError: {e}')
            raise self.RequestError()
        except httpx.NetworkError as e:
            self._log(msg=f'NetworkError: {e}')
            raise self.RequestError()
        except httpx.ConnectTimeout as e:
            self._log(msg=f'ConnectTimeout: {e}')
            raise self.RequestTimeoutError()
        except httpx.ReadTimeout as e:
            self._log(msg=f'ReadTimeout: {e}')
            raise self.RequestTimeoutError()
        except httpx.WriteTimeout as e:
            self._log(msg=f'WriteTimeout: {e}')
            raise self.RequestTimeoutError()
        except httpx.PoolTimeout as e:
            self._log(msg=f'PoolTimeout: {e}')
            raise self.RequestTimeoutError()
        except Exception as e:
            self._log(msg=f'Exception: {e}')
            raise self.RequestError()

    def extract_json(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as e:
            self._log(msg=f'extract_json: ValueError: {e}')
            raise self.ExtractJsonError()
        except Exception as e:
            self._log(msg=f'extract_json: {e}')
            raise self.ExtractJsonError()

    def extract_text(self, response: httpx.Response) -> str:
        try:
            return response.text
        except Exception as e:
            self._log(f'extract_text: {e}')
            raise self.ExtractTextError()
