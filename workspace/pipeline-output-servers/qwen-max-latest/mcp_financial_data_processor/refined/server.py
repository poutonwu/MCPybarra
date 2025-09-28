import sys
import os
import httpx
import json
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("mcp_financial_data_processor")

# Financial Datasets API base URL
FINANCIALDATASETS_API_BASE = "https://api.financialdatasets.ai"

# Retrieve API key from environment variables
API_KEY = os.environ.get('FINANCIALDATASETS_API_KEY')

if not API_KEY:
    raise ValueError("Environment variable 'FINANCIALDATASETS_API_KEY' is not set.")

# Configure proxy support if needed
HTTP_PROXY = os.environ.get('HTTP_PROXY')
HTTPS_PROXY = os.environ.get('HTTPS_PROXY')

# Shared AsyncClient for improved performance with additional configuration
client = httpx.AsyncClient(
    base_url=FINANCIALDATASETS_API_BASE,
    headers={"X-API-KEY": API_KEY, "Content-Type": "application/json"},
    timeout=30.0,  # Increased timeout for financial data queries
    follow_redirects=True  # Follow redirects automatically
)

@mcp.tool()
async def get_income_statements(stock_code: str, report_period: str, limit: int) -> str:
    """
    Fetches income statements for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').
        report_period: The reporting period (e.g., 'annual', 'quarterly', 'ttm').
        limit: The maximum number of results to return.

    Returns:
        A JSON-formatted string containing the income statement data.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_income_statements(stock_code="NVDA", report_period="annual", limit=10)
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")
        
        if report_period not in ['annual', 'quarterly', 'ttm']:
            raise ValueError("'report_period' must be one of: annual, quarterly, ttm.")
        
        if limit <= 0:
            raise ValueError("'limit' must be a positive integer.")

        url = f"/financials/income-statements?ticker={stock_code}&period={report_period}&limit={limit}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching income statements: {str(e)}")

@mcp.tool()
async def get_balance_sheets(stock_code: str, report_period: str, limit: int) -> str:
    """
    Retrieves balance sheets for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').
        report_period: The reporting period (e.g., 'annual', 'quarterly', 'ttm').
        limit: The maximum number of results to return.

    Returns:
        A JSON-formatted string containing the balance sheet data.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_balance_sheets(stock_code="NVDA", report_period="annual", limit=10)
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")
        
        if report_period not in ['annual', 'quarterly', 'ttm']:
            raise ValueError("'report_period' must be one of: annual, quarterly, ttm.")
        
        if limit <= 0:
            raise ValueError("'limit' must be a positive integer.")

        url = f"/financials/balance-sheets?ticker={stock_code}&period={report_period}&limit={limit}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching balance sheets: {str(e)}")

@mcp.tool()
async def get_cash_flows(stock_code: str, report_period: str, limit: int) -> str:
    """
    Extracts cash flow statements for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').
        report_period: The reporting period (e.g., 'annual', 'quarterly', 'ttm').
        limit: The maximum number of results to return.

    Returns:
        A JSON-formatted string containing the cash flow statement data.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_cash_flows(stock_code="NVDA", report_period="annual", limit=10)
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")
        
        if report_period not in ['annual', 'quarterly', 'ttm']:
            raise ValueError("'report_period' must be one of: annual, quarterly, ttm.")
        
        if limit <= 0:
            raise ValueError("'limit' must be a positive integer.")

        url = f"/financials/cash-flows?ticker={stock_code}&period={report_period}&limit={limit}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching cash flows: {str(e)}")

@mcp.tool()
async def get_stock_prices(stock_code: str, start_date: str, end_date: str) -> str:
    """
    Queries historical stock price data for a specified stock using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').
        start_date: The start date of the historical data range (format: YYYY-MM-DD).
        end_date: The end date of the historical data range (format: YYYY-MM-DD).

    Returns:
        A JSON-formatted string containing historical stock prices.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_stock_prices(stock_code="NVDA", start_date="2023-01-01", end_date="2023-12-31")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")
        
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("'start_date' and 'end_date' must be in format YYYY-MM-DD.")
        
        if start_date > end_date:
            raise ValueError("'start_date' must be before or equal to 'end_date'.")

        url = f"/stock-prices?ticker={stock_code}&start_date={start_date}&end_date={end_date}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching stock prices: {str(e)}")

@mcp.tool()
async def get_market_news(company_name: str) -> str:
    """
    Fetches the latest financial news related to a company or market using the financialdatasets API.

    Args:
        company_name: The name of the company (e.g., 'NVIDIA').

    Returns:
        A JSON-formatted string containing the latest financial news articles.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_market_news(company_name="NVIDIA")
    """
    try:
        # Input validation
        if not company_name or not company_name.strip():
            raise ValueError("'company_name' must be a non-empty string.")

        url = f"/market-news?company_name={company_name}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching market news: {str(e)}")

@mcp.tool()
async def get_company_profile(stock_code: str) -> str:
    """
    Retrieves a company profile including industry and location information using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing the company's profile.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_company_profile(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/company-profile?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching company profile: {str(e)}")

@mcp.tool()
async def get_analyst_estimates(stock_code: str) -> str:
    """
    Gets analyst estimates such as target prices and earnings forecasts for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing analyst estimates.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_analyst_estimates(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/analyst-estimates?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching analyst estimates: {str(e)}")

@mcp.tool()
async def get_dividend_history(stock_code: str) -> str:
    """
    Retrieves dividend history records for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing the dividend history.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_dividend_history(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/dividend-history?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching dividend history: {str(e)}")

@mcp.tool()
async def get_splits_history(stock_code: str) -> str:
    """
    Queries stock split history for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing the stock split history.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_splits_history(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/splits-history?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching splits history: {str(e)}")

@mcp.tool()
async def get_earnings_history(stock_code: str) -> str:
    """
    Fetches historical earnings data, such as EPS, for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing historical earnings data.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_earnings_history(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/earnings-history?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching earnings history: {str(e)}")

@mcp.tool()
async def get_financial_ratios(stock_code: str) -> str:
    """
    Gets financial ratios such as P/E and debt-to-equity for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing financial ratios.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_financial_ratios(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/financial-ratios?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching financial ratios: {str(e)}")

@mcp.tool()
async def get_ownership_data(stock_code: str) -> str:
    """
    Retrieves ownership structure data, such as institutional holding percentages, for a specified company using the financialdatasets API.

    Args:
        stock_code: The stock code of the company (e.g., 'NVDA').

    Returns:
        A JSON-formatted string containing ownership structure data.

    Raises:
        ValueError: If input parameters are invalid or API request fails.

    Example:
        get_ownership_data(stock_code="NVDA")
    """
    try:
        # Input validation
        if not stock_code or not stock_code.strip():
            raise ValueError("'stock_code' must be a non-empty string.")

        url = f"/ownership-data?ticker={stock_code}"
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json())
    except httpx.HTTPStatusError as e:
        raise ValueError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise ValueError(f"Request error occurred: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error fetching ownership data: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()