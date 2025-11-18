from __future__ import annotations

from enum import Enum


class SteamInterface(str, Enum):
    STEAM_CHARTS = "ISteamChartsService"
    STEAM_USER = "ISteamUserStats"
