"""Multi-city flight search models."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from .time_specs import TimeSpec
from .segments import FlightSegment

class MultiCityRequest(BaseModel):
    """Model for multi-city flight search."""
    type: Literal["multi_city"]
    segments: List[FlightSegment] = Field(..., min_items=2, description="Flight segments")
    cabin_class: str = Field("economy", description="Cabin class")
    adults: int = Field(1, description="Number of adult passengers")
    max_connections: int = Field(None, description="Maximum number of connections (0 for non-stop)")
    departure_time: TimeSpec | None = Field(None, description="Optional departure time range")
    arrival_time: TimeSpec | None = Field(None, description="Optional arrival time range") 