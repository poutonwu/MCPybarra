"""Flight segment models."""

from pydantic import BaseModel, Field

class FlightSegment(BaseModel):
    """Model for a single flight segment in a multi-city trip."""
    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code") 
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)") 