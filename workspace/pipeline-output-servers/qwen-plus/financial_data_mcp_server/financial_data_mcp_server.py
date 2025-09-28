import asyncio
import json
import os
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial_data_mcp_server")
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# Shared AsyncClient for performance
client = httpx.AsyncClient(
    base_url="https://api.financialdatasets.com",
    headers={"Authorization": f"Bearer {os.environ.get('FINANCIALDATASETS_API_KEY', 'REDACTED_SECRET')}"}
)

@mcp.tool()
async def get_income_statements(stock_code: str, reporting_period: str, limit: int) -> str:
    """
    Fetches income statements for a specified company.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').
        reporting_period (str): Reporting period (e.g., 'annual', 'quarterly', 'TTM').
        limit (int): Number of results to return.

    Returns:
        str: A JSON string containing income statement data.

    Example:
        >>> get_income_statements(stock_code="AAPL", reporting_period="annual", limit=5)
    """
    try:
        response = await client.get(f"/income-statements/{stock_code}", params={"period": reporting_period, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_balance_sheets(stock_code: str, reporting_period: str, limit: int) -> str:
    """
    Fetches balance sheets for a specified company.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').
        reporting_period (str): Reporting period (e.g., 'annual', 'quarterly', 'TTM').
        limit (int): Number of results to return.

    Returns:
        str: A JSON string containing balance sheet data.

    Example:
        >>> get_balance_sheets(stock_code="AAPL", reporting_period="annual", limit=5)
    """
    try:
        response = await client.get(f"/balance-sheets/{stock_code}", params={"period": reporting_period, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_cash_flows(stock_code: str, reporting_period: str, limit: int) -> str:
    """
    Extracts cash flow statements for a specified company.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').
        reporting_period (str): Reporting period (e.g., 'annual', 'quarterly', 'TTM').
        limit (int): Number of results to return.

    Returns:
        str: A JSON string containing cash flow data.

    Example:
        >>> get_cash_flows(stock_code="AAPL", reporting_period="annual", limit=5)
    """
    try:
        response = await client.get(f"/cash-flows/{stock_code}", params={"period": reporting_period, "limit": limit})
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_stock_prices(stock_code: str, start_date: str, end_date: str) -> str:
    """
    Queries historical stock prices for a specified range.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').
        start_date (str): Start date for the historical price range (YYYY-MM-DD).
        end_date (str): End date for the historical price range (YYYY-MM-DD).

    Returns:
        str: A JSON string containing historical stock price data.

    Example:
        >>> get_stock_prices(stock_code="AAPL", start_date="2023-01-01", end_date="2023-12-31")
    """
    try:
        response = await client.get(f"/stock-prices/{stock_code}", params={"start": start_date, "end": end_date})
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_market_news(company_identifier: str) -> str:
    """
    Retrieves financial news related to companies or markets.

    Args:
        company_identifier (str): Identifier for the company/market.

    Returns:
        str: A JSON string containing relevant news articles.

    Example:
        >>> get_market_news(company_identifier="AAPL")
    """
    try:
        response = await client.get(f"/market-news/{company_identifier}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_company_profile(stock_code: str) -> str:
    """
    Retrieves company profiles including industry and location details.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing company profile information.

    Example:
        >>> get_company_profile(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/company-profile/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_analyst_estimates(stock_code: str) -> str:
    """
    Fetches analyst estimates like target price and earnings forecasts.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing analyst predictions.

    Example:
        >>> get_analyst_estimates(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/analyst-estimates/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_dividend_history(stock_code: str) -> str:
    """
    Gets dividend history for a specified company.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing dividend records.

    Example:
        >>> get_dividend_history(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/dividend-history/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_splits_history(stock_code: str) -> str:
    """
    Queries stock split history for a specified company.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing stock split records.

    Example:
        >>> get_splits_history(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/splits-history/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_earnings_history(stock_code: str) -> str:
    """
    Fetches historical earnings data including EPS.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing earnings data.

    Example:
        >>> get_earnings_history(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/earnings-history/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_financial_ratios(stock_code: str) -> str:
    """
    Gets financial ratios such as P/E and Debt-to-Equity.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing financial ratios.

    Example:
        >>> get_financial_ratios(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/financial-ratios/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

@mcp.tool()
async def get_ownership_data(stock_code: str) -> str:
    """
    Retrieves ownership structure data like institutional holdings.

    Args:
        stock_code (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string containing ownership details.

    Example:
        >>> get_ownership_data(stock_code="AAPL")
    """
    try:
        response = await client.get(f"/ownership-data/{stock_code}")
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API Error: Status {e.response.status_code} - {e.response.text}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

if __name__ == "__main__":
    # Run the server
    mcp.run()