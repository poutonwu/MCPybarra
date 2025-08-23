"""Duffel API endpoint handlers."""

from typing import Dict, Any, List
import logging
import httpx

class OfferEndpoints:
    """Offer-related API endpoints."""
    
    def __init__(self, base_url: str, headers: Dict, logger: logging.Logger):
        self.base_url = base_url
        self.headers = headers
        self.logger = logger

    async def create_offer_request(
        self,
        slices: List[Dict],
        cabin_class: str = "economy",
        adult_count: int = 1,
        max_connections: int = None,
        return_offers: bool = True,
        supplier_timeout: int = 15000
    ) -> Dict:
        """Create a flight offer request."""
        try:
            # Format request data
            request_data = {
                "data": {
                    "slices": slices,
                    "passengers": [{"type": "adult"} for _ in range(adult_count)],
                    "cabin_class": cabin_class,
                }
            }

            if max_connections is not None:
                request_data["data"]["max_connections"] = max_connections

            params = {
                "return_offers": str(return_offers).lower(),
                "supplier_timeout": supplier_timeout
            }

            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                self.logger.info(f"Creating offer request with data: {request_data}")
                response = await client.post(
                    f"{self.base_url}/offer_requests",
                    headers=self.headers,
                    params=params,
                    json=request_data
                )
                response.raise_for_status()
                data = response.json()
                
                request_id = data["data"]["id"]
                offers = data["data"].get("offers", [])
                
                self.logger.info(f"Created offer request with ID: {request_id}")
                self.logger.info(f"Received {len(offers)} offers")
                
                return {
                    "request_id": request_id,
                    "offers": offers
                }

        except Exception as e:
            error_msg = f"Error creating offer request: {str(e)}"
            self.logger.error(error_msg)
            raise

    async def get_offer(self, offer_id: str) -> Dict:
        """Get details of a specific offer."""
        try:
            if not offer_id.startswith("off_"):
                raise ValueError("Invalid offer ID format - must start with 'off_'")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/offers/{offer_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Error getting offer {offer_id}: {str(e)}")
            raise 