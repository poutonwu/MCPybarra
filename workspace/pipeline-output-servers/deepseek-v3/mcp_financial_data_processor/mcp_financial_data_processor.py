import sys
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial_data_processor")
# Financial Datasets API 密钥
FINANCIAL_DATASETS_API_KEY="REDACTED_SECRET"
# Constants
FINANCIAL_DATA_API_BASE = "https://api.financialdatasets.com"
USER_AGENT = "financial-data-app/1.0 (contact@example.com)"

# Shared HTTP client for performance
client = httpx.AsyncClient(
    base_url=FINANCIAL_DATA_API_BASE,
    headers={"User-Agent": USER_AGENT}
)

@mcp.tool()
async def get_income_statements(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    Retrieves income statements for a specified company.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL").
        period: Reporting period ("annual", "quarterly", "TTM"). Default: "annual".
        limit: Maximum number of results to return. Default: 5.

    Returns:
        JSON-structured income statement data (revenue, expenses, net income, etc.).

    Raises:
        ValueError: If symbol is empty or period is invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if period not in ["annual", "quarterly", "TTM"]:
        raise ValueError("Invalid period. Must be 'annual', 'quarterly', or 'TTM'.")

    url = f"/income-statements/{symbol}?period={period}&limit={limit}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_balance_sheets(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    Retrieves balance sheet data for a specified company.

    Args:
        symbol: Stock ticker symbol.
        period: Reporting period. Default: "annual".
        limit: Maximum results to return. Default: 5.

    Returns:
        JSON-structured balance sheet data (assets, liabilities, equity).

    Raises:
        ValueError: If symbol is empty or period is invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if period not in ["annual", "quarterly", "TTM"]:
        raise ValueError("Invalid period. Must be 'annual', 'quarterly', or 'TTM'.")

    url = f"/balance-sheets/{symbol}?period={period}&limit={limit}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_cash_flows(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    Retrieves cash flow statements for a specified company.

    Args:
        symbol: Stock ticker symbol.
        period: Reporting period. Default: "annual".
        limit: Maximum results to return. Default: 5.

    Returns:
        JSON-structured cash flow data (operating, investing, financing activities).

    Raises:
        ValueError: If symbol is empty or period is invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if period not in ["annual", "quarterly", "TTM"]:
        raise ValueError("Invalid period. Must be 'annual', 'quarterly', or 'TTM'.")

    url = f"/cash-flows/{symbol}?period={period}&limit={limit}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_stock_prices(symbol: str, start_date: str, end_date: str) -> str:
    """
    Retrieves historical stock price data.

    Args:
        symbol: Stock ticker symbol.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        JSON-structured historical price data (date, open, high, low, close, volume).

    Raises:
        ValueError: If symbol, start_date, or end_date is invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    # Validate date format (simplified for brevity)
    if len(start_date) != 10 or len(end_date) != 10:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    url = f"/stock-prices/{symbol}?start_date={start_date}&end_date={end_date}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_market_news(symbol: str = None, limit: int = 10) -> str:
    """
    Retrieves financial news related to a company or market.

    Args:
        symbol: Stock ticker symbol. If omitted, returns general market news.
        limit: Maximum news items to return. Default: 10.

    Returns:
        JSON-structured news headlines, sources, and timestamps.

    Raises:
        httpx.HTTPStatusError: If the API request fails.
    """
    url = "/market-news"
    if symbol:
        url += f"?symbol={symbol}&limit={limit}"
    else:
        url += f"?limit={limit}"

    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_company_profile(symbol: str) -> str:
    """
    Retrieves company metadata (industry, location, etc.).

    Args:
        symbol: Stock ticker symbol.

    Returns:
        JSON-structured company profile data.

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/company-profile/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_analyst_estimates(symbol: str, limit: int = 5) -> str:
    """
    Retrieves analyst estimates (target price, earnings forecasts).

    Args:
        symbol: Stock ticker symbol.
        limit: Maximum estimates to return. Default: 5.

    Returns:
        JSON-structured analyst predictions.

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/analyst-estimates/{symbol}?limit={limit}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_dividend_history(symbol: str, limit: int = 10) -> str:
    """
    Retrieves dividend payment history.

    Args:
        symbol: Stock ticker symbol.
        limit: Maximum dividends to return. Default: 10.

    Returns:
        JSON-structured dividend data (date, amount).

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/dividend-history/{symbol}?limit={limit}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_splits_history(symbol: str) -> str:
    """
    Retrieves stock split history.

    Args:
        symbol: Stock ticker symbol.

    Returns:
        JSON-structured split data (date, ratio).

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/splits-history/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_earnings_history(symbol: str, limit: int = 5) -> str:
    """
    Retrieves historical earnings reports (EPS, revenue surprises).

    Args:
        symbol: Stock ticker symbol.
        limit: Maximum reports to return. Default: 5.

    Returns:
        JSON-structured earnings history.

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/earnings-history/{symbol}?limit={limit}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_financial_ratios(symbol: str) -> str:
    """
    Retrieves financial ratios (P/E, debt-to-equity, etc.).

    Args:
        symbol: Stock ticker symbol.

    Returns:
        JSON-structured financial ratios.

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/financial-ratios/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

@mcp.tool()
async def get_ownership_data(symbol: str) -> str:
    """
    Retrieves institutional ownership data.

    Args:
        symbol: Stock ticker symbol.

    Returns:
        JSON-structured ownership data (institutional holders, shares held).

    Raises:
        ValueError: If symbol is empty.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    url = f"/ownership-data/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()