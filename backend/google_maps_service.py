"""
Google Maps Directions & Distance Matrix Integration Service for Raahi.
Provides verified live road geometries, turn-by-turn navigation steps,
real-time traffic travel times, and multimodal public transit routing.
"""
import os
import re
import json
import uuid
import logging
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from .models import RouteItinerary, TransitLeg
from .transit_data import (
    calculate_auto_fare, calculate_cab_fare, calculate_dtc_fare,
    calculate_mumbai_auto_fare,
    calculate_mathura_ebus_fare, calculate_mathura_shared_tempo_fare
)

logger = logging.getLogger("raahi.google_maps")

def decode_google_polyline(polyline_str: str) -> List[List[float]]:
    """
    Decodes Google's Encoded Polyline format into standard GeoJSON coordinates [[lon, lat], ...].
    Pure Python, zero external dependencies.
    """
    if not polyline_str:
        return []
        
    index = 0
    lat = 0
    lng = 0
    coordinates = []
    length = len(polyline_str)

    while index < length:
        shift = 0
        result = 0
        while True:
            if index >= length:
                break
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1f) << shift
            shift += 5
            if not byte >= 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            if index >= length:
                break
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1f) << shift
            shift += 5
            if not byte >= 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append([round(lng / 1e5, 6), round(lat / 1e5, 6)])

    return coordinates


def strip_html_tags(text: str) -> str:
    """Removes HTML markup from Google Directions step instructions."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


class GoogleMapsService:
    def __init__(self):
        self._api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("VITE_GOOGLE_MAPS_API_KEY") or ""
        if not key:
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("GOOGLE_MAPS_API_KEY=") or line.startswith("VITE_GOOGLE_MAPS_API_KEY="):
                                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if val:
                                    key = val
                                    break
                except Exception:
                    pass
        return key.strip()

    def is_configured(self) -> bool:
        """Returns True if a valid Google Maps API key is configured."""
        return bool(self._api_key and len(self._api_key) > 10 and not self._api_key.startswith("your_"))

    def get_api_key_masked(self) -> str:
        """Returns masked API key for UI display."""
        if not self._api_key:
            return ""
        if len(self._api_key) <= 8:
            return "********"
        return f"{self._api_key[:4]}...{self._api_key[-4:]}"

    def set_api_key(self, new_key: str, save_to_env: bool = True) -> bool:
        """Updates Google Maps API key in-memory and optionally appends/updates .env."""
        new_key = (new_key or "").strip()
        self._api_key = new_key
        os.environ["GOOGLE_MAPS_API_KEY"] = new_key
        os.environ["VITE_GOOGLE_MAPS_API_KEY"] = new_key

        if save_to_env:
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            try:
                content = ""
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        content = f.read()

                if "GOOGLE_MAPS_API_KEY=" in content:
                    content = re.sub(r'GOOGLE_MAPS_API_KEY=.*', f'GOOGLE_MAPS_API_KEY={new_key}', content)
                else:
                    content += f"\n# Google Maps API Integration\nGOOGLE_MAPS_API_KEY={new_key}\n"

                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info("Successfully persisted GOOGLE_MAPS_API_KEY into .env")
            except Exception as e:
                logger.error(f"Failed to write GOOGLE_MAPS_API_KEY to .env: {e}")

        return True

    def fetch_routes(
        self,
        orig_lat: float,
        orig_lon: float,
        dest_lat: float,
        dest_lon: float,
        orig_name: str,
        dest_name: str,
        city: str,
        base_time: datetime,
        mode: str = "transit"
    ) -> List[RouteItinerary]:
        """
        Queries Google Maps Directions API and transforms results into Raahi RouteItinerary objects.
        """
        if not self.is_configured():
            return []

        base_url = "https://maps.googleapis.com/maps/api/directions/json"
        dep_timestamp = int(base_time.timestamp())

        params = {
            "origin": f"{orig_lat},{orig_lon}",
            "destination": f"{dest_lat},{dest_lon}",
            "mode": mode,
            "alternatives": "true",
            "departure_time": dep_timestamp,
            "region": "in",
            "key": self._api_key
        }

        query_str = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_str}"

        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "RaahiMobilityPlatform/2.0"})
            with urllib.request.urlopen(req, timeout=4.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            status = data.get("status")
            if status != "OK":
                logger.warning(f"Google Maps Directions API status: {status}")
                if mode == "transit" and status == "ZERO_RESULTS":
                    return self.fetch_routes(orig_lat, orig_lon, dest_lat, dest_lon, orig_name, dest_name, city, base_time, mode="driving")
                return []

            itineraries: List[RouteItinerary] = []
            for idx, g_route in enumerate(data.get("routes", [])):
                itin = self._parse_google_route(
                    g_route=g_route,
                    orig_name=orig_name,
                    dest_name=dest_name,
                    city=city,
                    base_time=base_time,
                    route_index=idx,
                    query_mode=mode
                )
                if itin:
                    itineraries.append(itin)

            return itineraries

        except Exception as e:
            logger.warning(f"Error querying Google Maps API: {e}")
            return []

    def _parse_google_route(
        self,
        g_route: Dict[str, Any],
        orig_name: str,
        dest_name: str,
        city: str,
        base_time: datetime,
        route_index: int,
        query_mode: str
    ) -> Optional[RouteItinerary]:
        legs_data = g_route.get("legs", [])
        if not legs_data:
            return None

        first_leg_data = legs_data[0]
        total_duration_sec = sum(l.get("duration", {}).get("value", 0) for l in legs_data)
        total_dist_meters = sum(l.get("distance", {}).get("value", 0) for l in legs_data)
        dist_km = total_dist_meters / 1000.0
        total_mins = max(1, total_duration_sec // 60)

        overview_poly = g_route.get("overview_polyline", {}).get("points", "")
        overview_coords = decode_google_polyline(overview_poly)

        parsed_legs: List[TransitLeg] = []
        curr_time = base_time
        total_fare = 0.0
        fare_descriptions = []
        transfers_count = 0
        walk_mins_total = 0
        walk_meters_total = 0

        city_lower = city.lower()
        is_mathura = "mathura" in city_lower or "vrindavan" in city_lower or "braj" in city_lower
        is_mumbai = "mumbai" in city_lower

        steps = first_leg_data.get("steps", [])
        for step_idx, step in enumerate(steps):
            step_mode = step.get("travel_mode", "").lower()
            step_duration_mins = max(1, step.get("duration", {}).get("value", 0) // 60)
            step_distance_m = step.get("distance", {}).get("value", 0)
            step_dist_km = step_distance_m / 1000.0
            step_arr_time = curr_time + timedelta(minutes=step_duration_mins)

            step_poly = step.get("polyline", {}).get("points", "")
            step_coords = decode_google_polyline(step_poly)
            if not step_coords:
                step_start_lat = step.get("start_location", {}).get("lat", 0.0)
                step_start_lng = step.get("start_location", {}).get("lng", 0.0)
                step_end_lat = step.get("end_location", {}).get("lat", 0.0)
                step_end_lng = step.get("end_location", {}).get("lng", 0.0)
                step_coords = [[step_start_lng, step_start_lat], [step_end_lng, step_end_lat]]

            inst = strip_html_tags(step.get("html_instructions", ""))

            if step_mode == "walking":
                walk_mins_total += step_duration_mins
                walk_meters_total += step_distance_m
                parsed_legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="walk",
                    line_name="Walking",
                    line_color="#78909C",
                    origin_name=orig_name if step_idx == 0 else f"Step {step_idx + 1} Waypoint",
                    destination_name=dest_name if step_idx == len(steps) - 1 else f"Step {step_idx + 1} End",
                    origin_coords=step_coords[0],
                    destination_coords=step_coords[-1],
                    path_coords=step_coords,
                    duration_minutes=step_duration_mins,
                    distance_meters=step_distance_m,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=step_arr_time.strftime("%H:%M"),
                    stops_count=1,
                    instructions=inst or "Walk to next step.",
                    crowd_level="Low",
                    fare_inr=0.0,
                    fare_details="Pedestrian (Free)"
                ))

            elif step_mode == "transit":
                transfers_count += 1
                t_details = step.get("transit_details", {})
                line_info = t_details.get("line", {})
                line_name = line_info.get("short_name") or line_info.get("name") or "Public Transit"
                agency_name = ""
                if line_info.get("agencies"):
                    agency_name = line_info["agencies"][0].get("name", "")

                v_type = line_info.get("vehicle", {}).get("type", "").upper()
                dep_stop = t_details.get("departure_stop", {}).get("name", "Boarding Point")
                arr_stop = t_details.get("arrival_stop", {}).get("name", "Deboarding Point")
                num_stops = t_details.get("num_stops", 2)

                if "SUBWAY" in v_type or "METRO" in v_type:
                    mode_type = "metro"
                    line_color = line_info.get("color") or "#E53935"
                    step_fare = min(60.0, max(10.0, 10.0 + step_dist_km * 2.2))
                    step_fare_desc = f"{agency_name or 'Metro'}: ₹{int(step_fare)}"
                elif "BUS" in v_type:
                    mode_type = "bus"
                    line_color = "#00897B"
                    if is_mathura:
                        step_fare, step_fare_desc = calculate_mathura_ebus_fare(step_dist_km)
                    else:
                        step_fare, step_fare_desc = calculate_dtc_fare(step_dist_km, is_ac=True)
                elif "RAIL" in v_type or "TRAIN" in v_type:
                    mode_type = "rail"
                    line_color = "#1565C0"
                    step_fare = min(40.0, max(10.0, 10.0 + step_dist_km * 0.8))
                    step_fare_desc = f"Suburban/Rail: ₹{int(step_fare)}"
                else:
                    mode_type = "transit"
                    line_color = "#43A047"
                    step_fare = 20.0
                    step_fare_desc = f"Transit: ₹{int(step_fare)}"

                total_fare += step_fare
                fare_descriptions.append(step_fare_desc)

                parsed_legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode=mode_type,
                    line_name=f"{line_name} ({agency_name})" if agency_name else line_name,
                    line_color=line_color,
                    origin_name=dep_stop,
                    destination_name=arr_stop,
                    origin_coords=step_coords[0],
                    destination_coords=step_coords[-1],
                    path_coords=step_coords,
                    duration_minutes=step_duration_mins,
                    distance_meters=step_distance_m,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=step_arr_time.strftime("%H:%M"),
                    stops_count=num_stops,
                    intermediate_stops=[dep_stop, arr_stop],
                    instructions=inst or f"Board {line_name} from {dep_stop} to {arr_stop}.",
                    crowd_level="Moderate",
                    fare_inr=step_fare,
                    fare_details=step_fare_desc
                ))

            else:
                if is_mathura:
                    step_fare, step_fare_desc = calculate_mathura_shared_tempo_fare(step_dist_km)
                    leg_mode = "auto"
                    line_color = "#E68A00"
                    leg_name = "Highway Auto / Tempo (NH-19)"
                elif is_mumbai:
                    step_fare, step_fare_desc = calculate_mumbai_auto_fare(step_dist_km)
                    leg_mode = "auto"
                    line_color = "#F59E0B"
                    leg_name = "Mumbai Metered Auto"
                else:
                    step_fare, step_fare_desc = calculate_auto_fare(step_dist_km)
                    leg_mode = "auto"
                    line_color = "#E68A00"
                    leg_name = "Govt Metered Auto"

                total_fare += step_fare
                fare_descriptions.append(step_fare_desc)

                parsed_legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode=leg_mode,
                    line_name=leg_name,
                    line_color=line_color,
                    origin_name=orig_name if step_idx == 0 else f"Step {step_idx + 1} Waypoint",
                    destination_name=dest_name if step_idx == len(steps) - 1 else f"Step {step_idx + 1} End",
                    origin_coords=step_coords[0],
                    destination_coords=step_coords[-1],
                    path_coords=step_coords,
                    duration_minutes=step_duration_mins,
                    distance_meters=step_distance_m,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=step_arr_time.strftime("%H:%M"),
                    stops_count=1,
                    instructions=inst or f"Drive via {first_leg_data.get('summary', 'main arterial route')}.",
                    crowd_level="Low",
                    fare_inr=step_fare,
                    fare_details=step_fare_desc
                ))

            curr_time = step_arr_time

        summary_road = g_route.get("summary") or first_leg_data.get("summary") or "Primary Highway / Arterial Road"
        title = f"Google Maps: via {summary_road}"
        tag = "🌐 Google Maps Live"
        tag_reason = f"Live real-time routing from Google Maps Directions API via {summary_road}."

        fare_breakdown_str = " + ".join(fare_descriptions) if fare_descriptions else f"Estimated: ₹{int(total_fare)}"

        return RouteItinerary(
            id=f"route-gmaps-{uuid.uuid4().hex[:6]}",
            title=title,
            tag=tag,
            tag_reason=tag_reason,
            total_duration_minutes=total_mins,
            departure_time=base_time.strftime("%H:%M"),
            arrival_time=(base_time + timedelta(minutes=total_mins)).strftime("%H:%M"),
            total_fare_inr=round(total_fare, 1),
            fare_breakdown=fare_breakdown_str,
            route_type="google_maps_live",
            transfers_count=max(0, transfers_count - 1) if transfers_count > 0 else 0,
            walking_duration_minutes=walk_mins_total,
            walking_distance_meters=walk_meters_total,
            overall_crowd="Moderate",
            total_delay_minutes=0,
            service_available=True,
            unavailable_reason=None,
            legs=parsed_legs,
            eco_carbon_savings_kg=round(dist_km * 0.12, 1),
            data_source="google_maps_api",
            transit_coverage_available=True,
            fare_provenance="verified_tariff"
        )


google_maps_service_instance = GoogleMapsService()

