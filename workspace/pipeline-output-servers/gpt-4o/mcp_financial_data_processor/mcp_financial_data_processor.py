import os
import sys
import asyncio
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial_mcp_server")

# Base URL and API Key for Financial Datasets API
API_BASE_URL = "https://financialdatasets.example.com/api"
API_KEY="REDACTED_SECRET"

# Shared HTTPX AsyncClient
client = httpx.AsyncClient(
    base_url=API_BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"}
)

@mcp.tool()
async def get_income_statements(ticker: str, period: str, limit: int) -> str:
    """
    Fetches income statements for a specified company.

    Args:
        ticker (str): Stock ticker of the company (e.g., "AAPL").
        period (str): Reporting period (e.g., "annual", "quarterly", "ttm").
        limit (int): Maximum number of statements to return.

    Returns:
        str: JSON object containing the company's income statements.

    Example:
        get_income_statements(ticker="AAPL", period="annual", limit=5)
    """
    try:
        response = await client.get("/income-statements", params={"ticker": ticker, "period": period, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_balance_sheets(ticker: str, period: str, limit: int) -> str:
    """
    Retrieves balance sheets for a specified company.

    Args:
        ticker (str): Stock ticker of the company.
        period (str): Reporting period (e.g., "annual", "quarterly", "ttm").
        limit (int): Maximum number of records to return.

    Returns:
        str: JSON object containing the company's balance sheets.

    Example:
        get_balance_sheets(ticker="AAPL", period="annual", limit=5)
    """
    try:
        response = await client.get("/balance-sheets", params={"ticker": ticker, "period": period, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_cash_flows(ticker: str, period: str, limit: int) -> str:
    """
    Fetches cash flow statements for a specified company.

    Args:
        ticker (str): Stock ticker of the company.
        period (str): Reporting period (e.g., "annual", "quarterly", "ttm").
        limit (int): Maximum number of records to return.

    Returns:
        str: JSON object containing the company's cash flow statements.

    Example:
        get_cash_flows(ticker="AAPL", period="annual", limit=5)
    """
    try:
        response = await client.get("/cash-flows", params={"ticker": ticker, "period": period, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_stock_prices(ticker: str, start_date: str, end_date: str) -> str:
    """
    Retrieves historical stock price data for a specified company.

    Args:
        ticker (str): Stock ticker of the company.
        start_date (str): Start date for the query (e.g., "2023-01-01").
        end_date (str): End date for the query (e.g., "2023-12-31").

    Returns:
        str: JSON object containing historical stock prices.

    Example:
        get_stock_prices(ticker="AAPL", start_date="2023-01-01", end_date="2023-12-31")
    """
    try:
        response = await client.get("/stock-prices", params={"ticker": ticker, "start_date": start_date, "end_date": end_date})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_market_news(ticker: str = None, limit: int = 10) -> str:
    """
    Fetches the latest financial news related to a company or the market.

    Args:
        ticker (str): Stock ticker of the company (optional).
        limit (int): Maximum number of news articles to return.

    Returns:
        str: JSON object containing market news articles.

    Example:
        get_market_news(ticker="AAPL", limit=5)
    """
    try:
        response = await client.get("/market-news", params={"ticker": ticker, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_company_profile(ticker: str) -> str:
    """
    Retrieves the profile of a specified company, including industry and location.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing the company's profile.

    Example:
        get_company_profile(ticker="AAPL")
    """
    try:
        response = await client.get("/company-profile", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_analyst_estimates(ticker: str) -> str:
    """
    Fetches analyst estimates for a specified company.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing analyst estimates such as target price and earnings forecasts.

    Example:
        get_analyst_estimates(ticker="AAPL")
    """
    try:
        response = await client.get("/analyst-estimates", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_dividend_history(ticker: str) -> str:
    """
    Retrieves dividend history for a specified company.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing dividend history records.

    Example:
        get_dividend_history(ticker="AAPL")
    """
    try:
        response = await client.get("/dividend-history", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_splits_history(ticker: str) -> str:
    """
    Fetches stock split history for a specified company.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing stock split history.

    Example:
        get_splits_history(ticker="AAPL")
    """
    try:
        response = await client.get("/splits-history", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_earnings_history(ticker: str) -> str:
    """
    Retrieves historical earnings data for a specified company.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing earnings history data such as EPS.

    Example:
        get_earnings_history(ticker="AAPL")
    """
    try:
        response = await client.get("/earnings-history", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_financial_ratios(ticker: str) -> str:
    """
    Fetches financial ratios for a specified company.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing financial ratios like P/E ratio and debt-to-equity ratio.

    Example:
        get_financial_ratios(ticker="AAPL")
    """
    try:
        response = await client.get("/financial-ratios", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_ownership_data(ticker: str) -> str:
    """
    Retrieves ownership data for a specified company.

    Args:
        ticker (str): Stock ticker of the company.

    Returns:
        str: JSON object containing ownership data, including institutional holdings.

    Example:
        get_ownership_data(ticker="AAPL")
    """
    try:
        response = await client.get("/ownership-data", params={"ticker": ticker})
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()

# Ensure the shared client is closed when the server stops
async def shutdown():
    await client.aclose()
asyncio.get_event_loop().run_until_complete(shutdown())