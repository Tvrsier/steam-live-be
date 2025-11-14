from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field


class GameSummary(BaseModel):
    """
    Represents a single game in the mockGames list.

    TODO: In the future those data can be modified or extended with real data gathered from Steam Web API
    (e.g. appid, tags, genres, platforms, etc.).
    """
    id: int
    name: str
    players: int
    peak: int
    trend: str
    price: float
    discount: int
    image: Optional[str] = None


class ChartPoint(BaseModel):
    """
    Data point for time series chars (mockChartData).
    """
    time: str
    players: int
    sales: int


class GlobalStats(BaseModel):
    """
    grouped stats showed in the dashboard (mockStats).
    """
    totalPlayers: int
    peakToday: int
    avgPlayers24h: int
    totalGames: int
    newToday: int
    onSaleToday: int


class DashboardMockData(BaseModel):
    """
    Main structure of the JSON that the backend will export
    (equivalent to mockGames + mockChartData + mockStats).

    TODO: when we switch to real data, this structure may be extended or reorganized
    while maintaining compatibility with the frontend.
    """
    games: List[GameSummary] = Field(default_factory=list)
    chartData: List[ChartPoint] = Field(default_factory=list)
    stats: GlobalStats

