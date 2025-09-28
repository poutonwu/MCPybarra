# duffel_flight_info_processor

## Overview

The `duffel_flight_info_processor` is a Model Context Protocol (MCP) server that provides flight information and booking capabilities through the Duffel API. It enables users to search for flights, retrieve detailed information about specific flight offers, and perform multi-city itinerary searches.

This server supports:
- Searching for one-way, round-trip, and multi-city flights
- Getting detailed information about specific flight offers
- Formatting flight data in a standardized way for easy consumption

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:
```
mcp[cli]
httpx
```

## Running the Server

To start the server, run the following command:

```bash
python duffel_flight_info_processor.py
```

Note: Make sure your environment has the `DUFFEL_API_KEY` set, or update the code to use your API key directly.

## Available Tools

### 1. `search_flights`

**Description:**  
Searches for flights based on origin, destination, dates, cabin class, and trip type.

**Parameters:**
- `origin`: Departure airport IATA code (3 uppercase letters)
- `destination`: Arrival airport IATA code (3 uppercase letters)
- `departure_date`: Departure date in YYYY-MM-DD format
- `return_date`: Return date in YYYY-MM-DD format (for round trips)
- `cabin_class`: Cabin class ('economy', 'premium_economy', 'business', 'first')
- `trip_type`: Type of trip ('one_way', 'round_trip', 'multi_city')
- `max_results`: Maximum number of results to return (1-20)

**Returns:**
A JSON list of flight information including flight number, airline, departure/arrival times, duration, price, stops, and cabin class.

---

### 2. `get_offer_details`

**Description:**  
Retrieves detailed information about a specific flight offer.

**Parameters:**
- `offer_id`: Unique identifier for the flight offer (obtained from search results)

**Returns:**
A JSON object containing detailed information including:
- Offer ID
- Flight number and airline info
- Segment details (origin, destination, departure/arrival times)
- Price breakdown (base price, taxes, total)
- Baggage allowance
- Booking conditions (changeable/refundable status)

---

### 3. `search_multi_city`

**Description:**  
Searches for multi-city itineraries with multiple legs.

**Parameters:**
- `itinerary`: List of dictionaries, each representing a leg with origin, destination, and date
- `cabin_class`: Cabin class ('economy', 'premium_economy', 'business', 'first')
- `max_results`: Maximum number of results to return (1-20)

**Returns:**
A JSON list of journey information including:
- Journey ID
- Total price
- Segment details for each leg
- Total travel duration
- Layover information between segments