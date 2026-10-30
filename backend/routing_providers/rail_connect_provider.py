"""
Indian Railways RailConnect Provider for Intercity & Suburban Commuter Rail.
Connects Indian Railways and Suburban networks across Mumbai, Bengaluru, Delhi NCR, and Mathura.
"""
import math
import logging
from datetime import datetime
from typing import List, Optional

from .base import BaseRoutingProvider
from ..models import CanonicalJourneyRequest, ResolvedPlace, RouteItinerary
from ..rail.service import rail_service_instance

logger = logging.getLogger("raahi.routing.rail_connect")

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RailConnectProvider(BaseRoutingProvider):
    name = "railconnect"
    coverage_description = "Indian Railways national intercity and suburban network"

    def can_route(self, origin: ResolvedPlace, destination: ResolvedPlace) -> bool:
        # Both must be in India
        orig_country = (origin.country or "India").lower()
        dest_country = (destination.country or "India").lower()
        if "india" not in orig_country or "india" not in dest_country:
            return False

        dist = haversine_km(origin.lat, origin.lon, destination.lat, destination.lon)
        # Must be at least 3 km apart (for suburban commuter hops) and within India distance (< 3500 km)
        if dist < 3.0 or dist > 3500.0:
            return False

        city_hint = origin.city or destination.city
        s1 = rail_service_instance.find_nearest_rail_station(origin.lat, origin.lon, max_dist_km=30.0, city=city_hint)
        s2 = rail_service_instance.find_nearest_rail_station(destination.lat, destination.lon, max_dist_km=30.0, city=city_hint)
        return s1 is not None and s2 is not None and s1[0].code != s2[0].code

    def plan_route(self, request: CanonicalJourneyRequest) -> List[RouteItinerary]:
        origin = request.origin
        dest = request.destination
        dist_km = haversine_km(origin.lat, origin.lon, dest.lat, dest.lon)

        now = datetime.now()
        dep_str = request.departure_time or now.strftime("%H:%M")
        try:
            if ":" in dep_str and len(dep_str) <= 5:
                hh, mm = map(int, dep_str.split(":"))
                base_time = now.replace(hour=hh, minute=mm, second=0)
            else:
                base_time = datetime.fromisoformat(dep_str)
        except Exception:
            base_time = now

        origin_dict = {"name": origin.name, "lat": origin.lat, "lon": origin.lon, "city": origin.city}
        dest_dict = {"name": dest.name, "lat": dest.lat, "lon": dest.lon, "city": dest.city}
        target_city = origin.city or dest.city or "Delhi NCR"

        try:
            rail_routes = rail_service_instance.find_rail_routes_sync(
                orig_dict=origin_dict,
                dest_dict=dest_dict,
                base_time=base_time,
                dist_km=dist_km,
                city=target_city
            )
            for r in rail_routes:
                r.data_source = "indian_railways_irctc"
                r.transit_coverage_available = True
                r.fare_provenance = "verified_tariff"
            return rail_routes
        except Exception as e:
            logger.warning("RailConnect planning failed: %s", e)
            return []

rail_connect_provider_instance = RailConnectProvider()
