# mcp_financial_data_processor

## Overview
This server provides access to financial data through the Model Context Protocol (MCP). It acts as a bridge to the Financial Datasets API, offering tools to retrieve income statements, balance sheets, stock prices, company profiles, and other financial information.

## Installation
1. Ensure Python 3.10+ is installed.
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

The following packages are required:
- `mcp[cli]`
- `httpx`

## Running the Server
To start the server, run the Python script from the command line:
```bash
python mcp_financial_data_processor.py
```

## Available Tools
The server provides these MCP tools for financial data retrieval:

### **Financial Statements**
- `get_income_statements(symbol: str, period: str = "annual", limit: int = 5)`  
  Retrieves income statement data (revenue, expenses, net income) for a company.

- `get_balance_sheets(symbol: str, period: str = "annual", limit: int = 5)`  
  Retrieves balance sheet data (assets, liabilities, equity) for a company.

- `get_cash_flows(symbol: str, period: str = "annual", limit: int = 5)`  
  Retrieves cash flow statements (operating, investing, financing activities).

### **Stock Market Data**
- `get_stock_prices(symbol: str, start_date: str, end_date: str)`  
  Retrieves historical stock price data between specified dates.

- `get_market_news(symbol: str = None, limit: int = 10)`  
  Retrieves financial news headlines related to a company or general market news.

### **Company Information**
- `get_company_profile(symbol: str)`  
  Retrieves metadata about a company (industry, location, etc.).

- `get_analyst_estimates(symbol: str, limit: int = 5)`  
  Retrieves analyst estimates including target prices and earnings forecasts.

- `get_dividend_history(symbol: str, limit: int = 10)`  
  Retrieves dividend payment history for a company.

- `get_splits_history(symbol: str)`  
  Retrieves stock split history for a company.

- `get_earnings_history(symbol: str, limit: int = 5)`  
  Retrieves historical earnings reports (EPS, revenue surprises).

- `get_financial_ratios(symbol: str)`  
  Retrieves key financial ratios (P/E, debt-to-equity, etc.).

- `get_ownership_data(symbol: str)`  
  Retrieves institutional ownership information for a company's stock.