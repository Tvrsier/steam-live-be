from __future__ import annotations

from enum import Enum
from typing import TypeAlias, Union


class SteamChartsEndpoint(str, Enum):
    GET_MOST_PLAYED_GAMES = "GetMostPlayedGames"


class SteamUserEndpoint(str, Enum):
    GET_CURRENT_PLAYERS = "GetNumberOfCurrentPlayers"


SteamEndpointName: TypeAlias = (
    Union[SteamChartsEndpoint, SteamUserEndpoint]
)
