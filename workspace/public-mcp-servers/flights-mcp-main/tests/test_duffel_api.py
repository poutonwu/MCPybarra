"""Tests for Duffel API client."""

import pytest
import logging
from datetime import datetime, timedelta
from flights.api import DuffelClient
from flights.models.search import FlightSearch
from flights.models.multi_city import MultiCityRequest

# Setup logging for tests
logger = logging.getLogger(__name__)

@pytest.fixture
async def client():
    """Create a test client."""
    client = DuffelClient(logger)
    async with client as c:
        yield c

@pytest.mark.asyncio
async def test_search_one_way(client):
    """Test one-way flight search."""
    # Get tomorrow's date for testing
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = await client.create_offer_request(
        slices=[{
            "origin": "SFO",
            "destination": "LAX",
            "departure_date": tomorrow
        }],
        cabin_class="economy",
        adult_count=1
    )
    
    assert response is not None
    assert "request_id" in response
    assert "offers" in response
    assert len(response["offers"]) > 0

@pytest.mark.asyncio
async def test_search_round_trip(client):
    """Test round-trip flight search."""
    # Get dates for testing
    departure = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    return_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    response = await client.create_offer_request(
        slices=[
            {
                "origin": "SFO",
                "destination": "LAX",
                "departure_date": departure
            },
            {
                "origin": "LAX",
                "destination": "SFO",
                "departure_date": return_date
            }
        ],
        cabin_class="economy",
        adult_count=1
    )
    
    assert response is not None
    assert "request_id" in response
    assert "offers" in response
    assert len(response["offers"]) > 0

@pytest.mark.asyncio
async def test_search_multi_city(client):
    """Test multi-city flight search."""
    # Get dates for testing
    first_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    second_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    
    response = await client.create_offer_request(
        slices=[
            {
                "origin": "SFO",
                "destination": "LAX",
                "departure_date": first_date
            },
            {
                "origin": "LAX",
                "destination": "JFK",
                "departure_date": second_date
            }
        ],
        cabin_class="economy",
        adult_count=1
    )
    
    assert response is not None
    assert "request_id" in response
    assert "offers" in response

@pytest.mark.asyncio
async def test_cabin_classes(client):
    """Test different cabin classes."""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    cabin_classes = ["economy", "premium_economy", "business", "first"]
    
    for cabin_class in cabin_classes:
        response = await client.create_offer_request(
            slices=[{
                "origin": "SFO",
                "destination": "LAX",
                "departure_date": tomorrow
            }],
            cabin_class=cabin_class,
            adult_count=1
        )
        
        assert response is not None
        assert "request_id" in response
        assert "offers" in response

@pytest.mark.asyncio
async def test_get_offer(client):
    """Test getting offer details."""
    # First create an offer request
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    offers_response = await client.create_offer_request(
        slices=[{
            "origin": "SFO",
            "destination": "LAX",
            "departure_date": tomorrow
        }],
        cabin_class="economy",
        adult_count=1
    )
    
    assert offers_response is not None
    assert "offers" in offers_response
    assert len(offers_response["offers"]) > 0
    
    # Get the first offer's details
    offer_id = offers_response["offers"][0]["id"]
    offer_details = await client.get_offer(offer_id)
    
    assert offer_details is not None
    assert "data" in offer_details

@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling for invalid requests."""
    with pytest.raises(Exception):
        await client.create_offer_request(
            slices=[{
                "origin": "INVALID",
                "destination": "ALSO_INVALID",
                "departure_date": "2025-01-01"
            }],
            cabin_class="economy",
            adult_count=1
        )

@pytest.mark.asyncio
async def test_invalid_offer_id(client):
    """Test error handling for invalid offer ID."""
    with pytest.raises(ValueError):
        await client.get_offer("invalid_offer_id") 