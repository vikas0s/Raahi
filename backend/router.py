"""
Multi-criteria transit journey planner for Raahi.
Computes Fastest, Lowest Fare, and Least Crowded routes with realistic coordinates and schedules.
"""
import math
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from .models import PlanRequest, PlanResponse, RouteItinerary, TransitLeg, GeoLocation
from .transit_data import PLACES_DATABASE, TRANSIT_LINES

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def interpolate_points(coord1: List[float], coord2: List[float], num_points: int = 4) -> List[List[float]]:
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    points = [coord1]
    for i in range(1, num_points):
        fraction = i / num_points
        # add a tiny curvature for realistic transit curves
        curvature_offset = math.sin(fraction * math.pi) * 0.0018
        points.append([
            round(lon1 + (lon2 - lon1) * fraction + curvature_offset * 0.3, 5),
            round(lat1 + (lat2 - lat1) * fraction + curvature_offset, 5)
        ])
    points.append(coord2)
    return points

class TransitRouter:
    def __init__(self):
        self.places = PLACES_DATABASE

    def find_place(self, name_or_query: str, city: str = "Delhi NCR") -> Optional[Dict[str, Any]]:
        query = name_or_query.strip().lower()
        city_places = self.places.get(city, self.places["Delhi NCR"])
        
        # 1. Exact match on name
        for p in city_places:
            if p["name"].lower() == query:
                return p
                
        # 2. Substring match on name
        for p in city_places:
            if query in p["name"].lower():
                return p
                
        # 3. Match in aliases
        for p in city_places:
            for alias in p.get("aliases", []):
                if query in alias or alias in query:
                    return p
                    
        # 4. Fallback to first place if not matched
        return city_places[0] if city_places else None

    def search_places(self, query: str, city: str = "Delhi NCR") -> List[Dict[str, Any]]:
        q = query.strip().lower()
        city_places = self.places.get(city, self.places["Delhi NCR"])
        if not q:
            return city_places[:8]
            
        matches = []
        for p in city_places:
            score = 0
            if q == p["name"].lower():
                score = 100
            elif p["name"].lower().startswith(q):
                score = 80
            elif q in p["name"].lower():
                score = 60
            else:
                for alias in p.get("aliases", []):
                    if q in alias:
                        score = max(score, 50)
            if score > 0:
                matches.append((score, p))
                
        matches.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matches]

    def plan_journey(self, request: PlanRequest, simulated_delays: Dict[str, int] = None) -> PlanResponse:
        if simulated_delays is None:
            simulated_delays = {}
            
        city = request.city or "Delhi NCR"
        origin_dict = self.find_place(request.origin, city)
        dest_dict = self.find_place(request.destination, city)
        
        if not origin_dict or not dest_dict:
            # Fallback default Delhi nodes
            origin_dict = self.places["Delhi NCR"][0] # Rajiv Chowk
            dest_dict = self.places["Delhi NCR"][4]   # Cyber City

        origin_loc = GeoLocation(
            name=origin_dict["name"],
            lat=origin_dict["lat"],
            lon=origin_dict["lon"],
            category=origin_dict.get("category", "metro_station"),
            city=city,
            aliases=origin_dict.get("aliases", [])
        )
        dest_loc = GeoLocation(
            name=dest_dict["name"],
            lat=dest_dict["lat"],
            lon=dest_dict["lon"],
            category=dest_dict.get("category", "landmark"),
            city=city,
            aliases=dest_dict.get("aliases", [])
        )

        now = datetime.now()
        dep_time_str = request.departure_time or now.strftime("%H:%M")
        try:
            if ":" in dep_time_str and len(dep_time_str) <= 5:
                hh, mm = map(int, dep_time_str.split(":"))
                base_time = now.replace(hour=hh, minute=mm, second=0)
            else:
                base_time = datetime.fromisoformat(dep_time_str)
        except Exception:
            base_time = now

        # Calculate straight-line distance
        dist_km = haversine_km(origin_dict["lat"], origin_dict["lon"], dest_dict["lat"], dest_dict["lon"])
        if dist_km < 0.2:
            dist_km = 1.2

        routes: List[RouteItinerary] = []

        # 1. OPTION 1: FASTEST (Metro Express / Multi-line primary)
        r1 = self._build_fastest_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays)
        routes.append(r1)

        # 2. OPTION 2: LOWEST FARE (Direct DTC Bus or Single Line Metro)
        r2 = self._build_cheapest_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays)
        routes.append(r2)

        # 3. OPTION 3: LEAST CROWDED / COMFORT (Alternative transfer or Electric AC transit)
        r3 = self._build_least_crowded_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays)
        routes.append(r3)

        # Sort routes according to requested primary preference
        if request.preferences.cheapest:
            routes.sort(key=lambda r: (r.total_fare_inr, r.total_duration_minutes))
        elif request.preferences.less_crowded:
            crowd_rank = {"Low": 1, "Moderate": 2, "High": 3, "Very High": 4}
            routes.sort(key=lambda r: (crowd_rank.get(r.overall_crowd, 2), r.total_duration_minutes))
        elif request.preferences.fewer_transfers:
            routes.sort(key=lambda r: (r.transfers_count, r.total_duration_minutes))
        else:
            # Default fastest
            routes.sort(key=lambda r: (r.total_duration_minutes, r.total_fare_inr))

        active_disruptions = sum(1 for d in simulated_delays.values() if d > 0)

        return PlanResponse(
            origin=origin_loc,
            destination=dest_loc,
            generated_at=now.isoformat(),
            routes=routes,
            active_disruptions_count=active_disruptions
        )

    def _build_fastest_route(self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int]) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        # Walking leg to origin transit hub (if needed)
        walk1_duration = 4
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Station Gate 2",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0012, 5), round(orig["lat"] + 0.0010, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0012, 5), round(orig["lat"] + 0.0010, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=320,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk towards Gate 2 pedestrian entrance. Security queue is clear.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        # Determine primary line
        has_airport = "airport" in orig["name"].lower() or "airport" in dest["name"].lower() or "igi" in orig["name"].lower() or "igi" in dest["name"].lower()
        if has_airport:
            line = "Airport Express"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = max(14, int(dist_km * 1.5))
            stops = ["New Delhi (NDLS)", "Shivaji Stadium", "Dhaula Kuan", "Delhi Aerocity", "IGI Airport T3"]
            fare = 60.0
        elif dist_km > 18:
            # Multi-segment metro
            line = "Yellow Line"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = int(dist_km * 1.6)
            stops = ["Rajiv Chowk", "Patel Chowk", "Central Secretariat", "AIIMS", "Hauz Khas", "Malviya Nagar", "Saket"]
            fare = 50.0
        else:
            line = "Blue Line" if "noida" in dest["name"].lower() or "anand" in dest["name"].lower() else "Yellow Line"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = max(12, int(dist_km * 1.8))
            stops = [orig["name"], "Interchange Station", dest["name"]]
            fare = 40.0

        delay = delays.get(line, 0)
        arr_time = curr_time + timedelta(minutes=transit_mins + delay)

        # Metro leg coordinates
        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        transit_path = interpolate_points(start_pt, end_pt, num_points=6)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="metro",
            line_name=line,
            line_color=line_color,
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=transit_path,
            duration_minutes=transit_mins,
            distance_meters=int(dist_km * 1000),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=len(stops),
            intermediate_stops=stops,
            instructions=f"Board {line} towards destination. Board from coach 3 or 4 for swift interchange.",
            crowd_level="High" if delay > 5 else "Moderate",
            delay_minutes=delay,
            is_delayed=delay > 0
        ))
        curr_time = arr_time

        # Final short walk
        walk2_duration = 3
        arr_time = curr_time + timedelta(minutes=walk2_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=f"{dest['name']} Exit 1",
            destination_name=dest["name"],
            origin_coords=[round(dest["lon"] - 0.0008, 5), round(dest["lat"] - 0.0006, 5)],
            destination_coords=[dest["lon"], dest["lat"]],
            path_coords=[[round(dest["lon"] - 0.0008, 5), round(dest["lat"] - 0.0006, 5)], [dest["lon"], dest["lat"]]],
            duration_minutes=walk2_duration,
            distance_meters=210,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Exit via Gate 1 escalators towards main avenue.",
            crowd_level="Low"
        ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        return RouteItinerary(
            id=f"route-fastest-{uuid.uuid4().hex[:6]}",
            title=f"Fastest via {line}",
            tag="Fastest",
            tag_reason=f"Saves ~{max(10, int(dist_km * 0.8))} mins compared to road bus alternatives",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=fare,
            transfers_count=0 if dist_km <= 15 else 1,
            walking_duration_minutes=walk1_duration + walk2_duration,
            walking_distance_meters=530,
            overall_crowd="Moderate",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.12, 1)
        )

    def _build_cheapest_route(self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int]) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_duration = 6
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Bus Stop",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0018, 5), round(orig["lat"] + 0.0015, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0018, 5), round(orig["lat"] + 0.0015, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=450,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to the roadside DTC bus shelter across the crossing.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        bus_line = "DTC Electric Bus 534"
        bus_color = TRANSIT_LINES[bus_line]["color"]
        bus_mins = max(24, int(dist_km * 3.1))
        delay = delays.get(bus_line, 0)
        arr_time = curr_time + timedelta(minutes=bus_mins + delay)

        # Bus route coordinates
        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        bus_path = interpolate_points(start_pt, end_pt, num_points=8)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="bus",
            line_name=bus_line,
            line_color=bus_color,
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=bus_path,
            duration_minutes=bus_mins,
            distance_meters=int(dist_km * 1150),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=8,
            intermediate_stops=["Origin Terminal", "Main Crossing", "Civil Lines", "Ring Road Flyover", "Destination Stand"],
            instructions="Board DTC Low-Floor AC Electric Bus. Valid with One Delhi Transit Card (₹10% discount).",
            crowd_level="Low" if delay == 0 else "Moderate",
            delay_minutes=delay,
            is_delayed=delay > 0
        ))
        curr_time = arr_time

        walk2_duration = 5
        arr_time = curr_time + timedelta(minutes=walk2_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name="Destination Bus Stop",
            destination_name=dest["name"],
            origin_coords=[round(dest["lon"] - 0.0010, 5), round(dest["lat"] - 0.0010, 5)],
            destination_coords=[dest["lon"], dest["lat"]],
            path_coords=[[round(dest["lon"] - 0.0010, 5), round(dest["lat"] - 0.0010, 5)], [dest["lon"], dest["lat"]]],
            duration_minutes=walk2_duration,
            distance_meters=350,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk along sidewalk to the main entrance.",
            crowd_level="Low"
        ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        return RouteItinerary(
            id=f"route-cheapest-{uuid.uuid4().hex[:6]}",
            title=f"Lowest Fare via {bus_line}",
            tag="Lowest Fare",
            tag_reason="Saves ₹25-₹40 with direct electric bus fare",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=15.0,
            transfers_count=0,
            walking_duration_minutes=walk1_duration + walk2_duration,
            walking_distance_meters=800,
            overall_crowd="Low",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.15, 1)
        )

    def _build_least_crowded_route(self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int]) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_duration = 4
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Station Gate 4 (Elevator access)",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0014, 5), round(orig["lat"] + 0.0012, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0014, 5), round(orig["lat"] + 0.0012, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=280,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Enter through Gate 4 with ramp & elevator access. Shorter queues.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        # Magenta line or quieter corridor
        line = "Magenta Line"
        line_color = TRANSIT_LINES[line]["color"]
        transit_mins = max(16, int(dist_km * 1.7))
        delay = delays.get(line, 0)
        arr_time = curr_time + timedelta(minutes=transit_mins + delay)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        path = interpolate_points(start_pt, end_pt, num_points=6)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="metro",
            line_name=line,
            line_color=line_color,
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=path,
            duration_minutes=transit_mins,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=5,
            intermediate_stops=["Hauz Khas", "Panchsheel Park", "Chirag Delhi", "Greater Kailash", "Nehru Enclave"],
            instructions=f"Take {line}. Platform screen doors enabled with ample seating capacity.",
            crowd_level="Low",
            delay_minutes=delay,
            is_delayed=delay > 0
        ))
        curr_time = arr_time

        walk2_duration = 3
        arr_time = curr_time + timedelta(minutes=walk2_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=f"{dest['name']} Gate 2",
            destination_name=dest["name"],
            origin_coords=[round(dest["lon"] - 0.0006, 5), round(dest["lat"] - 0.0006, 5)],
            destination_coords=[dest["lon"], dest["lat"]],
            path_coords=[[round(dest["lon"] - 0.0006, 5), round(dest["lat"] - 0.0006, 5)], [dest["lon"], dest["lat"]]],
            duration_minutes=walk2_duration,
            distance_meters=190,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Exit towards wide walkway with shade.",
            crowd_level="Low"
        ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        return RouteItinerary(
            id=f"route-leastcrowded-{uuid.uuid4().hex[:6]}",
            title=f"Least Crowded via {line}",
            tag="Least Crowded",
            tag_reason="Avoids crowded central interchange stations during peak hours",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=35.0,
            transfers_count=0,
            walking_duration_minutes=walk1_duration + walk2_duration,
            walking_distance_meters=470,
            overall_crowd="Low",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.14, 1)
        )

router_instance = TransitRouter()
