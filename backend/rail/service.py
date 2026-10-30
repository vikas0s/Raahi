"""
High-level RailConnect Service for Raahi.
Handles station resolution, caching, provider abstraction,
and seamless conversion of train schedules into multi-modal RouteItineraries.
Fully city-aware across Mumbai, Bengaluru, Delhi NCR, and Mathura & Vrindavan.
"""
import uuid
import math
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from .schemas import (
    RailStation, TrainSummary, TrainSchedule, LiveRunningStatus,
    StationBoardItem, StationBoardResponse
)
from .provider_interface import RailProviderInterface
from .providers.railradar import RailRadarProvider
from .providers.fallback_data import (
    RAIL_STATIONS, SCHEDULE_DATABASE, get_all_stations, find_station_by_query,
    get_fallback_trains_between, get_fallback_live_status, get_fallback_station_board
)
from ..models import RouteItinerary, TransitLeg


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _normalize_city(city_str: Optional[str]) -> Optional[str]:
    if not city_str:
        return None
    c = city_str.lower().strip()
    if "mumbai" in c or "bombay" in c:
        return "Mumbai"
    if "bengaluru" in c or "bangalore" in c:
        return "Bengaluru"
    if "mathura" in c or "vrindavan" in c or "braj" in c:
        return "Mathura & Vrindavan"
    if "delhi" in c or "ncr" in c or "noida" in c or "gurugram" in c or "gurgaon" in c or "ghaziabad" in c or "faridabad" in c:
        return "Delhi NCR"
    return city_str


class RailConnectService:
    def __init__(self, provider: Optional[RailProviderInterface] = None):
        self.provider: RailProviderInterface = provider or RailRadarProvider()
        self._stations_cache: Dict[str, RailStation] = dict(RAIL_STATIONS)

    async def search_stations(self, query: str, city: Optional[str] = None) -> List[RailStation]:
        """Search stations across provider and directory with strict city awareness."""
        norm_city = _normalize_city(city)
        if not query or len(query.strip()) < 2:
            if norm_city:
                return [s for s in self._stations_cache.values() if s.city == norm_city]
            return list(self._stations_cache.values())
        return await self.provider.search_stations(query, city=norm_city)

    def get_station_by_code(self, code: str) -> Optional[RailStation]:
        return self._stations_cache.get(code.upper().strip())

    def find_nearest_rail_station(
        self, lat: float, lon: float, max_dist_km: float = 30.0, city: Optional[str] = None
    ) -> Optional[Tuple[RailStation, float]]:
        """Find nearest railway station scoped to the requested city."""
        norm_city = _normalize_city(city)
        best_station: Optional[RailStation] = None
        min_dist = float("inf")
        for s in self._stations_cache.values():
            if norm_city and s.city != norm_city:
                continue
            d = haversine_km(lat, lon, s.lat, s.lon)
            if d < min_dist:
                min_dist = d
                best_station = s
        if best_station and min_dist <= max_dist_km:
            return best_station, round(min_dist, 2)
        return None

    def resolve_station_from_place(
        self, place_dict: Dict[str, Any], city: Optional[str] = None
    ) -> Optional[RailStation]:
        """Resolve a RailStation object from a place in PLACES_DATABASE, strictly within the city."""
        name = place_dict.get("name", "").strip()
        name_lower = name.lower()
        norm_city = _normalize_city(city or place_dict.get("city"))

        # 1. Check direct station code in brackets or exact code match
        for code, s in self._stations_cache.items():
            if norm_city and s.city != norm_city:
                continue
            if f"({code})" in name or f"[{code}]" in name or code.lower() == name_lower:
                return s

        # 2. Check station name or aliases (scoped to city)
        for s in self._stations_cache.values():
            if norm_city and s.city != norm_city:
                continue
            if s.name.lower() in name_lower or name_lower in s.name.lower():
                return s
            for alias in s.aliases:
                if alias.lower() in name_lower or name_lower in alias.lower():
                    return s

        # 3. Check nearest rail station if within 4.5 km within the same city
        lat = place_dict.get("lat")
        lon = place_dict.get("lon")
        if lat is not None and lon is not None:
            res = self.find_nearest_rail_station(lat, lon, max_dist_km=4.5, city=norm_city)
            if res:
                return res[0]

        return None

    async def get_trains_between(
        self, from_code: str, to_code: str, date: Optional[str] = None
    ) -> List[TrainSummary]:
        return await self.provider.get_trains_between(from_code, to_code, date)

    async def get_train_schedule(self, train_no: str) -> Optional[TrainSchedule]:
        return await self.provider.get_train_schedule(train_no)

    async def get_live_running_status(self, train_no: str, date: Optional[str] = None) -> Optional[LiveRunningStatus]:
        return await self.provider.get_live_running_status(train_no, date)

    async def get_station_board(self, station_code: str, hours: int = 4) -> StationBoardResponse:
        code = station_code.upper().strip()
        station = self._stations_cache.get(code)
        if not station:
            station = RailStation(
                code=code,
                name=f"{code} Railway Station",
                city="Indian Railways",
                lat=28.6139,
                lon=77.2090
            )
        departures = await self.provider.get_station_board(code, hours)
        return StationBoardResponse(
            station=station,
            departures=departures,
            generated_at=datetime.now().isoformat()
        )

    def _get_intermediate_stops(self, train: TrainSummary, orig_code: str, dest_code: str) -> List[str]:
        """Extract intermediate station stops between orig and dest."""
        for sch in SCHEDULE_DATABASE.values():
            if sch.train_number == train.train_number:
                codes = [h.station_code for h in sch.halts]
                names = [h.station_name for h in sch.halts]
                if orig_code in codes and dest_code in codes:
                    idx1 = codes.index(orig_code)
                    idx2 = codes.index(dest_code)
                    start_i, end_i = min(idx1, idx2), max(idx1, idx2)
                    sub = names[start_i + 1:end_i]
                    if sub:
                        return sub
        return [f"{train.halts_count} intermediate station halts"] if train.halts_count > 0 else ["Direct Non-Stop Service"]

    def _get_suburban_branding(
        self, train: TrainSummary, orig_station: RailStation, dest_station: RailStation
    ) -> Tuple[str, str, str]:
        """Returns (tag, tag_reason, line_color) tailored to the specific suburban corridor."""
        orig_c = orig_station.code
        dest_c = dest_station.code
        c_set = {orig_c, dest_c}

        # Mumbai Suburban Railway
        if orig_station.city == "Mumbai" or dest_station.city == "Mumbai":
            wr_codes = {"CCG", "MEL", "CYR", "GTR", "BCL", "MX", "PL", "EPR", "DDR", "BA", "KHAR", "STC", "VLP", "ADH", "JOS", "RMAR", "GMN", "MDD", "KILE", "BVI", "DIC", "BYR", "NIG", "BSR", "NSP", "VR", "DR"}
            cr_codes = {"CSMT", "MSD", "SNRD", "BY", "CHG", "CRD", "PR", "DR", "MTN", "SIN", "CLA", "VVH", "GC", "VK", "KJRD", "BND", "NHU", "MLND", "TNA", "KLVA", "MBQ", "DIVA", "KOPR", "DI", "THK", "KYN"}
            hb_codes = {"DKRD", "RRD", "CTGN", "SVE", "VDLR", "GTBN", "CHF", "TKNG", "MNKD", "GV", "VSH", "SNCR", "JNJ", "NEU", "SWDV", "BEPR", "KHAG", "MANR", "KNDS", "PNVL"}

            if c_set.issubset(wr_codes) or "western" in train.train_name.lower():
                is_fast = "fast" in train.train_name.lower()
                speed_str = "Fast EMU" if is_fast else "Slow EMU"
                return (
                    f"🚆 Mumbai Suburban Railway (Western Line {speed_str})",
                    f"WR Suburban Local ({orig_station.name} to {dest_station.name}). High frequency 3-5m headway.",
                    "#0284C7"
                )
            elif c_set.issubset(cr_codes) or "central" in train.train_name.lower():
                is_fast = "fast" in train.train_name.lower()
                speed_str = "Fast Local" if is_fast else "Slow Local"
                return (
                    f"🚆 Mumbai Suburban Railway (Central Line {speed_str})",
                    f"CR Lifeline Main Line EMU ({orig_station.name} to {dest_station.name}). Regular service.",
                    "#DC2626"
                )
            elif any(c in hb_codes for c in c_set) or "harbour" in train.train_name.lower():
                return (
                    "🚆 Mumbai Suburban Railway (Harbour Line Local)",
                    f"Harbour Suburban corridor linking {orig_station.name} and {dest_station.name} via Navi Mumbai.",
                    "#0D9488"
                )
            return (
                "🚆 Mumbai Suburban Railway (Local Train)",
                f"Suburban commuter train between {orig_station.name} and {dest_station.name}.",
                "#0284C7"
            )

        # Bengaluru SWR Commuter Rail
        if orig_station.city == "Bengaluru" or dest_station.city == "Bengaluru":
            return (
                f"🚆 SWR Commuter Rail ({train.train_name})",
                f"South Western Railway Suburban MEMU/DEMU ({orig_station.name} to {dest_station.name}). Bypasses Outer Ring Road traffic at flat ₹{int(train.fares.get('UR', 10))}.",
                "#7C3AED"
            )

        # Delhi NCR Suburban & Ring Railway
        if orig_station.city == "Delhi NCR" or dest_station.city == "Delhi NCR":
            ring_codes = {"SOJ", "LPN", "SWNR", "BRSQ", "DSJ", "KIPN", "NRVR", "PTNR", "DLPC"}
            if any(c in ring_codes for c in c_set) or "ring" in train.train_name.lower():
                return (
                    "🚆 Delhi Ring Railway (Suburban EMU)",
                    f"Northern Railway 35-km circular Ring Railway suburban EMU connecting {orig_station.name} and {dest_station.name}.",
                    "#16A34A"
                )
            return (
                "🚆 Delhi Suburban EMU Local",
                f"Northern Railway Suburban EMU ({orig_station.name} to {dest_station.name}). Fast unreserved commute at ₹{int(train.fares.get('UR', 10))}.",
                "#8B1E1E"
            )

        # Mathura & Vrindavan
        if orig_station.city == "Mathura & Vrindavan" or dest_station.city == "Mathura & Vrindavan":
            if "rail bus" in train.train_name.lower() or c_set == {"MTJ", "BDB"}:
                return (
                    "🚆 Mathura - Vrindavan Rail Bus (#04419 / #04420)",
                    "Dedicated heritage commuter rail bus connecting Mathura Junction directly to Vrindavan at just ₹10 flat.",
                    "#059669"
                )
            return (
                "🚆 Mathura Local Commuter Shuttle",
                f"Frequent passenger commuter shuttle connecting {orig_station.name} and {dest_station.name} at ₹{int(train.fares.get('UR', 10))}.",
                "#B45309"
            )

        return (
            f"🚆 {train.train_type} Train ({train.train_number})",
            f"Direct Indian Railways connection. Unreserved General Fare ₹{int(train.fares.get('UR', 30))}.",
            "#8B1E1E"
        )

    def find_rail_routes_sync(
        self,
        orig_dict: Dict[str, Any],
        dest_dict: Dict[str, Any],
        base_time: datetime,
        dist_km: float,
        city: str
    ) -> List[RouteItinerary]:
        """Synchronous multi-modal railway routing engine for TransitRouter."""
        norm_city = _normalize_city(city)
        self._stations_cache.update(RAIL_STATIONS)

        orig_station = self.resolve_station_from_place(orig_dict, city=norm_city)
        dest_station = self.resolve_station_from_place(dest_dict, city=norm_city)

        orig_lat = orig_dict.get("lat", 0.0)
        orig_lon = orig_dict.get("lon", 0.0)
        dest_lat = dest_dict.get("lat", 0.0)
        dest_lon = dest_dict.get("lon", 0.0)

        if not orig_station and orig_lat and orig_lon:
            nearest = self.find_nearest_rail_station(orig_lat, orig_lon, max_dist_km=25.0, city=norm_city)
            if nearest:
                orig_station = nearest[0]

        if not dest_station and dest_lat and dest_lon:
            nearest = self.find_nearest_rail_station(dest_lat, dest_lon, max_dist_km=25.0, city=norm_city)
            if nearest:
                dest_station = nearest[0]

        if not orig_station or not dest_station or orig_station.code == dest_station.code:
            return []

        # Strict city boundary enforcement
        if norm_city and (orig_station.city != norm_city or dest_station.city != norm_city):
            return []

        # 1. Check direct trains between stations
        trains = get_fallback_trains_between(orig_station.code, dest_station.code)

        if trains:
            fm_km = haversine_km(orig_lat, orig_lon, orig_station.lat, orig_station.lon)
            lm_km = haversine_km(dest_station.lat, dest_station.lon, dest_lat, dest_lon)
            return self._build_itineraries_from_trains(
                trains=trains,
                orig_dict=orig_dict,
                dest_dict=dest_dict,
                orig_station=orig_station,
                dest_station=dest_station,
                base_time=base_time,
                dist_km=dist_km,
                fm_km=fm_km,
                lm_km=lm_km
            )

        # 2. If no direct train, check 1-interchange transfer within the SAME suburban network
        transfer_route = self._build_suburban_transfer_route(
            orig_dict=orig_dict,
            dest_dict=dest_dict,
            orig_station=orig_station,
            dest_station=dest_station,
            base_time=base_time,
            dist_km=dist_km,
            norm_city=norm_city
        )
        if transfer_route:
            return [transfer_route]

        return []

    def _build_suburban_transfer_route(
        self,
        orig_dict: Dict[str, Any],
        dest_dict: Dict[str, Any],
        orig_station: RailStation,
        dest_station: RailStation,
        base_time: datetime,
        dist_km: float,
        norm_city: Optional[str]
    ) -> Optional[RouteItinerary]:
        """Builds a 1-transfer multi-line suburban railway itinerary (e.g. Western -> Dadar -> Central)."""
        city_hubs: Dict[str, List[str]] = {
            "Mumbai": ["DDR", "CLA", "ADH", "CSMT"],
            "Delhi NCR": ["NDLS", "NZM", "DLI", "TKJ"],
            "Bengaluru": ["SBC", "YPR", "BYPL"]
        }
        hubs = city_hubs.get(norm_city or orig_station.city, [])

        for hub_code in hubs:
            if hub_code in (orig_station.code, dest_station.code):
                continue
            hub_station = self.get_station_by_code(hub_code)
            if not hub_station:
                continue

            leg1_trains = get_fallback_trains_between(orig_station.code, hub_code)
            leg2_trains = get_fallback_trains_between(hub_code, dest_station.code)

            if leg1_trains and leg2_trains:
                t1 = leg1_trains[0]
                t2 = leg2_trains[0]
                return self._assemble_transfer_itinerary(
                    orig_dict=orig_dict,
                    dest_dict=dest_dict,
                    orig_station=orig_station,
                    dest_station=dest_station,
                    hub_station=hub_station,
                    train1=t1,
                    train2=t2,
                    base_time=base_time,
                    dist_km=dist_km
                )
        return None

    def _assemble_transfer_itinerary(
        self,
        orig_dict: Dict[str, Any],
        dest_dict: Dict[str, Any],
        orig_station: RailStation,
        dest_station: RailStation,
        hub_station: RailStation,
        train1: TrainSummary,
        train2: TrainSummary,
        base_time: datetime,
        dist_km: float
    ) -> RouteItinerary:
        legs: List[TransitLeg] = []
        curr_time = base_time
        orig_lat = orig_dict.get("lat", orig_station.lat)
        orig_lon = orig_dict.get("lon", orig_station.lon)
        dest_lat = dest_dict.get("lat", dest_station.lat)
        dest_lon = dest_dict.get("lon", dest_station.lon)

        fm_km = haversine_km(orig_lat, orig_lon, orig_station.lat, orig_station.lon)
        lm_km = haversine_km(dest_station.lat, dest_station.lon, dest_lat, dest_lon)

        # 1. First Mile
        fm_fare = 0.0
        if fm_km > 0.4:
            fm_mins = max(5, int(fm_km * 3.2))
            fm_arr = curr_time + timedelta(minutes=fm_mins)
            fm_mode = "auto" if fm_km > 2.0 else "erickshaw"
            fm_fare = 15.0 if fm_mode == "erickshaw" else (30.0 + max(0.0, fm_km - 1.5) * 11.0)
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode=fm_mode,
                line_name=f"Feeder {'Auto' if fm_mode == 'auto' else 'E-Rickshaw'}",
                line_color="#E68A00" if fm_mode == "auto" else "#00897B",
                origin_name=orig_dict.get("name", "Origin"),
                destination_name=f"{orig_station.name} ({orig_station.code})",
                origin_coords=[orig_lon, orig_lat],
                destination_coords=[orig_station.lon, orig_station.lat],
                path_coords=[[orig_lon, orig_lat], [orig_station.lon, orig_station.lat]],
                duration_minutes=fm_mins,
                distance_meters=int(fm_km * 1000),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=fm_arr.strftime("%H:%M"),
                stops_count=1,
                instructions=f"Take feeder transit to {orig_station.name}.",
                crowd_level="Moderate",
                fare_inr=round(fm_fare, 0),
                fare_details=f"Feeder fare: ₹{int(fm_fare)}"
            ))
            curr_time = fm_arr + timedelta(minutes=4)

        # 2. Train Leg 1
        tag1, _, col1 = self._get_suburban_branding(train1, orig_station, hub_station)
        dep1 = curr_time
        arr1 = dep1 + timedelta(minutes=train1.duration_minutes)
        fare1 = train1.fares.get("UR", 10.0)
        stops1 = self._get_intermediate_stops(train1, orig_station.code, hub_station.code)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="rail",
            line_name=f"{train1.train_name}",
            line_color=col1,
            origin_name=f"{orig_station.name} ({orig_station.code})",
            destination_name=f"{hub_station.name} ({hub_station.code})",
            origin_coords=[orig_station.lon, orig_station.lat],
            destination_coords=[hub_station.lon, hub_station.lat],
            path_coords=[[orig_station.lon, orig_station.lat], [hub_station.lon, hub_station.lat]],
            duration_minutes=train1.duration_minutes,
            distance_meters=int(train1.distance_km * 1000),
            departure_time=dep1.strftime("%H:%M"),
            arrival_time=arr1.strftime("%H:%M"),
            stops_count=len(stops1),
            intermediate_stops=stops1,
            instructions=f"Board {train1.train_name} from {train1.platform_origin or 'Platform 1'} towards {hub_station.name}.",
            crowd_level="Moderate",
            fare_inr=fare1,
            fare_details=f"Suburban Fare: ₹{int(fare1)}",
            train_number=train1.train_number,
            train_name=train1.train_name,
            train_type=train1.train_type,
            platform=train1.platform_origin or "PF 1",
            coach_classes=train1.classes,
            data_source=train1.data_source
        ))
        curr_time = arr1

        # 3. Station Foot Overbridge Interchange Walk
        inter_walk_mins = 5
        inter_arr = curr_time + timedelta(minutes=inter_walk_mins)
        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="walk",
            line_name=f"Transfer Walk at {hub_station.name}",
            line_color="#52544D",
            origin_name=f"{hub_station.name} Platform",
            destination_name=f"{hub_station.name} Connecting Platform",
            origin_coords=[hub_station.lon, hub_station.lat],
            destination_coords=[hub_station.lon, hub_station.lat],
            path_coords=[[hub_station.lon, hub_station.lat], [hub_station.lon, hub_station.lat]],
            duration_minutes=inter_walk_mins,
            distance_meters=180,
            departure_time=curr_time.strftime("%H:%M"),
            arrival_time=inter_arr.strftime("%H:%M"),
            stops_count=0,
            instructions=f"Use foot overbridge (FOB) at {hub_station.name} to change platforms for connecting suburban line.",
            crowd_level="Moderate",
            fare_inr=0.0
        ))
        curr_time = inter_arr

        # 4. Train Leg 2
        tag2, _, col2 = self._get_suburban_branding(train2, hub_station, dest_station)
        dep2 = curr_time
        arr2 = dep2 + timedelta(minutes=train2.duration_minutes)
        fare2 = train2.fares.get("UR", 10.0)
        stops2 = self._get_intermediate_stops(train2, hub_station.code, dest_station.code)

        legs.append(TransitLeg(
            id=str(uuid.uuid4())[:8],
            mode="rail",
            line_name=f"{train2.train_name}",
            line_color=col2,
            origin_name=f"{hub_station.name} ({hub_station.code})",
            destination_name=f"{dest_station.name} ({dest_station.code})",
            origin_coords=[hub_station.lon, hub_station.lat],
            destination_coords=[dest_station.lon, dest_station.lat],
            path_coords=[[hub_station.lon, hub_station.lat], [dest_station.lon, dest_station.lat]],
            duration_minutes=train2.duration_minutes,
            distance_meters=int(train2.distance_km * 1000),
            departure_time=dep2.strftime("%H:%M"),
            arrival_time=arr2.strftime("%H:%M"),
            stops_count=len(stops2),
            intermediate_stops=stops2,
            instructions=f"Board connecting {train2.train_name} from {train2.platform_origin or 'PF 3'} to {dest_station.name}.",
            crowd_level="Moderate",
            fare_inr=fare2,
            fare_details=f"Suburban Fare: ₹{int(fare2)}",
            train_number=train2.train_number,
            train_name=train2.train_name,
            train_type=train2.train_type,
            platform=train2.platform_origin or "PF 3",
            coach_classes=train2.classes,
            data_source=train2.data_source
        ))
        curr_time = arr2

        # 5. Last Mile
        lm_fare = 0.0
        if lm_km > 0.4:
            lm_mins = max(5, int(lm_km * 3.2))
            lm_arr = curr_time + timedelta(minutes=lm_mins)
            lm_mode = "auto" if lm_km > 2.0 else "erickshaw"
            lm_fare = 15.0 if lm_mode == "erickshaw" else (30.0 + max(0.0, lm_km - 1.5) * 11.0)
            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode=lm_mode,
                line_name=f"Last-Mile {'Auto' if lm_mode == 'auto' else 'E-Rickshaw'}",
                line_color="#E68A00" if lm_mode == "auto" else "#00897B",
                origin_name=f"{dest_station.name} ({dest_station.code})",
                destination_name=dest_dict.get("name", "Destination"),
                origin_coords=[dest_station.lon, dest_station.lat],
                destination_coords=[dest_lon, dest_lat],
                path_coords=[[dest_station.lon, dest_station.lat], [dest_lon, dest_lat]],
                duration_minutes=lm_mins,
                distance_meters=int(lm_km * 1000),
                departure_time=curr_time.strftime("%H:%M"),
                arrival_time=lm_arr.strftime("%H:%M"),
                stops_count=1,
                instructions=f"Exit {dest_station.name} and take last-mile transit to destination.",
                crowd_level="Moderate",
                fare_inr=round(lm_fare, 0),
                fare_details=f"Last-mile fare: ₹{int(lm_fare)}"
            ))
            curr_time = lm_arr

        total_duration = int((curr_time - base_time).total_seconds() / 60)
        total_fare = fm_fare + fare1 + fare2 + lm_fare
        total_distance_m = int(dist_km * 1000)

        city_name = orig_station.city
        return RouteItinerary(
            id=str(uuid.uuid4())[:8],
            title=f"{city_name} Suburban: {orig_station.code} ➔ {hub_station.code} ➔ {dest_station.code}",
            tag=f"🚆 {city_name} Suburban Interchange",
            tag_reason=f"Connecting route via {hub_station.name} transfer. Fast unreserved suburban rail across lines.",
            total_duration_minutes=total_duration,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=curr_time.strftime("%H:%M"),
            total_fare_inr=round(total_fare, 0),
            fare_breakdown=f"Train 1 (₹{int(fare1)}) + Train 2 (₹{int(fare2)})" + (f" + Feeder (₹{int(fm_fare + lm_fare)})" if (fm_fare + lm_fare) > 0 else ""),
            route_type="rail_connect",
            transfers_count=len(legs) - 1,
            walking_duration_minutes=inter_walk_mins,
            walking_distance_meters=180,
            overall_crowd="Moderate",
            total_delay_minutes=0,
            legs=legs,
            eco_carbon_savings_kg=round(dist_km * 0.085, 1),
            service_available=True
        )

    def _build_itineraries_from_trains(
        self,
        trains: List[TrainSummary],
        orig_dict: Dict[str, Any],
        dest_dict: Dict[str, Any],
        orig_station: RailStation,
        dest_station: RailStation,
        base_time: datetime,
        dist_km: float,
        fm_km: float,
        lm_km: float
    ) -> List[RouteItinerary]:
        rail_routes: List[RouteItinerary] = []
        orig_lat = orig_dict.get("lat", orig_station.lat)
        orig_lon = orig_dict.get("lon", orig_station.lon)
        dest_lat = dest_dict.get("lat", dest_station.lat)
        dest_lon = dest_dict.get("lon", dest_station.lon)

        for train in trains[:2]:
            legs: List[TransitLeg] = []
            curr_time = base_time

            # 1. First Mile Leg
            fm_fare = 0.0
            fm_walk_mins = 0
            if fm_km > 0.4:
                fm_mins = max(5, int(fm_km * 3.2))
                fm_arr = curr_time + timedelta(minutes=fm_mins)
                fm_mode = "auto" if fm_km > 2.0 else "erickshaw"
                fm_fare = 15.0 if fm_mode == "erickshaw" else (30.0 + max(0.0, fm_km - 1.5) * 11.0)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode=fm_mode,
                    line_name=f"First-Mile {'Feeder Auto' if fm_mode == 'auto' else 'E-Rickshaw (Toto)'}",
                    line_color="#E68A00" if fm_mode == "auto" else "#00897B",
                    origin_name=orig_dict.get("name", "Origin"),
                    destination_name=f"{orig_station.name} ({orig_station.code})",
                    origin_coords=[orig_lon, orig_lat],
                    destination_coords=[orig_station.lon, orig_station.lat],
                    path_coords=[[orig_lon, orig_lat], [orig_station.lon, orig_station.lat]],
                    duration_minutes=fm_mins,
                    distance_meters=int(fm_km * 1000),
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=fm_arr.strftime("%H:%M"),
                    stops_count=1,
                    instructions=f"Take feeder transit to {orig_station.name}. Allow 4 mins for platform entry.",
                    crowd_level="Moderate",
                    fare_inr=round(fm_fare, 0),
                    fare_details=f"Local feeder fare: ₹{int(fm_fare)}"
                ))
                curr_time = fm_arr + timedelta(minutes=4)
            elif fm_km > 0.05:
                fm_walk_mins = max(3, int(fm_km * 12))
                fm_arr = curr_time + timedelta(minutes=fm_walk_mins)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="walk",
                    line_name="Walk to Station Entrance",
                    origin_name=orig_dict.get("name", "Origin"),
                    destination_name=f"{orig_station.name} ({orig_station.code})",
                    origin_coords=[orig_lon, orig_lat],
                    destination_coords=[orig_station.lon, orig_station.lat],
                    path_coords=[[orig_lon, orig_lat], [orig_station.lon, orig_station.lat]],
                    duration_minutes=fm_walk_mins,
                    distance_meters=int(fm_km * 1000),
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=fm_arr.strftime("%H:%M"),
                    stops_count=0,
                    instructions=f"Walk directly into {orig_station.name} ({orig_station.code}). Head to {train.platform_origin or 'Platform 1'}.",
                    crowd_level="Low",
                    fare_inr=0.0
                ))
                curr_time = fm_arr

            # 2. Railway Suburban Leg
            train_dep = curr_time
            train_arr = train_dep + timedelta(minutes=train.duration_minutes)
            rail_fare = train.fares.get("UR") or train.fares.get("2S") or (list(train.fares.values())[0] if train.fares else 10.0)
            fare_class_label = "UR" if "UR" in train.fares else ("2S" if "2S" in train.fares else (train.classes[0] if train.classes else "Suburban"))
            classes_str = " · ".join(train.classes) if train.classes else "UR / General"

            tag, tag_reason, line_color = self._get_suburban_branding(train, orig_station, dest_station)
            stops_list = self._get_intermediate_stops(train, orig_station.code, dest_station.code)

            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="rail",
                line_name=f"{train.train_name}",
                line_color=line_color,
                origin_name=f"{orig_station.name} ({orig_station.code})",
                destination_name=f"{dest_station.name} ({dest_station.code})",
                origin_coords=[orig_station.lon, orig_station.lat],
                destination_coords=[dest_station.lon, dest_station.lat],
                path_coords=[[orig_station.lon, orig_station.lat], [dest_station.lon, dest_station.lat]],
                duration_minutes=train.duration_minutes,
                distance_meters=int(train.distance_km * 1000),
                departure_time=train_dep.strftime("%H:%M"),
                arrival_time=train_arr.strftime("%H:%M"),
                stops_count=len(stops_list),
                intermediate_stops=stops_list,
                instructions=f"Board {train.train_name} from {train.platform_origin or 'Platform 1'}. Available classes: {classes_str}. Status: {train.live_status}.",
                crowd_level="Moderate",
                delay_minutes=train.live_delay_mins,
                is_delayed=train.live_delay_mins > 0,
                fare_inr=rail_fare,
                fare_details=f"IR Suburban Fare: ₹{int(rail_fare)} ({fare_class_label})",
                train_number=train.train_number,
                train_name=train.train_name,
                train_type=train.train_type,
                platform=train.platform_origin or "PF 1",
                coach_classes=train.classes,
                data_source=train.data_source
            ))
            curr_time = train_arr

            # 3. Last Mile Leg
            lm_fare = 0.0
            lm_walk_mins = 0
            if lm_km > 0.4:
                lm_mins = max(5, int(lm_km * 3.2))
                lm_arr = curr_time + timedelta(minutes=lm_mins)
                lm_mode = "auto" if lm_km > 2.0 else "erickshaw"
                lm_fare = 15.0 if lm_mode == "erickshaw" else (30.0 + max(0.0, lm_km - 1.5) * 11.0)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode=lm_mode,
                    line_name=f"Last-Mile {'Auto' if lm_mode == 'auto' else 'Toto (E-Rickshaw)'}",
                    line_color="#E68A00" if lm_mode == "auto" else "#00897B",
                    origin_name=f"{dest_station.name} ({dest_station.code})",
                    destination_name=dest_dict.get("name", "Destination"),
                    origin_coords=[dest_station.lon, dest_station.lat],
                    destination_coords=[dest_lon, dest_lat],
                    path_coords=[[dest_station.lon, dest_station.lat], [dest_lon, dest_lat]],
                    duration_minutes=lm_mins,
                    distance_meters=int(lm_km * 1000),
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=lm_arr.strftime("%H:%M"),
                    stops_count=1,
                    instructions=f"Exit {dest_station.name} and take last-mile transit directly to destination.",
                    crowd_level="Moderate",
                    fare_inr=round(lm_fare, 0),
                    fare_details=f"Last-mile fare: ₹{int(lm_fare)}"
                ))
                curr_time = lm_arr
            elif lm_km > 0.05:
                lm_walk_mins = max(3, int(lm_km * 12))
                lm_arr = curr_time + timedelta(minutes=lm_walk_mins)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="walk",
                    line_name="Walk to Final Destination",
                    origin_name=f"{dest_station.name} ({dest_station.code})",
                    destination_name=dest_dict.get("name", "Destination"),
                    origin_coords=[dest_station.lon, dest_station.lat],
                    destination_coords=[dest_lon, dest_lat],
                    path_coords=[[dest_station.lon, dest_station.lat], [dest_lon, dest_lat]],
                    duration_minutes=lm_walk_mins,
                    distance_meters=int(lm_km * 1000),
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=lm_arr.strftime("%H:%M"),
                    stops_count=0,
                    instructions=f"Walk {int(lm_km * 1000)}m from {dest_station.name} to {dest_dict.get('name', 'destination')}.",
                    crowd_level="Low",
                    fare_inr=0.0
                ))
                curr_time = lm_arr

            total_duration = int((curr_time - base_time).total_seconds() / 60)
            total_fare = fm_fare + rail_fare + lm_fare
            total_walk_time = fm_walk_mins + lm_walk_mins
            total_walk_dist = int((fm_km if fm_km <= 0.4 else 0.0 + (lm_km if lm_km <= 0.4 else 0.0)) * 1000)

            parts = []
            if fm_fare > 0:
                parts.append(f"Feeder (₹{int(fm_fare)})")
            parts.append(f"Train #{train.train_number} (₹{int(rail_fare)})")
            if lm_fare > 0:
                parts.append(f"Last-Mile (₹{int(lm_fare)})")
            fare_breakdown = " + ".join(parts)

            rail_routes.append(RouteItinerary(
                id=str(uuid.uuid4())[:8],
                title=f"{train.train_name}",
                tag=tag,
                tag_reason=tag_reason,
                total_duration_minutes=total_duration,
                departure_time=base_time.strftime("%H:%M"),
                arrival_time=curr_time.strftime("%H:%M"),
                total_fare_inr=round(total_fare, 0),
                fare_breakdown=fare_breakdown,
                route_type="rail_connect",
                transfers_count=len(legs) - 1,
                walking_duration_minutes=total_walk_time,
                walking_distance_meters=total_walk_dist,
                overall_crowd="Moderate",
                total_delay_minutes=train.live_delay_mins,
                legs=legs,
                eco_carbon_savings_kg=round(dist_km * 0.085, 1),
                service_available=True
            ))

        return rail_routes

    async def find_rail_routes(
        self,
        orig_dict: Dict[str, Any],
        dest_dict: Dict[str, Any],
        base_time: datetime,
        dist_km: float,
        city: str
    ) -> List[RouteItinerary]:
        """Async version using provider data."""
        return self.find_rail_routes_sync(orig_dict, dest_dict, base_time, dist_km, city)


# Singleton service instance
rail_service_instance = RailConnectService()
