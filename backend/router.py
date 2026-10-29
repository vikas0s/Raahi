"""
Multi-criteria transit journey planner for Raahi.
Computes Fastest, DTC Electric Bus (Govt slabs), Govt Metered Auto, Direct Cab,
and First-Mile / Last-Mile Multimodal routes for Delhi NCR and Indian cities.
"""
import math
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from .models import PlanRequest, PlanResponse, RouteItinerary, TransitLeg, GeoLocation
from .transit_data import (
    PLACES_DATABASE, TRANSIT_LINES, DELHI_GOVT_FARES,
    calculate_dtc_fare, calculate_auto_fare, calculate_erickshaw_fare, calculate_cab_fare
)

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
        
        # 1. Exact match
        for p in city_places:
            if p["name"].lower() == query:
                return p
                
        # 2. Substring match
        for p in city_places:
            if query in p["name"].lower():
                return p
                
        # 3. Match in aliases
        for p in city_places:
            for alias in p.get("aliases", []):
                if query in alias or alias in query:
                    return p
                    
        # 4. Fallback to first place
        return city_places[0] if city_places else None

    def search_places(self, query: str, city: str = "Delhi NCR") -> List[Dict[str, Any]]:
        q = query.strip().lower()
        city_places = self.places.get(city, self.places["Delhi NCR"])
        if not q:
            return city_places[:10]
            
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

    def _get_nearest_metro_node(self, place: Dict[str, Any], city: str = "Delhi NCR") -> Tuple[Dict[str, Any], float]:
        """Finds nearest metro station node if the current place is not directly attached to a metro line."""
        # 1. Check if place is already a direct metro station
        if place.get("category") == "metro_station" and place.get("has_direct_metro", True):
            return place, 0.0

        # 2. Check if nearest_metro property is explicitly defined
        city_places = self.places.get(city, self.places["Delhi NCR"])
        if place.get("nearest_metro"):
            for p in city_places:
                if place["nearest_metro"].lower() in p["name"].lower():
                    dist = haversine_km(place["lat"], place["lon"], p["lat"], p["lon"])
                    return p, dist

        # 3. Find closest metro station by distance
        min_dist = float("inf")
        closest_station = None
        for p in city_places:
            if p.get("category") == "metro_station":
                d = haversine_km(place["lat"], place["lon"], p["lat"], p["lon"])
                if d < min_dist:
                    min_dist = d
                    closest_station = p

        if closest_station:
            return closest_station, min_dist
        return place, 0.0

    def plan_journey(self, request: PlanRequest, simulated_delays: Dict[str, int] = None) -> PlanResponse:
        if simulated_delays is None:
            simulated_delays = {}
            
        city = request.city or "Delhi NCR"
        origin_dict = self.find_place(request.origin, city)
        dest_dict = self.find_place(request.destination, city)
        
        if not origin_dict or not dest_dict:
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

        is_night = base_time.hour >= 23 or base_time.hour < 5

        # Straight-line distance
        dist_km = haversine_km(origin_dict["lat"], origin_dict["lon"], dest_dict["lat"], dest_dict["lon"])
        if dist_km < 0.2:
            dist_km = 1.2

        routes: List[RouteItinerary] = []

        # 1. OPTION 1: FASTEST MULTIMODAL METRO (With First-Mile/Last-Mile E-Rickshaw/Auto if needed)
        r1 = self._build_fastest_multimodal_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, city)
        routes.append(r1)

        # 2. OPTION 2: DTC ELECTRIC BUS (Official Delhi Govt Slabs: ₹10/₹15/₹20/₹25 + Pink Pass ₹0)
        r2 = self._build_dtc_ebus_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, request.preferences.pink_pass)
        routes.append(r2)

        # 3. OPTION 3: DELHI GOVT METERED AUTO (TSR - Gazetted ₹30 first 1.5km + ₹11/km)
        r3 = self._build_direct_auto_route(origin_dict, dest_dict, dist_km, base_time, is_night)
        routes.append(r3)

        # 4. OPTION 4: DIRECT CAB / TAXI (BluSmart EV / Ride-Hailing Cab)
        r4 = self._build_direct_cab_route(origin_dict, dest_dict, dist_km, base_time)
        routes.append(r4)

        # 5. OPTION 5: LOWEST FARE NON-AC BUS (DTC Non-AC: ₹5/₹10/₹15)
        r5 = self._build_cheapest_bus_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, request.preferences.pink_pass)
        routes.append(r5)

        # Sort according to user preference
        if request.preferences.cheapest or request.preferences.pink_pass:
            routes.sort(key=lambda r: (r.total_fare_inr, r.total_duration_minutes))
        elif request.preferences.prefer_ebus:
            routes.sort(key=lambda r: (0 if r.tag == "DTC Electric Bus" else 1, r.total_duration_minutes))
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

    def _build_fastest_multimodal_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int], city: str
    ) -> RouteItinerary:
        """Rapid transit route integrating First-Mile & Last-Mile Auto/E-Rickshaw when metro is far."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        orig_hub, first_mile_km = self._get_nearest_metro_node(orig, city)
        dest_hub, last_mile_km = self._get_nearest_metro_node(dest, city)

        first_mile_needed = first_mile_km > 0.8
        last_mile_needed = last_mile_km > 0.8

        total_fare = 0.0
        fare_parts: List[str] = []

        # ----------------- FIRST MILE LEG -----------------
        if first_mile_needed:
            # Use E-Rickshaw if <= 2.5km, otherwise Auto-Rickshaw
            if first_mile_km <= 2.5:
                fm_mode = "erickshaw"
                fm_line = "Shared E-Rickshaw Feeder"
                fm_fare, fm_desc = calculate_erickshaw_fare(first_mile_km)
                fm_duration = max(7, int(first_mile_km * 4.5))
                fm_instruction = f"Take shared E-Rickshaw from {orig['name']} to {orig_hub['name']} Gate 2 stand. High frequency."
            else:
                fm_mode = "auto"
                fm_line = "Delhi Govt Metered Auto"
                fm_fare, fm_desc = calculate_auto_fare(first_mile_km)
                fm_duration = max(10, int(first_mile_km * 3.0))
                fm_instruction = f"Hire metered Auto-Rickshaw to {orig_hub['name']} Metro Station. Direct feeder."

            total_fare += fm_fare
            fare_parts.append(f"{fm_mode.capitalize()} (₹{int(fm_fare)})")
            arr_time = curr_time + timedelta(minutes=fm_duration)

            start_pt = [orig["lon"], orig["lat"]]
            end_pt = [orig_hub["lon"], orig_hub["lat"]]
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode=fm_mode,
                line_name=fm_line,
                line_color="#E68A00" if fm_mode == "auto" else "#00897B",
                origin_name=orig["name"],
                destination_name=f"{orig_hub['name']} Metro Station",
                origin_coords=start_pt,
                destination_coords=end_pt,
                path_coords=interpolate_points(start_pt, end_pt, num_points=4),
                duration_minutes=fm_duration,
                distance_meters=int(first_mile_km * 1000),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[f"{orig['name']} Stand", f"{orig_hub['name']} Gate 2"],
                instructions=fm_instruction,
                crowd_level="Moderate",
                fare_inr=fm_fare,
                fare_details=fm_desc
            ))
            curr_time = arr_time
        else:
            # Short walk to platform
            walk_dur = 4
            arr_time = curr_time + timedelta(minutes=walk_dur)
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="walk",
                origin_name=orig["name"],
                destination_name=f"{orig_hub['name']} Gate 2",
                origin_coords=[orig["lon"], orig["lat"]],
                destination_coords=[orig_hub["lon"], orig_hub["lat"]],
                path_coords=[[orig["lon"], orig["lat"]], [orig_hub["lon"], orig_hub["lat"]]],
                duration_minutes=walk_dur,
                distance_meters=320,
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                instructions="Walk towards Gate 2 pedestrian concourse. Security queue is clear.",
                crowd_level="Low"
            ))
            curr_time = arr_time

        # ----------------- MAIN RAPID METRO HAUL -----------------
        metro_dist_km = haversine_km(orig_hub["lat"], orig_hub["lon"], dest_hub["lat"], dest_hub["lon"])
        if metro_dist_km < 1.0:
            metro_dist_km = 3.0

        has_airport = "airport" in orig["name"].lower() or "airport" in dest["name"].lower() or "igi" in orig["name"].lower() or "igi" in dest["name"].lower()
        if has_airport:
            line = "Airport Express"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = max(14, int(metro_dist_km * 1.5))
            stops = ["New Delhi (NDLS)", "Shivaji Stadium", "Dhaula Kuan", "Delhi Aerocity", "IGI Airport T3"]
            metro_fare = 60.0
        elif metro_dist_km > 18:
            line = "Yellow Line"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = int(metro_dist_km * 1.6)
            stops = ["Rajiv Chowk", "Central Secretariat", "AIIMS", "Hauz Khas", "Malviya Nagar", "Saket"]
            metro_fare = 50.0
        else:
            line = "Blue Line" if "noida" in dest["name"].lower() or "anand" in dest["name"].lower() else "Yellow Line"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = max(12, int(metro_dist_km * 1.8))
            stops = [orig_hub["name"], "Interchange Junction", dest_hub["name"]]
            metro_fare = 40.0

        total_fare += metro_fare
        fare_parts.append(f"Metro (₹{int(metro_fare)})")

        delay = delays.get(line, 0)
        arr_time = curr_time + timedelta(minutes=transit_mins + delay)

        metro_start = [orig_hub["lon"], orig_hub["lat"]]
        metro_end = [dest_hub["lon"], dest_hub["lat"]]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="metro",
            line_name=line,
            line_color=line_color,
            origin_name=orig_hub["name"],
            destination_name=dest_hub["name"],
            origin_coords=metro_start,
            destination_coords=metro_end,
            path_coords=interpolate_points(metro_start, metro_end, num_points=6),
            duration_minutes=transit_mins,
            distance_meters=int(metro_dist_km * 1000),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=len(stops),
            intermediate_stops=stops,
            instructions=f"Board {line} towards destination. Board from coach 3 or 4 for swift interchange.",
            crowd_level="High" if delay > 5 else "Moderate",
            delay_minutes=delay,
            is_delayed=delay > 0,
            fare_inr=metro_fare,
            fare_details=f"DMRC Token/Smart Card Fare: ₹{int(metro_fare)}"
        ))
        curr_time = arr_time

        # ----------------- LAST MILE LEG -----------------
        if last_mile_needed:
            if last_mile_km <= 2.5:
                lm_mode = "erickshaw"
                lm_line = "Shared E-Rickshaw Feeder"
                lm_fare, lm_desc = calculate_erickshaw_fare(last_mile_km)
                lm_duration = max(7, int(last_mile_km * 4.5))
                lm_instruction = f"Take shared E-Rickshaw from {dest_hub['name']} Exit to {dest['name']}."
            else:
                lm_mode = "auto"
                lm_line = "Delhi Govt Metered Auto"
                lm_fare, lm_desc = calculate_auto_fare(last_mile_km)
                lm_duration = max(9, int(last_mile_km * 3.0))
                lm_instruction = f"Hire metered Auto-Rickshaw from {dest_hub['name']} station to {dest['name']}."

            total_fare += lm_fare
            fare_parts.append(f"{lm_mode.capitalize()} (₹{int(lm_fare)})")
            arr_time = curr_time + timedelta(minutes=lm_duration)

            lm_start = [dest_hub["lon"], dest_hub["lat"]]
            lm_end = [dest["lon"], dest["lat"]]
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode=lm_mode,
                line_name=lm_line,
                line_color="#E68A00" if lm_mode == "auto" else "#00897B",
                origin_name=f"{dest_hub['name']} Exit",
                destination_name=dest["name"],
                origin_coords=lm_start,
                destination_coords=lm_end,
                path_coords=interpolate_points(lm_start, lm_end, num_points=4),
                duration_minutes=lm_duration,
                distance_meters=int(last_mile_km * 1000),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[f"{dest_hub['name']} Stand", dest["name"]],
                instructions=lm_instruction,
                crowd_level="Low",
                fare_inr=lm_fare,
                fare_details=lm_desc
            ))
        else:
            walk_dur = 3
            arr_time = curr_time + timedelta(minutes=walk_dur)
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="walk",
                origin_name=f"{dest_hub['name']} Exit Gate",
                destination_name=dest["name"],
                origin_coords=[dest_hub["lon"], dest_hub["lat"]],
                destination_coords=[dest["lon"], dest["lat"]],
                path_coords=[[dest_hub["lon"], dest_hub["lat"]], [dest["lon"], dest["lat"]]],
                duration_minutes=walk_dur,
                distance_meters=210,
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                instructions="Exit towards destination walkway. Ramp & wide pedestrian path.",
                crowd_level="Low"
            ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        tag_title = f"Metro + First/Last Mile Connector" if (first_mile_needed or last_mile_needed) else f"Fastest via {line}"
        tag_reason = "Combines high-speed rail with seamless first/last-mile feeder connections" if (first_mile_needed or last_mile_needed) else "Saves 15-25 mins compared to road traffic alternatives"

        return RouteItinerary(
            id=f"route-fastest-{uuid.uuid4().hex[:6]}",
            title=tag_title,
            tag="Fastest",
            tag_reason=tag_reason,
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=total_fare,
            fare_breakdown=" + ".join(fare_parts),
            route_type="metro_multimodal",
            transfers_count=(1 if first_mile_needed else 0) + (1 if last_mile_needed else 0) + (1 if dist_km > 16 else 0),
            walking_duration_minutes=7 if not first_mile_needed else 3,
            walking_distance_meters=530 if not first_mile_needed else 180,
            overall_crowd="Moderate",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.14, 1)
        )

    def _build_dtc_ebus_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int], is_pink_pass: bool
    ) -> RouteItinerary:
        """DTC Low-Floor AC Electric Bus Route with official Delhi Govt gazetted fare slabs."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_duration = 5
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} DTC Bus Shelter",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0015, 5), round(orig["lat"] + 0.0012, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0015, 5), round(orig["lat"] + 0.0012, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=350,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to roadside DTC EV Bus Stop. Digital ETA countdown board active.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        bus_line = "DTC Electric Bus (Tata Ultra EV)"
        bus_mins = max(22, int(dist_km * 3.0))
        delay = delays.get(bus_line, 0)
        arr_time = curr_time + timedelta(minutes=bus_mins + delay)

        # Official Delhi Government Fare Slab Calculation
        ebus_fare, fare_desc = calculate_dtc_fare(dist_km, is_electric=True, is_pink_pass=is_pink_pass)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="ebus",
            line_name="DTC AC Electric Bus E-534",
            line_color="#00A86B",
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=interpolate_points(start_pt, end_pt, num_points=8),
            duration_minutes=bus_mins,
            distance_meters=int(dist_km * 1150),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=7,
            intermediate_stops=["Origin Terminal", "Ring Road Flyover", "Central Crossing", "AIIMS Hub", "Destination Stand"],
            instructions="Board DTC Low-Floor AC Electric Bus. 100% Zero-Emission. Pink Pass free for women commuters.",
            crowd_level="Low" if delay == 0 else "Moderate",
            delay_minutes=delay,
            is_delayed=delay > 0,
            fare_inr=ebus_fare,
            fare_details=fare_desc
        ))
        curr_time = arr_time

        walk2_duration = 4
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
            distance_meters=280,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Exit bus and walk along sidewalk towards main gate.",
            crowd_level="Low"
        ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        return RouteItinerary(
            id=f"route-ebus-{uuid.uuid4().hex[:6]}",
            title="DTC Electric Bus (Govt Slab)",
            tag="DTC Electric Bus",
            tag_reason="Delhi Govt AC Electric Bus: Gazetted fare slab (₹10-₹25) + Pink Ticket (₹0 Free for Women)",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=ebus_fare,
            pink_pass_fare_inr=0.0,
            fare_breakdown=fare_desc,
            route_type="dtc_ebus",
            transfers_count=0,
            walking_duration_minutes=walk1_duration + walk2_duration,
            walking_distance_meters=630,
            overall_crowd="Low",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.18, 1)
        )

    def _build_direct_auto_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, is_night: bool
    ) -> RouteItinerary:
        """Delhi Government Regulated Metered TSR (Three-Wheeler Auto-Rickshaw) Option."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        # Direct auto pickup with 1 minute walk
        walk1_duration = 1
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Auto Stand",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0004, 5), round(orig["lat"] + 0.0003, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0004, 5), round(orig["lat"] + 0.0003, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=60,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to street auto stand or hail on-demand.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        auto_fare, fare_desc = calculate_auto_fare(dist_km, is_night=is_night)
        # Average auto road speed in Delhi: 26 km/h
        auto_duration = max(10, int((dist_km / 26.0) * 60))
        arr_time = curr_time + timedelta(minutes=auto_duration)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="auto",
            line_name="Delhi Govt Metered Auto (TSR)",
            line_color="#E68A00",
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=interpolate_points(start_pt, end_pt, num_points=8),
            duration_minutes=auto_duration,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=0,
            intermediate_stops=[],
            instructions="Direct point-to-point ride. Pay strictly by Delhi Govt Gazetted meter or ONDC digital auto.",
            crowd_level="Low",
            fare_inr=auto_fare,
            fare_details=fare_desc
        ))

        total_mins = auto_duration + walk1_duration
        return RouteItinerary(
            id=f"route-auto-{uuid.uuid4().hex[:6]}",
            title="Delhi Govt Metered Auto (TSR)",
            tag="Govt Metered Auto",
            tag_reason="Direct point-to-point without transfers. Regulated Delhi Govt meter (₹30 base + ₹11/km)",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=auto_fare,
            fare_breakdown=fare_desc,
            route_type="auto_rickshaw",
            transfers_count=0,
            walking_duration_minutes=walk1_duration,
            walking_distance_meters=60,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.05, 1)
        )

    def _build_direct_cab_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime
    ) -> RouteItinerary:
        """BluSmart EV / On-Demand Cab Option for maximum comfort and speed."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_duration = 1
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Curbside Pickup Point",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0003, 5), round(orig["lat"] + 0.0002, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0003, 5), round(orig["lat"] + 0.0002, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=40,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to designated cab pickup curbside.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        # Average taxi road speed: 32 km/h
        cab_duration = max(12, int((dist_km / 32.0) * 60))
        cab_fare, fare_desc = calculate_cab_fare(dist_km, cab_duration)
        arr_time = curr_time + timedelta(minutes=cab_duration)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="taxi",
            line_name="BluSmart EV / App Taxi",
            line_color="#3B5360",
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=interpolate_points(start_pt, end_pt, num_points=8),
            duration_minutes=cab_duration,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=0,
            intermediate_stops=[],
            instructions="Door-to-door AC cab pickup. Zero walking, direct highway express navigation.",
            crowd_level="Low",
            fare_inr=cab_fare,
            fare_details=fare_desc
        ))

        return RouteItinerary(
            id=f"route-cab-{uuid.uuid4().hex[:6]}",
            title="Direct Cab (BluSmart EV)",
            tag="Direct Cab",
            tag_reason="Door-to-door AC comfort. Zero walking or interchange waiting",
            total_duration_minutes=cab_duration,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            total_fare_inr=cab_fare,
            fare_breakdown=fare_desc,
            route_type="cab_taxi",
            transfers_count=0,
            walking_duration_minutes=0,
            walking_distance_meters=0,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.08, 1)
        )

    def _build_cheapest_bus_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int], is_pink_pass: bool
    ) -> RouteItinerary:
        """DTC Non-AC / Cluster Green Bus Route with ₹5/₹10/₹15 fare slabs."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_duration = 5
        arr_time = curr_time + timedelta(minutes=walk1_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Cluster Stand",
            origin_coords=[orig["lon"], orig["lat"]],
            destination_coords=[round(orig["lon"] + 0.0016, 5), round(orig["lat"] + 0.0013, 5)],
            path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0016, 5), round(orig["lat"] + 0.0013, 5)]],
            duration_minutes=walk1_duration,
            distance_meters=390,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to roadside DTC Green Bus Stand.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        bus_line = "DTC Green Bus 419"
        bus_mins = max(25, int(dist_km * 3.3))
        delay = delays.get(bus_line, 0)
        arr_time = curr_time + timedelta(minutes=bus_mins + delay)

        non_ac_fare, fare_desc = calculate_dtc_fare(dist_km, is_electric=False, is_pink_pass=is_pink_pass)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="bus",
            line_name=bus_line,
            line_color="#388E3C",
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=interpolate_points(start_pt, end_pt, num_points=8),
            duration_minutes=bus_mins,
            distance_meters=int(dist_km * 1150),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=8,
            intermediate_stops=["Origin Terminal", "Main Crossing", "Civil Lines", "Ring Road Flyover", "Destination Stand"],
            instructions="Board DTC Non-AC Green Bus. Gulabi Ticket (₹0 Free) valid for women.",
            crowd_level="Moderate",
            delay_minutes=delay,
            is_delayed=delay > 0,
            fare_inr=non_ac_fare,
            fare_details=fare_desc
        ))
        curr_time = arr_time

        walk2_duration = 4
        arr_time = curr_time + timedelta(minutes=walk2_duration)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name="Destination Stand",
            destination_name=dest["name"],
            origin_coords=[round(dest["lon"] - 0.0009, 5), round(dest["lat"] - 0.0009, 5)],
            destination_coords=[dest["lon"], dest["lat"]],
            path_coords=[[round(dest["lon"] - 0.0009, 5), round(dest["lat"] - 0.0009, 5)], [dest["lon"], dest["lat"]]],
            duration_minutes=walk2_duration,
            distance_meters=300,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to destination.",
            crowd_level="Low"
        ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        return RouteItinerary(
            id=f"route-cheapest-{uuid.uuid4().hex[:6]}",
            title="DTC Ordinary Bus (₹5-₹15)",
            tag="Lowest Fare",
            tag_reason="Delhi Govt Non-AC fare slab: ₹5 to ₹15 only. Free for women with Pink Pass.",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=non_ac_fare,
            pink_pass_fare_inr=0.0,
            fare_breakdown=fare_desc,
            route_type="budget_bus",
            transfers_count=0,
            walking_duration_minutes=walk1_duration + walk2_duration,
            walking_distance_meters=690,
            overall_crowd="Moderate",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.16, 1)
        )

router_instance = TransitRouter()
