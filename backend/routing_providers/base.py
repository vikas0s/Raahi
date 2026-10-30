"""
Base definitions and interfaces for Raahi Routing Providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import CanonicalJourneyRequest, ResolvedPlace, RouteItinerary

class BaseRoutingProvider(ABC):
    """
    Abstract interface for all transit and routing providers in Raahi.
    """
    name: str = "base_provider"
    coverage_description: str = "Base routing provider"

    @abstractmethod
    def can_route(self, origin: ResolvedPlace, destination: ResolvedPlace) -> bool:
        """
        Determines whether this provider supports routing between the given endpoints.
        """
        pass

    @abstractmethod
    def plan_route(self, request: CanonicalJourneyRequest) -> List[RouteItinerary]:
        """
        Calculates and returns valid route alternatives matching the canonical request.
        Must respect origin and destination order invariant.
        """
        pass

