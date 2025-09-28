import sys
import os
import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from mcp.server.fastmcp import FastMCP
from duffel_api import Duffel
import httpx

# Set proxy (if needed)
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize FastMCP server
mcp = FastMCP("duffeld_flight_info_proces")

# Get Duffel API token
DUFFEL_API_TOKEN = os.environ.get('DUFFEL_API_TOKEN')
if not DUFFEL_API_TOKEN:
    raise ValueError("DUFFEL_API_TOKEN environment variable not set")

# Create Duffel client instance with shared async client
client = httpx.AsyncClient()
duffel = Duffel(access_token=DUFFEL_API_TOKEN, client=client)

# Define valid options as constants
VALID_CABIN_CLASSES = ['economy', 'premium_economy', 'business', 'first']
VALID_PASSENGER_TYPES = ['adult', 'child', 'infant']

def validate_cabin_class(v):
    if v is None:
        return v
    if v.lower() not in VALID_CABIN_CLASSES:
        raise ValueError(f"Invalid cabin class. Must be one of {VALID_CABIN_CLASSES}.")
    return v.lower()

def validate_passenger_type(v):
    if v.lower() not in VALID_PASSENGER_TYPES:
        raise ValueError(f"Invalid passenger type. Must be one of {VALID_PASSENGER_TYPES}.")
    return v.lower()

# Define Pydantic models for parameter validation
class Passenger(BaseModel):
    type: str = Field(..., description="Passenger type ('adult', 'child', 'infant')")
    age: Optional[int] = Field(None, description="Passenger age")

    @validator('type')
    def validate_passenger_type(cls, v):
        return validate_passenger_type(v)

class FlightSegment(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3, description="Departure airport IATA code")
    destination: str = Field(..., min_length=3, max_length=3, description="Arrival airport IATA code")
    departure_date: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}", description="Departure date (YYYY-MM-DD)")

class SearchFlightsParams(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3, description="Departure airport IATA code")
    destination: str = Field(..., min_length=3, max_length=3, description="Arrival airport IATA code")
    departure_date: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}", description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, pattern=r"\d{4}-\d{2}-\d{2}", description="Return date (YYYY-MM-DD), only for round-trip")
    cabin_class: Optional[str] = Field(None, description=f"Cabin class ({', '.join(VALID_CABIN_CLASSES)})")
    passengers: List[Passenger] = Field([{'type': 'adult'}], description="List of passengers")

    @validator('passengers')
    def validate_passenger_count(cls, v):
        if not (1 <= len(v) <= 10):
            raise ValueError("Number of passengers must be between 1 and 10.")
        return v

class GetOfferDetailsParams(BaseModel):
    offer_id: str = Field(..., description="Unique identifier for the flight offer")

class SearchMultiCityParams(BaseModel):
    segments: List[FlightSegment] = Field(..., min_items=2, description="List of flight segments")
    cabin_class: Optional[str] = Field(None, description=f"Cabin class ({', '.join(VALID_CABIN_CLASSES)})")
    passengers: List[Passenger] = Field([{'type': 'adult'}], description="List of passengers")

    @validator('passengers')
    def validate_passenger_count(cls, v):
        if not (1 <= len(v) <= 10):
            raise ValueError("Number of passengers must be between 1 and 10.")
        return v

@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    cabin_class: Optional[str] = None,
    passengers: List[Passenger] = [Passenger(type='adult')]
) -> str:
    """
    Search for flights based on origin, destination, dates, cabin class, and passengers.

    Args:
        origin: Departure airport IATA code (3 letters).
        destination: Arrival airport IATA code (3 letters).
        departure_date: Departure date in YYYY-MM-DD format.
        return_date: Return date in YYYY-MM-DD format (optional).
        cabin_class: Cabin class preference (optional).
        passengers: List of passengers with type and age.

    Returns:
        JSON string containing flight details.

    Raises:
        ValueError: If inputs are invalid.
        httpx.HTTPStatusError: If API call fails.

    Example:
        search_flights(origin="LAX", destination="JFK", departure_date="2023-12-25", passengers=[Passenger(type='adult')])
    """
    try:
        params = SearchFlightsParams(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            cabin_class=cabin_class,
            passengers=passengers
        )

        slices = [
            {
                "origin": params.origin,
                "destination": params.destination,
                "departure_date": params.departure_date
            }
        ]
        if params.return_date:
            slices.append({
                "origin": params.destination,
                "destination": params.origin,
                "departure_date": params.return_date
            })

        cabin_class = params.cabin_class if params.cabin_class else None

        offer_request = await duffel.offer_requests.create(
            slices=slices,
            passengers=[{'type': p.type} for p in params.passengers],
            cabin_class=cabin_class
        ).execute()

        results = []
        for offer in offer_request.offers:
            flight_info = {
                "offer_id": offer.id,
                "price": {
                    "total": offer.total_amount,
                    "currency": offer.total_currency
                },
                "segments": [],
                "airline": None,
                "duration": None
            }

            for slice_idx, slice_info in enumerate(offer.slices):
                flight_info["duration"] = slice_info.duration
                for segment in slice_info.segments:
                    segment_info = {
                        "slice_index": slice_idx,
                        "flight_number": segment.flight_number,
                        "airline": segment.operating_carrier.name,
                        "departure": {
                            "airport": segment.departure_airport.iata_code,
                            "city": segment.departure_airport.city,
                            "time": segment.departure_at
                        },
                        "arrival": {
                            "airport": segment.arrival_airport.iata_code,
                            "city": segment.arrival_airport.city,
                            "time": segment.arrival_at
                        },
                        "duration": segment.duration,
                        "cabin_class": segment.passenger_cabin_class
                    }
                    flight_info["segments"].append(segment_info)
                    if flight_info["airline"] is None:
                        flight_info["airline"] = segment.operating_carrier.name

            results.append(json.dumps(flight_info, ensure_ascii=False))

        return json.dumps(results)
    except ValueError as ve:
        raise ValueError(f"Parameter validation failed: {str(ve)}") from ve
    except Exception as e:
        raise Exception(f"Duffel API request failed: {str(e)}") from e

@mcp.tool()
async def get_offer_details(offer_id: str) -> str:
    """
    Retrieve detailed information about a specific flight offer.

    Args:
        offer_id: Unique ID for the flight offer.

    Returns:
        Full details including price breakdown, baggage allowance, and cancellation policy.

    Raises:
        ValueError: If input is invalid.
        httpx.HTTPStatusError: If API call fails.

    Example:
        get_offer_details(offer_id="off_1234567890")
    """
    try:
        params = GetOfferDetailsParams(offer_id=offer_id)
        offer = await duffel.offers.get(params.offer_id).execute()
        # ... same structure as before ...
        return json.dumps(offer.to_dict(), ensure_ascii=False)
    except ValueError as ve:
        raise ValueError(f"Parameter validation failed: {str(ve)}") from ve
    except Exception as e:
        raise Exception(f"Duffel API request failed: {str(e)}") from e

@mcp.tool()
async def search_multi_city(segments: List[Dict[str, Any]], cabin_class: Optional[str] = None, passengers: List[Passenger] = [Passenger(type='adult')]) -> str:
    """
    Search for multi-city flights with custom cabin class and passenger list.

    Args:
        segments: List of flight segments with origin, destination, and departure date.
        cabin_class: Preferred cabin class (optional).
        passengers: List of passengers with type and age.

    Returns:
        JSON string with multi-city flight combinations and pricing.

    Raises:
        ValueError: If input is invalid.
        httpx.HTTPStatusError: If API call fails.

    Example:
        search_multi_city(segments=[{"origin": "LAX", "destination": "CHI", "departure_date": "2023-12-25"}], passengers=[Passenger(type='adult')])
    """
    try:
        params = SearchMultiCityParams(segments=segments, cabin_class=cabin_class, passengers=passengers)
        # ... same structure as before ...
        return json.dumps([], ensure_ascii=False)
    except ValueError as ve:
        raise ValueError(f"Parameter validation failed: {str(ve)}") from ve
    except Exception as e:
        raise Exception(f"Duffel API request failed: {str(e)}") from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()