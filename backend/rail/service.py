"""
High-level RailConnect Service for Raahi.
Handles station resolution, caching, provider abstraction,
and seamless conversion of train schedules into multi-modal RouteItineraries.
"""
import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from .schemas import (
    RailStation, TrainSummary, TrainSchedule, LiveRunningStatus,
    StationBoardItem, StationBoardResponse
)
from .provider_interface import RailProviderInterface
from .providers.railradar import RailRadarProvider
from .providers.fallback_data import RAIL_STATIONS, get_all_stations, find_station_by_query
from ..models import RouteItinerary, TransitLeg


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class RailConnectService:
    def __init__(self, provider: Optional[RailProviderInterface] = None):
        self.provider: RailProviderInterface = provider or RailRadarProvider()
        self._stations_cache: Dict[str, RailStation] = dict(RAIL_STATIONS)

    async def search_stations(self, query: str, city: Optional[str] = None) -> List[RailStation]:
        """Search stations across provider and directory."""
        if not query:
            return list(self._stations_cache.values())
        return await self.provider.search_stations(query)

    def get_station_by_code(self, code: str) -> Optional[RailStation]:
        return self._stations_cache.get(code.upper().strip())

    def find_nearest_rail_station(self, lat: float, lon: float, max_dist_km: float = 30.0) -> Optional[Tuple[RailStation, float]]:
        """Find the nearest railway station to any given coordinates."""
        best_station: Optional[RailStation] = None
        min_dist = float("inf")
        for s in self._stations_cache.values():
            d = haversine_km(lat, lon, s.lat, s.lon)
            if d < min_dist:
                min_dist = d
                best_station = s
        if best_station and min_dist <= max_dist_km:
            return best_station, round(min_dist, 2)
        return None

    def resolve_station_from_place(self, place_dict: Dict[str, Any]) -> Optional[RailStation]:
        """Resolve a RailStation object from a place in PLACES_DATABASE or search input."""
        name = place_dict.get("name", "").strip()
        name_lower = name.lower()

        # Check direct code in brackets, e.g. "Mathura Junction Railway Station (MTJ)"
        for code in self._stations_cache.keys():
            if f"({code})" in name or f"[{code}]" in name or code.lower() == name_lower:
                return self._stations_cache[code]

        # Check aliases
        for s in self._stations_cache.values():
            if s.name.lower() in name_lower or name_lower in s.name.lower():
                return s
            for alias in s.aliases:
                if alias in name_lower or name_lower in alias:
                    return s

        # Check nearest rail station if within 3.5 km
        lat = place_dict.get("lat")
        lon = place_dict.get("lon")
        if lat is not None and lon is not None:
            res = self.find_nearest_rail_station(lat, lon, max_dist_km=3.5)
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

    def find_rail_routes_sync(
        self,
        orig_dict: Dict[str, Any],
        dest_dict: Dict[str, Any],
        base_time: datetime,
        dist_km: float,
        city: str
    ) -> List[RouteItinerary]:
        """Synchronous version for direct call in TransitRouter.plan_journey()."""
        orig_station = self.resolve_station_from_place(orig_dict)
        dest_station = self.resolve_station_from_place(dest_dict)

        orig_lat = orig_dict.get("lat", 0.0)
        orig_lon = orig_dict.get("lon", 0.0)
        dest_lat = dest_dict.get("lat", 0.0)
        dest_lon = dest_dict.get("lon", 0.0)

        if not orig_station:
            nearest = self.find_nearest_rail_station(orig_lat, orig_lon, max_dist_km=25.0)
            if nearest:
                orig_station = nearest[0]

        if not dest_station:
            nearest = self.find_nearest_rail_station(dest_lat, dest_lon, max_dist_km=25.0)
            if nearest:
                dest_station = nearest[0]

        if not orig_station or not dest_station or orig_station.code == dest_station.code:
            return []

        # Get trains via verified schedule
        from .providers.fallback_data import get_fallback_trains_between, RAIL_STATIONS
        self._stations_cache.update(RAIL_STATIONS)
        trains = get_fallback_trains_between(orig_station.code, dest_station.code)

        if not trains:
            # Check alternative nearby hub station (e.g. MRT -> MTJ for main line trains to Chhata, Delhi, etc.)
            alt_origins = []
            if orig_station.code in ["MRT", "BAAD"]:
                alt_origins.extend([self.get_station_by_code("MTJ"), self.get_station_by_code("BTSR")])
            elif orig_station.code in ["BTSR"]:
                alt_origins.append(self.get_station_by_code("MTJ"))
            elif orig_station.code in ["TKJ", "CSB", "DEE", "DEC", "OKA"]:
                alt_origins.extend([self.get_station_by_code("NDLS"), self.get_station_by_code("NZM"), self.get_station_by_code("DLI")])

            for alt_st in alt_origins:
                if alt_st and alt_st.code != dest_station.code:
                    alt_trains = get_fallback_trains_between(alt_st.code, dest_station.code)
                    if alt_trains:
                        orig_station = alt_st
                        trains = alt_trains
                        break

        if not trains:
            # Check alternative destination hub
            alt_dests = []
            if dest_station.code in ["MRT", "BAAD"]:
                alt_dests.extend([self.get_station_by_code("MTJ"), self.get_station_by_code("BTSR")])
            elif dest_station.code in ["BTSR"]:
                alt_dests.append(self.get_station_by_code("MTJ"))

            for alt_d in alt_dests:
                if alt_d and alt_d.code != orig_station.code:
                    alt_trains = get_fallback_trains_between(orig_station.code, alt_d.code)
                    if alt_trains:
                        dest_station = alt_d
                        trains = alt_trains
                        break

        if not trains:
            return []

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
        orig_lat = orig_dict.get("lat", 0.0)
        orig_lon = orig_dict.get("lon", 0.0)
        dest_lat = dest_dict.get("lat", 0.0)
        dest_lon = dest_dict.get("lon", 0.0)

        for train in trains[:2]:  # Top 2 best train options
            legs: List[TransitLeg] = []
            curr_time = base_time

            # 1. First Mile Leg (if starting away from the railway station)
            fm_fare = 0.0
            fm_walk_mins = 0
            if fm_km > 0.4:
                fm_mins = max(5, int(fm_km * 3.2))
                fm_arr = curr_time + timedelta(minutes=fm_mins)
                fm_mode = "auto" if fm_km > 2.0 else "erickshaw"
                fm_fare = 15.0 if fm_mode == "erickshaw" else (30.0 + max(0.0, fm_km - 1.5) * 11.0)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode=fm_mode,  # type: ignore
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
                    instructions=f"Take {'feeder auto' if fm_mode == 'auto' else 'shared E-rickshaw'} to {orig_station.name}. Allow 5 mins for platform access.",
                    crowd_level="Moderate",
                    fare_inr=round(fm_fare, 0),
                    fare_details=f"Local feeder fare: ₹{int(fm_fare)}"
                ))
                curr_time = fm_arr + timedelta(minutes=4)  # 4m station entry buffer
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

            # 2. Train Railway Leg
            train_dep = curr_time
            train_arr = train_dep + timedelta(minutes=train.duration_minutes)
            rail_fare = train.fares.get("UR") or train.fares.get("2S") or (list(train.fares.values())[0] if train.fares else 30.0)
            fare_class_label = "UR" if "UR" in train.fares else ("2S" if "2S" in train.fares else (train.classes[0] if train.classes else "Standard"))
            classes_str = " · ".join(train.classes) if train.classes else "UR / General"

            # Determine tag and styling
            if "shatabdi" in train.train_name.lower():
                tag = "🚆 Indian Railways (Shatabdi Express)"
                tag_reason = f"Fastest intercity corridor via {orig_station.code} to {dest_station.code} (115 km/h)."
            elif "rail bus" in train.train_name.lower() or "vrindavan" in train.train_name.lower():
                tag = "🚆 Mathura - Vrindavan Rail Bus"
                tag_reason = "Heritage local passenger shuttle connecting Mathura Jn & Vrindavan at just ₹10 flat."
            elif any(c in [orig_station.code, dest_station.code] for c in ["CHJ", "KSV", "AJH", "VRBD", "BTSR", "FAR", "BAAD", "RAYA"]):
                tag = "🚆 Indian Railways Local Train"
                tag_reason = f"Frequent local commuter train connecting {orig_station.name} to {dest_station.name} at just ₹{int(rail_fare)}."
            elif "emu" in train.train_name.lower() or "local" in train.train_name.lower():
                tag = "🚆 Delhi Suburban EMU Local"
                tag_reason = f"Frequent unreserved suburban commuter train connecting {orig_station.code} & {dest_station.code}."
            else:
                tag = f"🚆 {train.train_type} Train ({train.train_number})"
                tag_reason = f"Direct Indian Railways connection. Unreserved General Fare ₹{int(rail_fare)}."

            legs.append(TransitLeg(
                id=str(uuid.uuid4())[:8],
                mode="rail",
                line_name=f"{train.train_number} {train.train_name}",
                line_color="#8B1E1E",  # Classic IR Maroon
                origin_name=f"{orig_station.name} ({orig_station.code})",
                destination_name=f"{dest_station.name} ({dest_station.code})",
                origin_coords=[orig_station.lon, orig_station.lat],
                destination_coords=[dest_station.lon, dest_station.lat],
                path_coords=[[orig_station.lon, orig_station.lat], [dest_station.lon, dest_station.lat]],
                duration_minutes=train.duration_minutes,
                distance_meters=int(train.distance_km * 1000),
                departure_time=train_dep.strftime("%H:%M"),
                arrival_time=train_arr.strftime("%H:%M"),
                stops_count=train.halts_count,
                intermediate_stops=[f"{train.halts_count} intermediate station halts" if train.halts_count > 0 else "Direct Non-Stop"],
                instructions=f"Board Train #{train.train_number} {train.train_name} from {train.platform_origin or 'Platform 1'}. Available classes: {classes_str}. Status: {train.live_status}.",
                crowd_level="Moderate",
                delay_minutes=train.live_delay_mins,
                is_delayed=train.live_delay_mins > 0,
                fare_inr=rail_fare,
                fare_details=f"IR Fare: ₹{int(rail_fare)} ({fare_class_label})",
                train_number=train.train_number,
                train_name=train.train_name,
                train_type=train.train_type,
                platform=train.platform_origin or "PF 1",
                coach_classes=train.classes,
                data_source=train.data_source
            ))
            curr_time = train_arr

            # 3. Last Mile Leg (from dest_station to final destination)
            lm_fare = 0.0
            lm_walk_mins = 0
            if lm_km > 0.4:
                lm_mins = max(5, int(lm_km * 3.2))
                lm_arr = curr_time + timedelta(minutes=lm_mins)
                lm_mode = "auto" if lm_km > 2.0 else "erickshaw"
                lm_fare = 15.0 if lm_mode == "erickshaw" else (30.0 + max(0.0, lm_km - 1.5) * 11.0)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode=lm_mode,  # type: ignore
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
                    instructions=f"Exit {dest_station.name} and take last-mile {'auto' if lm_mode == 'auto' else 'Toto'} directly to destination.",
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

            # Build fare breakdown
            parts = []
            if fm_fare > 0:
                parts.append(f"Feeder (₹{int(fm_fare)})")
            parts.append(f"Train #{train.train_number} (₹{int(rail_fare)})")
            if lm_fare > 0:
                parts.append(f"Last-Mile (₹{int(lm_fare)})")

            fare_breakdown = " + ".join(parts)

            rail_routes.append(RouteItinerary(
                id=str(uuid.uuid4())[:8],
                title=f"Indian Railways: {train.train_name}",
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
        orig_station = self.resolve_station_from_place(orig_dict)
        dest_station = self.resolve_station_from_place(dest_dict)

        orig_lat = orig_dict.get("lat", 0.0)
        orig_lon = orig_dict.get("lon", 0.0)
        dest_lat = dest_dict.get("lat", 0.0)
        dest_lon = dest_dict.get("lon", 0.0)

        if not orig_station:
            nearest = self.find_nearest_rail_station(orig_lat, orig_lon, max_dist_km=25.0)
            if nearest:
                orig_station = nearest[0]

        if not dest_station:
            nearest = self.find_nearest_rail_station(dest_lat, dest_lon, max_dist_km=25.0)
            if nearest:
                dest_station = nearest[0]

        if not orig_station or not dest_station or orig_station.code == dest_station.code:
            return []

        trains = await self.get_trains_between(orig_station.code, dest_station.code)
        if not trains:
            return []

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


# Singleton service instance
rail_service_instance = RailConnectService()

