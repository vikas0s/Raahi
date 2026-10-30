"""
Routing Manager for Raahi Multi-Modal Mobility Platform.
Orchestrates routing providers, selects coverage, and enforces origin/destination invariants.
"""
import logging
from typing import List, Optional, Tuple

from .base import BaseRoutingProvider
from .local_transit_provider import local_transit_provider_instance
from .rail_connect_provider import rail_connect_provider_instance
from .global_road_provider import global_road_provider_instance
from ..models import CanonicalJourneyRequest, ResolvedPlace, RouteItinerary

logger = logging.getLogger("raahi.routing.manager")

class RoutingManager:
    def __init__(self):
        self.providers: List[BaseRoutingProvider] = [
            local_transit_provider_instance,
            rail_connect_provider_instance,
            global_road_provider_instance
        ]

    def plan_canonical_journey(self, request: CanonicalJourneyRequest) -> Tuple[List[RouteItinerary], str]:
        """
        Plans journey by querying the best suited provider(s) and enforcing route validation.
        Returns (validated_routes, coverage_type).
        Coverage types: 'full_transit', 'intercity_rail', 'road_only', 'unsupported'.
        """
        origin = request.origin
        dest = request.destination

        # 1. Validation check on coordinates
        if origin.lat == 0.0 and origin.lon == 0.0 or dest.lat == 0.0 and dest.lon == 0.0:
            return [], "unsupported"

        candidate_routes: List[RouteItinerary] = []
        coverage_type = "road_only"

        # Check Local Public Transit first (highest fidelity multi-modal in supported cities)
        if local_transit_provider_instance.can_route(origin, dest):
            transit_routes = local_transit_provider_instance.plan_route(request)
            if transit_routes:
                candidate_routes.extend(transit_routes)
                coverage_type = "full_transit"

        # If not local transit or intercity, check RailConnect
        if not candidate_routes and rail_connect_provider_instance.can_route(origin, dest):
            rail_routes = rail_connect_provider_instance.plan_route(request)
            if rail_routes:
                candidate_routes.extend(rail_routes)
                coverage_type = "intercity_rail"

        # If still no routes or if road alternatives are needed, use Global Road Provider
        if not candidate_routes:
            if global_road_provider_instance.can_route(origin, dest):
                road_routes = global_road_provider_instance.plan_route(request)
                if road_routes:
                    candidate_routes.extend(road_routes)
                    coverage_type = "road_only"
            else:
                coverage_type = "unsupported"

        # 2. STRICT INVARIANT VALIDATION: Reject any route with mismatched or reversed endpoints
        validated_routes = [r for r in candidate_routes if self._validate_route_endpoints(r, origin, dest)]

        # 3. Sort by user preferences
        validated_routes = self._sort_routes(validated_routes, request)

        return validated_routes, coverage_type

    def _validate_route_endpoints(self, route: RouteItinerary, origin: ResolvedPlace, dest: ResolvedPlace) -> bool:
        """
        Ensures that the route starts at the requested origin and ends at the requested destination.
        Rejects routes that have endpoints reversed or pointing to an unrelated place.
        """
        if not route.legs:
            return False

        first_leg = route.legs[0]
        last_leg = route.legs[-1]

        # Coordinate tolerance (approx 5 km to allow for nearest transit stop boarding)
        orig_lat_diff = abs(first_leg.origin_coords[1] - origin.lat)
        orig_lon_diff = abs(first_leg.origin_coords[0] - origin.lon)
        dest_lat_diff = abs(last_leg.destination_coords[1] - dest.lat)
        dest_lon_diff = abs(last_leg.destination_coords[0] - dest.lon)

        # Check for reversed route: first leg starting at destination or last leg ending at origin!
        is_reversed = (
            abs(first_leg.origin_coords[1] - dest.lat) < 0.02 and
            abs(last_leg.destination_coords[1] - origin.lat) < 0.02
        )
        if is_reversed and orig_lat_diff > 0.05:
            logger.error("REJECTED ROUTE: Provider returned reversed route! (starts at dest instead of orig)")
            return False

        # Tolerance: must be within reasonable boarding radius (< ~6.0 km)
        if orig_lat_diff > 0.15 or orig_lon_diff > 0.15 or dest_lat_diff > 0.15 or dest_lon_diff > 0.15:
            # Check name similarity as fallback
            orig_name_clean = origin.name.lower()
            dest_name_clean = dest.name.lower()
            leg_orig_clean = first_leg.origin_name.lower()
            leg_dest_clean = last_leg.destination_name.lower()

            if orig_name_clean not in leg_orig_clean and leg_orig_clean not in orig_name_clean:
                logger.warning("REJECTED ROUTE: Origin mismatch: '%s' vs '%s'", origin.name, first_leg.origin_name)
                return False
            if dest_name_clean not in leg_dest_clean and leg_dest_clean not in dest_name_clean:
                logger.warning("REJECTED ROUTE: Destination mismatch: '%s' vs '%s'", dest.name, last_leg.destination_name)
                return False

        return True

    def _sort_routes(self, routes: List[RouteItinerary], req: CanonicalJourneyRequest) -> List[RouteItinerary]:
        prefs = req.preferences
        if prefs.cheapest:
            return sorted(routes, key=lambda r: (0 if r.service_available else 1, r.total_fare_inr, r.total_duration_minutes))
        elif prefs.less_walking:
            return sorted(routes, key=lambda r: (0 if r.service_available else 1, r.walking_distance_meters, r.total_duration_minutes))
        elif prefs.less_crowded:
            crowd_rank = {"Low": 1, "Moderate": 2, "High": 3, "Very High": 4}
            return sorted(routes, key=lambda r: (0 if r.service_available else 1, crowd_rank.get(r.overall_crowd, 2), r.total_duration_minutes))
        elif prefs.fewer_transfers:
            return sorted(routes, key=lambda r: (0 if r.service_available else 1, r.transfers_count, r.total_duration_minutes))
        else:
            # Default fastest
            return sorted(routes, key=lambda r: (0 if r.service_available else 1, r.total_duration_minutes, r.total_fare_inr))

routing_manager_instance = RoutingManager()

