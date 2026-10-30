"""
FastAPI application for Raahi — Your City, Effortlessly Connected.
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Load unified root .env configuration
root_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=root_env)

from .models import (
    PlanRequest, PlanResponse, TransitIncident, SimulateDelayRequest,
    SavedRoute, SavedRouteCreate, ChatRequest, ChatResponse, StopDeparture
)
from .router import router_instance
from .simulation import simulator_instance
from .storage import get_all_saved_routes, create_saved_route, delete_saved_route
from .chat_engine import chat_assistant_instance
from .transit_data import PLACES_DATABASE
from .otd_service import otd_service_instance, LiveVehicle
from .rail.service import rail_service_instance
from .rail.schemas import (
    RailStation, TrainSummary, TrainSchedule, LiveRunningStatus,
    StationBoardResponse, RailSearchResponse
)

app = FastAPI(
    title="Raahi Transit API",
    description="Intelligent Public Transit Route Planning Engine (MISSION BHARAT DEV-P05)",
    version="1.0.0"
)

# Enable CORS for frontend Vite dev server (port 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_transit_delays():
    incidents = simulator_instance.get_incidents()
    delays_map = simulator_instance.get_delays_map()
    return {
        "active_disruptions": incidents,
        "total_disruptions": len(incidents),
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
def chat_with_assistant(req: ChatRequest):
    return chat_assistant_instance.process_message(req)

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

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process client ping
            await websocket.send_json({
                "type": "HEARTBEAT_ACK",
                "server_time": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
