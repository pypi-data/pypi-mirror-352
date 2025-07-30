import json
from typing import Literal, Optional, Union
from urllib.parse import urljoin

import aiohttp


class ResponseWrapper:
    def __init__(self, response: aiohttp.ClientResponse, session: aiohttp.ClientSession):
        self._response = response
        self._session = session

    def __getattr__(self, name):
        return getattr(self._response, name)

    async def close(self):
        await self._session.close()


class HttpClient:
    """HTTP client"""

    def __init__(
        self,
        api_key: str,
        auth_type: Optional[Literal["basic", "bearer"]] = None,
        base_url: Optional[str] = None,
    ):
        """Constructor for HTTP client

        Args:
            api_key: The API key to use for authentication
            auth_type: Authentication type, either "basic" or "bearer". Defaults to "basic"
            base_url: Optional base URL for the API, defaults to https://api.inworld.ai/v1
        """
        auth_type = auth_type or "basic"
        self.__base_url = base_url or "https://api.inworld.ai/v1"

        if auth_type.lower() not in ["basic", "bearer"]:
            raise ValueError("auth_type must be either 'basic' or 'bearer'")

        auth_prefix = "Basic" if auth_type.lower() == "basic" else "Bearer"
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"{auth_prefix} {api_key}",
        }

    async def request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        stream: bool = False,
    ) -> Union[dict | ResponseWrapper]:
        requestData = (
            json.dumps(data) if method != "get" and data and len(data.keys()) > 0 else None
        )
        requestParams = data if method == "get" and data else None
        requestUrl = urljoin(self.__base_url, path)
        session = aiohttp.ClientSession()

        try:
            response = await session.request(
                method,
                url=requestUrl,
                json=requestParams,
                data=requestData,
                headers=self.__headers,
                params=requestParams,
            )

            wrapped_response = ResponseWrapper(response, session)

            if stream:
                original_content = response.content

                async def validating_stream():
                    async for chunk in original_content:
                        if chunk:
                            try:
                                yield await self.__validate(chunk)
                            except Exception:
                                raise

                response.content = validating_stream()
                return wrapped_response
            else:
                await self.__validate(wrapped_response)
                return_item: dict = await wrapped_response.json()
                await wrapped_response.close()
                return return_item

        except Exception:
            await session.close()
            raise

    async def __validate(
        self,
        response: Union[ResponseWrapper, bytes],
    ) -> Union[ResponseWrapper, bytes]:
        try:
            if isinstance(response, bytes):
                body = json.loads(response)
            else:
                body = await response.json()
            if body.get("error") is not None:
                body = body["error"]
            if isinstance(body, dict) and body.get("code") is not None:
                raise Exception(body.get("message"))
        except Exception:
            raise
        return response
