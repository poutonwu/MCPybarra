import re
import sys
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("financial_data")

# 配置常量
FINANCIALDATASETS_API_BASE = "https://api.financialdatasets.com"
API_VERSION = "v1"
USER_AGENT = "financial-data-server/1.0 (contact@example.com)"

# 创建异步HTTP客户端（复用连接以提高性能）
client = httpx.AsyncClient(
    base_url=f"{FINANCIALDATASETS_API_BASE}/{API_VERSION}",
    headers={"User-Agent": USER_AGENT}
)

@mcp.tool()
async def get_income_statements(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    获取指定公司的财务报表数据。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。
        period: 报告周期，可选值为 'annual'（年度）, 'quarterly'（季度）, 或 'ttm'（最近十二个月）。
        limit: 返回结果的最大数量，必须是正整数，默认为5，最大不超过20。

    Returns:
        包含收入报表数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司最近5年的年度收入报表:
        get_income_statements(symbol="AAPL", period="annual", limit=5)
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")
    
    if period.lower() not in ["annual", "quarterly", "ttm"]:
        raise ValueError(f"无效的报告周期: {period}。有效值为 'annual', 'quarterly', 或 'ttm'")
    
    if not 1 <= limit <= 20:
        raise ValueError(f"返回数量限制超出范围: {limit}。有效范围是 1 到 20")

    # 发起API请求
    url = f"/income-statements/{symbol}"
    params = {"period": period.lower(), "limit": limit}
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_balance_sheets(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    获取指定公司的资产负债表数据。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。
        period: 报告周期，可选值为 'annual'（年度）, 'quarterly'（季度）, 或 'ttm'（最近十二个月）。
        limit: 返回结果的最大数量，必须是正整数，默认为5，最大不超过20。

    Returns:
        包含资产负债表数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司最近5年的年度资产负债表:
        get_balance_sheets(symbol="AAPL", period="annual", limit=5)
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")
    
    if period.lower() not in ["annual", "quarterly", "ttm"]:
        raise ValueError(f"无效的报告周期: {period}。有效值为 'annual', 'quarterly', 或 'ttm'")
    
    if not 1 <= limit <= 20:
        raise ValueError(f"返回数量限制超出范围: {limit}。有效范围是 1 到 20")

    # 发起API请求
    url = f"/balance-sheets/{symbol}"
    params = {"period": period.lower(), "limit": limit}
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_cash_flows(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    获取指定公司的现金流量表数据。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。
        period: 报告周期，可选值为 'annual'（年度）, 'quarterly'（季度）, 或 'ttm'（最近十二个月）。
        limit: 返回结果的最大数量，必须是正整数，默认为5，最大不超过20。

    Returns:
        包含现金流量表数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司最近5年的年度现金流量表:
        get_cash_flows(symbol="AAPL", period="annual", limit=5)
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")
    
    if period.lower() not in ["annual", "quarterly", "ttm"]:
        raise ValueError(f"无效的报告周期: {period}。有效值为 'annual', 'quarterly', 或 'ttm'")
    
    if not 1 <= limit <= 20:
        raise ValueError(f"返回数量限制超出范围: {limit}。有效范围是 1 到 20")

    # 发起API请求
    url = f"/cash-flows/{symbol}"
    params = {"period": period.lower(), "limit": limit}
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_stock_prices(symbol: str, start_date: str = None, end_date: str = None) -> str:
    """
    获取指定股票的历史价格数据。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。
        start_date: 开始日期，格式为 'YYYY-MM-DD'（可选）。
        end_date: 结束日期，格式为 'YYYY-MM-DD'（可选）。如果未提供，默认为当前日期。

    Returns:
        包含历史价格数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司从2023-01-01到2023-12-31的历史股价:
        get_stock_prices(symbol="AAPL", start_date="2023-01-01", end_date="2023-12-31")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")
    
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if start_date and not re.match(date_pattern, start_date):
        raise ValueError(f"无效的开始日期: {start_date}。正确格式为 'YYYY-MM-DD'")
    
    if end_date and not re.match(date_pattern, end_date):
        raise ValueError(f"无效的结束日期: {end_date}。正确格式为 'YYYY-MM-DD'")

    # 发起API请求
    url = f"/stock-prices/{symbol}"
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_market_news(ticker: str = None, limit: int = 5) -> str:
    """
    获取与公司或市场相关的最新金融新闻。
    
    Args:
        ticker: 股票代码 (例如, 'AAPL' 代表苹果公司)（可选）。
        limit: 返回结果的最大数量，必须是正整数，默认为5，最大不超过20。

    Returns:
        包含金融新闻数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的最新5条新闻:
        get_market_news(ticker="AAPL", limit=5)
    """
    # 输入验证
    if ticker and not ticker.strip():
        raise ValueError("股票代码不能为空")
    
    if not 1 <= limit <= 20:
        raise ValueError(f"返回数量限制超出范围: {limit}。有效范围是 1 到 20")

    # 发起API请求
    url = "/market-news"
    params = {}
    if ticker:
        params["ticker"] = ticker
    params["limit"] = limit
    
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_company_profile(symbol: str) -> str:
    """
    获取公司简介信息，包括行业、所在地等。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含公司简介信息的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的公司简介:
        get_company_profile(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/company-profile/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_analyst_estimates(symbol: str) -> str:
    """
    获取分析师预测数据，如目标价格和收益预测。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含分析师预测数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的分析师预测数据:
        get_analyst_estimates(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/analyst-estimates/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_dividend_history(symbol: str) -> str:
    """
    获取公司股息历史记录。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含股息历史记录的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的股息历史记录:
        get_dividend_history(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/dividend-history/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_splits_history(symbol: str) -> str:
    """
    查询股票分割历史。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含股票分割历史的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的股票分割历史:
        get_splits_history(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/splits-history/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_earnings_history(symbol: str) -> str:
    """
    获取公司历史财报数据，如每股收益。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含历史财报数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的历史财报数据:
        get_earnings_history(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/earnings-history/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_financial_ratios(symbol: str) -> str:
    """
    获取公司财务比率，如市盈率和负债权益比。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含财务比率数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的财务比率:
        get_financial_ratios(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/financial-ratios/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


@mcp.tool()
async def get_ownership_data(symbol: str) -> str:
    """
    获取公司股权结构数据，如机构持股比例。
    
    Args:
        symbol: 股票代码 (例如, 'AAPL' 代表苹果公司)。

    Returns:
        包含股权结构数据的JSON字符串。

    Raises:
        ValueError: 如果输入参数无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        获取苹果公司的股权结构数据:
        get_ownership_data(symbol="AAPL")
    """
    # 输入验证
    if not symbol or not symbol.strip():
        raise ValueError("股票代码不能为空")

    # 发起API请求
    url = f"/ownership-data/{symbol}"
    response = await client.get(url)
    response.raise_for_status()
    return response.text


async def main():
    """主函数，配置并运行服务器"""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        await mcp.run_stdio_async()
    finally:
        # 优雅地关闭资源
        await client.aclose()
        print("HTTP client closed.")


if __name__ == "__main__":
    # 在Windows上, asyncio.run() 可能需要这个策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())