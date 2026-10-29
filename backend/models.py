from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class GeoLocation(BaseModel):
    name: str
    lat: float
    lon: float
    category: str = "metro_station" # metro_station, bus_stop, landmark, railway_station
    city: str = "Delhi NCR"
    aliases: List[str] = []

class TravelPreference(BaseModel):
    fastest: bool = True
    cheapest: bool = False
    less_crowded: bool = False
    fewer_transfers: bool = False
    less_walking: bool = False
    accessible: bool = False
    prefer_ebus: bool = False
    allow_auto: bool = True
    allow_taxi: bool = True
    pink_pass: bool = False # Delhi Govt free travel for women on DTC/cluster buses
    prefer_multimodal: bool = False # Doorstep Auto/E-Rickshaw + Metro chaining

class PlanRequest(BaseModel):
    origin: str
    destination: str
    city: str = "Delhi NCR"
    departure_time: Optional[str] = None # ISO format or HH:MM
    preferences: TravelPreference = Field(default_factory=TravelPreference)

class TransitLeg(BaseModel):
    id: str
    mode: Literal["walk", "metro", "bus", "rail", "auto", "taxi", "erickshaw", "ebus"]
    line_name: Optional[str] = None # e.g. "Yellow Line", "Blue Line", "DTC Electric Bus 534", "Delhi Govt Metered Auto"
    line_color: Optional[str] = None # Hex color
    origin_name: str
    destination_name: str
    origin_coords: List[float] # [lon, lat]
    destination_coords: List[float] # [lon, lat]
    path_coords: List[List[float]] = [] # [[lon, lat], ...] for map polylines
    duration_minutes: int
    distance_meters: int
    departure_time: str
    arrival_time: str
    stops_count: int = 0
    intermediate_stops: List[str] = []
    instructions: str
    crowd_level: Literal["Low", "Moderate", "High", "Very High"] = "Moderate"
    delay_minutes: int = 0
    is_delayed: bool = False
    accessibility: bool = True
    fare_inr: float = 0.0
    fare_details: Optional[str] = None # e.g. "Govt notified: ₹30 first 1.5km + ₹11/km"

class RouteItinerary(BaseModel):
    id: str
    title: str # e.g. "DTC Electric Bus Corridor" or "Metro + First-Mile Auto"
    tag: str # "Fastest", "Lowest Fare", "Least Crowded", "DTC Electric Bus", "Govt Metered Auto", "Direct Cab", etc.
    tag_reason: str
    total_duration_minutes: int
    departure_time: str
    arrival_time: str
    total_fare_inr: float
    pink_pass_fare_inr: Optional[float] = None # ₹0 for women on DTC bus routes
    fare_breakdown: Optional[str] = None # e.g. "Auto (₹45) + Metro (₹40)"
    route_type: Optional[str] = "transit" # "metro_multimodal", "dtc_ebus", "auto_rickshaw", "cab_taxi", "budget_bus"
    transfers_count: int
    walking_duration_minutes: int
    walking_distance_meters: int
    overall_crowd: Literal["Low", "Moderate", "High", "Very High"] = "Moderate"
    total_delay_minutes: int = 0
    legs: List[TransitLeg]
    eco_carbon_savings_kg: float = 1.4
    service_available: bool = True  # Whether this transit mode is currently operational
    unavailable_reason: Optional[str] = None  # e.g. "Metro closed (11 PM – 6 AM)"

class PlanResponse(BaseModel):
    origin: GeoLocation
    destination: GeoLocation
    generated_at: str
    routes: List[RouteItinerary]
    active_disruptions_count: int = 0

class TransitIncident(BaseModel):
    id: str
    line_name: str
    mode: Literal["metro", "bus", "rail"]
    severity: Literal["minor", "moderate", "severe"]
    delay_minutes: int
    crowd_level: Literal["Low", "Moderate", "High", "Very High"]
    affected_stations: List[str]
    headline: str
    description: str
    last_updated: str
    is_simulated: bool = False

class SimulateDelayRequest(BaseModel):
    scenario: Literal["metro_signal_delay", "bus_breakdown", "peak_hour_surge", "monsoon_rain", "reset"]
    target_line: Optional[str] = None
    delay_minutes: Optional[int] = None

class SavedRouteCreate(BaseModel):
    name: str # e.g. "Home to Cyber City"
    origin: str
    destination: str
    city: str = "Delhi NCR"
    preferred_mode: str = "fastest"

class SavedRoute(BaseModel):
    id: str
    name: str
    origin: str
    destination: str
    city: str = "Delhi NCR"
    preferred_mode: str = "fastest"
    created_at: str
    typical_duration_minutes: int
    typical_fare_inr: float
    typical_transfers: int
    current_delay_minutes: int = 0
    active_status: str = "Normal Service"

class ChatRequest(BaseModel):
    message: str
    language: Literal["en", "hi", "hinglish"] = "en"
    context_origin: Optional[str] = None
    context_destination: Optional[str] = None
    city: str = "Delhi NCR"

class ChatResponse(BaseModel):
    reply: str
    action_type: Optional[Literal["show_route", "show_delays", "save_route", "general_info"]] = None
    route_data: Optional[RouteItinerary] = None
    suggested_actions: List[Dict[str, str]] = [] # [{"label": "View Route", "action": "view_route"}]
    detected_intent: str = "general"

class StopDeparture(BaseModel):
    line: str
    destination: str
    mode: str
    scheduled_time: str
    estimated_time: str
    status: str
    crowd: str
    platform: Optional[str] = None
