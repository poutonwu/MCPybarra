"""Duffel API client."""

import logging
import httpx
from typing import Dict, Any, List
from ..config import get_api_token
from .endpoints import OfferEndpoints

class DuffelClient:
    """Client for interacting with the Duffel API."""

    def __init__(self, logger: logging.Logger, timeout: float = 30.0):
        """Initialize the Duffel API client."""
        self.logger = logger
        self.timeout = timeout
        self._token = get_api_token()
        self.base_url = "https://api.duffel.com/air"

        # Headers setup
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Duffel-Version": "v2",
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }

        self.logger.info(f"API key starts with: {self._token[:8] if self._token else None}")
        self.logger.info(f"Using base URL: {self.base_url}")

        # Initialize endpoints
        self.offers = OfferEndpoints(self.base_url, self.headers, self.logger)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass

    async def create_offer_request(self, **kwargs) -> Dict[str, Any]:
        """Create an offer request."""
        return await self.offers.create_offer_request(**kwargs)

    async def get_offer(self, offer_id: str) -> Dict[str, Any]:
        """Get offer details."""
        return await self.offers.get_offer(offer_id)
