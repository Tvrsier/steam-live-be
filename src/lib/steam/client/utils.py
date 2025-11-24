from __future__ import annotations

from typing import Literal, Any
from src.lib.config import get_settings
from pydantic import ConfigDict, BaseModel


class SteamRequestParams(BaseModel):
    model_config = ConfigDict(extra="allow")

    access_token: str | None = None
    call_method: Literal["get", "post"] = "get"

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
