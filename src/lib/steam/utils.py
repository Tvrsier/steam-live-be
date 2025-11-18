from __future__ import annotations

from functools import wraps
from typing import Set, Dict, TypeVar, Callable, Any, cast

from src.lib.steam.endpoint import *
from src.lib.steam.interfaces import SteamInterface

INTERFACE_ENDPOINT_MAP: Dict[SteamInterface, Set[str]] = {
    SteamInterface.STEAM_CHARTS: {e.value for e in SteamChartsEndpoint},
    SteamInterface.STEAM_USER: {e.value for e in SteamUserEndpoint}
}

F = TypeVar("F", bound=Callable[..., Any])


def validate_interface_endpoint(func: F) -> F:
    @wraps(func)
    def wrapper(interface: SteamInterface, endpoint: SteamEndpointName, *args: Any, **kwargs: Any) -> str:
        allowed = INTERFACE_ENDPOINT_MAP.get(interface)

        if allowed is not None and endpoint.value not in allowed:
            raise ValueError(f"Endpoint {endpoint.value} is not recognized in interface {interface.name}.")

        return func(interface, endpoint, *args, **kwargs)

    return cast(F, wrapper)
