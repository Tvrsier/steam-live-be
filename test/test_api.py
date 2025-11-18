from src.lib.steam import steam_client
from src.lib.steam.endpoint import SteamChartsEndpoint, SteamUserEndpoint
from src.lib.steam.interfaces import SteamInterface
from src.lib.steam import build_steam_url
import pytest


def test_api_call_success():
    url = build_steam_url(SteamInterface.STEAM_CHARTS, SteamChartsEndpoint.GET_MOST_PLAYED_GAMES)
    result = steam_client.call_api(url)
    assert "response" in result


def test_api_call_success_with_params():
    url = build_steam_url(SteamInterface.STEAM_USER, SteamUserEndpoint.GET_CURRENT_PLAYERS)
    params = steam_client.SteamRequestParams(appid=3564740)  # type: ignore[call-arg]
    result = steam_client.call_api(url, params=params)
    assert "response" in result
