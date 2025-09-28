import os
import sys
import json
import pandas as pd
import yfinance as yf
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial_data_server")
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
def _validate_ticker(ticker: str) -> yf.Ticker:
    """Helper function to validate a ticker and return a Ticker object."""
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker symbol must be a non-empty string.")
    
    stock = yf.Ticker(ticker)
    # yfinance lazily loads data. A quick check for info can validate the ticker.
    if stock.history(period="1d").empty:
        raise ValueError(f"Invalid or unknown ticker symbol: '{ticker}'")
    return stock

def _dataframe_to_json(df: pd.DataFrame) -> str:
    """Helper function to convert a DataFrame to a JSON string."""
    if df.empty:
        return json.dumps([])
    # Reset index to make the date/period a column
    df_copy = df.copy()
    df_copy.reset_index(inplace=True)
    # Convert all column names to string, as some can be datetime objects
    df_copy.columns = df_copy.columns.map(str)
    return df_copy.to_json(orient='records', date_format='iso')

@mcp.tool()
def get_income_statements(ticker: str, period: str = 'annual', limit: int = 4) -> str:
    """
    Retrieves the income statements for a specified company stock ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL').
        period (str): The reporting period. Accepts 'annual', 'quarterly'. Defaults to 'annual'.
        limit (int): The maximum number of recent reports to return. Defaults to 4.

    Returns:
        str: A JSON string representing a list of income statement records, sorted from most recent to oldest.
    
    Example:
        get_income_statements(ticker='AAPL', period='annual', limit=2)
    """
    try:
        if period not in ['annual', 'quarterly']:
            raise ValueError("Period must be either 'annual' or 'quarterly'.")
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")

        stock = _validate_ticker(ticker)
        
        if period == 'annual':
            data = stock.income_stmt
        else:
            data = stock.quarterly_income_stmt
            
        data = data.iloc[:, :limit] # Limit the number of columns (reports)
        return _dataframe_to_json(data.transpose())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_balance_sheets(ticker: str, period: str = 'annual', limit: int = 4) -> str:
    """
    Retrieves the balance sheets for a specified company stock ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        period (str): The reporting period. Accepts 'annual', 'quarterly'. Defaults to 'annual'.
        limit (int): The maximum number of recent reports to return. Defaults to 4.

    Returns:
        str: A JSON string representing a list of balance sheet records, sorted from most recent to oldest.

    Example:
        get_balance_sheets(ticker='MSFT', period='quarterly', limit=4)
    """
    try:
        if period not in ['annual', 'quarterly']:
            raise ValueError("Period must be either 'annual' or 'quarterly'.")
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")

        stock = _validate_ticker(ticker)
        
        if period == 'annual':
            data = stock.balance_sheet
        else:
            data = stock.quarterly_balance_sheet
            
        data = data.iloc[:, :limit]
        return _dataframe_to_json(data.transpose())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_cash_flows(ticker: str, period: str = 'annual', limit: int = 4) -> str:
    """
    Retrieves the cash flow statements for a specified company stock ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'GOOGL').
        period (str): The reporting period. Accepts 'annual', 'quarterly'. Defaults to 'annual'.
        limit (int): The maximum number of recent reports to return. Defaults to 4.

    Returns:
        str: A JSON string representing a list of cash flow statement records, sorted from most recent to oldest.

    Example:
        get_cash_flows(ticker='GOOGL', period='annual', limit=4)
    """
    try:
        if period not in ['annual', 'quarterly']:
            raise ValueError("Period must be either 'annual' or 'quarterly'.")
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer.")

        stock = _validate_ticker(ticker)
        
        if period == 'annual':
            data = stock.cashflow
        else:
            data = stock.quarterly_cashflow
            
        data = data.iloc[:, :limit]
        return _dataframe_to_json(data.transpose())
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_stock_prices(ticker: str, start_date: str, end_date: str) -> str:
    """
    Retrieves historical OHLC (Open, High, Low, Close) stock price data for a specified ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'TSLA').
        start_date (str): The start date for the data in 'YYYY-MM-DD' format.
        end_date (str): The end date for the data in 'YYYY-MM-DD' format.

    Returns:
        str: A JSON string representing a list of daily price records.

    Example:
        get_stock_prices(ticker='TSLA', start_date='2023-01-01', end_date='2023-01-31')
    """
    try:
        stock = _validate_ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        if data.empty:
            return json.dumps({"message": "No data found for the given ticker and date range."})
        return _dataframe_to_json(data)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_market_news(ticker: str) -> str:
    """
    Retrieves recent news articles related to a specific company.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'NVDA').

    Returns:
        str: A JSON string representing a list of news articles.

    Example:
        get_market_news(ticker='NVDA')
    """
    try:
        stock = _validate_ticker(ticker)
        news = stock.news
        if not news:
            return json.dumps({"message": f"No news found for ticker '{ticker}'."})
        return json.dumps(news)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_company_profile(ticker: str) -> str:
    """
    Retrieves the summary profile for a company, including sector, industry, employee count, and business summary.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AMZN').

    Returns:
        str: A JSON string representing a dictionary of the company's profile information.

    Example:
        get_company_profile(ticker='AMZN')
    """
    try:
        stock = _validate_ticker(ticker)
        profile = stock.info
        if not profile:
            raise ValueError(f"Could not retrieve profile for ticker '{ticker}'.")
        # Filter out large, non-serializable, or less useful items
        filtered_profile = {k: v for k, v in profile.items() if isinstance(v, (str, int, float, bool, list, dict))}
        return json.dumps(filtered_profile)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_analyst_estimates(ticker: str) -> str:
    """
    Retrieves analyst recommendations and ratings for a specific stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'NFLX').

    Returns:
        str: A JSON string representing a list of analyst recommendation records over time.

    Example:
        get_analyst_estimates(ticker='NFLX')
    """
    try:
        stock = _validate_ticker(ticker)
        recommendations = stock.recommendations
        if recommendations is None or recommendations.empty:
            return json.dumps({"message": f"No analyst estimates found for ticker '{ticker}'."})
        return _dataframe_to_json(recommendations)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_dividend_history(ticker: str) -> str:
    """
    Retrieves the historical dividend payment data for a specific stock.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'KO').

    Returns:
        str: A JSON string representing a list of dividend payments, with date and amount for each.

    Example:
        get_dividend_history(ticker='KO')
    """
    try:
        stock = _validate_ticker(ticker)
        dividends = stock.dividends
        if dividends.empty:
            return json.dumps({"message": f"No dividend history found for ticker '{ticker}'."})
        dividends_df = dividends.reset_index()
        dividends_df.columns = ['Date', 'Dividends']
        return dividends_df.to_json(orient='records', date_format='iso')
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_splits_history(ticker: str) -> str:
    """
    Retrieves the historical stock split data for a specific company.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL').

    Returns:
        str: A JSON string representing a list of stock splits, with date and ratio for each.

    Example:
        get_splits_history(ticker='AAPL')
    """
    try:
        stock = _validate_ticker(ticker)
        splits = stock.splits
        if splits.empty:
            return json.dumps({"message": f"No stock split history found for ticker '{ticker}'."})
        splits_df = splits.reset_index()
        splits_df.columns = ['Date', 'Stock Splits']
        return splits_df.to_json(orient='records', date_format='iso')
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_earnings_history(ticker: str) -> str:
    """
    Retrieves the company's historical earnings data, including reported and estimated EPS.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'META').

    Returns:
        str: A JSON string representing a list of historical earnings events.

    Example:
        get_earnings_history(ticker='META')
    """
    try:
        stock = _validate_ticker(ticker)
        earnings = stock.earnings
        if earnings.empty:
            return json.dumps({"message": f"No earnings history found for ticker '{ticker}'."})
        return _dataframe_to_json(earnings)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_financial_ratios(ticker: str) -> str:
    """
    Retrieves key financial ratios for a company, such as P/E ratio, forward P/E, and price-to-book ratio.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'JPM').

    Returns:
        str: A JSON string representing a dictionary of selected financial ratios.

    Example:
        get_financial_ratios(ticker='JPM')
    """
    try:
        stock = _validate_ticker(ticker)
        info = stock.info
        if not info:
             raise ValueError(f"Could not retrieve info for ticker '{ticker}' to calculate ratios.")
        
        ratios = {
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "priceToBook": info.get("priceToBook"),
            "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
            "enterpriseToRevenue": info.get("enterpriseToRevenue"),
            "enterpriseToEbitda": info.get("enterpriseToEbitda"),
            "marketCap": info.get("marketCap"),
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),
            "beta": info.get("beta")
        }
        # Filter out None values for a cleaner output
        ratios = {k: v for k, v in ratios.items() if v is not None}
        return json.dumps(ratios)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_ownership_data(ticker: str) -> str:
    """
    Retrieves the company's ownership structure, including major and institutional holders.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'BRK-A').

    Returns:
        str: A JSON string containing lists for 'major_holders' and 'institutional_holders'.

    Example:
        get_ownership_data(ticker='BRK-A')
    """
    try:
        stock = _validate_ticker(ticker)
        major_holders = stock.major_holders
        institutional_holders = stock.institutional_holders
        
        if (major_holders is None or major_holders.empty) and \
           (institutional_holders is None or institutional_holders.empty):
            return json.dumps({"message": f"No ownership data found for ticker '{ticker}'."})

        ownership_data = {
            "major_holders": major_holders.to_dict(orient='records') if major_holders is not None and not major_holders.empty else [],
            "institutional_holders": institutional_holders.to_dict(orient='records') if institutional_holders is not None and not institutional_holders.empty else []
        }
        return json.dumps(ownership_data)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()