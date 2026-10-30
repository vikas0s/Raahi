from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class GeoLocation(BaseModel):
    name: str
    lat: float
    lon: float
    category: str = "metro_station" # metro_station, bus_stop, landmark, railway_station, locality
    city: str = "Delhi NCR"
    state: Optional[str] = None
    country: Optional[str] = None
    aliases: List[str] = []

class ResolvedPlace(BaseModel):
    name: str
    display_name: str
    lat: float
    lon: float
    category: str = "place" # metro_station, railway_station, airport, landmark, locality, address, university
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    place_id: Optional[str] = None
    raw_query: Optional[str] = None
    is_ambiguous: bool = False
    disambiguation_options: List[str] = []

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
    prefer_rail: bool = False # Indian Railways & Local Suburban Trains

class CanonicalJourneyRequest(BaseModel):
    origin: ResolvedPlace
    destination: ResolvedPlace
    departure_time: Optional[str] = None # ISO format or HH:MM
    arrival_time: Optional[str] = None
    time_mode: Literal["now", "depart_at", "arrive_by"] = "now"
    preferences: TravelPreference = Field(default_factory=TravelPreference)
    preferred_modes: List[str] = Field(default_factory=list)
    budget_max_fare: Optional[float] = None
    currency: str = "INR"

class PlanRequest(BaseModel):
    origin: str
    destination: str
    city: str = "Delhi NCR"
    origin_coords: Optional[List[float]] = None # [lon, lat] or [lat, lon]
    destination_coords: Optional[List[float]] = None # [lon, lat] or [lat, lon]
    departure_time: Optional[str] = None # ISO format or HH:MM
    arrival_time: Optional[str] = None # ISO format or HH:MM when Arrive By is chosen
    time_mode: Optional[Literal["now", "depart_at", "arrive_by"]] = "now"
    preferences: TravelPreference = Field(default_factory=TravelPreference)

class TransitLeg(BaseModel):
    id: str
    mode: Literal["walk", "metro", "bus", "rail", "auto", "taxi", "erickshaw", "ebus", "drive", "cycle", "ferry"]
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
    train_number: Optional[str] = None
    train_name: Optional[str] = None
    train_type: Optional[str] = None
    platform: Optional[str] = None
    coach_classes: Optional[List[str]] = None
    data_source: Optional[str] = None

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
    route_type: Optional[str] = "transit" # "metro_multimodal", "dtc_ebus", "auto_rickshaw", "cab_taxi", "budget_bus", "road_direct", "rail_connect"
    transfers_count: int
    walking_duration_minutes: int
    walking_distance_meters: int
    overall_crowd: Literal["Low", "Moderate", "High", "Very High"] = "Moderate"
    total_delay_minutes: int = 0
    legs: List[TransitLeg]
    eco_carbon_savings_kg: float = 1.4
    service_available: bool = True # Whether this transit mode is currently operational
    unavailable_reason: Optional[str] = None # e.g. "Metro closed (11 PM – 6 AM)"
    data_source: Optional[str] = "local_transit_network" # "local_transit_network", "railconnect", "osrm_global_road"
    fare_provenance: Optional[str] = "verified_tariff" # "verified_tariff", "estimated_meter", "not_available"
    transit_coverage_available: bool = True
    coverage_advisory: Optional[str] = None

class PlanResponse(BaseModel):
    origin: GeoLocation
    destination: GeoLocation
    generated_at: str
    routes: List[RouteItinerary]
    active_disruptions_count: int = 0

class TransitIncident(BaseModel):
    id: str
    line_name: str
    mode: Literal["walk", "metro", "bus", "rail", "auto", "taxi", "erickshaw", "ebus"]
    severity: Literal["minor", "moderate", "severe"]
    delay_minutes: int
    crowd_level: Literal["Low", "Moderate", "High", "Very High"]
    affected_stations: List[str]
    headline: str
    description: str
    last_updated: str
    is_simulated: bool = False

class SimulateDelayRequest(BaseModel):
    scenario: str
    city: Optional[str] = "Delhi NCR"
    target_line: Optional[str] = None
    delay_minutes: Optional[int] = None

class CityRealtimeContext(BaseModel):
    city: str
    day_name: str
    day_type: str
    current_time_str: str
    time_window: str
    status_headline: str
    status_description: str
    crowd_level: str
    recommended_mode: str
    special_advisory: Optional[str] = None

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
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    context_origin: Optional[str] = None
    context_destination: Optional[str] = None
    city: str = "Delhi NCR"

class ChatResponse(BaseModel):
    reply: str
    session_id: Optional[str] = None
    action_type: Optional[Literal["show_route", "show_delays", "save_route", "general_info", "clarification"]] = None
    route_data: Optional[RouteItinerary] = None
    suggested_actions: List[Dict[str, str]] = [] # [{"label": "View Route", "action": "view_route"}]
    detected_intent: str = "general"
    is_grounded_route: bool = False
    audio_base64: Optional[str] = None
    canonical_request: Optional[CanonicalJourneyRequest] = None
    clarification_needed: bool = False
    clarification_question: Optional[str] = None
    coverage_type: Optional[str] = None # "full_transit", "intercity_rail", "road_only", "unsupported"

class ResetSessionRequest(BaseModel):
    session_id: str

class TTSRequest(BaseModel):
    text: str
    language_code: str = "hi-IN"
    speaker: str = "meera"

class TTSResponse(BaseModel):
    status: str
    audio_base64: Optional[str] = None
    error: Optional[str] = None

class StopDeparture(BaseModel):
    line: str
    destination: str
    mode: str
    scheduled_time: str
    estimated_time: str
    status: str
    crowd: str
    platform: Optional[str] = None

class ReverseGeocodeResponse(BaseModel):
    status: str = "ok"
    lat: float
    lon: float
    city: str
    matched_transit_city: Optional[str] = None
    locality: Optional[str] = None
    formatted_address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
