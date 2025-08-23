"""Flight search models."""

from typing import Optional, List
from pydantic import BaseModel, Field
from .time_specs import TimeSpec

class FlightSearch(BaseModel):
    """Model for flight search parameters."""
    type: str = Field(..., description="Type of flight: 'one_way', 'round_trip', or 'multi_city'")
    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: str | None = Field(None, description="Return date for round trips (YYYY-MM-DD)")
    departure_time: TimeSpec | None = Field(None, description="Preferred departure time range")
    arrival_time: TimeSpec | None = Field(None, description="Preferred arrival time range")
    cabin_class: str = Field("economy", description="Cabin class (economy, business, first)")
    adults: int = Field(1, description="Number of adult passengers")
    max_connections: int = Field(None, description="Maximum number of connections (0 for non-stop)")
    additional_stops: Optional[List[dict]] = Field(None, description="Additional stops for multi-city trips") 