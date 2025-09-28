# mcp_duffeld_flight_info

## Overview
This is an MCP (Model Context Protocol) server that provides flight information services. It enables large language models to query flight data, including searching for flights, retrieving offer details, and searching for multi-city itineraries.

## Installation
Make sure you have Python 3.10 or higher installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes:
```
mcp[cli]
httpx
```

## Running the Server
To start the server, run the following command:

```bash
python mcp_duffeld_flight_info.py
```

Replace `mcp_duffeld_flight_info.py` with the actual filename where the server code is saved.

## Available Tools

### `search_flights`
Searches for flights based on departure, destination, date, cabin class, and trip type.

**Parameters:**
- `departure`: Airport code (e.g., "JFK")
- `destination`: Airport code (e.g., "LAX")
- `date`: Travel date in "YYYY-MM-DD" format
- `cabin_class`: One of "economy", "business", or "first"
- `trip_type`: One of "one-way", "round-trip", or "multi-city"

**Returns:** JSON string containing matching flight results or error message.

---

### `get_offer_details`
Retrieves detailed information about a specific flight offer using its unique ID.

**Parameters:**
- `offer_id`: Unique identifier for the flight offer

**Returns:** JSON string with detailed flight information or error message.

---

### `search_multi_city`
Searches for multi-city flight itineraries by defining multiple travel segments.

**Parameters:**
- `segments`: List of dictionaries, each containing:
  - `departure`: Airport code (e.g., "JFK")
  - `destination`: Airport code (e.g., "LAX")
  - `date`: Travel date in "YYYY-MM-DD" format

**Returns:** JSON string containing multi-city flight options or error message.