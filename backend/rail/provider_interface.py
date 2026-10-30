"""
Abstract Base Interface for Railway Data Providers in Raahi.
Allows switching or augmenting providers (RailRadar, IndianRailways, Mock/Fallback) cleanly.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .schemas import (
    RailStation, TrainSummary, TrainSchedule, LiveRunningStatus, StationBoardItem
)


class RailProviderInterface(ABC):
    @abstractmethod
    async def search_stations(self, query: str) -> List[RailStation]:
        """Search railway stations by name or code."""
        pass

    @abstractmethod
    async def get_trains_between(
        self, from_code: str, to_code: str, date: Optional[str] = None
    ) -> List[TrainSummary]:
        """Fetch trains running between two railway station codes."""
        pass

    @abstractmethod
    async def get_train_schedule(self, train_no: str) -> Optional[TrainSchedule]:
        """Fetch complete schedule, halts, and timings for a train."""
        pass

    @abstractmethod
    async def get_live_running_status(
        self, train_no: str, date: Optional[str] = None
    ) -> Optional[LiveRunningStatus]:
        """Fetch live running status, delay, and current location."""
        pass

    @abstractmethod
    async def get_station_board(
        self, station_code: str, hours: int = 4
    ) -> List[StationBoardItem]:
        """Fetch live station departure/arrival board."""
        pass

