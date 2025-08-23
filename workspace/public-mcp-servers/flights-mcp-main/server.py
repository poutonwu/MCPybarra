"""Server initialization for find-flights MCP."""

import logging
from src.flights.services.search import mcp

# Set up logging
logger = logging.getLogger(__name__)

def main():
    """Entry point for the find-flights-mcp application."""
    logger.info("Starting Find Flights MCP server")
    try:
        mcp.run(transport='stdio')
        logger.info("Server initialized successfully")
    except Exception as e:
        logger.error(f"Server error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()