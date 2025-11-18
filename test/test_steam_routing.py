from __future__ import annotations

from enum import Enum

import pytest

from src.lib.steam import build_steam_url
from src.lib.steam.interfaces import SteamInterface
from src.lib.steam.endpoint import SteamChartsEndpoint
from src.lib import config


class InvalidEndpoint(str, Enum):
    INVALID_ENDPOINT = "InvalidEndpoint"


class DummySettings(config.Settings):
    steam_api_base_url: str = "https://api.steampowered.com"
    steam_api_default_version: int = 1


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    dummy = DummySettings()

    def _get_settings_override() -> config.Settings:
        return dummy

    monkeypatch.setattr(config, "get_settings", _get_settings_override)


def test_build_steam_url_valid():
    url = build_steam_url(SteamInterface.STEAM_CHARTS, SteamChartsEndpoint.GET_MOST_PLAYED_GAMES)

    assert url == "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"


def test_build_steam_url_invalid_endpoint():
    with pytest.raises(ValueError) as exc_info:
        build_steam_url(SteamInterface.STEAM_CHARTS, InvalidEndpoint.INVALID_ENDPOINT)  # type: ignore

        msg = str(exc_info.value)
        assert "is not recognized in interface" in msg
        assert "InvalidEndpoint" in msg
