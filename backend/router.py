"""
Multi-criteria transit journey planner for Raahi.
Computes Fastest, DTC Electric Bus (Govt slabs), Govt Metered Auto, Direct Cab,
and First-Mile / Last-Mile Multimodal routes for Delhi NCR and Indian cities.
"""
import math
import uuid
import urllib.request
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from .models import PlanRequest, PlanResponse, RouteItinerary, TransitLeg, GeoLocation
from .transit_data import (
    PLACES_DATABASE, TRANSIT_LINES, DELHI_GOVT_FARES,
    calculate_dtc_fare, calculate_auto_fare, calculate_erickshaw_fare, calculate_cab_fare,
    calculate_delhi_taxi_fare,
    is_transit_operational, get_closed_message,
    calculate_mathura_erickshaw_fare, calculate_mathura_shared_tempo_fare,
    calculate_mathura_ebus_fare, calculate_mathura_reserved_auto_fare, calculate_mathura_taxi_fare
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

_ROAD_GEOMETRY_CACHE: Dict[str, List[List[float]]] = {}

def get_road_geometry(coord1: List[float], coord2: List[float], mode: str = "driving") -> List[List[float]]:
    """
    Fetch realistic street-level route geometry following Delhi roads via OSRM,
    with an in-memory cache and resilient curved corridor fallback.
    """
    lon1, lat1 = round(coord1[0], 4), round(coord1[1], 4)
    lon2, lat2 = round(coord2[0], 4), round(coord2[1], 4)
    cache_key = f"{lon1},{lat1};{lon2},{lat2};{mode}"
    if cache_key in _ROAD_GEOMETRY_CACHE:
        return _ROAD_GEOMETRY_CACHE[cache_key]

    try:
        url = f"http://router.project-osrm.org/route/v1/{mode}/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
        req = urllib.request.Request(url, headers={"User-Agent": "RaahiTransit/1.0"})
        with urllib.request.urlopen(req, timeout=1.8) as resp:
            data = json.loads(resp.read().decode())
            if data.get("routes") and len(data["routes"]) > 0:
                coords = data["routes"][0]["geometry"]["coordinates"]
                if len(coords) >= 2:
                    _ROAD_GEOMETRY_CACHE[cache_key] = coords
                    return coords
    except Exception:
        pass

    fallback = interpolate_points(coord1, coord2, num_points=8)
    _ROAD_GEOMETRY_CACHE[cache_key] = fallback
    return fallback

class TransitRouter:
    def __init__(self):
        self.places = PLACES_DATABASE

    def _resolve_city_places(self, city: str) -> List[Dict[str, Any]]:
        c = (city or "").strip().lower()
        if "mathura" in c or "vrindavan" in c or "braj" in c:
            return self.places.get("Mathura & Vrindavan", [])
        elif "mumbai" in c:
            return self.places.get("Mumbai", [])
        elif "bengaluru" in c or "bangalore" in c:
            return self.places.get("Bengaluru", [])
        else:
            return self.places.get("Delhi NCR", [])

    def find_place(self, name_or_query: str, city: str = "Delhi NCR") -> Optional[Dict[str, Any]]:
        query = name_or_query.strip().lower()
        city_places = self._resolve_city_places(city)
        
        # 1. Exact match in selected city
        for p in city_places:
            if p["name"].lower() == query:
                return p
                
        # 2. Substring match in selected city
        for p in city_places:
            if query in p["name"].lower() or p["name"].lower() in query:
                return p
                
        # 3. Match in aliases in selected city
        for p in city_places:
            for alias in p.get("aliases", []):
                if query in alias or alias in query:
                    return p

        # 4. Global match across all cities if not found in current city
        for c_key, c_places in self.places.items():
            for p in c_places:
                if p["name"].lower() == query:
                    return p
                for alias in p.get("aliases", []):
                    if query in alias or alias in query:
                        return p
                    
        # 5. Fallback to first place in city
        return city_places[0] if city_places else None

    def search_places(self, query: str, city: str = "Delhi NCR") -> List[Dict[str, Any]]:
        q = query.strip().lower()
        city_places = self._resolve_city_places(city)
        if not q:
            return city_places[:12]
            
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
                    if q == alias:
                        score = max(score, 90)
                    elif alias.startswith(q):
                        score = max(score, 70)
                    elif q in alias:
                        score = max(score, 50)
            if score > 0:
                matches.append((score, p))
                
        matches.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matches]

    def _get_nearest_metro_node(self, place: Dict[str, Any], city: str = "Delhi NCR") -> Tuple[Dict[str, Any], float]:
        """Finds nearest metro station node if the current place is not directly attached to a metro line."""
        # 1. Check if place is already a direct metro station or has direct metro access
        if place.get("has_direct_metro", False) or place.get("category") == "metro_station":
            return place, 0.0

        city_places = self.places.get(city, self.places.get("Delhi NCR", []))

        # 2. Check if nearest_metro property is explicitly defined
        if place.get("nearest_metro"):
            for p in city_places:
                if place["nearest_metro"].lower() in p["name"].lower():
                    dist = haversine_km(place["lat"], place["lon"], p["lat"], p["lon"])
                    return p, dist

        # 3. Find closest node that HAS direct metro access
        min_dist = float("inf")
        closest_station = None
        for p in city_places:
            if p.get("has_direct_metro", False) or p.get("category") == "metro_station":
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
        is_mathura = "mathura" in city.lower() or "vrindavan" in city.lower() or "braj" in city.lower()
        origin_dict = self.find_place(request.origin, city)
        dest_dict = self.find_place(request.destination, city)
        
        if not origin_dict or not dest_dict:
            if is_mathura:
                m_places = self.places.get("Mathura & Vrindavan", [])
                origin_dict = origin_dict or (m_places[0] if m_places else None) # Mathura Junction
                dest_dict = dest_dict or (m_places[21] if len(m_places) > 21 else m_places[-1]) # Bankey Bihari Ji
            else:
                origin_dict = origin_dict or self.places["Delhi NCR"][0] # Rajiv Chowk
                dest_dict = dest_dict or self.places["Delhi NCR"][4]   # Cyber City

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

        # Straight-line distance
        dist_km = haversine_km(origin_dict["lat"], origin_dict["lon"], dest_dict["lat"], dest_dict["lon"])
        if dist_km < 0.2:
            dist_km = 1.2

        # Route directly to Mathura & Vrindavan transit engine
        if is_mathura:
            return self._plan_mathura_journey(
                origin_dict=origin_dict,
                dest_dict=dest_dict,
                origin_loc=origin_loc,
                dest_loc=dest_loc,
                dist_km=dist_km,
                base_time=base_time,
                request=request,
                simulated_delays=simulated_delays
            )

        is_night = base_time.hour >= 23 or base_time.hour < 5

        # Check transit service availability based on real operating hours
        metro_available = is_transit_operational("dmrc_metro", base_time.hour, base_time.minute)
        airport_express_available = is_transit_operational("airport_express", base_time.hour, base_time.minute)
        bus_available = is_transit_operational("dtc_bus", base_time.hour, base_time.minute)

        # Straight-line distance
        dist_km = haversine_km(origin_dict["lat"], origin_dict["lon"], dest_dict["lat"], dest_dict["lon"])
        if dist_km < 0.2:
            dist_km = 1.2

        routes: List[RouteItinerary] = []

        # 1. OPTION 1: FASTEST / MULTI-TRANSPORT AUTO + METRO
        #    Only show if metro is currently operational
        if metro_available:
            r1 = self._build_fastest_multimodal_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, city)
            routes.append(r1)

            # 1B. OPTION 1B (BUDGET MULTI-TRANSPORT): SHARED E-RICKSHAW + METRO
            _, fm_km = self._get_nearest_metro_node(origin_dict, city)
            if fm_km >= 0.6 and fm_km <= 4.0 and dist_km > 3.0:
                r1b = self._build_budget_multimodal_erickshaw_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, city)
                routes.append(r1b)
        else:
            # Add a "Metro Closed" placeholder so user knows why metro isn't shown
            r1_closed = self._build_metro_closed_night_route(origin_dict, dest_dict, dist_km, base_time, is_night)
            routes.append(r1_closed)

        # 2. OPTION 2: DTC ELECTRIC BUS (Official Delhi Govt Slabs: ₹10/₹15/₹20/₹25 + Pink Pass ₹0)
        if bus_available:
            r2 = self._build_dtc_ebus_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, request.preferences.pink_pass)
            routes.append(r2)
        else:
            # Mark as unavailable but still show so user knows the option exists
            r2 = self._build_dtc_ebus_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, request.preferences.pink_pass)
            r2.service_available = False
            r2.unavailable_reason = get_closed_message("dtc_bus")
            routes.append(r2)

        # 3. OPTION 3: DELHI GOVT METERED AUTO (TSR - Gazetted ₹30 first 1.5km + ₹11/km)
        #    Autos run 24/7 in Delhi
        r3 = self._build_direct_auto_route(origin_dict, dest_dict, dist_km, base_time, is_night)
        routes.append(r3)

        # 4. OPTION 4: DIRECT CAB / TAXI (BluSmart EV / Ride-Hailing Cab)
        #    Cabs run 24/7
        r4 = self._build_direct_cab_route(origin_dict, dest_dict, dist_km, base_time)
        routes.append(r4)

        # 5. OPTION 5: LOWEST FARE NON-AC BUS (DTC Non-AC: ₹5/₹10/₹15)
        if bus_available:
            r5 = self._build_cheapest_bus_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, request.preferences.pink_pass)
            routes.append(r5)
        else:
            r5 = self._build_cheapest_bus_route(origin_dict, dest_dict, dist_km, base_time, simulated_delays, request.preferences.pink_pass)
            r5.service_available = False
            r5.unavailable_reason = get_closed_message("dtc_bus")
            routes.append(r5)

        # 6. OPTION 6 (FOR SHORT DISTANCE): SHARED E-RICKSHAW HOPPER (<= 3.0 km)
        if dist_km <= 3.0:
            r6 = self._build_delhi_erickshaw_short_route(origin_dict, dest_dict, dist_km, base_time)
            routes.append(r6)

        # Sort according to user preference (unavailable services always pushed to bottom)
        def _avail_key(r):
            return 0 if r.service_available else 1

        if getattr(request.preferences, "prefer_multimodal", False):
            routes.sort(key=lambda r: (_avail_key(r), 0 if "Multi-Transport" in r.tag else 1, r.total_duration_minutes))
        elif request.preferences.cheapest or request.preferences.pink_pass:
            routes.sort(key=lambda r: (_avail_key(r), r.total_fare_inr, r.total_duration_minutes))
        elif request.preferences.prefer_ebus:
            routes.sort(key=lambda r: (_avail_key(r), 0 if r.tag == "DTC Electric Bus" else 1, r.total_duration_minutes))
        elif request.preferences.less_crowded:
            crowd_rank = {"Low": 1, "Moderate": 2, "High": 3, "Very High": 4}
            routes.sort(key=lambda r: (_avail_key(r), crowd_rank.get(r.overall_crowd, 2), r.total_duration_minutes))
        elif request.preferences.fewer_transfers:
            routes.sort(key=lambda r: (_avail_key(r), r.transfers_count, r.total_duration_minutes))
        else:
            # Default fastest
            routes.sort(key=lambda r: (_avail_key(r), r.total_duration_minutes, r.total_fare_inr))

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
        """Rapid transit route integrating Doorstep Auto First-Mile & Last-Mile feeder when metro is away."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        orig_hub, first_mile_km = self._get_nearest_metro_node(orig, city)
        dest_hub, last_mile_km = self._get_nearest_metro_node(dest, city)

        first_mile_needed = first_mile_km >= 0.6
        last_mile_needed = last_mile_km >= 0.6

        total_fare = 0.0
        fare_parts: List[str] = []

        # ----------------- FIRST MILE LEG -----------------
        if first_mile_needed:
            # Doorstep Auto-Rickshaw feeder connecting home/colony to nearest metro station
            fm_mode = "auto"
            fm_line = f"Delhi Govt Metered Auto ({first_mile_km:.1f} km)"
            fm_fare, fm_desc = calculate_auto_fare(first_mile_km)
            fm_duration = max(6, int((first_mile_km / 25.0) * 60))
            fm_instruction = f"Hire doorstep metered Auto-Rickshaw from {orig['name']} to {orig_hub['name']} Metro Station (Gate 2 / Auto Stand). Feeder leg saves {int(first_mile_km * 12)} mins walking."

            total_fare += fm_fare
            fare_parts.append(f"Auto (₹{int(fm_fare)})")
            arr_time = curr_time + timedelta(minutes=fm_duration)

            start_pt = [orig["lon"], orig["lat"]]
            end_pt = [orig_hub["lon"], orig_hub["lat"]]
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode=fm_mode,
                line_name=fm_line,
                line_color="#E68A00",
                origin_name=orig["name"],
                destination_name=f"{orig_hub['name']} Metro Station",
                origin_coords=start_pt,
                destination_coords=end_pt,
                path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
                duration_minutes=fm_duration,
                distance_meters=int(first_mile_km * 1000),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[f"{orig['name']} Curbside", f"{orig_hub['name']} Gate 2 Stand"],
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
                path_coords=get_road_geometry(lm_start, lm_end, mode="driving"),
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
        is_short = dist_km <= 4.0
        if is_short:
            tag_title = f"Metro ({line}) — {dist_km:.1f} km"
            tag = "Metro (Alternative)"
            tag_reason = f"DMRC rapid transit ({dist_km:.1f} km). Direct Auto is typically faster for this short trip due to zero station walking & queues."
        elif first_mile_needed or last_mile_needed:
            tag_title = f"Multi-Transport: Doorstep Auto ➔ Metro ({line})"
            tag = "Multi-Transport (Auto + Metro)"
            tag_reason = f"Door-to-door multi-transport: Hires Auto ({first_mile_km:.1f} km, ₹{int(fm_fare if first_mile_needed else 0)}) from home/colony directly to {orig_hub['name']} Metro Station, skips highway jams via rapid rail, and drops at destination."
        else:
            tag_title = f"Fastest via {line}"
            tag = "Fastest"
            tag_reason = "Rapid DMRC metro transit. Saves 15-25 mins compared to road traffic alternatives."

        return RouteItinerary(
            id=f"route-fastest-{uuid.uuid4().hex[:6]}",
            title=tag_title,
            tag=tag,
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


    def _build_budget_multimodal_erickshaw_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, delays: Dict[str, int], city: str
    ) -> RouteItinerary:
        """Budget Multimodal Route: Shared E-Rickshaw feeder from colony stand to Metro, then Metro rail, then last-mile drop."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        orig_hub, first_mile_km = self._get_nearest_metro_node(orig, city)
        dest_hub, last_mile_km = self._get_nearest_metro_node(dest, city)

        total_fare = 0.0
        fare_parts: List[str] = []

        # 1. First-mile: Shared E-Rickshaw feeder
        fm_fare, fm_desc = calculate_erickshaw_fare(first_mile_km)
        fm_duration = max(8, int((first_mile_km / 18.0) * 60))
        total_fare += fm_fare
        fare_parts.append(f"E-Rickshaw (₹{int(fm_fare)})")
        arr_time = curr_time + timedelta(minutes=fm_duration)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [orig_hub["lon"], orig_hub["lat"]]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="erickshaw",
            line_name="Shared E-Rickshaw Feeder",
            line_color="#00897B",
            origin_name=orig["name"],
            destination_name=f"{orig_hub['name']} Metro Stand",
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
            duration_minutes=fm_duration,
            distance_meters=int(first_mile_km * 1000),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=1,
            intermediate_stops=[f"{orig['name']} Colony Stand", f"{orig_hub['name']} Metro Stand"],
            instructions=f"Board shared E-Rickshaw from {orig['name']} colony stand to {orig_hub['name']} Metro station gate. Economical feeder (₹{int(fm_fare)}).",
            crowd_level="Moderate",
            fare_inr=fm_fare,
            fare_details=fm_desc
        ))
        curr_time = arr_time

        # 2. Main Trunk Metro Haul
        metro_dist_km = haversine_km(orig_hub["lat"], orig_hub["lon"], dest_hub["lat"], dest_hub["lon"])
        if metro_dist_km < 1.0:
            metro_dist_km = 3.0

        if metro_dist_km > 18:
            line = "Yellow Line"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = int(metro_dist_km * 1.6)
            stops = ["Interchange Concourse", "Platform Express", dest_hub["name"]]
            metro_fare = 50.0
        else:
            line = "Blue Line" if ("noida" in dest["name"].lower() or "anand" in dest["name"].lower()) else "Yellow Line"
            line_color = TRANSIT_LINES[line]["color"]
            transit_mins = max(12, int(metro_dist_km * 1.8))
            stops = [orig_hub["name"], "Platform Junction", dest_hub["name"]]
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
            instructions=f"Board {line} from platform towards {dest_hub['name']}.",
            crowd_level="Moderate",
            delay_minutes=delay,
            is_delayed=delay > 0,
            fare_inr=metro_fare,
            fare_details=f"DMRC Smart Card/Token: ₹{int(metro_fare)}"
        ))
        curr_time = arr_time

        # 3. Last-Mile Leg
        if last_mile_km >= 0.8:
            lm_fare, lm_desc = calculate_erickshaw_fare(last_mile_km)
            lm_duration = max(7, int((last_mile_km / 18.0) * 60))
            total_fare += lm_fare
            fare_parts.append(f"E-Rickshaw (₹{int(lm_fare)})")
            arr_time = curr_time + timedelta(minutes=lm_duration)
            lm_start = [dest_hub["lon"], dest_hub["lat"]]
            lm_end = [dest["lon"], dest["lat"]]
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="erickshaw",
                line_name="Shared E-Rickshaw Feeder",
                line_color="#00897B",
                origin_name=f"{dest_hub['name']} Exit",
                destination_name=dest["name"],
                origin_coords=lm_start,
                destination_coords=lm_end,
                path_coords=get_road_geometry(lm_start, lm_end, mode="driving"),
                duration_minutes=lm_duration,
                distance_meters=int(last_mile_km * 1000),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[f"{dest_hub['name']} Stand", dest["name"]],
                instructions=f"Take shared E-Rickshaw from {dest_hub['name']} Exit to {dest['name']}.",
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
                instructions="Exit towards destination walkway.",
                crowd_level="Low"
            ))

        total_mins = sum(leg.duration_minutes for leg in legs) + delay
        return RouteItinerary(
            id=f"route-budget-multi-{uuid.uuid4().hex[:6]}",
            title=f"Budget Multi-Transport: E-Rickshaw ➔ Metro ({line})",
            tag="Multi-Transport (E-Rickshaw + Metro)",
            tag_reason=f"Economical multi-transport: ₹{int(fm_fare)} shared E-Rickshaw feeder from colony stand to {orig_hub['name']} Metro Station, then rapid rail.",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=total_fare,
            fare_breakdown=" + ".join(fare_parts),
            route_type="metro_multimodal",
            transfers_count=2,
            walking_duration_minutes=2,
            walking_distance_meters=120,
            overall_crowd="Moderate",
            total_delay_minutes=delay,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.15, 1)
        )

    def _build_metro_closed_night_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, is_night: bool
    ) -> RouteItinerary:
        """Night fallback route when metro service is closed (11 PM – 6 AM).
        Suggests Auto or Cab as the best late-night alternative."""

        # Build a direct auto route as the night alternative
        auto_fare, fare_desc = calculate_auto_fare(dist_km, is_night=is_night)
        auto_duration = max(10, int((dist_km / 26.0) * 60))
        arr_time = base_time + timedelta(minutes=auto_duration)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        legs = [
            TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="walk",
                origin_name=orig["name"],
                destination_name=f"{orig['name']} Auto Stand",
                origin_coords=[orig["lon"], orig["lat"]],
                destination_coords=[round(orig["lon"] + 0.0004, 5), round(orig["lat"] + 0.0003, 5)],
                path_coords=[[orig["lon"], orig["lat"]], [round(orig["lon"] + 0.0004, 5), round(orig["lat"] + 0.0003, 5)]],
                duration_minutes=1,
                distance_meters=60,
                departure_time=base_time.strftime("%H:%M"),
                arrival_time=(base_time + timedelta(minutes=1)).strftime("%H:%M"),
                instructions="Walk to nearest auto/cab stand.",
                crowd_level="Low"
            ),
            TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="auto",
                line_name="Night Auto / Cab (Metro Closed)",
                line_color="#E68A00",
                origin_name=orig["name"],
                destination_name=dest["name"],
                origin_coords=start_pt,
                destination_coords=end_pt,
                path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
                duration_minutes=auto_duration,
                distance_meters=int(dist_km * 1050),
                departure_time=(base_time + timedelta(minutes=1)).strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=0,
                intermediate_stops=[],
                instructions="Metro service closed. Take a metered auto or book a cab. Night surcharge (25%) applies for autos between 11 PM – 5 AM.",
                crowd_level="Low",
                fare_inr=auto_fare,
                fare_details=fare_desc
            )
        ]

        # Calculate first metro availability
        if base_time.hour >= 23:
            next_metro_str = "6:00 AM tomorrow"
        else:
            next_metro_str = "6:00 AM"

        return RouteItinerary(
            id=f"route-night-{uuid.uuid4().hex[:6]}",
            title="Night Auto (Metro Closed)",
            tag="Metro Closed",
            tag_reason=f"🚇 Delhi Metro is closed (11 PM – 6 AM). Next service at {next_metro_str}. Auto/Cab available 24/7.",
            total_duration_minutes=auto_duration + 1,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            total_fare_inr=auto_fare,
            fare_breakdown=fare_desc,
            route_type="night_fallback",
            transfers_count=0,
            walking_duration_minutes=1,
            walking_distance_meters=60,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.05, 1),
            service_available=False,
            unavailable_reason=get_closed_message("dmrc_metro")
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
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
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
        # Average road speed in Delhi: 26 km/h
        auto_duration = max(5, int((dist_km / 26.0) * 60))
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
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
            duration_minutes=auto_duration,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=0,
            intermediate_stops=[],
            instructions=f"Direct doorstep ride ({dist_km:.1f} km). Pay strictly by GNCTD Gazetted meter (₹30 base + ₹11/km). Night charge 25% (11PM-5AM).",
            crowd_level="Low",
            fare_inr=auto_fare,
            fare_details=fare_desc
        ))

        total_mins = auto_duration + walk1_duration
        is_short = dist_km <= 6.5
        tag = "Short Distance Recommended" if is_short else "Govt Metered Auto"
        tag_reason = (
            f"⚡ Best for short trips ({dist_km:.1f} km): Direct doorstep ride, zero station stairs/queues. Regulated GNCTD Gazetted Meter: ₹30 first 1.5km + ₹11/km (ARU Notification 09.01.2023)."
            if is_short else
            f"Direct point-to-point ride ({dist_km:.1f} km). Regulated Delhi Govt meter (₹30 base + ₹11/km)."
        )

        return RouteItinerary(
            id=f"route-auto-{uuid.uuid4().hex[:6]}",
            title=f"Delhi Govt Metered Auto (TSR) — {dist_km:.1f} km",
            tag=tag,
            tag_reason=tag_reason,
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=auto_fare,
            fare_breakdown=fare_desc,
            route_type="auto_rickshaw",
            transfers_count=0,
            walking_duration_minutes=walk1_duration,
            walking_distance_meters=50,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.05, 1)
        )

    def _build_delhi_erickshaw_short_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime
    ) -> RouteItinerary:
        """Shared E-Rickshaw hopper for hyper-local trips / metro last-mile in Delhi."""
        fare, desc = calculate_erickshaw_fare(dist_km)
        erick_duration = max(5, int(dist_km * 3.5))
        arr_time = base_time + timedelta(minutes=erick_duration)

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        legs = [
            TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="erickshaw",
                line_name="Shared E-Rickshaw Feeder",
                line_color="#00897B",
                origin_name=orig["name"],
                destination_name=dest["name"],
                origin_coords=start_pt,
                destination_coords=end_pt,
                path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
                duration_minutes=erick_duration,
                distance_meters=int(dist_km * 1050),
                departure_time=base_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[f"{orig['name']} Stand", dest["name"]],
                instructions=f"Hop on shared electric E-Rickshaw ({dist_km:.1f} km). Direct local hop.",
                crowd_level="Low",
                fare_inr=fare,
                fare_details=desc
            )
        ]

        return RouteItinerary(
            id=f"route-delhi-erick-{uuid.uuid4().hex[:6]}",
            title=f"Shared E-Rickshaw Feeder — {dist_km:.1f} km",
            tag="Local E-Rickshaw Hop",
            tag_reason=f"⚡ Hyper-local short hop ({dist_km:.1f} km). Flat ₹10-₹15 fare, ideal for colony & market trips.",
            total_duration_minutes=erick_duration,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            total_fare_inr=fare,
            fare_breakdown=desc,
            route_type="erickshaw",
            transfers_count=0,
            walking_duration_minutes=0,
            walking_distance_meters=0,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.12, 1)
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
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
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
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
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

    # ==============================================================================
    # Mathura & Vrindavan Specialized Local Transit Routing Engine
    # ==============================================================================

    def _plan_mathura_journey(
        self,
        origin_dict: Dict,
        dest_dict: Dict,
        origin_loc: GeoLocation,
        dest_loc: GeoLocation,
        dist_km: float,
        base_time: datetime,
        request: PlanRequest,
        simulated_delays: Dict[str, int]
    ) -> PlanResponse:
        """
        Specialized transit routing engine for Mathura & Vrindavan (Braj Dham).
        NO Metro — zero metro references.
        High-frequency Shared E-Rickshaws (Toto), Shared CNG Tempos,
        and Mathura-Vrindavan Electric Nagar Seva Bus (UP Urban Transport).
        """
        routes: List[RouteItinerary] = []
        is_night = base_time.hour >= 22 or base_time.hour < 5

        ebus_available = is_transit_operational("mathura_ebus", base_time.hour, base_time.minute)
        tempo_available = is_transit_operational("mathura_shared_tempo", base_time.hour, base_time.minute)
        erickshaw_available = is_transit_operational("mathura_erickshaw", base_time.hour, base_time.minute)

        # 1. OPTION 1: SHARED E-RICKSHAW / MULTIMODAL TEMPO (MOST POPULAR)
        r1 = self._build_mathura_shared_popular_route(origin_dict, dest_dict, dist_km, base_time, erickshaw_available, tempo_available)
        routes.append(r1)

        # 1B. MULTI-TRANSPORT FEEDER (HOME E-RICKSHAW + TEMPO + TOTO)
        if dist_km >= 3.5:
            r_multi = self._build_mathura_multimodal_feeder_route(origin_dict, dest_dict, dist_km, base_time, erickshaw_available, tempo_available)
            routes.append(r_multi)

        # 2. OPTION 2: MATHURA-VRINDAVAN ELECTRIC NAGAR SEVA BUS (UP URBAN TRANSPORT)
        r2 = self._build_mathura_ebus_route(origin_dict, dest_dict, dist_km, base_time, ebus_available)
        routes.append(r2)

        # 3. OPTION 3: DIRECT RESERVED AUTO (FULL BOOKING)
        r3 = self._build_mathura_reserved_auto_route(origin_dict, dest_dict, dist_km, base_time, is_night)
        routes.append(r3)

        # 4. OPTION 4: SHARED TEMPO / VIKRAM EXPRESS (DIRECT ARTERIAL)
        r4 = self._build_mathura_shared_tempo_route(origin_dict, dest_dict, dist_km, base_time, tempo_available)
        routes.append(r4)

        # 5. OPTION 5: PRIVATE TOURIST TAXI (LIMITED CAB AVAILABILITY)
        r5 = self._build_mathura_taxi_route(origin_dict, dest_dict, dist_km, base_time)
        routes.append(r5)

        # Sort according to user preference
        def _avail_key(r):
            return 0 if r.service_available else 1

        if request.preferences.cheapest:
            routes.sort(key=lambda r: (_avail_key(r), r.total_fare_inr, r.total_duration_minutes))
        elif request.preferences.prefer_ebus:
            routes.sort(key=lambda r: (_avail_key(r), 0 if "Electric" in r.tag else 1, r.total_duration_minutes))
        elif request.preferences.fewer_transfers:
            routes.sort(key=lambda r: (_avail_key(r), r.transfers_count, r.total_duration_minutes))
        else:
            routes.sort(key=lambda r: (_avail_key(r), r.total_duration_minutes, r.total_fare_inr))

        active_disruptions = sum(1 for d in simulated_delays.values() if d > 0)
        return PlanResponse(
            origin=origin_loc,
            destination=dest_loc,
            generated_at=datetime.now().isoformat(),
            routes=routes,
            active_disruptions_count=active_disruptions
        )

    def _build_mathura_shared_popular_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, erickshaw_avail: bool, tempo_avail: bool
    ) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        if dist_km <= 4.5:
            fare, desc = calculate_mathura_erickshaw_fare(dist_km)
            erickshaw_mins = max(7, int(dist_km * 3.4))
            arr_time = curr_time + timedelta(minutes=erickshaw_mins)

            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="erickshaw",
                line_name="Shared E-Rickshaw Feeder (Toto)",
                line_color="#00897B",
                origin_name=orig["name"],
                destination_name=dest["name"],
                origin_coords=start_pt,
                destination_coords=end_pt,
                path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
                duration_minutes=erickshaw_mins,
                distance_meters=int(dist_km * 1050),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[f"{orig['name']} Stand", f"{dest['name']} Gate"],
                instructions="Board shared battery E-Rickshaw (Toto). High frequency, departs every 1-2 mins, doorstep drop.",
                crowd_level="Low",
                fare_inr=fare,
                fare_details=desc
            ))
            total_mins = erickshaw_mins
            total_fare = fare
            title = "Shared E-Rickshaw (Toto)"
            tag_reason = "⚡ Mathura-Vrindavan Lifeline: Direct battery E-Rickshaw, departs every 1-2 mins, zero wait."
            transfers = 0
            walk_mins = 0
            walk_dist = 0
        else:
            walk1_mins = 2
            arr_time = curr_time + timedelta(minutes=walk1_mins)
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="walk",
                origin_name=orig["name"],
                destination_name=f"{orig['name']} Auto / Tempo Stand",
                origin_coords=start_pt,
                destination_coords=[round(start_pt[0] + 0.0006, 5), round(start_pt[1] + 0.0005, 5)],
                path_coords=[start_pt, [round(start_pt[0] + 0.0006, 5), round(start_pt[1] + 0.0005, 5)]],
                duration_minutes=walk1_mins,
                distance_meters=100,
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                instructions="Walk to shared tempo / Vikram stand outside main gate.",
                crowd_level="Low"
            ))
            curr_time = arr_time

            tempo_dist = dist_km - 1.2
            tempo_mins = max(18, int(tempo_dist * 2.1))
            tempo_fare, tempo_desc = calculate_mathura_shared_tempo_fare(tempo_dist)
            arr_time = curr_time + timedelta(minutes=tempo_mins)

            mid_pt = [round(dest["lon"] - 0.003, 5), round(dest["lat"] - 0.003, 5)]
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="auto",
                line_name="Shared Tempo / Vikram (Braj Corridor)",
                line_color="#E68A00",
                origin_name=f"{orig['name']} Stand",
                destination_name=f"{dest['name']} Chauraha Stand",
                origin_coords=start_pt,
                destination_coords=mid_pt,
                path_coords=get_road_geometry(start_pt, mid_pt, mode="driving"),
                duration_minutes=tempo_mins,
                distance_meters=int(tempo_dist * 1050),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=4,
                intermediate_stops=["Highway Corridor", "Birla Mandir Marg", "Pagal Baba Stand", "Attalla Chungi"],
                instructions="Board shared CNG Tempo/Vikram. Fixed corridor fare, departs when filled.",
                crowd_level="Moderate",
                fare_inr=tempo_fare,
                fare_details=tempo_desc
            ))
            curr_time = arr_time

            erick_mins = 6
            erick_fare, erick_desc = 10.0, "Shared E-Rickshaw: ₹10 (Temple Doorstep Feeder)"
            arr_time = curr_time + timedelta(minutes=erick_mins)
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="erickshaw",
                line_name="Shared E-Rickshaw Feeder (Toto)",
                line_color="#00897B",
                origin_name=f"{dest['name']} Chauraha Stand",
                destination_name=dest["name"],
                origin_coords=mid_pt,
                destination_coords=end_pt,
                path_coords=get_road_geometry(mid_pt, end_pt, mode="driving"),
                duration_minutes=erick_mins,
                distance_meters=1200,
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=arr_time.strftime("%H:%M"),
                stops_count=1,
                intermediate_stops=[dest["name"]],
                instructions="Hop onto shared battery E-Rickshaw through Kunj Gali directly to temple gate.",
                crowd_level="Low",
                fare_inr=erick_fare,
                fare_details=erick_desc
            ))

            total_mins = walk1_mins + tempo_mins + erick_mins
            total_fare = tempo_fare + erick_fare
            title = "Shared Tempo + Local E-Rickshaw"
            tag_reason = "⚡ The #1 local choice: Fast shared tempo along corridor + direct E-rickshaw to temple doorstep."
            transfers = 1
            walk_mins = walk1_mins
            walk_dist = 100

        avail = erickshaw_avail if dist_km <= 4.5 else (tempo_avail and erickshaw_avail)
        unavail_reason = None if avail else "Night service reduced (10:30 PM – 5 AM). Use 24/7 Station Reserved Auto."

        return RouteItinerary(
            id=f"route-mathura-pop-{uuid.uuid4().hex[:6]}",
            title=title,
            tag="Most Popular",
            tag_reason=tag_reason,
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=total_fare,
            fare_breakdown=f"Total: ₹{int(total_fare)} (Local Shared Fare)",
            route_type="mathura_shared",
            transfers_count=transfers,
            walking_duration_minutes=walk_mins,
            walking_distance_meters=walk_dist,
            overall_crowd="Moderate",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.16, 1),
            service_available=avail,
            unavailable_reason=unavail_reason
        )

    def _build_mathura_ebus_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, ebus_avail: bool
    ) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_mins = 4
        arr_time = curr_time + timedelta(minutes=walk1_mins)
        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        bus_stop_start = [round(start_pt[0] + 0.0010, 5), round(start_pt[1] + 0.0008, 5)]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Electric Bus Shelter",
            origin_coords=start_pt,
            destination_coords=bus_stop_start,
            path_coords=[start_pt, bus_stop_start],
            duration_minutes=walk1_mins,
            distance_meters=260,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to nearest roadside Electric Bus Shelter on main highway/marg.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        ebus_mins = max(20, int(dist_km * 2.3))
        ebus_fare, fare_desc = calculate_mathura_ebus_fare(dist_km)
        arr_time = curr_time + timedelta(minutes=ebus_mins)

        bus_stop_end = [round(end_pt[0] - 0.0010, 5), round(end_pt[1] - 0.0008, 5)]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="ebus",
            line_name="Mathura-Vrindavan Electric Nagar Seva Bus",
            line_color="#00A86B",
            origin_name=f"{orig['name']} Bus Shelter",
            destination_name=f"{dest['name']} Bus Shelter",
            origin_coords=bus_stop_start,
            destination_coords=bus_stop_end,
            path_coords=get_road_geometry(bus_stop_start, bus_stop_end, mode="driving"),
            duration_minutes=ebus_mins,
            distance_meters=int(dist_km * 1100),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=6,
            intermediate_stops=["Mathura Jn Stand", "New Bus Stand Masani", "Birla Mandir", "Pagal Baba", "Prem Mandir Stand", "Chatikara Morh"],
            instructions="Board Directorate of Urban Transport UP AC Electric Bus. 100% Zero-Emission Braj Heritage Fleet.",
            crowd_level="Low",
            fare_inr=ebus_fare,
            fare_details=fare_desc
        ))
        curr_time = arr_time

        walk2_mins = 4
        arr_time = curr_time + timedelta(minutes=walk2_mins)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=f"{dest['name']} Bus Shelter",
            destination_name=dest["name"],
            origin_coords=bus_stop_end,
            destination_coords=end_pt,
            path_coords=[bus_stop_end, end_pt],
            duration_minutes=walk2_mins,
            distance_meters=240,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk from bus shelter to destination entrance.",
            crowd_level="Low"
        ))

        total_mins = walk1_mins + ebus_mins + walk2_mins
        return RouteItinerary(
            id=f"route-mathura-ebus-{uuid.uuid4().hex[:6]}",
            title="Electric Nagar Seva Bus (UP Urban Transport)",
            tag="Green Electric Bus",
            tag_reason="🌱 Official UP Urban AC Electric Bus. 100% Zero-Emission, clean & lowest fare across Braj corridor.",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=ebus_fare,
            fare_breakdown=fare_desc,
            route_type="mathura_ebus",
            transfers_count=0,
            walking_duration_minutes=walk1_mins + walk2_mins,
            walking_distance_meters=500,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.20, 1),
            service_available=ebus_avail,
            unavailable_reason=None if ebus_avail else get_closed_message("mathura_ebus")
        )

    def _build_mathura_reserved_auto_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, is_night: bool
    ) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_mins = 1
        arr_time = curr_time + timedelta(minutes=walk1_mins)
        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Auto Stand",
            origin_coords=start_pt,
            destination_coords=[round(start_pt[0] + 0.0003, 5), round(start_pt[1] + 0.0003, 5)],
            path_coords=[start_pt, [round(start_pt[0] + 0.0003, 5), round(start_pt[1] + 0.0003, 5)]],
            duration_minutes=walk1_mins,
            distance_meters=50,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to station/roadside private auto stand.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        auto_mins = max(10, int(dist_km * 1.9))
        auto_fare, fare_desc = calculate_mathura_reserved_auto_fare(dist_km, is_night=is_night)
        arr_time = curr_time + timedelta(minutes=auto_mins)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="auto",
            line_name="Reserved Auto-Rickshaw (निजी ऑटो)",
            line_color="#D97706",
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
            duration_minutes=auto_mins,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=0,
            intermediate_stops=[],
            instructions="Direct point-to-point private auto hire. Standard local negotiated rate or prepaid stand counter.",
            crowd_level="Low",
            fare_inr=auto_fare,
            fare_details=fare_desc
        ))

        total_mins = walk1_mins + auto_mins
        return RouteItinerary(
            id=f"route-mathura-auto-{uuid.uuid4().hex[:6]}",
            title="Direct Reserved Auto (निजी ऑटो)",
            tag="Direct Reserved Auto",
            tag_reason="🛺 Dedicated three-wheeler for families & luggage. Direct point-to-point without sharing.",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=auto_fare,
            fare_breakdown=fare_desc,
            route_type="mathura_auto",
            transfers_count=0,
            walking_duration_minutes=walk1_mins,
            walking_distance_meters=50,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.05, 1),
            service_available=True
        )

    def _build_mathura_shared_tempo_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, tempo_avail: bool
    ) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        walk1_mins = 3
        arr_time = curr_time + timedelta(minutes=walk1_mins)
        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        stand_pt = [round(start_pt[0] + 0.0008, 5), round(start_pt[1] + 0.0006, 5)]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Shared Tempo Stand",
            origin_coords=start_pt,
            destination_coords=stand_pt,
            path_coords=[start_pt, stand_pt],
            duration_minutes=walk1_mins,
            distance_meters=180,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Walk to main roadside shared Tempo/Vikram stand.",
            crowd_level="Low"
        ))
        curr_time = arr_time

        tempo_mins = max(14, int(dist_km * 2.1))
        tempo_fare, fare_desc = calculate_mathura_shared_tempo_fare(dist_km)
        arr_time = curr_time + timedelta(minutes=tempo_mins)

        dest_stand_pt = [round(end_pt[0] - 0.0008, 5), round(end_pt[1] - 0.0006, 5)]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="auto",
            line_name="Shared Tempo / Vikram (Braj Corridor)",
            line_color="#E68A00",
            origin_name=f"{orig['name']} Stand",
            destination_name=f"{dest['name']} Drop Point",
            origin_coords=stand_pt,
            destination_coords=dest_stand_pt,
            path_coords=get_road_geometry(stand_pt, dest_stand_pt, mode="driving"),
            duration_minutes=tempo_mins,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=3,
            intermediate_stops=["Corridor Hub", "Highway Crossing", "Attalla Chungi"],
            instructions="Direct shared Vikram/Tempo along highway/main road. Departs on full seating.",
            crowd_level="Moderate",
            fare_inr=tempo_fare,
            fare_details=fare_desc
        ))
        curr_time = arr_time

        walk2_mins = 3
        arr_time = curr_time + timedelta(minutes=walk2_mins)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            origin_name=f"{dest['name']} Drop Point",
            destination_name=dest["name"],
            origin_coords=dest_stand_pt,
            destination_coords=end_pt,
            path_coords=[dest_stand_pt, end_pt],
            duration_minutes=walk2_mins,
            distance_meters=180,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            instructions="Short walk to destination.",
            crowd_level="Low"
        ))

        total_mins = walk1_mins + tempo_mins + walk2_mins
        return RouteItinerary(
            id=f"route-mathura-tempo-{uuid.uuid4().hex[:6]}",
            title="Shared Tempo / Vikram (Direct)",
            tag="Lowest Fare",
            tag_reason="💰 Direct arterial shared tempo along Mathura-Vrindavan Marg / Govardhan Road. Flat ₹15 - ₹45/seat.",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=tempo_fare,
            fare_breakdown=fare_desc,
            route_type="mathura_tempo",
            transfers_count=0,
            walking_duration_minutes=walk1_mins + walk2_mins,
            walking_distance_meters=360,
            overall_crowd="Moderate",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.12, 1),
            service_available=tempo_avail,
            unavailable_reason=None if tempo_avail else get_closed_message("mathura_shared_tempo")
        )

    def _build_mathura_taxi_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime
    ) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        cab_mins = max(12, int(dist_km * 1.8))
        cab_fare, fare_desc = calculate_mathura_taxi_fare(dist_km)
        arr_time = curr_time + timedelta(minutes=cab_mins)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="taxi",
            line_name="Private Tourist Taxi (मथुरा टूरिस्ट टैक्सी)",
            line_color="#475569",
            origin_name=orig["name"],
            destination_name=dest["name"],
            origin_coords=start_pt,
            destination_coords=end_pt,
            path_coords=get_road_geometry(start_pt, end_pt, mode="driving"),
            duration_minutes=cab_mins,
            distance_meters=int(dist_km * 1050),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            stops_count=0,
            intermediate_stops=[],
            instructions="Private tourist agency cab. Note: On-demand app cabs (Ola/Uber) have very limited coverage in Mathura.",
            crowd_level="Low",
            fare_inr=cab_fare,
            fare_details=fare_desc
        ))

        return RouteItinerary(
            id=f"route-mathura-taxi-{uuid.uuid4().hex[:6]}",
            title="Private Tourist Taxi (Agency Cab)",
            tag="Private Taxi (Limited)",
            tag_reason="⚠️ On-demand app cabs (Ola/Uber) are scarce in Mathura. Private agency tourist cars are available.",
            total_duration_minutes=cab_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=arr_time.strftime("%H:%M"),
            total_fare_inr=cab_fare,
            fare_breakdown=fare_desc,
            route_type="mathura_taxi",
            transfers_count=0,
            walking_duration_minutes=0,
            walking_distance_meters=0,
            overall_crowd="Low",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.04, 1),
            service_available=True
        )

    def _build_mathura_multimodal_feeder_route(
        self, orig: Dict, dest: Dict, dist_km: float, base_time: datetime, erick_avail: bool, tempo_avail: bool
    ) -> RouteItinerary:
        """Door-to-door Braj transit: Home E-Rickshaw to Tempo Stand + Shared Tempo + Mandir Toto."""
        legs: List[TransitLeg] = []
        curr_time = base_time

        start_pt = [orig["lon"], orig["lat"]]
        end_pt = [dest["lon"], dest["lat"]]

        # Leg 1: E-Rickshaw from home to Highway Tempo Stand
        fm_dur = 6
        fm_fare = 10.0
        arr1 = curr_time + timedelta(minutes=fm_dur)
        tempo_stand_pt = [round(start_pt[0] + 0.008, 5), round(start_pt[1] + 0.008, 5)]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="erickshaw",
            line_name="Doorstep E-Rickshaw (Toto)",
            line_color="#00897B",
            origin_name=orig["name"],
            destination_name=f"{orig['name']} Highway Tempo Stand",
            origin_coords=start_pt,
            destination_coords=tempo_stand_pt,
            path_coords=get_road_geometry(start_pt, tempo_stand_pt, mode="driving"),
            duration_minutes=fm_dur,
            distance_meters=1400,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr1.strftime("%H:%M"),
            stops_count=1,
            intermediate_stops=[f"{orig['name']} Colony Stand", f"{orig['name']} Highway Stand"],
            instructions=f"Take doorstep E-Rickshaw (Toto) from your colony to Highway Tempo Stand. Flat ₹10.",
            crowd_level="Low",
            fare_inr=fm_fare,
            fare_details="Braj Local Toto Flat ₹10 Feeder"
        ))
        curr_time = arr1

        # Leg 2: Shared Tempo / Vikram (Highway Arterial)
        tempo_dist = max(3.0, dist_km - 2.5)
        tempo_dur = max(16, int(tempo_dist * 2.1))
        tempo_fare, tempo_desc = calculate_mathura_shared_tempo_fare(tempo_dist)
        arr2 = curr_time + timedelta(minutes=tempo_dur)
        chungi_pt = [round(end_pt[0] - 0.006, 5), round(end_pt[1] - 0.006, 5)]
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="auto",
            line_name="Shared Tempo / Vikram Express",
            line_color="#E68A00",
            origin_name=f"{orig['name']} Highway Stand",
            destination_name=f"{dest['name']} Chungi Gate",
            origin_coords=tempo_stand_pt,
            destination_coords=chungi_pt,
            path_coords=get_road_geometry(tempo_stand_pt, chungi_pt, mode="driving"),
            duration_minutes=tempo_dur,
            distance_meters=int(tempo_dist * 1000),
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr2.strftime("%H:%M"),
            stops_count=3,
            intermediate_stops=["Mandi Chauraha", "Chatikara Road", f"{dest['name']} Chungi"],
            instructions="Board high-frequency Shared Tempo / Vikram along the arterial road. Fixed corridor fare.",
            crowd_level="Moderate",
            fare_inr=tempo_fare,
            fare_details=tempo_desc
        ))
        curr_time = arr2

        # Leg 3: Temple Zone Battery Toto
        lm_dur = 5
        lm_fare = 10.0
        arr3 = curr_time + timedelta(minutes=lm_dur)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="erickshaw",
            line_name="Temple Zone Battery Toto",
            line_color="#00897B",
            origin_name=f"{dest['name']} Chungi Gate",
            destination_name=dest["name"],
            origin_coords=chungi_pt,
            destination_coords=end_pt,
            path_coords=get_road_geometry(chungi_pt, end_pt, mode="driving"),
            duration_minutes=lm_dur,
            distance_meters=1100,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=arr3.strftime("%H:%M"),
            stops_count=1,
            intermediate_stops=[f"{dest['name']} Chungi", dest["name"]],
            instructions=f"Take direct battery Toto into the pedestrian temple zone directly to {dest['name']} entrance.",
            crowd_level="Low",
            fare_inr=lm_fare,
            fare_details="Temple Zone Battery Toto Flat ₹10"
        ))

        total_fare = fm_fare + tempo_fare + lm_fare
        total_mins = fm_dur + tempo_dur + lm_dur
        return RouteItinerary(
            id=f"route-mathura-multi-{uuid.uuid4().hex[:6]}",
            title="Multi-Transport: Home E-Rickshaw ➔ Highway Tempo ➔ Mandir Toto",
            tag="Multi-Transport (Braj Feeder)",
            tag_reason="Complete door-to-door Braj transit: E-Rickshaw from home to Highway Tempo stand, fast shared corridor, and direct temple entrance drop.",
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=total_fare,
            fare_breakdown=f"Toto (₹{int(fm_fare)}) + Tempo (₹{int(tempo_fare)}) + Toto (₹{int(lm_fare)})",
            route_type="bus_ebus",
            transfers_count=2,
            walking_duration_minutes=1,
            walking_distance_meters=80,
            overall_crowd="Moderate",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.12, 1)
        )

router_instance = TransitRouter()
