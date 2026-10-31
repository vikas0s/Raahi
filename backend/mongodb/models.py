"""
Pydantic document models and serialization schemas for Raahi MongoDB integration.
Follows GTFS semantics and provides clean ObjectId / id serialization.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict


def current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


class MongoBaseModel(BaseModel):
    """Base model handling MongoDB _id and id conversions."""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )


# ==============================================================================
# Transit Core Collections
# ==============================================================================

class CityDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "delhi-ncr", "mumbai", "bengaluru", "mathura-vrindavan"
    name: str                     # e.g. "Delhi NCR", "Mumbai"
    country: str = "India"
    timezone: str = "Asia/Kolkata"
    center_lat: float
    center_lon: float
    is_active: bool = True
    supported_transport_modes: List[str] = Field(default_factory=lambda: ["metro", "bus", "rail", "auto"])
    created_at: datetime = Field(default_factory=current_utc_time)
    updated_at: datetime = Field(default_factory=current_utc_time)


class GeoPoint(MongoBaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude] (GeoJSON standard)


class StationDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "delhi-ncr_rajiv-chowk", "mtj"
    external_stop_id: Optional[str] = None
    city_id: str
    name: str
    latitude: float
    longitude: float
    location: GeoPoint
    stop_type: str = "metro_station"  # metro_station, railway_station, bus_stop, auto_stand, landmark
    parent_station_id: Optional[str] = None
    source: str = "verified_places_catalog"
    source_dataset_version: str = "2026.1"
    updated_at: datetime = Field(default_factory=current_utc_time)


class TransitAgencyDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "dmrc", "best", "wr", "cr", "bmrc", "bmtc", "mvda"
    external_agency_id: Optional[str] = None
    name: str
    city_id: str
    source: str = "official"
    active_status: str = "active"
    updated_at: datetime = Field(default_factory=current_utc_time)


class RouteDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "route-wr-slow-01"
    external_route_id: Optional[str] = None
    agency_id: str
    city_id: str
    route_name: str
    route_type: str = "metro"  # suburban_rail, metro, bus, erickshaw, tempo
    line_color: str = "#304B3C"
    source: str = "gtfs_schedule"
    updated_at: datetime = Field(default_factory=current_utc_time)


class TripDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "trip-90001"
    external_trip_id: Optional[str] = None
    route_id: str
    service_id: str = "daily_all"
    headsign: str
    source: str = "schedule"
    updated_at: datetime = Field(default_factory=current_utc_time)


class StopTimeDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "st_90001_1"
    trip_id: str
    stop_id: str
    stop_sequence: int
    arrival_time: str    # HH:MM
    departure_time: str  # HH:MM
    service_id: str = "daily_all"
    source: str = "schedule"
    updated_at: datetime = Field(default_factory=current_utc_time)


class ServiceCalendarDocument(MongoBaseModel):
    id: str = Field(alias="_id")  # e.g. "daily_all", "weekdays"
    service_id: str
    operating_days: List[str]  # ["Monday", "Tuesday", ...]
    start_date: str = "2026-01-01"
    end_date: str = "2026-12-31"
    exceptions: List[str] = Field(default_factory=list)


# ==============================================================================
# User & Application Data Collections
# ==============================================================================

class UserDocument(MongoBaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    email_normalized: Optional[str] = None
    password_hash: str = ""
    role: str = "commuter"
    avatar_url: Optional[str] = None
    email_verified: bool = True
    status: str = "active"
    created_at: datetime = Field(default_factory=current_utc_time)
    updated_at: datetime = Field(default_factory=current_utc_time)
    last_login_at: Optional[datetime] = None


class SavedRouteDocument(MongoBaseModel):
    id: str = Field(alias="_id")
    user_id: str = "user-demo-default"
    name: str
    origin: str
    destination: str
    city: str
    preferred_mode: str = "fastest"
    typical_duration_minutes: int = 30
    typical_fare_inr: float = 20.0
    typical_transfers: int = 0
    current_delay_minutes: int = 0
    active_status: str = "Normal Service"
    created_at: datetime = Field(default_factory=current_utc_time)


class SavedPlaceDocument(MongoBaseModel):
    id: str = Field(alias="_id")
    user_id: str = "user-demo-default"
    name: str
    address: str
    category: str = "favorite"  # home, work, favorite, transit_hub
    latitude: float
    longitude: float
    city: str
    created_at: datetime = Field(default_factory=current_utc_time)


class UserPreferenceDocument(MongoBaseModel):
    id: str = Field(alias="_id")
    user_id: str = "user-demo-default"
    preferred_language: str = "en"
    selected_city: str = "Delhi NCR"
    travel_preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "fastest": True,
        "cheapest": False,
        "prefer_rail": True
    })
    accessible_only: bool = False
    reduced_motion: bool = False
    updated_at: datetime = Field(default_factory=current_utc_time)


class ChatMessageDoc(MongoBaseModel):
    role: str   # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=current_utc_time)


class AIConversationDocument(MongoBaseModel):
    id: str = Field(alias="_id")
    session_id: str
    user_id: str = "user-demo-default"
    conversation_title: str = "Transit Consultation"
    city: Optional[str] = None
    messages: List[ChatMessageDoc] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=current_utc_time)
    updated_at: datetime = Field(default_factory=current_utc_time)


class RecentSearchDocument(MongoBaseModel):
    id: str = Field(alias="_id")
    user_id: str = "user-demo-default"
    source_query: str
    dest_query: str
    city: str
    departure_time: Optional[str] = None
    created_at: datetime = Field(default_factory=current_utc_time)

