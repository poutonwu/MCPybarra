"""Flight search models."""

from .search import FlightSearch
from .multi_city import MultiCityRequest
from .segments import FlightSegment
from .offers import OfferDetails

__all__ = [
    'FlightSearch',
    'MultiCityRequest',
    'FlightSegment',
    'OfferDetails',
] 