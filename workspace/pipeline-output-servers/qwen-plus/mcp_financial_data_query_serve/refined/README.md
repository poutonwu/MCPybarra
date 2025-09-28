# mcp_financial_data_query_serve

## Overview
This MCP server provides access to financial data through a set of tools that retrieve income statements, balance sheets, cash flows, stock prices, market news, and more. It connects to the `financialdatasets.ai` API to fetch structured financial information for analysis and reporting.

## Installation
Make sure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes:
```
mcp[cli]
httpx
```

## Running the Server
To start the server, run the Python script from the command line:

```bash
python mcp_financial_data_query_serve.py
```

## Available Tools

The following tools are available for interacting with financial data:

### 1. `get_income_statements`
Fetches income statements (profit and loss data) for a company by stock symbol and report period (annual, quarterly, ttm).

### 2. `get_balance_sheets`
Retrieves balance sheet data including assets, liabilities, and equity for a given company.

### 3. `get_cash_flows`
Provides cash flow statements showing operating, investing, and financing activities.

### 4. `get_stock_prices`
Queries historical stock price data for a given symbol and optional date range.

### 5. `get_market_news`
Fetches recent market-related news articles filtered by stock symbol or topic.

### 6. `get_company_profile`
Gets basic company profile information such as industry, location, market cap, and exchange.

### 7. `get_analyst_estimates`
Retrieves analyst estimates including target price range, average rating, and revenue forecasts.

### 8. `get_dividend_history`
Returns historical dividend records including ex-date, payment date, and amount.

### 9. `get_splits_history`
Fetches stock split history including date and ratio of splits.

### 10. `get_earnings_history`
Gets historical earnings reports including EPS and other key financial metrics.

### 11. `get_financial_ratios`
Provides key financial ratios like P/E ratio, debt-to-equity, and current ratio.

### 12. `get_ownership_data`
Returns ownership structure data including institutional and insider ownership percentages.