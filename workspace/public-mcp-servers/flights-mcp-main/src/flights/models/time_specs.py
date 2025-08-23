"""Time specification models."""

from pydantic import BaseModel, Field

class TimeSpec(BaseModel):
    """Model for time range specification."""
    from_time: str = Field(..., description="Start time (HH:MM)", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    to_time: str = Field(..., description="End time (HH:MM)", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$") 