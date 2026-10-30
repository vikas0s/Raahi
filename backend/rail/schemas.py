"""
Pydantic v2 schemas for Raahi RailConnect — Indian Railways & Local Train Journey Planner.
Supports Express, Superfast, Passenger, MEMU, DEMU, and EMU Suburban Trains.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class RailStation(BaseModel):
    code: str = Field(..., description="IR Station Code, e.g., MTJ, NDLS, BDB")
    name: str = Field(..., description="Full Station Name, e.g., Mathura Junction")
    city: str = Field(..., description="City or District, e.g., Mathura, Delhi NCR")
    state: str = Field(default="Delhi / Uttar Pradesh", description="State")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    platforms_count: int = Field(default=2, description="Number of platforms")
    category: str = Field(default="railway_station", description="Station category")
    aliases: List[str] = Field(default_factory=list, description="Common commuter aliases/search terms")
    zone: Optional[str] = Field(default=None, description="Railway Zone, e.g., NR, NCR, WCR")


class TrainHalt(BaseModel):
    station_code: str
    station_name: str
    arrival_time: Optional[str] = "00:00"
    departure_time: Optional[str] = "00:00"
    halt_minutes: int
    distance_km: float
    platform: Optional[str] = None
    day_offset: int = 1


class TrainSchedule(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    origin_code: str
    origin_name: str
    destination_code: str
    destination_name: str
    halts: List[TrainHalt] = Field(default_factory=list)
    running_days: List[str] = Field(default_factory=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])


class TrainSummary(BaseModel):
    train_number: str
    train_name: str
    train_type: str = "Express"
    origin_code: str
    origin_name: str
    destination_code: str
    destination_name: str
    departure_time: Optional[str] = "00:00"  # HH:MM format
    arrival_time: Optional[str] = "00:00"    # HH:MM format
    duration_minutes: int
    distance_km: float
    running_days: List[str] = Field(default_factory=lambda: ["Daily"])
    classes: List[str] = Field(default_factory=list, description="e.g. ['UR', '2S', 'SL', '3A', 'CC']")
    fares: Dict[str, float] = Field(default_factory=dict, description="e.g. {'UR': 10, '2S': 45, 'SL': 140}")
    halts_count: int = 0
    platform_origin: Optional[str] = None
    platform_dest: Optional[str] = None
    live_delay_mins: int = 0
    live_status: str = "On Time"
    is_live: bool = False
    data_source: str = "verified_schedule"  # "railradar_live" or "verified_schedule"


class LiveRunningStatus(BaseModel):
    train_number: str
    train_name: str
    train_type: str = "Express"
    current_station: str
    current_status: str  # e.g. "Running On Time", "Delayed by 18 mins", "Departed Palwal"
    delay_minutes: int = 0
    speed_kmh: Optional[int] = None
    last_reported_time: str = ""
    next_station: Optional[str] = None
    eta_destination: str = ""
    is_live: bool = False
    data_source: str = "verified_schedule"  # "railradar_live" or "verified_schedule"


class StationBoardItem(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    origin_code: str
    destination_code: str
    destination_name: str
    scheduled_time: str
    expected_time: str
    platform: str = "PF 1"
    status: str = "On Time"  # "On Time", "Delayed 15m", "Platform Changed", "Arrived"
    delay_minutes: int = 0
    is_live: bool = False


class StationBoardResponse(BaseModel):
    station: RailStation
    departures: List[StationBoardItem] = Field(default_factory=list)
    generated_at: str


class RailSearchResponse(BaseModel):
    from_station: RailStation
    to_station: RailStation
    date: str
    trains_count: int
    trains: List[TrainSummary]
    data_source: str

