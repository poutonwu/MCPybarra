"""Duffel API configuration."""

import os
from typing import Final

# API Constants
DUFFEL_API_URL: Final = "https://api.duffel.com"
DUFFEL_API_VERSION: Final = "v2"

def get_api_token() -> str:
    """Get Duffel API token from environment."""
    token = os.getenv("DUFFEL_API_KEY_LIVE")
    if not token:
        raise ValueError("DUFFEL_API_KEY_LIVE environment variable not set")
    return token 