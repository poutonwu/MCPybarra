import os
import sys
import json
import re  # Fixed: Added missing import for regex functionality
from mcp.server.fastmcp import FastMCP
from duffel_api import Duffel

# Version: duffel-api==1.10.0
# It's recommended to install a specific version to ensure compatibility.
# pip install "duffel-api==1.10.0"

# --- Configuration and Initialization ---

# Initialize FastMCP Server
mcp = FastMCP("mcp_duffeld_flight_search")

# For security, fetch the Duffel API access token from environment variables.
# Hardcoding tokens is a security risk.
# Example: export DUFFEL_ACCESS_TOKEN='your_real_duffel_access_token'
DUFFEL_ACCESS_TOKEN = os.environ.get("DUFFEL_ACCESS_TOKEN", "REDACTED_SECRET")

# If the access token is not set, the server will fail at startup,
# which is a deliberate choice to enforce secure configuration.
if not DUFFEL_ACCESS_TOKEN:
    raise ValueError("DUFFEL_ACCESS_TOKEN environment variable not set. Please provide a valid Duffel API token.")

# Set up proxy if needed, which is good practice for corporate environments.
# Example: export HTTP_PROXY='http://127.0.0.1:7890'
if 'HTTP_PROXY' in os.environ:
    os.environ['HTTPS_PROXY'] = os.environ['HTTP_PROXY']

# Instantiate the Duffel client with explicit API version
try:
    duffel = Duffel(access_token=DUFFEL_ACCESS_TOKEN, api_version="v2")
except TypeError:
    # Fallback for older versions that don't support api_version parameter
    duffel = Duffel(access_token=DUFFEL_ACCESS_TOKEN)

# --- Tool Implementations ---

@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str = "economy",
    return_date: str = None,
) -> str:
    """Search for one-way or round-trip flights based on origin, destination, dates, and cabin class.

    To perform a round-trip search, provide both `departure_date` and `return_date`.
    If only `departure_date` is provided, a one-way search will be performed.

    Args:
        origin (str): The IATA code for the departure airport (e.g., "LHR").
        destination (str): The IATA code for the destination airport (e.g., "JFK").
        departure_date (str): The departure date in "YYYY-MM-DD" format.
        cabin_class (str): The cabin class. Valid options are "economy", "premium_economy",
                           "business", and "first". Defaults to "economy".
        return_date (str, optional): The return date in "YYYY-MM-DD" format.
                                     If provided, a round-trip search is executed.
                                     If omitted, a one-way search is performed.

    Returns:
        str: A JSON string containing a list of flight offers. Each offer includes price,
             flight times, airline, and a summary of the itinerary. Returns an empty
             list if no flights are found.

    Raises:
        ValueError: If the input parameters are invalid (e.g., incorrect date format).
        Exception: If the API call fails or another internal error occurs.
    """
    try:
        # --- Robustness: Input Validation ---
        if not all([origin, destination, departure_date]):
            raise ValueError("Missing required parameters: origin, destination, and departure_date must be provided.")

        if not re.match(r'^[A-Z]{3}$', origin):
            raise ValueError(f"Invalid origin IATA code: '{origin}'. Must be 3 uppercase letters (e.g., LHR).")
        if not re.match(r'^[A-Z]{3}$', destination):
            raise ValueError(f"Invalid destination IATA code: '{destination}'. Must be 3 uppercase letters (e.g., JFK).")

        if return_date and return_date < departure_date:
            raise ValueError("Return date cannot be earlier than departure date.")

        slices = [
            {"origin": origin, "destination": destination, "departure_date": departure_date},
        ]
        if return_date:
            slices.append(
                {"origin": destination, "destination": origin, "departure_date": return_date}
            )

        # --- Functionality: Core Logic ---
        offer_request = (
            duffel.offer_requests.create()
            .slices(slices)
            .passengers([{}])  # Search for one adult passenger
            .cabin_class(cabin_class)
            .execute()
        )

        # --- Performance: Use list comprehension for efficient serialization ---
        # --- Transparency: Include relevant information in response ---
        offers_list = [
            {
                "id": offer.id,
                "total_amount": offer.total_amount,
                "total_currency": offer.total_currency,
                "tax_amount": offer.tax_amount,
                "slices": [
                    {
                        "origin": s.origin.iata_code,
                        "destination": s.destination.iata_code,
                        "departure_date": s.departing_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "arrival_date": s.arriving_at.strftime('%Y-%m-%d %H:%M:%S'),
                        "carrier": s.operating_carrier.name,
                    }
                    for s in offer.slices
                ],
            }
            for offer in duffel.offers.list(offer_request.id)
        ]
        return json.dumps(offers_list)

    except Exception as e:
        # --- Transparency: Clear Error Messages ---
        error_message = f"An unexpected error occurred in search_flights: {e}"
        return json.dumps({"error": error_message, "status": "failed"})

@mcp.tool()
def get_offer_details(offer_id: str) -> str:
    """Retrieve the full details for a specific flight offer.

    This includes passenger pricing, baggage allowance, cancellation policies,
    and complete segment information.

    Args:
        offer_id (str): The unique identifier for a flight offer, returned by
                        `search_flights` or `search_multi_city`.

    Returns:
        str: A JSON string containing the complete details for the specified
             flight offer. An error is raised if the ID is invalid or expired.

    Raises:
        ValueError: If offer_id is not provided.
        Exception: If the API call fails or the offer is not found.
    """
    try:
        # --- Robustness: Input Validation ---
        if not offer_id:
            raise ValueError("Parameter 'offer_id' cannot be empty.")

        # --- Functionality: Core Logic ---
        offer = duffel.offers.get(offer_id)

        # The offer object from the API is complex. We convert it to a dict for JSON serialization.
        # This is a simplified representation. A real implementation might need a more complex serializer.
        offer_details = {
            "id": offer.id,
            "live_mode": offer.live_mode,
            "total_amount": offer.total_amount,
            "total_currency": offer.total_currency,
            "passengers": [{"type": p.type} for p in offer.passengers],
            "slices": [
                {
                    "origin": s.origin.name,
                    "destination": s.destination.name,
                    "departure": s.departing_at.isoformat(),
                    "arrival": s.arriving_at.isoformat(),
                    "duration": str(s.duration),
                    "segments": [
                        {
                            "operating_carrier": seg.operating_carrier.name,
                            "aircraft": seg.aircraft.name,
                            "origin_terminal": seg.origin.terminal,
                            "destination_terminal": seg.destination.terminal,
                        } for seg in s.segments
                    ]
                } for s in offer.slices
            ]
        }
        return json.dumps(offer_details)

    except Exception as e:
        # --- Transparency: Clear Error Messages ---
        error_message = f"Failed to get details for offer '{offer_id}'. It might be invalid or expired. Error: {e}"
        return json.dumps({"error": error_message, "status": "failed"})

@mcp.tool()
def search_multi_city(slices: list, cabin_class: str = "economy") -> str:
    """Handle complex multi-city itinerary searches with multiple flight legs.

    Args:
        slices (list[dict]): A list of dictionaries, each describing a leg of the journey.
                             Each dictionary must contain the keys: `origin` (departure
                             airport IATA code), `destination` (destination airport IATA
                             code), and `departure_date` (the departure date for that
                             leg in "YYYY-MM-DD" format).
        cabin_class (str): The cabin class to be applied to all legs. Valid options are
                           "economy", "premium_economy", "business", and "first".
                           Defaults to "economy".

    Returns:
        str: A JSON string containing a list of flight offers that match the entire
             multi-city itinerary. Returns an empty list if the itinerary cannot
             be fulfilled.

    Raises:
        ValueError: If the `slices` format is incorrect or the list is empty.
        Exception: If the API call fails.
    """
    try:
        # --- Robustness: Input Validation ---
        if not isinstance(slices, list) or not slices:
            raise ValueError("'slices' must be a non-empty list of flight segments.")
        
        for idx, s in enumerate(slices):
            if not all(k in s for k in ["origin", "destination", "departure_date"]):
                raise ValueError(f"Each slice must contain 'origin', 'destination', and 'departure_date'. Problem at slice {idx}.")
            
            if not re.match(r'^[A-Z]{3}$', s["origin"]):
                raise ValueError(f"Invalid origin IATA code: '{s['origin']}' in slice {idx}. Must be 3 uppercase letters (e.g., LHR).")
            if not re.match(r'^[A-Z]{3}$', s["destination"]):
                raise ValueError(f"Invalid destination IATA code: '{s['destination']}' in slice {idx}. Must be 3 uppercase letters (e.g., JFK).")

        # --- Functionality: Core Logic ---
        offer_request = (
            duffel.offer_requests.create()
            .slices(slices)
            .passengers([{}])  # Search for one adult passenger
            .cabin_class(cabin_class)
            .execute()
        )

        offers_list = [
            {
                "id": offer.id,
                "total_amount": offer.total_amount,
                "total_currency": offer.total_currency,
                "slices_summary": [
                    f"{s.origin.iata_code} -> {s.destination.iata_code} on {s.departing_at.date()}"
                    for s in offer.slices
                ],
            }
            for offer in duffel.offers.list(offer_request.id)
        ]
        return json.dumps(offers_list)

    except Exception as e:
        # --- Transparency: Clear Error Messages ---
        error_message = f"An unexpected error occurred in search_multi_city: {e}"
        return json.dumps({"error": error_message, "status": "failed"})

# --- Server Execution ---

if __name__ == "__main__":
    # Ensure UTF-8 encoding for cross-platform compatibility.
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()