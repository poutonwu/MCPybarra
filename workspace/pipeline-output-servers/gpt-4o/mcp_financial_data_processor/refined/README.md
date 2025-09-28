# mcp_financial_data_processor

## Overview
The `mcp_financial_data_processor` is a Model Context Protocol (MCP) server that provides access to various financial data sources through a set of tools. It allows LLMs to query income statements, balance sheets, cash flow statements, stock prices, market news, and company profiles for financial analysis.

This server connects to an external financial data API (`https://financialdatasets.example.com/api`) using an API key and offers robust validation and error handling for all available tools.

## Installation
Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your environment contains the following key dependency:
- `mcp[cli]`
- `httpx`

Set the required environment variable with your API key:

```bash
export FINANCIAL_API_KEY="your_api_key_here"
```

## Running the Server
To start the server, run the following command from the terminal:

```bash
python mcp_financial_data_processor.py
```

By default, the server uses the `stdio` transport protocol, suitable for local integration with LLM tooling frameworks.

## Available Tools

### 1. `get_income_statements`
Fetches income statements for a specified company.

**Parameters:**
- `ticker`: Stock ticker symbol (e.g., "AAPL")
- `period`: Reporting period ("annual", "quarterly", or "ttm")
- `limit`: Maximum number of statements to return

### 2. `get_balance_sheets`
Retrieves balance sheets for a specified company.

**Parameters:**
- `ticker`: Stock ticker symbol
- `period`: Reporting period ("annual", "quarterly", or "ttm")
- `limit`: Number of records to return

### 3. `get_cash_flows`
Fetches cash flow statements for a company.

**Parameters:**
- `ticker`: Stock ticker symbol
- `period`: Reporting period ("annual", "quarterly", or "ttm")
- `limit`: Maximum number of records to return

### 4. `get_stock_prices`
Gets historical stock price data between a start and end date.

**Parameters:**
- `ticker`: Stock ticker symbol
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format (can be in the future)

### 5. `get_market_news`
Fetches recent financial news related to a specific company or general market news.

**Parameters:**
- `ticker`: Optional stock ticker symbol
- `limit`: Maximum number of articles to return

### 6. `get_company_profile`
Retrieves a company's profile including industry, location, and other metadata.

**Parameters:**
- `ticker`: Stock ticker symbol