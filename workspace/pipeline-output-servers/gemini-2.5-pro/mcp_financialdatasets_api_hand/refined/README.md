# mcp_financialdatasets_api_hand

## Overview
This server provides access to a wide range of financial data through the Model Context Protocol (MCP). It enables clients to retrieve company financials, stock prices, news, ownership structure, and more using standardized API tools backed by Yahoo Finance data.

## Installation
1. Ensure Python 3.10+ is installed
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Requirements include:
- `mcp[cli]`
- `yfinance`
- `pandas`
- `httpx`

## Running the Server
Start the server using Python:
```bash
python financial_data_server.py
```

The server will initialize and begin listening for MCP connections via standard input/output.

## Available Tools

### get_income_statements
Retrieves income statements (profit & loss) for a company. Supports annual or quarterly reports with configurable result limits.

### get_balance_sheets
Fetches balance sheet data showing company assets/liabilities. Available in annual or quarterly formats with customizable report count.

### get_cash_flows
Gets cash flow statements detailing operating, investing, and financing activities. Configurable period and limit options.

### get_stock_prices
Retrieve historical OHLC stock price data for specified date ranges.

### get_market_news
Fetch recent news articles related to a specific company ticker.

### get_company_profile
Get summary profile including industry, business description, employee count, and key financial metrics.

### get_analyst_estimates
Retrieve analyst recommendations and ratings history for a stock.

### get_dividend_history
Get historical dividend payments with dates and amounts.

### get_splits_history
Retrieve historical stock split events with dates and ratio changes.

### get_earnings_history
Access company's historical earnings data including reported vs estimated EPS.

### get_financial_ratios
Get key valuation ratios like P/E, forward P/E, price-to-book, and more.

### get_ownership_data
Retrieve ownership structure including major and institutional holders.