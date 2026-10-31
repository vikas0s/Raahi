
from .mongodb.connection import (
    get_async_db,
    check_mongo_health,
    close_mongo_connection
)
from .mongodb.repositories import (
    CityRepository,
    StationRepository,
    RouteRepository,
    SavedRouteRepository,
    SavedPlaceRepository,
    UserPreferenceRepository,
    AIConversationRepository
)
from .models import (
    CityResponse, StationResponse, RouteResponse,
    SavedPlaceCreate, SavedPlaceResponse,
    UserPreferencesUpdate, UserPreferencesResponse,
    DatabaseHealthResponse
)
from contextlib import asynccontextmanager
from pydantic import BaseModel
"""
FastAPI application for Raahi — Your City, Effortlessly Connected.
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Depends
from .auth import auth_router, get_current_user, get_optional_current_user, UserResponse
from fastapi.middleware.cors import CORSMiddleware


# Load unified root .env configuration
root_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=root_env)

from .models import (
    PlanRequest, PlanResponse, TransitIncident, SimulateDelayRequest,
    SavedRoute, SavedRouteCreate, ChatRequest, ChatResponse, StopDeparture, ReverseGeocodeResponse,
    ResetSessionRequest, TTSRequest, TTSResponse
)
from .router import router_instance
from .simulation import simulator_instance
from .storage import get_all_saved_routes, create_saved_route, delete_saved_route
from .chat_engine import chat_assistant_instance
from .sarvam_service import sarvam_service_instance
from .transit_data import PLACES_DATABASE
from .otd_service import otd_service_instance, LiveVehicle
from .rail.service import rail_service_instance
from .rail.schemas import (
    RailStation, TrainSummary, TrainSchedule, LiveRunningStatus,
    StationBoardResponse, RailSearchResponse
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check MongoDB health and ensure indexes/records are ready
    try:
        health = await check_mongo_health()
        if health.get("is_connected"):
            db = get_async_db()
            stn_count = await db.stations.count_documents({})
            if stn_count == 0:
                from .mongodb.seeder import seed_mongodb
                seed_mongodb()
    except Exception as e:
        print(f"MongoDB startup verification: {e}")
    yield
    # Shutdown: Close client cleanly
    try:
        await close_mongo_connection()
    except Exception:
        pass

app = FastAPI(lifespan=lifespan, 
    title="Raahi Transit API",
    description="Intelligent Public Transit Route Planning Engine (MISSION BHARAT DEV-P05)",
    version="1.0.0"
)

# Enable CORS for frontend Vite dev server (supports credentials & HttpOnly cookies)
CORS_ORIGINS = [
    "https://raahi-steel.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
env_cors = os.getenv("CORS_ORIGINS")
if env_cors:
    CORS_ORIGINS.extend([o.strip() for o in env_cors.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# WebSocket Connection Manager for Telemetry and Incident Broadcasting
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

# In-memory store of recent computed itineraries for GET /itinerary/{id}
computed_itineraries = {}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Raahi Transit API",
        "timestamp": datetime.now().isoformat(),
        "cities_supported": list(PLACES_DATABASE.keys()),
        "version": "1.0.0"
    }

@app.get("/places/search")
def search_places(
    q: str = Query("", description="Search term for station, bus stop or landmark"),
    city: str = Query("Delhi NCR", description="Selected city")
):
    results = router_instance.search_places(q, city)
    return {
        "query": q,
        "city": city,
        "count": len(results),
        "results": results
    }

_REVERSE_GEOCODE_CACHE = {}

KNOWN_TRANSIT_HUBS = {
    "Delhi NCR": (28.6139, 77.2090),
    "Mathura & Vrindavan": (27.4924, 77.6737),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946)
}

def _match_transit_cluster(lat: float, lon: float, detected_city: str = "") -> Optional[str]:
    c_lower = (detected_city or "").lower()
    if any(k in c_lower for k in ["mathura", "vrindavan", "braj"]):
        return "Mathura & Vrindavan"
    if any(k in c_lower for k in ["delhi", "gurugram", "gurgaon", "noida", "faridabad", "ghaziabad"]):
        return "Delhi NCR"
    if any(k in c_lower for k in ["mumbai", "thane", "navi mumbai"]):
        return "Mumbai"
    if any(k in c_lower for k in ["bengaluru", "bangalore"]):
        return "Bengaluru"

    import math
    closest = None
    min_dist = float("inf")
    for name, (h_lat, h_lon) in KNOWN_TRANSIT_HUBS.items():
        r = 6371.0
        phi1, phi2 = math.radians(lat), math.radians(h_lat)
        dphi = math.radians(h_lat - lat)
        dlam = math.radians(h_lon - lon)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2)**2
        d = 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        if d < min_dist:
            min_dist = d
            closest = name
    if min_dist <= 75.0:
        return closest
    return None

@app.get("/places/reverse-geocode", response_model=ReverseGeocodeResponse)
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Reverse geocodes (lat, lon) to a city and locality, matching to supported transit clusters.
    Uses cached in-memory entries and OpenStreetMap Nominatim with resilient fallback.
    """
    cache_key = (round(lat, 3), round(lon, 3))
    if cache_key in _REVERSE_GEOCODE_CACHE:
        return _REVERSE_GEOCODE_CACHE[cache_key]

    import urllib.request
    import json

    detected_city = None
    locality = None
    state = None
    formatted = None

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "RaahiTransit/1.0"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode())
            addr = data.get("address", {})
            locality = addr.get("suburb") or addr.get("neighbourhood") or addr.get("residential") or addr.get("quarter") or addr.get("village") or addr.get("road")
            detected_city = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("state_district") or addr.get("county") or addr.get("suburb")
            state = addr.get("state")
            formatted = data.get("display_name")
    except Exception as e:
        pass

    matched_cluster = _match_transit_cluster(lat, lon, detected_city or "")
    if not detected_city:
        if matched_cluster == "Delhi NCR":
            detected_city = "Delhi"
        elif matched_cluster == "Mathura & Vrindavan":
            detected_city = "Mathura"
        elif matched_cluster:
            detected_city = matched_cluster
        else:
            detected_city = "Current Location"

    res = ReverseGeocodeResponse(
        status="ok",
        lat=lat,
        lon=lon,
        city=detected_city,
        matched_transit_city=matched_cluster,
        locality=locality or detected_city,
        formatted_address=formatted,
        state=state
    )
    _REVERSE_GEOCODE_CACHE[cache_key] = res
    return res

@app.post("/plan", response_model=PlanResponse)
async def plan_journey(request: PlanRequest):
    delays_map = simulator_instance.get_delays_map()
    response = router_instance.plan_journey(request, delays_map)
    for route in response.routes:
        computed_itineraries[route.id] = route
    return response

@app.get("/itinerary/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    if itinerary_id in computed_itineraries:
        return computed_itineraries[itinerary_id]
    raise HTTPException(status_code=404, detail=f"Itinerary '{itinerary_id}' not found or expired")

@app.get("/delays")
def get_transit_delays(city: str = Query("Delhi NCR")):
    incidents = simulator_instance.get_incidents(city)
    delays_map = simulator_instance.get_delays_map()
    context = simulator_instance.get_city_realtime_context(city)
    return {
        "city": city,
        "active_disruptions": incidents,
        "total_disruptions": len(incidents),
        "realtime_context": context,
        "delays_summary": delays_map,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/simulate/delay")
async def simulate_delay(req: SimulateDelayRequest):
    result = simulator_instance.apply_scenario(req)
    # Broadcast to all connected WebSockets
    await ws_manager.broadcast({
        "type": "SIMULATION_UPDATE",
        "data": result,
        "timestamp": datetime.now().isoformat()
    })
    return result

@app.post("/chat", response_model=ChatResponse)
@app.post("/api/assistant/chat", response_model=ChatResponse)
async def chat_with_assistant(req: ChatRequest):
    return await chat_assistant_instance.process_message(req)

@app.post("/api/assistant/reset")
def reset_assistant_session(req: ResetSessionRequest):
    chat_assistant_instance.session_manager.reset(req.session_id)
    return {"status": "ok", "session_id": req.session_id, "message": "Session reset"}

@app.post("/api/assistant/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        content = await file.read()
        transcript = await sarvam_service_instance.transcribe_speech(content, filename=file.filename or "audio.wav")
        return {"status": "ok", "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assistant/synthesize", response_model=TTSResponse)
async def synthesize_speech_endpoint(req: TTSRequest):
    try:
        audio_base64 = await sarvam_service_instance.synthesize_speech(req.text, req.language_code, req.speaker)
        return TTSResponse(status="ok", audio_base64=audio_base64)
    except Exception as e:
        return TTSResponse(status="error", error=str(e))


# ==============================================================================
# Persistent MongoDB Transit & Mobility APIs
# ==============================================================================

@app.get("/api/health/database", response_model=DatabaseHealthResponse)
async def get_database_health():
    """Checks MongoDB database connectivity, latency, and status without leaking secrets."""
    return await check_mongo_health()


@app.get("/api/health")
async def combined_health_check():
    """Combined service and database health check."""
    db_health = await check_mongo_health()
    return {
        "status": "healthy" if db_health.get("is_connected") else "degraded",
        "service": "Raahi Transit API",
        "timestamp": datetime.now().isoformat(),
        "database": db_health,
        "cities_supported": list(PLACES_DATABASE.keys()),
        "version": "1.0.0"
    }


@app.get("/api/cities", response_model=List[CityResponse])
async def list_cities(active_only: bool = True):
    """Retrieve supported transit cities from MongoDB."""
    db = get_async_db()
    repo = CityRepository(db)
    cities = await repo.get_all(active_only=active_only)
    if not cities:
        # Fallback to in-memory metadata
        return [
            CityResponse(
                id=c.lower().replace(" ", "-").replace("&", "").strip(),
                name=c,
                center_lat=KNOWN_TRANSIT_HUBS.get(c, (28.6139, 77.2090))[0],
                center_lon=KNOWN_TRANSIT_HUBS.get(c, (28.6139, 77.2090))[1],
                is_active=True,
                supported_transport_modes=["metro", "bus", "rail", "auto"]
            )
            for c in PLACES_DATABASE.keys()
        ]
    return [CityResponse(**c) for c in cities]


@app.get("/api/stations", response_model=List[StationResponse])
async def list_stations(
    city_id: Optional[str] = Query(None, description="City ID (e.g. delhi-ncr, mumbai)"),
    stop_type: Optional[str] = Query(None, description="Stop type (e.g. metro_station, railway_station)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Retrieve persisted transit stations from MongoDB with pagination."""
    db = get_async_db()
    repo = StationRepository(db)
    stations = await repo.get_by_city(city_id=city_id, stop_type=stop_type, limit=limit, offset=offset)
    return [StationResponse(**s) for s in stations]


@app.get("/api/stations/search", response_model=List[StationResponse])
async def search_stations_api(
    q: str = Query(..., min_length=1, description="Station search query"),
    city: Optional[str] = Query(None, description="Optional city name or ID filter"),
    limit: int = Query(15, ge=1, le=50)
):
    """Search transit stations using MongoDB index."""
    db = get_async_db()
    repo = StationRepository(db)
    city_id = None
    if city:
        city_clean = city.lower()
        if "delhi" in city_clean:
            city_id = "delhi-ncr"
        elif "mumbai" in city_clean:
            city_id = "mumbai"
        elif "bengaluru" in city_clean or "bangalore" in city_clean:
            city_id = "bengaluru"
        elif "mathura" in city_clean or "vrindavan" in city_clean:
            city_id = "mathura-vrindavan"

    stations = await repo.search(query=q, city_id=city_id, limit=limit)
    return [StationResponse(**s) for s in stations]


@app.get("/api/stations/nearby", response_model=List[StationResponse])
async def find_nearby_stations(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_meters: float = Query(3000, ge=100, le=25000, description="Search radius in meters"),
    limit: int = Query(10, ge=1, le=50)
):
    """Geospatial proximity query for stations near coordinates using MongoDB 2dsphere index."""
    db = get_async_db()
    repo = StationRepository(db)
    nearby = await repo.find_nearby(lat=lat, lon=lon, max_distance_meters=radius_meters, limit=limit)
    return [StationResponse(**s) for s in nearby]


@app.get("/api/routes", response_model=List[RouteResponse])
async def list_transit_routes(
    city_id: Optional[str] = Query(None, description="City ID filter"),
    route_type: Optional[str] = Query(None, description="Route type (e.g. suburban_rail, metro)")
):
    """Retrieve persisted transit routes from MongoDB."""
    db = get_async_db()
    repo = RouteRepository(db)
    routes = await repo.get_by_city(city_id=city_id, route_type=route_type)
    return [RouteResponse(**r) for r in routes]


@app.get("/api/saved-places", response_model=List[SavedPlaceResponse])
async def get_saved_places(current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    """Retrieve user saved places (Home, Work, Favorites) from MongoDB."""
    db = get_async_db()
    repo = SavedPlaceRepository(db)
    uid = current_user.id if current_user else "user-demo-default"
    places = await repo.get_by_user(user_id=uid)
    return [
        SavedPlaceResponse(
            id=p["id"],
            user_id=p["user_id"],
            name=p["name"],
            address=p["address"],
            category=p["category"],
            latitude=p["latitude"],
            longitude=p["longitude"],
            city=p["city"],
            created_at=str(p.get("created_at", ""))
        )
        for p in places
    ]


@app.post("/api/saved-places", response_model=SavedPlaceResponse)
async def add_saved_place(payload: SavedPlaceCreate, current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    """Create or update a user saved place in MongoDB."""
    db = get_async_db()
    repo = SavedPlaceRepository(db)
    uid = current_user.id if current_user else "user-demo-default"
    created = await repo.create(payload.model_dump(), user_id=uid)
    return SavedPlaceResponse(
        id=created["id"],
        user_id=created["user_id"],
        name=created["name"],
        address=created["address"],
        category=created["category"],
        latitude=created["latitude"],
        longitude=created["longitude"],
        city=created["city"],
        created_at=str(created.get("created_at", ""))
    )


@app.delete("/api/saved-places/{place_id}")
async def delete_saved_place_endpoint(place_id: str, current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    """Delete a saved place from MongoDB."""
    db = get_async_db()
    repo = SavedPlaceRepository(db)
    uid = current_user.id if current_user else "user-demo-default"
    success = await repo.delete(place_id=place_id, user_id=uid)
    if not success:
        raise HTTPException(status_code=404, detail="Saved place not found")
    return {"success": True, "deleted_id": place_id}


@app.get("/api/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    """Retrieve persistent user preferences from MongoDB."""
    db = get_async_db()
    repo = UserPreferenceRepository(db)
    uid = current_user.id if current_user else "user-demo-default"
    pref = await repo.get_by_user(user_id=uid)
    return UserPreferencesResponse(
        id=pref["id"],
        user_id=pref["user_id"],
        preferred_language=pref.get("preferred_language", "en"),
        selected_city=pref.get("selected_city", "Delhi NCR"),
        accessible_only=pref.get("accessible_only", False),
        reduced_motion=pref.get("reduced_motion", False),
        travel_preferences=pref.get("travel_preferences", {})
    )


@app.put("/api/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(payload: UserPreferencesUpdate, current_user: Optional[UserResponse] = Depends(get_optional_current_user)):
    """Update user preferences in MongoDB."""
    db = get_async_db()
    repo = UserPreferenceRepository(db)
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    uid = current_user.id if current_user else "user-demo-default"
    pref = await repo.update(user_id=uid, updates=updates)
    return UserPreferencesResponse(
        id=pref["id"],
        user_id=pref["user_id"],
        preferred_language=pref.get("preferred_language", "en"),
        selected_city=pref.get("selected_city", "Delhi NCR"),
        accessible_only=pref.get("accessible_only", False),
        reduced_motion=pref.get("reduced_motion", False),
        travel_preferences=pref.get("travel_preferences", {})
    )


@app.get("/api/saved-routes", response_model=List[SavedRoute])
def get_saved_routes_api(city: Optional[str] = Query(None, description="Optional city filter")):
    """Retrieve saved routes backed by MongoDB with SQLite fallback."""
    return get_all_saved_routes(city=city)


@app.post("/api/saved-routes", response_model=SavedRoute)
def create_saved_route_api(route: SavedRouteCreate):
    """Create a saved commute in MongoDB and persistent storage."""
    return create_saved_route(route)


@app.delete("/api/saved-routes/{route_id}")
def delete_saved_route_api(route_id: str):
    """Delete a saved commute from MongoDB."""
    success = delete_saved_route(route_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved route not found")
    return {"message": "Route deleted successfully", "id": route_id}

@app.get("/saved-routes", response_model=List[SavedRoute])
def list_saved_routes(city: Optional[str] = Query(None)):
    return get_all_saved_routes(city)

@app.post("/saved-routes", response_model=SavedRoute)
def add_saved_route(req: SavedRouteCreate):
    # compute realistic values based on origin and dest
    origin_p = router_instance.find_place(req.origin, req.city)
    dest_p = router_instance.find_place(req.destination, req.city)
    dist = 15.0
    if origin_p and dest_p:
        from .router import haversine_km
        dist = haversine_km(origin_p["lat"], origin_p["lon"], dest_p["lat"], dest_p["lon"])
    duration = max(18, int(dist * 1.8))
    fare = 40.0 if dist < 12 else 50.0
    return create_saved_route(req, duration=duration, fare=fare, transfers=1 if dist > 15 else 0)

@app.delete("/saved-routes/{route_id}")
def remove_saved_route(route_id: str):
    success = delete_saved_route(route_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved route not found")
    return {"deleted": True, "id": route_id}

@app.get("/stops/{stop_id}/departures", response_model=List[StopDeparture])
def get_stop_departures(stop_id: str):
    # Live schedule board for a transit stop
    now = datetime.now()
    return [
        StopDeparture(
            line="Yellow Line",
            destination="Millennium City Centre Gurugram",
            mode="metro",
            scheduled_time=(now + asyncio.run(asyncio.sleep(0)) or now).strftime("%H:%M"),
            estimated_time="On Time (2 min)",
            status="Approaching Platform 2",
            crowd="Moderate",
            platform="Platform 2"
        ),
        StopDeparture(
            line="Blue Line",
            destination="Noida Electronic City / Vaishali",
            mode="metro",
            scheduled_time=(now + asyncio.run(asyncio.sleep(0)) or now).strftime("%H:%M"),
            estimated_time="On Time (4 min)",
            status="Scheduled",
            crowd="High",
            platform="Platform 3"
        ),
        StopDeparture(
            line="DTC Electric Bus 534",
            destination="Anand Vihar ISBT",
            mode="bus",
            scheduled_time=(now + asyncio.run(asyncio.sleep(0)) or now).strftime("%H:%M"),
            estimated_time="6 mins",
            status="Live GPS Tracking",
            crowd="Low",
            platform="Bay 4"
        )
    ]

@app.get("/transit/live-vehicles", response_model=List[LiveVehicle])
async def get_live_vehicles(
    city: str = Query("Delhi NCR", description="Selected city"),
    limit: int = Query(120, ge=1, le=500, description="Max vehicles to return for map rendering")
):
    """
    Returns real-time GPS coordinates of active transit vehicles (DTC buses / Mathura E-Buses & Tempos)
    using the live Delhi Transport Stack (DTS) GTFS-RT feed or Mathura Smart City Telemetry.
    """
    c = city.lower()
    if "mathura" in c or "vrindavan" in c or "braj" in c:
        return await otd_service_instance.fetch_mathura_live_vehicles()
    elif "mumbai" in c:
        return await otd_service_instance.fetch_mumbai_live_vehicles()
    elif "delhi" in c:
        return await otd_service_instance.fetch_live_vehicles(limit=limit)
    return []

# ==============================================================================
# Raahi RailConnect — Indian Railways & Local Train APIs
# ==============================================================================

@app.get("/api/rail/stations", response_model=List[RailStation])
async def search_rail_stations(
    query: str = Query("", description="Station name or code, e.g. MTJ, NDLS, Vrindavan"),
    city: Optional[str] = Query(None, description="Optional city filter")
):
    """Search stations across Indian Railways and suburban networks."""
    return await rail_service_instance.search_stations(query, city)

@app.get("/api/rail/trains", response_model=RailSearchResponse)
async def get_trains_between_stations(
    from_station: str = Query(..., description="Origin IR Station Code, e.g. NDLS, MTJ"),
    to_station: str = Query(..., description="Destination IR Station Code, e.g. MTJ, BDB"),
    date: Optional[str] = Query(None, description="Travel date (YYYY-MM-DD)")
):
    """Fetch all direct and regional trains between two railway stations."""
    from_s = rail_service_instance.get_station_by_code(from_station)
    to_s = rail_service_instance.get_station_by_code(to_station)
    if not from_s:
        from_s = RailStation(code=from_station.upper(), name=f"{from_station.upper()} Station", city="Indian Railways", lat=28.61, lon=77.20)
    if not to_s:
        to_s = RailStation(code=to_station.upper(), name=f"{to_station.upper()} Station", city="Indian Railways", lat=27.48, lon=77.67)

    trains = await rail_service_instance.get_trains_between(from_station, to_station, date)
    source = trains[0].data_source if trains else "verified_schedule"
    return RailSearchResponse(
        from_station=from_s,
        to_station=to_s,
        date=date or datetime.now().strftime("%Y-%m-%d"),
        trains_count=len(trains),
        trains=trains,
        data_source=source
    )

@app.get("/api/rail/schedule/{train_no}", response_model=TrainSchedule)
async def get_train_schedule(train_no: str):
    """Fetch complete station sequence, arrival, departure, halt, and platform info."""
    schedule = await rail_service_instance.get_train_schedule(train_no)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"Timetable for train #{train_no} not found")
    return schedule

@app.get("/api/rail/live-status/{train_no}", response_model=LiveRunningStatus)
async def get_live_train_status(
    train_no: str,
    date: Optional[str] = Query(None, description="Travel date (YYYY-MM-DD)")
):
    """Fetch real-time running status, current location, ETA, and delay minutes."""
    status = await rail_service_instance.get_live_running_status(train_no, date)
    if not status:
        raise HTTPException(status_code=404, detail=f"Live running status for train #{train_no} unavailable")
    return status

@app.get("/api/rail/station-board/{station_code}", response_model=StationBoardResponse)
async def get_station_departure_board(
    station_code: str,
    hours: int = Query(4, ge=1, le=12, description="Departure lookahead window in hours")
):
    """Fetch live departure/arrival board for a railway station."""
    return await rail_service_instance.get_station_board(station_code, hours)

class GoogleMapsKeyPayload(BaseModel):
    api_key: str

@app.get("/api/settings/google-maps-status")
def get_google_maps_status():
    """Check if Google Maps API key is configured."""
    from .google_maps_service import google_maps_service_instance
    return {
        "configured": google_maps_service_instance.is_configured(),
        "masked_key": google_maps_service_instance.get_api_key_masked()
    }

@app.post("/api/settings/google-maps-key")
def update_google_maps_key(payload: GoogleMapsKeyPayload):
    """Dynamically save and activate Google Maps API key."""
    from .google_maps_service import google_maps_service_instance
    success = google_maps_service_instance.set_api_key(payload.api_key)
    return {
        "success": success,
        "configured": google_maps_service_instance.is_configured(),
        "masked_key": google_maps_service_instance.get_api_key_masked()
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "server_time": datetime.now().isoformat()
        })
        while True:
            data = await websocket.receive_text()
            # Echo or process client ping
            await websocket.send_json({
                "type": "HEARTBEAT_ACK",
                "server_time": datetime.now().isoformat()
            })
    except (WebSocketDisconnect, Exception):
        ws_manager.disconnect(websocket)
