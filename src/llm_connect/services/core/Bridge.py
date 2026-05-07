from typing import Any, Dict, Literal, Optional

import httpx

from llm_connect.configs.brother import PATH


class Bridge:
    def __init__(self):
        self.path = PATH

    async def create_deck(
        self,
        jwt: str,
        name: str,
        description: str,
        icon: str,
        color: str,
        is_shared: bool = False,
    ) -> Dict[str, Any]:

        payload = {
            "name": name,
            "description": description,
            "icon": icon,
            "color": color,
            "isShared": is_shared,
        }

        return await self._request(
            path="/api/decks",
            method="POST",
            jwt=jwt,
            json=payload,
        )

    async def _request(
        url: str,
        jwt: Optional[str] = None,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Generic HTTP client for calling other services with optional JWT auth.
        """

        final_headers = headers.copy() if headers else {}

        # attach JWT if provided
        if jwt:
            final_headers["Authorization"] = f"Bearer {jwt}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=final_headers,
                )

                response.raise_for_status()

                # assume JSON response
                return response.json()

            # catch the error and then raise for
            # the UI
            except httpx.HTTPStatusError as e:
                raise e

            except httpx.RequestError as e:
                raise e
