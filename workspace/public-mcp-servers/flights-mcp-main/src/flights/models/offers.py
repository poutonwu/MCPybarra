"""Offer-related models."""

from pydantic import BaseModel, Field

class OfferDetails(BaseModel):
    """Model for getting detailed offer information."""
    offer_id: str = Field(..., description="The ID of the offer to get details for") 