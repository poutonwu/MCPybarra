# mcp_financial_data_processor

## Overview

The `mcp_financial_data_processor` is a Model Context Protocol (MCP) server that provides access to various financial data sources via the FinancialDatasets API. It allows Large Language Models (LLMs) to query real-time and historical financial information, including income statements, balance sheets, stock prices, market news, analyst estimates, and more.

This server enables seamless integration with LLM applications by exposing structured tools for financial data retrieval while ensuring robustness, clarity, and performance through async I/O, input validation, and error handling.

---

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the MCP SDK and other dependencies:

```bash
pip install mcp[cli] httpx
```

3. Save the server code in a file named `mcp_financial_data_processor.py`.
4. Create a `requirements.txt` file containing:

```
mcp[cli]
httpx
```

---

## Running the Server

To run the server, execute the following command:

```bash
python mcp_financial_data_processor.py
```

Make sure to set your FinancialDatasets API key as an environment variable before running:

```bash
export FINANCIALDATASETS_API_KEY='your_api_key_here'
```

If behind a proxy, also set:

```bash
export HTTP_PROXY='http://your.proxy.server:port'
export HTTPS_PROXY='https://your.proxy.server:port'
```

---

## Available Tools

Each tool provides access to a specific type of financial data from the FinancialDatasets API. All tools raise descriptive `ValueError` exceptions on invalid input or failed requests.

### 1. `get_income_statements(stock_code: str, report_period: str, limit: int) -> str`

Fetches income statements for a company.  
**Example:** `get_income_statements(stock_code="NVDA", report_period="annual", limit=10)`

### 2. `get_balance_sheets(stock_code: str, report_period: str, limit: int) -> str`

Retrieves balance sheets for a company.  
**Example:** `get_balance_sheets(stock_code="NVDA", report_period="quarterly", limit=5)`

### 3. `get_cash_flows(stock_code: str, report_period: str, limit: int) -> str`

Extracts cash flow statements for a company.  
**Example:** `get_cash_flows(stock_code="AAPL", report_period="ttm", limit=8)`

### 4. `get_stock_prices(stock_code: str, start_date: str, end_date: str) -> str`

Queries historical stock price data.  
**Example:** `get_stock_prices(stock_code="TSLA", start_date="2023-01-01", end_date="2023-12-31")`

### 5. `get_market_news(company_name: str) -> str`

Fetches the latest financial news related to a company or market.  
**Example:** `get_market_news(company_name="NVIDIA")`

### 6. `get_company_profile(stock_code: str) -> str`

Retrieves a company profile including industry and location information.  
**Example:** `get_company_profile(stock_code="MSFT")`

### 7. `get_analyst_estimates(stock_code: str) -> str`

Gets analyst estimates such as target prices and earnings forecasts.  
**Example:** `get_analyst_estimates(stock_code="AMZN")`

### 8. `get_dividend_history(stock_code: str) -> str`

Retrieves dividend history records for a company.  
**Example:** `get_dividend_history(stock_code="JNJ")`

### 9. `get_splits_history(stock_code: str) -> str`

Queries stock split history for a company.  
**Example:** `get_splits_history(stock_code="GOOGL")`

### 10. `get_earnings_history(stock_code: str) -> str`

Fetches historical earnings data, such as EPS.  
**Example:** `get_earnings_history(stock_code="INTC")`

### 11. `get_financial_ratios(stock_code: str) -> str`

Gets financial ratios such as P/E and debt-to-equity.  
**Example:** `get_financial_ratios(stock_code="WMT")`

### 12. `get_ownership_data(stock_code: str) -> str`

Retrieves ownership structure data, such as institutional holding percentages.  
**Example:** `get_ownership_data(stock_code="META")`