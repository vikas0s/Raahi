"""
Raahi RailConnect Package — Indian Railways & Local Train Journey Planner.
"""
from .schemas import (
    RailStation, TrainSummary, TrainSchedule, TrainHalt, LiveRunningStatus,
    StationBoardItem, StationBoardResponse, RailSearchResponse
)
from .provider_interface import RailProviderInterface
from .providers.railradar import RailRadarProvider
from .service import RailConnectService, rail_service_instance

__all__ = [
    "RailStation",
    "TrainSummary",
    "TrainSchedule",
    "TrainHalt",
    "LiveRunningStatus",
    "StationBoardItem",
    "StationBoardResponse",
    "RailSearchResponse",
    "RailProviderInterface",
    "RailRadarProvider",
    "RailConnectService",
    "rail_service_instance"
]

