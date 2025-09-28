# mcp_flight_info_query

## Overview
This server provides flight information querying capabilities through the Model Context Protocol (MCP). It connects to the Duffel Airlines API to search for flights, get detailed offer information, and handle multi-city flight queries.

## Installation
1. Ensure Python 3.10+ is installed.
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

The following packages are typically required:
- `mcp[cli]`
- `httpx`
- `pydantic`

## Running the Server
To start the server, run the following command:
```bash
python mcp_flight_info_query.py
```

Ensure that the server file is properly encoded in UTF-8.

## Available Tools

### `search_flights`
Searches for flights based on departure, destination, date, cabin class, and trip type.

**Parameters:**
- `departure`: IATA code or name of departure city/airport
- `destination`: IATA code or name of destination city/airport
- `date`: Departure date in YYYY-MM-DD format
- `cabin_class`: Cabin class (economy, business, first; defaults to economy)
- `trip_type`: Type of trip (one-way, round-trip, multi-city)
- `return_date`: Return date for round-trip flights (YYYY-MM-DD)

Returns a JSON array of flight objects.

---

### `get_offer_details`
Retrieves detailed information about a specific flight offer.

**Parameter:**
- `offer_id`: Unique identifier for the flight offer

Returns a JSON object containing detailed offer information.

---

### `search_multi_city`
Handles complex multi-city flight queries with multiple segments.

**Parameters:**
- `segments`: List of flight segments, each with:
  - `departure`: IATA code or name of departure city/airport
  - `destination`: IATA code or name of destination city/airport
  - `date`: Departure date in YYYY-MM-DD format
- `cabin_class`: Cabin class (economy, business, first; defaults to economy)

Returns a JSON array of flight combinations across all segments.