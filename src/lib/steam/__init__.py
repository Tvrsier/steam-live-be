from __future__ import annotations

from src.lib.steam.endpoint import SteamEndpointName
from src.lib.steam.interfaces import SteamInterface
from src.lib.steam.utils import validate_interface_endpoint
from src.lib.config import get_settings


__all__ = [
    "SteamInterface",
    "SteamEndpointName",
    "build_steam_url",
]


@validate_interface_endpoint
def build_steam_url(interface: SteamInterface, endpoint: SteamEndpointName, version: int | None = None) -> str:
    settings = get_settings()
    base = settings.steam_api_base_url.rstrip("/")
    v = version or settings.steam_api_default_version

    return f"{base}/{interface.value}/{endpoint.value}/v{v}/"
