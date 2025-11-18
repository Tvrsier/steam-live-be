from __future__ import annotations

from typing import Dict, Any

import httpx
from pydantic import BaseModel, ConfigDict

from src.lib.config import get_settings


class SteamRequestParams(BaseModel):
    model_config = ConfigDict(extra="allow")

    access_token: str | None = None
    call_method: str | None = "get"

    def as_query(self) -> dict[str, Any]:
        data = self.model_dump(exclude={"call_method"}, exclude_none=True)

        if "access_token" not in data:
            settings = get_settings()
            if not settings.steam_api_key:
                raise ValueError("Steam API key is not configured.")
            data["access_token"] = settings.steam_api_key

        return data


class SteamApiError(Exception):
    pass


def call_api(url: str, params: SteamRequestParams | None = None) -> Dict[str, Any]:
    params = params or SteamRequestParams()
    query = params.as_query()
    data: Dict | None = None
    try:
        resp = None
        if params.call_method == "get":
            resp = httpx.get(url=url, params=query, timeout=10.0)
        elif params.call_method == "post":
            resp = httpx.post(url=url, params=query, timeout=10.0)
        else:
            raise NotImplementedError(f"HTTP method {params.call_method} is not implemented.")
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        raise SteamApiError(f"HTTP error occurred: {str(e)}") from e
    except Exception as e:
        raise SteamApiError(f"An error occurred while calling the Steam API: {str(e)}") from e

    if not isinstance(data, dict):
        raise SteamApiError("Invalid response format from Steam API.")
    return data
