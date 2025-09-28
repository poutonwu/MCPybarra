import os
import re
import sys
import asyncio
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("duffeld_flight_info")

# Base URL for the flight API
FLIGHT_API_BASE = "https://api.flightdata.com"

# Proxy configuration
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Shared AsyncClient for HTTP requests
client = httpx.AsyncClient(base_url=FLIGHT_API_BASE, headers={"User-Agent": "flight-info-app/1.0"})

@mcp.tool()
async def search_flights(departure: str, destination: str, date: str, cabin_class: str, trip_type: str) -> str:
    """
    Queries flight information based on departure, destination, date, cabin class, and trip type.

    Args:
        departure (str): The airport code or city for departure (e.g., "JFK").
        destination (str): The airport code or city for arrival (e.g., "LAX").
        date (str): Travel date in "YYYY-MM-DD" format.
        cabin_class (str): Cabin class (e.g., "economy", "business", "first").
        trip_type (str): Type of trip ("one-way", "round-trip", "multi-city").

    Returns:
        str: JSON string containing flight details.

    Example:
        search_flights(departure="JFK", destination="LAX", date="2023-12-25", cabin_class="economy", trip_type="one-way")
    """
    try:
        # Validate input parameters
        if not re.match(r"^[A-Z]{3}$", departure):
            raise ValueError(f"Invalid departure code: {departure}")
        if not re.match(r"^[A-Z]{3}$", destination):
            raise ValueError(f"Invalid destination code: {destination}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            raise ValueError(f"Invalid date format: {date}")
        if cabin_class not in ["economy", "business", "first"]:
            raise ValueError(f"Invalid cabin class: {cabin_class}")
        if trip_type not in ["one-way", "round-trip", "multi-city"]:
            raise ValueError(f"Invalid trip type: {trip_type}")

        # Perform the API request
        response = await client.get(
            "/flights/search",
            params={
                "departure": departure,
                "destination": destination,
                "date": date,
                "cabin_class": cabin_class,
                "trip_type": trip_type
            }
        )
        response.raise_for_status()
        return response.text

    except httpx.RequestError as exc:
        return json.dumps({"error": f"Request error: {exc}"})
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": f"HTTP error: {exc.response.status_code}"})
    except ValueError as exc:
        return json.dumps({"error": str(exc)})

@mcp.tool()
async def get_offer_details(offer_id: str) -> str:
    """
    Retrieves detailed information about a specific flight offer.

    Args:
        offer_id (str): Unique identifier for the flight offer.

    Returns:
        str: JSON string with detailed flight information.

    Example:
        get_offer_details(offer_id="12345")
    """
    try:
        # Validate input parameters
        if not offer_id or not offer_id.strip():
            raise ValueError("Offer ID cannot be empty.")

        # Perform the API request
        response = await client.get(f"/offers/{offer_id}")
        response.raise_for_status()
        return response.text

    except httpx.RequestError as exc:
        return json.dumps({"error": f"Request error: {exc}"})
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": f"HTTP error: {exc.response.status_code}"})
    except ValueError as exc:
        return json.dumps({"error": str(exc)})

@mcp.tool()
async def search_multi_city(segments: list) -> str:
    """
    Handles searches for multi-city flight itineraries.

    Args:
        segments (list): A list of trip segments where each segment is a dictionary containing:
            - departure (str): Departure airport or city.
            - destination (str): Destination airport or city.
            - date (str): Travel date in "YYYY-MM-DD" format.

    Returns:
        str: JSON string containing multi-city flight options.

    Example:
        search_multi_city(segments=[
            {"departure": "JFK", "destination": "LAX", "date": "2023-12-25"},
            {"departure": "LAX", "destination": "SFO", "date": "2023-12-30"}
        ])
    """
    try:
        # Validate input parameters
        if not segments or not isinstance(segments, list):
            raise ValueError("Segments must be a non-empty list.")

        for segment in segments:
            if not re.match(r"^[A-Z]{3}$", segment.get("departure", "")):
                raise ValueError(f"Invalid departure code in segment: {segment}")
            if not re.match(r"^[A-Z]{3}$", segment.get("destination", "")):
                raise ValueError(f"Invalid destination code in segment: {segment}")
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", segment.get("date", "")):
                raise ValueError(f"Invalid date format in segment: {segment}")

        # Perform the API request
        response = await client.post("/flights/multi-city", json={"segments": segments})
        response.raise_for_status()
        return response.text

    except httpx.RequestError as exc:
        return json.dumps({"error": f"Request error: {exc}"})
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": f"HTTP error: {exc.response.status_code}"})
    except ValueError as exc:
        return json.dumps({"error": str(exc)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()