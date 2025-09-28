# mcp_duffeld_flight_info_proces

## Overview

This server provides flight information services through the Model Context Protocol (MCP). It enables querying flight data from Duffel's API, including one-way flights, round-trip flights, and multi-city itineraries. The server supports retrieving general flight search results as well as detailed offer information.

## Installation

Ensure you have Python 3.10+ installed. Then install dependencies using pip:

```bash
pip install -r requirements.txt
```

The following packages are required:
- `mcp[cli]`
- `httpx`
- `pyflightdata`

## Running the Server

To start the server, run the following command:

```bash
python mcp_duffeld_flight_info_proces.py
```

You can optionally set environment variables for authentication:

```bash
export FLIGHT_API_KEY=your_api_key
export FLIGHT_EMAIL=your_email
export FLIGHT_PASSWORD=your_password
```

## Available Tools

### `search_flights`

Searches for available flights based on origin, destination, departure date, and optional return date and cabin class.

**Parameters:**
- `origin`: Departure city or airport code (required)
- `destination`: Arrival city or airport code (required)
- `departure_date`: Departure date in 'YYYY-MM-DD' format (required)
- `return_date`: Return date in 'YYYY-MM-DD' format (optional, required for round trips)
- `cabin_class`: Desired cabin class (e.g., 'Economy', 'Business') (optional)
- `flight_type`: Type of flight query ('one_way', 'round_trip') (required)

**Returns:** JSON string containing list of available flights with pricing, timing, and airline info.

---

### `get_offer_details`

Retrieves detailed information about a specific flight offer.

**Parameters:**
- `offer_id`: Unique identifier for the flight offer (required)

**Returns:** JSON string containing detailed information about the specified flight offer.

---

### `search_multi_city`

Performs a complex flight search across multiple cities/destinations.

**Parameters:**
- `cities`: List of dictionaries containing 'origin', 'destination', and 'departure_date' keys for each leg of the journey (required)
- `cabin_class`: Desired cabin class (optional)

**Returns:** JSON string containing list of available multi-city flight options with relevant details.