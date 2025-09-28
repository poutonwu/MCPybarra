import sys
import os
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any
import json
import re
import asyncio

# Initialize FastMCP server
mcp = FastMCP("financial_data_query")

# Set up environment variables for proxy support
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Create an async HTTP client with base URL and headers
API_BASE_URL = "https://api.financialdatasets.ai"
USER_AGENT = "financial-data-query/1.0"

# Global variable to hold the HTTP client
client = None

def initialize_client():
    """Initialize the HTTP client with proper configuration."""
    global client
    try:
        client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json"
            },
            timeout=30.0  # Add a timeout for better error handling
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize HTTP client: {str(e)}") from e

# Initialize the client at module load time
initialize_client()

def validate_stock_symbol(symbol: str) -> None:
    """Validate stock symbol format."""
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        raise ValueError(f"Invalid stock symbol format: '{symbol}'. Must be uppercase letters (1-5 characters).")

def validate_report_period(period: str) -> None:
    """Validate report period value."""
    if period not in ['annual', 'quarterly', 'ttm']:
        raise ValueError(f"Invalid report period: '{period}'. Must be one of 'annual', 'quarterly', or 'ttm'.")

def validate_positive_integer(value: int, param_name: str) -> None:
    """Validate that a value is a positive integer."""
    if value <= 0:
        raise ValueError(f"{param_name} must be a positive integer. Received: {value}")

def validate_date_format(date_str: str) -> None:
    """Validate date format (YYYY-MM-DD)."""
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        raise ValueError(f"Invalid date format: '{date_str}'. Expected format: 'YYYY-MM-DD'")

async def make_api_request(endpoint: str, params: dict) -> str:
    """Make API request and handle common error cases."""
    global client
    
    if client is None:
        raise RuntimeError("HTTP client not initialized. Please call initialize_client() first.")
        
    try:
        # Log the full URL for debugging
        full_url = f"{client.base_url}{endpoint}?{ '&'.join([f'{k}={v}' for k, v in params.items()]) }"
        print(f"Making API request to: {full_url}")  # Debug logging
        
        response = await client.get(endpoint, params=params)
        
        # Detailed error information
        if response.status_code >= 400:
            error_msg = f"API request failed with status {response.status_code}: {response.reason_phrase}"
            try:
                # Try to parse JSON error response
                error_data = response.json()
                error_msg += f"\nResponse content: {json.dumps(error_data, indent=2)}"
            except json.JSONDecodeError:
                # Fallback to raw text if not JSON
                error_msg += f"\nResponse content: {response.text}"
            raise ValueError(error_msg)
            
        # Validate content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            raise ValueError(f"Unexpected content type: {content_type}")
            
        return response.text
    except httpx.TimeoutException as e:
        raise ValueError("API request timed out. Please check your internet connection and try again.") from e
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"API request failed: {str(e)}") from e

@mcp.tool()
async def get_income_statements(stock_symbol: str, report_period: str, limit: int = 10) -> str:
    """获取指定公司的财务报表数据，包括报告日期、总收入、成本、净利润等字段。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。
        report_period: 报告周期 (必填)，可选值为 'annual', 'quarterly', 'ttm'。
        limit: 返回记录数量限制 (可选，默认10)，必须为正整数。

    Returns:
        JSON 格式字符串，包含收入声明数据。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_income_statements(stock_symbol='AAPL', report_period='annual', limit=5)
        '[{"date":"2023-09-30","totalRevenue":383285000000,"costOfRevenue":246597000000,"netIncome":99803000000},...]'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        validate_report_period(report_period)
        validate_positive_integer(limit, "limit")
        
        # Make API request
        result = await make_api_request("/income-statements", {
            "symbol": stock_symbol,
            "period": report_period,
            "limit": limit
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_income_statements failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_balance_sheets(stock_symbol: str, report_period: str, limit: int = 10) -> str:
    """获取公司资产负债表，包括资产、负债和股东权益详细信息。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。
        report_period: 报告周期 (必填)，可选值为 'annual', 'quarterly', 'ttm'。
        limit: 返回记录数量限制 (可选，默认10)，必须为正整数。

    Returns:
        JSON 格式字符串，包含资产负债表数据。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_balance_sheets(stock_symbol='AAPL', report_period='annual', limit=5)
        '[{"date":"2023-09-30","totalAssets":4323456000000,"totalLiabilities":2123456000000,...}]'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        validate_report_period(report_period)
        validate_positive_integer(limit, "limit")
        
        # Make API request
        result = await make_api_request("/balance-sheets", {
            "symbol": stock_symbol,
            "period": report_period,
            "limit": limit
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_balance_sheets failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_cash_flows(stock_symbol: str, report_period: str, limit: int = 10) -> str:
    """获取公司现金流量表，提供结构化的现金流数据。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。
        report_period: 报告周期 (必填)，可选值为 'annual', 'quarterly', 'ttm'。
        limit: 返回记录数量限制 (可选，默认10)，必须为正整数。

    Returns:
        JSON 格式字符串，包含现金流量数据，分为经营、投资和融资活动现金流。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_cash_flows(stock_symbol='AAPL', report_period='annual', limit=5)
        '[{"date":"2023-09-30","operatingCashFlow":110764000000,"investingCashFlow":-34567000000,...}]'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        validate_report_period(report_period)
        validate_positive_integer(limit, "limit")
        
        # Make API request
        result = await make_api_request("/cash-flows", {
            "symbol": stock_symbol,
            "period": report_period,
            "limit": limit
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_cash_flows failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_stock_prices(stock_symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """查询指定股票的历史价格数据，支持自定义时间范围。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。
        start_date: 开始日期 (可选)，格式为 'YYYY-MM-DD'。
        end_date: 结束日期 (可选)，格式为 'YYYY-MM-DD'。

    Returns:
        JSON 格式字符串，包含日期范围内的历史价格数据（开盘价、收盘价、最高价、最低价、成交量）。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_stock_prices(stock_symbol='AAPL', start_date='2023-01-01', end_date='2023-12-31')
        '{"meta":{"symbol":"AAPL",...},"values":[{"datetime":"2023-12-29","open":"191.20001","high":"191.58","low":"190.33","close":"191.43","volume":"50294500"}]}'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Date format validation
        if start_date:
            validate_date_format(start_date)
        if end_date:
            validate_date_format(end_date)
        
        # Make API request
        params = {
            "symbol": stock_symbol
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        result = await make_api_request("/stock-prices", params)
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_stock_prices failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_market_news(stock_symbol: Optional[str] = None, topic: Optional[str] = None) -> str:
    """获取与公司或市场相关的最新金融新闻。

    Args:
        stock_symbol: 股票代码 (可选)，必须是大写字母组成的字符串，如 'AAPL'。
        topic: 新闻主题 (可选)，用于过滤特定主题的新闻。

    Returns:
        JSON 格式字符串，包含最新金融新闻，包括标题、来源、摘要和相关链接。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_market_news(stock_symbol='AAPL', topic='technology')
        '[{"title":"Apple Announces New Product Line","source":"Financial Times","summary":"Apple Inc. announced a new line of products today...","url":"https://example.com/news1"}]'
    """
    try:
        # Input validation
        if stock_symbol:
            validate_stock_symbol(stock_symbol)
        
        # Make API request
        params = {}
        if stock_symbol:
            params["symbol"] = stock_symbol
        if topic:
            params["topic"] = topic
            
        result = await make_api_request("/market-news", params)
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_market_news failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_company_profile(stock_symbol: str) -> str:
    """获取公司简介信息，包括行业、所在地、市值、上市交易所等。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含公司基本信息。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_company_profile(stock_symbol='AAPL')
        '{"symbol":"AAPL","name":"Apple Inc.","industry":"Technology","location":"Cupertino, CA","marketCap":"2.8T","exchange":"NASDAQ"}'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/company-profile", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_company_profile failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_analyst_estimates(stock_symbol: str) -> str:
    """获取分析师预测数据，包括目标价格范围、收益预测、评级变化等。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含分析师预测数据。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_analyst_estimates(stock_symbol='AAPL')
        '{"symbol":"AAPL","targetPriceHigh":220.00,"targetPriceLow":180.00,"averageRating":"Buy","revenueEstimate":390000000000}'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/analyst-estimates", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_analyst_estimates failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_dividend_history(stock_symbol: str) -> str:
    """获取公司股息历史记录，包括除息日、支付日和股息金额。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含股息历史记录。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_dividend_history(stock_symbol='AAPL')
        '[{"exDate":"2023-02-10","paymentDate":"2023-02-16","dividend":0.23},...]'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/dividend-history", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_dividend_history failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_splits_history(stock_symbol: str) -> str:
    """获取股票分割历史记录，包括分割日期和分割比例。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含股票分割记录。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_splits_history(stock_symbol='AAPL')
        '[{"splitDate":"2020-08-31","splitRatio":"4:1"},...]'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/splits-history", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_splits_history failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_earnings_history(stock_symbol: str) -> str:
    """获取公司历史财报数据，如每股收益(EPS)及其他关键财务指标。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含每股收益(EPS)数据及其他关键财务指标的历史记录。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_earnings_history(stock_symbol='AAPL')
        '[{"fiscalDateEnding":"2023-09-30","reportedCurrency":"USD","grossProfit":169149000000,...}]'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/earnings-history", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_earnings_history failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_financial_ratios(stock_symbol: str) -> str:
    """获取公司财务比率，如市盈率(P/E)、负债权益比、流动比率等关键财务比率。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含市盈率(P/E)、负债权益比、流动比率等关键财务比率。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_financial_ratios(stock_symbol='AAPL')
        '{"symbol":"AAPL","peRatio":29.3,"debtToEquity":1.85,"currentRatio":1.15}'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/financial-ratios", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_financial_ratios failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

@mcp.tool()
async def get_ownership_data(stock_symbol: str) -> str:
    """获取公司股权结构数据，如机构持股比例、内部人士持股比例等所有权信息。

    Args:
        stock_symbol: 股票代码 (必填)，必须是大写字母组成的字符串，如 'AAPL'。

    Returns:
        JSON 格式字符串，包含机构持股比例、内部人士持股比例等所有权信息。

    Raises:
        ValueError: 如果输入参数无效或API请求失败。

    示例:
        >>> get_ownership_data(stock_symbol='AAPL')
        '{"symbol":"AAPL","institutionalOwnershipPercent":62.5,"insiderOwnershipPercent":0.58}'
    """
    try:
        # Input validation
        validate_stock_symbol(stock_symbol)
        
        # Make API request
        result = await make_api_request("/ownership-data", {
            "symbol": stock_symbol
        })
        
        # Return raw JSON string to maintain structure
        return result
    except Exception as e:
        # Wrap all exceptions with clear error message
        error_msg = f"get_ownership_data failed: {str(e)}"
        print(f"ERROR: {error_msg}")  # Log error locally
        raise ValueError(error_msg) from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()