import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from pyflightdata import FlightData
from typing import List, Dict

# Initialize FastMCP server
mcp = FastMCP("duffeld_flight_info")

# Initialize FlightData client
flight_data_client = FlightData()

# Environment variable for API key (if needed)
API_KEY = os.environ.get('FLIGHT_API_KEY')

@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    cabin_class: str = "Economy",
    flight_type: str = "one_way"
) -> str:
    """
    Queries flight information based on parameters such as origin, destination, date, and cabin class.

    Args:
        origin: The departure city or airport code (required).
        destination: The arrival city or airport code (required).
        departure_date: Departure date in 'YYYY-MM-DD' format (required).
        return_date: Return date in 'YYYY-MM-DD' format for round-trip queries (optional).
        cabin_class: Desired cabin class (e.g., 'Economy', 'Business') (optional).
        flight_type: Type of flight query ('one_way', 'round_trip', 'multi_city') (required).

    Returns:
        A JSON string containing a list of available flights with details on prices, timings, and airlines.

    Example:
        search_flights(
            origin="JFK",
            destination="LAX",
            departure_date="2023-12-01",
            return_date="2023-12-10",
            cabin_class="Business",
            flight_type="round_trip"
        )
    """
    try:
        # Validate inputs
        if not origin or not destination or not departure_date:
            raise ValueError("Missing required parameters: origin, destination, or departure_date.")
        
        if flight_type not in ("one_way", "round_trip"):
            raise ValueError("Unsupported flight type. Choose 'one_way' or 'round_trip'.")
        
        if flight_type == "round_trip" and not return_date:
            raise ValueError("Return date is required for round-trip queries.")

        # Authenticate if API key is required
        if API_KEY:
            flight_data_client.login(API_KEY)

        # Perform the flight search
        if flight_type == "one_way":
            flights = flight_data_client.get_flight_search(
                origin=origin,
                destination=destination,
                date=departure_date,
                cabin_class=cabin_class
            )
        elif flight_type == "round_trip":
            flights = flight_data_client.get_round_trip_search(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                cabin_class=cabin_class
            )

        # Convert result to JSON string
        return json.dumps(flights)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_offer_details(offer_id: str) -> str:
    """
    Retrieves detailed information about a specific flight offer.

    Args:
        offer_id: The unique identifier for the flight offer (required).

    Returns:
        A JSON string containing detailed information about the specified flight offer.

    Example:
        get_offer_details(offer_id="OFFER123456789")
    """
    try:
        # Validate input
        if not offer_id:
            raise ValueError("Missing required parameter: offer_id.")

        # Authenticate if API key is required
        if API_KEY:
            flight_data_client.login(API_KEY)

        # Fetch detailed offer information
        offer_details = flight_data_client.get_offer_details(offer_id)

        # Convert result to JSON string
        return json.dumps(offer_details)

    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_multi_city(cities: List[Dict[str, str]], cabin_class: str = "Economy") -> str:
    """
    Handles complex multi-city flight queries by planning an itinerary across several destinations.

    Args:
        cities: A list of dictionaries where each dictionary contains 'origin', 'destination', and 'departure_date' keys (required).
        cabin_class: Desired cabin class (optional).

    Returns:
        A JSON string containing a list of available multi-city flight options with relevant details.

    Example:
        search_multi_city(
            cities=[
                {"origin": "JFK", "destination": "LAX", "departure_date": "2023-12-01"},
                {"origin": "LAX", "destination": "SFO", "departure_date": "2023-12-05"}
            ],
            cabin_class="Business"
        )
    """
    try:
        # Validate inputs
        if not cities or not isinstance(cities, list) or len(cities) < 2:
            raise ValueError("Invalid or insufficient cities provided. At least two cities are required.")
        
        for city in cities:
            if not all(key in city for key in ("origin", "destination", "departure_date")):
                raise ValueError("Each city must contain 'origin', 'destination', and 'departure_date' keys.")

        # Authenticate if API key is required
        if API_KEY:
            flight_data_client.login(API_KEY)

        # Prepare the multi-city search payload
        formatted_cities = [
            {
                "origin": city['origin'],
                "destination": city['destination'],
                "date": city['departure_date']
            } for city in cities
        ]

        # Perform multi-city search
        multi_city_flights = flight_data_client.get_multi_city_search(
            cities=formatted_cities,
            cabin_class=cabin_class
        )

        # Convert result to JSON string
        return json.dumps(multi_city_flights)

    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()