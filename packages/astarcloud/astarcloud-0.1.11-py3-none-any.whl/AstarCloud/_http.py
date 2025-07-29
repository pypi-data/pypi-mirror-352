from __future__ import annotations
import httpx
from ._exceptions import APIError, AuthenticationError


class _HTTP:
    BASE_URL = "https://api.astarcloud.no"

    def __init__(self, api_key: str, timeout: float = 30.0):
        self._headers = {
            "X-Api-Key": f"{api_key}",
            "User-Agent": "AstarCloud-Python/0.1.0",
        }
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout, headers=self._headers)

    def post(self, path: str, json: dict) -> dict:
        url = f"{self.BASE_URL}{path}"
        r = self._client.post(url, json=json)
        if r.status_code == 401:
            raise AuthenticationError(r.text)
        if r.status_code >= 400:
            raise APIError(r.text, status=r.status_code)
        return r.json()

    def close(self):
        self._client.close()
