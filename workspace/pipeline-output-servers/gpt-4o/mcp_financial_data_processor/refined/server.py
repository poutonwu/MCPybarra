import os
import sys
import asyncio
import httpx
import json
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("financial_mcp_server")

# Base URL and API Key for Financial Datasets API
API_BASE_URL = "https://financialdatasets.example.com/api"
API_KEY = "REDACTED_SECRET"

if not API_KEY:
    raise ValueError("FINANCIAL_API_KEY environment variable is not set")

# Shared HTTPX AsyncClient
client = httpx.AsyncClient(
    base_url=API_BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"}
)

async def validate_ticker(ticker: str):
    """Validate that a ticker symbol is in the correct format."""
    if not ticker or not isinstance(ticker, str) or len(ticker) > 10:
        logger.error(f"Invalid ticker symbol: '{ticker}'")
        raise ValueError(f"Invalid ticker symbol: '{ticker}'. Ticker should be a string of 1-10 characters (e.g., 'AAPL').")

async def validate_period(period: str):
    """Validate that the period parameter has an acceptable value."""
    valid_periods = ["annual", "quarterly", "ttm"]
    if period not in valid_periods:
        logger.error(f"Invalid period: '{period}'")
        raise ValueError(f"Invalid period: '{period}'. Valid periods are {valid_periods}")

async def validate_limit(limit: int):
    """Validate that the limit parameter has an acceptable value."""
    if not isinstance(limit, int) or limit <= 0:
        logger.error(f"Invalid limit: '{limit}'")
        raise ValueError(f"Invalid limit: '{limit}'. Limit must be a positive integer.")

async def validate_date(date_str: str, allow_future: bool = False):
    """Validate that a date string is in the correct format and represents a valid date."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if not allow_future and date_obj > datetime.now():
            logger.error(f"Date cannot be in the future: '{date_str}' but allow_future={allow_future}")
            raise ValueError(f"Date cannot be in the future: '{date_str}'")
    except ValueError as e:
        logger.error(f"Invalid date format: '{date_str}': {str(e)}")
        raise ValueError(f"Invalid date format: '{date_str}'. Please use YYYY-MM-DD format.") from e

@mcp.tool()
async def get_income_statements(ticker: str, period: str, limit: int) -> str:
    """
    Fetches income statements for a specified company.

    Args:
        ticker (str): Stock ticker of the company (e.g., "AAPL"). Must be a string of 1-10 characters.
        period (str): Reporting period (e.g., "annual", "quarterly", "ttm"). Must be one of ["annual", "quarterly", "ttm"].
        limit (int): Maximum number of statements to return. Must be a positive integer.

    Returns:
        str: JSON object containing the company's income statements.

    Raises:
        ValueError: If any input validation fails.
        httpx.HTTPStatusError: If the API request fails.

    Example:
        get_income_statements(ticker="AAPL", period="annual", limit=5)
    """
    try:
        logger.debug(f"Fetching income statements for {ticker} ({period}, {limit})")
        await validate_ticker(ticker)
        await validate_period(period)
        await validate_limit(limit)
        
        response = await client.get("/income-statements", params={"ticker": ticker, "period": period, "limit": limit})
        response.raise_for_status()
        logger.debug(f"Successfully fetched income statements for {ticker}")
        return json.dumps(response.json())
    except ValueError as ve:
        logger.error(f"Input validation failed: {str(ve)}")
        return json.dumps({"error": f"Input validation failed: {str(ve)}"})
    except httpx.HTTPStatusError as he:
        logger.error(f"API request failed with status {he.response.status_code}: {str(he)}")
        return json.dumps({"error": f"API request failed with status {he.response.status_code}: {str(he)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

# Similar validation logic would be implemented for all other tools with appropriate parameters
# For brevity, only get_income_statements shows the full pattern - but in practice, all tools would be updated similarly

@mcp.tool()
async def get_balance_sheets(ticker: str, period: str, limit: int) -> str:
    """
    Retrieves balance sheets for a specified company.

    Args:
        ticker (str): Stock ticker of the company. Must be a string of 1-10 characters.
        period (str): Reporting period (e.g., "annual", "quarterly", "ttm"). Must be one of ["annual", "quarterly", "ttm"].
        limit (int): Maximum number of records to return. Must be a positive integer.

    Returns:
        str: JSON object containing the company's balance sheets.

    Raises:
        ValueError: If any input validation fails.
        httpx.HTTPStatusError: If the API request fails.
    """
    try:
        logger.debug(f"Fetching balance sheets for {ticker} ({period}, {limit})")
        await validate_ticker(ticker)
        await validate_period(period)
        await validate_limit(limit)
        
        response = await client.get("/balance-sheets", params={"ticker": ticker, "period": period, "limit": limit})
        response.raise_for_status()
        logger.debug(f"Successfully fetched balance sheets for {ticker}")
        return json.dumps(response.json())
    except ValueError as ve:
        logger.error(f"Input validation failed: {str(ve)}")
        return json.dumps({"error": f"Input validation failed: {str(ve)}"})
    except httpx.HTTPStatusError as he:
        logger.error(f"API request failed with status {he.response.status_code}: {str(he)}")
        return json.dumps({"error": f"API request failed with status {he.response.status_code}: {str(he)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@mcp.tool()
async def get_cash_flows(ticker: str, period: str, limit: int) -> str:
    """
    Fetches cash flow statements for a specified company.

    Args:
        ticker (str): Stock ticker of the company. Must be a string of 1-10 characters.
        period (str): Reporting period (e.g., "annual", "quarterly", "ttm"). Must be one of ["annual", "quarterly", "ttm"].
        limit (int): Maximum number of records to return. Must be a positive integer.

    Returns:
        str: JSON object containing the company's cash flow statements.

    Raises:
        ValueError: If any input validation fails.
        httpx.HTTPStatusError: If the API request fails.
    """
    try:
        logger.debug(f"Fetching cash flows for {ticker} ({period}, {limit})")
        await validate_ticker(ticker)
        await validate_period(period)
        await validate_limit(limit)
        
        response = await client.get("/cash-flows", params={"ticker": ticker, "period": period, "limit": limit})
        response.raise_for_status()
        logger.debug(f"Successfully fetched cash flows for {ticker}")
        return json.dumps(response.json())
    except ValueError as ve:
        logger.error(f"Input validation failed: {str(ve)}")
        return json.dumps({"error": f"Input validation failed: {str(ve)}"})
    except httpx.HTTPStatusError as he:
        logger.error(f"API request failed with status {he.response.status_code}: {str(he)}")
        return json.dumps({"error": f"API request failed with status {he.response.status_code}: {str(he)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@mcp.tool()
async def get_stock_prices(ticker: str, start_date: str, end_date: str) -> str:
    """
    Retrieves historical stock price data for a specified company.

    Args:
        ticker (str): Stock ticker of the company. Must be a string of 1-10 characters.
        start_date (str): Start date for the query (e.g., "2023-01-01"). Must be in YYYY-MM-DD format.
        end_date (str): End date for the query (e.g., "2023-12-31"). Must be in YYYY-MM-DD format.

    Returns:
        str: JSON object containing historical stock prices.

    Raises:
        ValueError: If any input validation fails.
        httpx.HTTPStatusError: If the API request fails.
    """
    try:
        logger.debug(f"Fetching stock prices for {ticker} between {start_date} and {end_date}")
        await validate_ticker(ticker)
        await validate_date(start_date, allow_future=False)
        await validate_date(end_date, allow_future=True)
        
        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
            raise ValueError(f"Start date ({start_date}) cannot be after end date ({end_date})")
        
        response = await client.get("/stock-prices", params={"ticker": ticker, "start_date": start_date, "end_date": end_date})
        response.raise_for_status()
        logger.debug(f"Successfully fetched stock prices for {ticker}")
        return json.dumps(response.json())
    except ValueError as ve:
        logger.error(f"Input validation failed: {str(ve)}")
        return json.dumps({"error": f"Input validation failed: {str(ve)}"})
    except httpx.HTTPStatusError as he:
        logger.error(f"API request failed with status {he.response.status_code}: {str(he)}")
        return json.dumps({"error": f"API request failed with status {he.response.status_code}: {str(he)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@mcp.tool()
async def get_market_news(ticker: str = None, limit: int = 10) -> str:
    """
    Fetches the latest financial news related to a company or the market.

    Args:
        ticker (str): Stock ticker of the company (optional). If provided, must be a string of 1-10 characters.
        limit (int): Maximum number of news articles to return. Must be a positive integer.

    Returns:
        str: JSON object containing market news articles.

    Raises:
        ValueError: If any input validation fails.
        httpx.HTTPStatusError: If the API request fails.
    """
    try:
        logger.debug(f"Fetching market news for {ticker if ticker else 'general'} market")
        
        if ticker:  # Only validate ticker if it's provided
            await validate_ticker(ticker)
        await validate_limit(limit)
        
        response = await client.get("/market-news", params={"ticker": ticker, "limit": limit})
        response.raise_for_status()
        logger.debug(f"Successfully fetched market news")
        return json.dumps(response.json())
    except ValueError as ve:
        logger.error(f"Input validation failed: {str(ve)}")
        return json.dumps({"error": f"Input validation failed: {str(ve)}"})
    except httpx.HTTPStatusError as he:
        logger.error(f"API request failed with status {he.response.status_code}: {str(he)}")
        return json.dumps({"error": f"API request failed with status {he.response.status_code}: {str(he)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@mcp.tool()
async def get_company_profile(ticker: str) -> str:
    """
    Retrieves the profile of a specified company, including industry and location.

    Args:
        ticker (str): Stock ticker of the company. Must be a string of 1-10 characters.

    Returns:
        str: JSON object containing the company's profile.

    Raises:
        ValueError: If ticker validation fails.
        httpx.HTTPStatusError: If the API request fails.
    """
    try:
        logger.debug(f"Fetching company profile for {ticker}")
        await validate_ticker(ticker)
        
        response = await client.get("/company-profile", params={"ticker": ticker})
        response.raise_for_status()
        logger.debug(f"Successfully fetched company profile for {ticker}")
        
        # Ensure the response is properly formatted
        result = response.json()
        if result and isinstance(result, dict):
            return json.dumps(result)
        else:
            logger.error(f"Invalid response format from API: {result}")
            return json.dumps({"error": "Invalid response format from API"})
            
    except ValueError as ve:
        logger.error(f"Input validation failed: {str(ve)}")
        return json.dumps({"error": f"Input validation failed: {str(ve)}"})
    except httpx.HTTPStatusError as he:
        logger.error(f"API request failed with status {he.response.status_code}: {str(he)}")
        return json.dumps({"error": f"API request failed with status {he.response.status_code}: {str(he)}"})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()

# Ensure the shared client is closed when the server stops
async def shutdown():
    await client.aclose()
asyncio.get_event_loop().run_until_complete(shutdown())