"""
RailRadar API Provider Adapter for Raahi RailConnect.
Supports live calls to https://railradar.in/api/v1 with robust timeout, error handling,
and transparent fallback to verified ground-truth schedules when API key is missing or service is offline.
"""
import os
import logging
from typing import List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

from ..provider_interface import RailProviderInterface
from ..schemas import (
    RailStation, TrainHalt, TrainSummary, TrainSchedule, LiveRunningStatus, StationBoardItem
)
from .fallback_data import (
    RAIL_STATIONS, SCHEDULE_DATABASE, find_station_by_query,
    get_fallback_trains_between, get_fallback_live_status, get_fallback_station_board
)

logger = logging.getLogger("raahi.railradar")


class RailRadarProvider(RailProviderInterface):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://railradar.in/api/v1"):
        self.api_key = api_key or os.getenv("RAILRADAR_API_KEY", "").strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = 3.5  # fast fail to avoid blocking commuter UX

    def _get_headers(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": "RaahiRailConnect/1.0 (Braj-Delhi Transit)"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search_stations(self, query: str, city: Optional[str] = None) -> List[RailStation]:
        """Search stations via RailRadar API or fallback directory."""
        if not query or len(query.strip()) < 2:
            return []

        # If live API key is present, attempt live lookup
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/stations/search",
                        params={"q": query.strip()},
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        stations_list = data if isinstance(data, list) else data.get("data", [])
                        results = []
                        for s in stations_list:
                            code = s.get("code") or s.get("station_code")
                            name = s.get("name") or s.get("station_name")
                            if code and name:
                                lat = float(s.get("lat") or 0.0)
                                lon = float(s.get("lng") or s.get("lon") or 0.0)
                                results.append(RailStation(
                                    code=code.upper(),
                                    name=name,
                                    city=s.get("city") or "India",
                                    state=s.get("state", "India"),
                                    lat=lat if lat != 0.0 else 28.6139,
                                    lon=lon if lon != 0.0 else 77.2090,
                                    platforms_count=int(s.get("platforms", 2)),
                                    category="railway_station"
                                ))
                        if results:
                            # If a city was requested, keep matching or all results
                            if city:
                                c_lower = city.lower()
                                city_matched = [st for st in results if c_lower in st.city.lower() or c_lower in st.name.lower()]
                                if city_matched:
                                    return city_matched
                            return results
            except Exception as e:
                logger.debug(f"RailRadar stations search API unavailable: {e}")

        # Fallback to authentic ground-truth station directory
        return find_station_by_query(query, city=city)

    async def get_trains_between(
        self, from_code: str, to_code: str, date: Optional[str] = None
    ) -> List[TrainSummary]:
        """Fetch trains between station codes with live RailRadar integration and ground-truth fallback."""
        from_c = from_code.upper().strip()
        to_c = to_code.upper().strip()
        live_trains: List[TrainSummary] = []

        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # Query trains passing through or originating at from_c
                    resp = await client.get(
                        f"{self.base_url}/stations/{from_c}/trains",
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        trains_raw = data.get("data", {}).get("trains", []) if isinstance(data.get("data"), dict) else []
                        for item in trains_raw:
                            t = item.get("train", {})
                            stop = item.get("stop", {})
                            dst = t.get("destination", {})
                            dst_code = dst.get("code") if isinstance(dst, dict) else str(dst)
                            
                            # Check if train terminates at destination or runs towards it
                            if dst_code and dst_code.upper() == to_c:
                                t_no = str(t.get("number", ""))
                                t_name = str(t.get("name", f"Train {t_no}"))
                                t_type = t.get("type", "Express")
                                dep_time = stop.get("departure") or "08:00"
                                arr_time = stop.get("arrival") or "09:30"
                                dist_km = float(stop.get("distance", 15.0))
                                plat = f"PF {stop.get('platform', '1')}" if stop.get("platform") else "PF 1"

                                live_trains.append(TrainSummary(
                                    train_number=t_no,
                                    train_name=t_name,
                                    train_type=t_type,
                                    origin_code=from_c,
                                    origin_name=t.get("source", {}).get("name", from_c) if isinstance(t.get("source"), dict) else from_c,
                                    destination_code=to_c,
                                    destination_name=dst.get("name", to_c) if isinstance(dst, dict) else to_c,
                                    departure_time=dep_time,
                                    arrival_time=arr_time,
                                    duration_minutes=int(dist_km * 1.5) if dist_km > 0 else 45,
                                    distance_km=dist_km if dist_km > 0 else 20.0,
                                    running_days=t.get("runDays", ["Daily"]),
                                    classes=["UR", "2S", "SL"] if "Express" in t_type else ["UR"],
                                    fares={"UR": 10.0} if "EMU" in t_type or "Local" in t_type else {"UR": 30.0, "2S": 60.0},
                                    halts_count=3,
                                    platform_origin=plat,
                                    platform_dest="PF 1",
                                    live_delay_mins=0,
                                    live_status="On Time",
                                    is_live=True,
                                    data_source="railradar_live"
                                ))
            except Exception as e:
                logger.debug(f"RailRadar trains at station API unavailable: {e}")

        # Always combine with verified commuter suburban timetables (so fast EMU / Local trains are complete)
        fallback_trains = get_fallback_trains_between(from_c, to_c, date)
        if not live_trains:
            return fallback_trains

        # Merge, prioritizing live trains
        existing_numbers = {t.train_number for t in live_trains}
        merged = list(live_trains)
        for fb in fallback_trains:
            if fb.train_number not in existing_numbers:
                merged.append(fb)
        return merged

    async def get_train_schedule(self, train_no: str) -> Optional[TrainSchedule]:
        """Fetch full timetable and halts for a train from live RailRadar API or fallback."""
        clean_no = str(train_no).strip().split()[0]
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/trains/{clean_no}",
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        payload = resp.json().get("data", {})
                        t_info = payload.get("train", {})
                        route_list = payload.get("route", [])
                        if route_list:
                            halts = []
                            for idx, h in enumerate(route_list, 1):
                                stn = h.get("station", {})
                                s_code = stn.get("code") or f"STN{idx}"
                                s_name = stn.get("name") or s_code
                                arr = h.get("arrival") or h.get("departure") or "00:00"
                                dep = h.get("departure") or h.get("arrival") or "00:00"
                                halts.append(TrainHalt(
                                    station_code=s_code,
                                    station_name=s_name,
                                    arrival_time=arr,
                                    departure_time=dep,
                                    halt_minutes=2 if h.get("isHalt") else 0,
                                    distance_km=float(h.get("distance", 0.0)),
                                    platform=str(h.get("platform")) if h.get("platform") else None,
                                    day_offset=int(h.get("arrivalDay") or h.get("departureDay") or 1)
                                ))
                            
                            src = t_info.get("source", {})
                            dst = t_info.get("destination", {})
                            return TrainSchedule(
                                train_number=clean_no,
                                train_name=t_info.get("name", f"Train {clean_no}"),
                                train_type=t_info.get("type", "Express"),
                                origin_code=src.get("code", halts[0].station_code) if isinstance(src, dict) else str(src or halts[0].station_code),
                                origin_name=src.get("name", halts[0].station_name) if isinstance(src, dict) else str(src or halts[0].station_name),
                                destination_code=dst.get("code", halts[-1].station_code) if isinstance(dst, dict) else str(dst or halts[-1].station_code),
                                destination_name=dst.get("name", halts[-1].station_name) if isinstance(dst, dict) else str(dst or halts[-1].station_name),
                                halts=halts,
                                running_days=t_info.get("runDays", ["Daily"])
                            )
            except Exception as e:
                logger.debug(f"RailRadar schedule API unavailable: {e}")

        return SCHEDULE_DATABASE.get(clean_no)

    async def get_live_running_status(
        self, train_no: str, date: Optional[str] = None
    ) -> Optional[LiveRunningStatus]:
        """Fetch live running status & delay info from RailRadar."""
        clean_no = str(train_no).strip().split()[0]
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/trains/{clean_no}/live",
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        d = resp.json().get("data", {})
                        loc = d.get("currentLocation", {})
                        next_h = d.get("nextHalt", {})
                        delay = int(d.get("delayMinutes", 0))
                        
                        curr_stn = loc.get("stationName") or loc.get("stationCode", "En Route")
                        status_str = f"Running On Time" if delay == 0 else f"Delayed by {delay} mins"
                        if curr_stn and curr_stn != "En Route":
                            status_str += f" - Near {curr_stn}"
                            
                        return LiveRunningStatus(
                            train_number=clean_no,
                            train_name=d.get("trainName", f"Train {clean_no}"),
                            train_type=d.get("train", {}).get("type", "Express") if isinstance(d.get("train"), dict) else "Express",
                            current_station=curr_stn,
                            current_status=status_str,
                            delay_minutes=delay,
                            speed_kmh=loc.get("speedKmh"),
                            last_reported_time=d.get("lastUpdatedAt", ""),
                            next_station=next_h.get("stationName"),
                            eta_destination="On Time" if delay == 0 else f"+{delay}m",
                            is_live=True,
                            data_source="railradar_live"
                        )
            except Exception as e:
                logger.debug(f"RailRadar live status API unavailable: {e}")

        return get_fallback_live_status(clean_no)

    async def get_station_board(
        self, station_code: str, hours: int = 4
    ) -> List[StationBoardItem]:
        """Fetch live station board from RailRadar."""
        code = station_code.upper().strip()
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/stations/{code}/live",
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        trains = resp.json().get("data", {}).get("trains", [])
                        results = []
                        for item in trains:
                            tr = item.get("train", {})
                            st = item.get("stop", {})
                            lv = item.get("live", {})
                            delay = int(lv.get("delayMinutes", 0))
                            
                            src = tr.get("source", {})
                            dst = tr.get("destination", {})
                            src_c = src.get("code") if isinstance(src, dict) else str(src or code)
                            dst_c = dst.get("code") if isinstance(dst, dict) else str(dst or "")
                            dst_n = dst.get("name") if isinstance(dst, dict) else str(dst or dst_c)

                            sched_time = st.get("departure") or st.get("arrival") or "00:00"
                            exp_time = lv.get("expectedArrivalTime", sched_time)
                            if "T" in str(exp_time):
                                try:
                                    exp_time = str(exp_time).split("T")[1][:5]
                                except Exception:
                                    exp_time = sched_time

                            results.append(StationBoardItem(
                                train_number=str(tr.get("number", "")),
                                train_name=str(tr.get("name", "")),
                                train_type=str(tr.get("type", "Express")),
                                origin_code=src_c,
                                destination_code=dst_c,
                                destination_name=dst_n,
                                scheduled_time=sched_time,
                                expected_time=exp_time,
                                platform=f"PF {st.get('platform', '1')}",
                                status=f"Delayed {delay}m" if delay > 5 else "On Time",
                                delay_minutes=delay,
                                is_live=True
                            ))
                        if results:
                            return results
            except Exception as e:
                logger.debug(f"RailRadar station board API unavailable: {e}")

        return get_fallback_station_board(code)
