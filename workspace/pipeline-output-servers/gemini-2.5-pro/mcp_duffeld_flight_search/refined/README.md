# mcp_duffeld_flight_search

## Overview
This server implements a Model Context Protocol (MCP) interface for flight search functionality using the Duffel API. It provides tools for searching one-way, round-trip, and multi-city flights based on origin, destination, dates, and cabin class.

## Installation
1. Install Python 3.10 or higher
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:
```
mcp[cli]
duffel-api==1.10.0
```

## Running the Server
Set the Duffel API access token as an environment variable and run the server:

```bash
export DUFFEL_ACCESS_TOKEN='your_real_duffel_access_token'
python mcp_duffeld_flight_search.py
```

If you're behind a proxy, you can also set it:
```bash
export HTTP_PROXY='http://127.0.0.1:7890'
```

## Available Tools

### `search_flights`
Searches for one-way or round-trip flights between specified airports and dates.

**Parameters:**
- `origin`: IATA code of departure airport (e.g., "LHR")
- `destination`: IATA code of destination airport (e.g., "JFK")
- `departure_date`: Departure date in "YYYY-MM-DD" format
- `cabin_class`: Cabin class ("economy", "premium_economy", "business", or "first", defaults to "economy")
- `return_date`: Optional return date in "YYYY-MM-DD" format

**Returns:** A JSON string containing a list of flight offers with price, flight times, airline, and itinerary summary.

### `get_offer_details`
Retrieves full details for a specific flight offer.

**Parameters:**
- `offer_id`: Unique identifier for a flight offer returned by `search_flights` or `search_multi_city`

**Returns:** A JSON string containing complete details about the specified flight offer including pricing, baggage allowance, and cancellation policies.

### `search_multi_city`
Searches for flights with multiple destinations (multi-city itineraries).

**Parameters:**
- `slices`: List of dictionaries describing each leg of the journey. Each dictionary must contain `origin`, `destination`, and `departure_date`.
- `cabin_class`: Cabin class for all legs ("economy", "premium_economy", "business", or "first", defaults to "economy")

**Returns:** A JSON string containing a list of flight offers that match the entire multi-city itinerary.