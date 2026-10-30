"""
RailRadar API Provider Adapter for Raahi RailConnect.
Supports live calls to https://railradar.in/api/v1 with robust timeout, error handling,
and transparent fallback to verified ground-truth schedules when API key is missing or service is offline.
"""
import os
import logging
from typing import List, Optional
import httpx

from ..provider_interface import RailProviderInterface
from ..schemas import (
    RailStation, TrainSummary, TrainSchedule, LiveRunningStatus, StationBoardItem
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
        self.timeout = 2.8  # fast fail to avoid blocking commuter UX

    def _get_headers(self) -> dict:
        headers = {
            "Accept": "application/json",
            "User-Agent": "RaahiRailConnect/1.0 (Braj-Delhi Transit)"
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search_stations(self, query: str) -> List[RailStation]:
        """Search stations via RailRadar API or fallback directory."""
        if not query or len(query.strip()) < 2:
            return []

        # If live API key is present, attempt live lookup
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/stations",
                        params={"query": query},
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        stations_list = data if isinstance(data, list) else data.get("stations", data.get("data", []))
                        results = []
                        for s in stations_list:
                            code = s.get("code") or s.get("station_code")
                            name = s.get("name") or s.get("station_name")
                            if code and name:
                                results.append(RailStation(
                                    code=code.upper(),
                                    name=name,
                                    city=s.get("city", "Delhi NCR / UP"),
                                    state=s.get("state", "India"),
                                    lat=float(s.get("lat", 28.6139)),
                                    lon=float(s.get("lon", 77.2090)),
                                    platforms_count=int(s.get("platforms", 2)),
                                    category="railway_station"
                                ))
                        if results:
                            return results
            except Exception as e:
                logger.debug(f"RailRadar stations API unavailable: {e}")

        # Fallback to authentic ground-truth station directory
        return find_station_by_query(query)

    async def get_trains_between(
        self, from_code: str, to_code: str, date: Optional[str] = None
    ) -> List[TrainSummary]:
        """Fetch trains between station codes with live RailRadar integration and ground-truth fallback."""
        from_c = from_code.upper().strip()
        to_c = to_code.upper().strip()

        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/trains-between-stations",
                        params={"from": from_c, "to": to_c, "date": date or ""},
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        trains_raw = data if isinstance(data, list) else data.get("trains", data.get("data", []))
                        results = []
                        for t in trains_raw:
                            t_no = str(t.get("train_number") or t.get("number", ""))
                            t_name = str(t.get("train_name") or t.get("name", f"Train {t_no}"))
                            t_type = t.get("type", "Express")
                            if "shatabdi" in t_name.lower():
                                t_type = "Shatabdi"
                            elif "vande bharat" in t_name.lower():
                                t_type = "Vande Bharat"
                            elif "emu" in t_name.lower() or "local" in t_name.lower():
                                t_type = "EMU / Local"
                            elif "passenger" in t_name.lower() or "rail bus" in t_name.lower():
                                t_type = "Passenger"
                            
                            results.append(TrainSummary(
                                train_number=t_no,
                                train_name=t_name,
                                train_type=t_type,
                                origin_code=from_c,
                                origin_name=t.get("from_station_name", from_c),
                                destination_code=to_c,
                                destination_name=t.get("to_station_name", to_c),
                                departure_time=t.get("departure_time", "08:00"),
                                arrival_time=t.get("arrival_time", "09:30"),
                                duration_minutes=int(t.get("duration_minutes", 90)),
                                distance_km=float(t.get("distance_km", 140.0)),
                                running_days=t.get("running_days", ["Daily"]),
                                classes=t.get("classes", ["UR", "2S", "SL"]),
                                fares=t.get("fares", {"UR": 30.0, "2S": 60.0}),
                                halts_count=int(t.get("halts_count", 3)),
                                platform_origin=t.get("platform_origin", "PF 1"),
                                platform_dest=t.get("platform_dest", "PF 1"),
                                live_delay_mins=int(t.get("delay_minutes", 0)),
                                live_status=t.get("status", "On Time"),
                                is_live=True,
                                data_source="railradar_live"
                            ))
                        if results:
                            return results
            except Exception as e:
                logger.debug(f"RailRadar trains-between API unavailable: {e}")

        # High-fidelity verified schedule fallback
        return get_fallback_trains_between(from_c, to_c, date)

    async def get_train_schedule(self, train_no: str) -> Optional[TrainSchedule]:
        """Fetch full timetable and halts for a train."""
        clean_no = str(train_no).strip().split()[0]
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/trains/{clean_no}/schedule",
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if "halts" in data:
                            return TrainSchedule.model_validate(data)
            except Exception as e:
                logger.debug(f"RailRadar schedule API unavailable: {e}")

        return SCHEDULE_DATABASE.get(clean_no)

    async def get_live_running_status(
        self, train_no: str, date: Optional[str] = None
    ) -> Optional[LiveRunningStatus]:
        """Fetch live running status & delay info."""
        clean_no = str(train_no).strip().split()[0]
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/trains/{clean_no}/live",
                        params={"date": date or ""},
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return LiveRunningStatus(
                            train_number=clean_no,
                            train_name=data.get("train_name", f"Train {clean_no}"),
                            train_type=data.get("train_type", "Express"),
                            current_station=data.get("current_station", "En Route"),
                            current_status=data.get("status", "Running"),
                            delay_minutes=int(data.get("delay_minutes", 0)),
                            speed_kmh=data.get("speed_kmh"),
                            last_reported_time=data.get("last_reported_time", ""),
                            next_station=data.get("next_station"),
                            eta_destination=data.get("eta", "On Time"),
                            is_live=True,
                            data_source="railradar_live"
                        )
            except Exception as e:
                logger.debug(f"RailRadar live status API unavailable: {e}")

        return get_fallback_live_status(clean_no)

    async def get_station_board(
        self, station_code: str, hours: int = 4
    ) -> List[StationBoardItem]:
        """Fetch live station board."""
        code = station_code.upper().strip()
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        f"{self.base_url}/stations/{code}/live-board",
                        params={"hours": hours},
                        headers=self._get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        items = data if isinstance(data, list) else data.get("departures", [])
                        results = []
                        for item in items:
                            results.append(StationBoardItem(
                                train_number=item.get("train_number", ""),
                                train_name=item.get("train_name", ""),
                                train_type=item.get("train_type", "Express"),
                                origin_code=item.get("origin_code", code),
                                destination_code=item.get("destination_code", ""),
                                destination_name=item.get("destination_name", ""),
                                scheduled_time=item.get("scheduled_time", ""),
                                expected_time=item.get("expected_time", ""),
                                platform=item.get("platform", "PF 1"),
                                status=item.get("status", "On Time"),
                                delay_minutes=int(item.get("delay_minutes", 0)),
                                is_live=True
                            ))
                        if results:
                            return results
            except Exception as e:
                logger.debug(f"RailRadar station board API unavailable: {e}")

        return get_fallback_station_board(code)

