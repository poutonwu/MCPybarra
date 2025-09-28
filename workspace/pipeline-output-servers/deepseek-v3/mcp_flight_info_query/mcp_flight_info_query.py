import sys
import httpx
import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import os
# Initialize FastMCP server
mcp = FastMCP("duffeld_flight_mcp")
DUFFEL_API_TOKEN=os.getenv("DUFFEL_API_TOKEN")
# Constants
DUFFELD_API_BASE = "https://api.duffeld.com"
USER_AGENT = "duffeld-flight-app/1.0 (contact@example.com)"

# Shared HTTP client
client = httpx.AsyncClient(
    base_url=DUFFELD_API_BASE,
    headers={"User-Agent": USER_AGENT}
)

# Data Models
class FlightSegment(BaseModel):
    departure: str
    destination: str
    date: str

class FlightOffer(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float
    flight_number: str

class OfferDetails(BaseModel):
    airline: str
    flight_details: Dict[str, Any]
    price_breakdown: Dict[str, Any]
    baggage_allowance: Dict[str, Any]

class MultiCitySegment(BaseModel):
    departure: str
    destination: str
    date: str

# Tools
@mcp.tool()
async def search_flights(
    departure: str,
    destination: str,
    date: str,
    cabin_class: str = "economy",
    trip_type: str = "one-way",
    return_date: Optional[str] = None
) -> str:
    """
    Queries flight information based on departure, destination, date, cabin class, and trip type.

    Args:
        departure: IATA code or name of the departure city/airport.
        destination: IATA code or name of the destination city/airport.
        date: Departure date in YYYY-MM-DD format.
        cabin_class: Cabin class (e.g., "economy", "business", "first"). Defaults to "economy".
        trip_type: Type of trip ("one-way", "round-trip", "multi-city").
        return_date: Return date for round-trip flights in YYYY-MM-DD format. Required if trip_type is "round-trip".

    Returns:
        JSON array of flight objects.

    Raises:
        ValueError: If parameters are invalid.
        httpx.HTTPStatusError: If API request fails.
    """
    try:
        # Validate parameters
        if trip_type == "round-trip" and not return_date:
            raise ValueError("return_date is required for round-trip flights")
        if trip_type not in ["one-way", "round-trip", "multi-city"]:
            raise ValueError("Invalid trip_type specified")

        # Prepare request
        params = {
            "departure": departure,
            "destination": destination,
            "date": date,
            "cabin_class": cabin_class,
            "trip_type": trip_type
        }
        if return_date:
            params["return_date"] = return_date

        response = await client.get("/flights/search", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to search flights: {str(e)}")

@mcp.tool()
async def get_offer_details(offer_id: str) -> str:
    """
    Retrieves detailed information for a specific flight offer.

    Args:
        offer_id: Unique identifier for the flight offer.

    Returns:
        JSON object containing detailed offer information.

    Raises:
        ValueError: If offer_id is invalid.
        httpx.HTTPStatusError: If API request fails.
    """
    if not offer_id or not isinstance(offer_id, str):
        raise ValueError("Invalid offer_id provided")

    try:
        response = await client.get(f"/offers/{offer_id}")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get offer details: {str(e)}")

@mcp.tool()
async def search_multi_city(
    segments: List[Dict[str, str]],
    cabin_class: str = "economy"
) -> str:
    """
    Handles complex multi-city flight queries.

    Args:
        segments: List of flight segments, each with departure, destination, and date.
        cabin_class: Cabin class (e.g., "economy", "business", "first"). Defaults to "economy".

    Returns:
        JSON array of flight combinations.

    Raises:
        ValueError: If segments are invalid.
        httpx.HTTPStatusError: If API request fails.
    """
    try:
        # Validate segments
        if not segments or not isinstance(segments, list):
            raise ValueError("At least one segment is required")
        
        for segment in segments:
            if not all(key in segment for key in ["departure", "destination", "date"]):
                raise ValueError("Each segment must contain departure, destination, and date")

        # Prepare request
        payload = {
            "segments": segments,
            "cabin_class": cabin_class
        }

        response = await client.post("/flights/multi-city", json=payload)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to search multi-city flights: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()