# **Implementation Plan: Financial Data MCP Server**

This document outlines the implementation plan for creating a Financial Data MCP Server based on the user's request.

## 1. Server Overview

The MCP server will provide a comprehensive interface for querying and analyzing financial market data. It will leverage the `yfinance` library to fetch data from Yahoo Finance. The server will expose a set of tools enabling users to retrieve company financial statements (income statements, balance sheets, cash flows), historical stock prices, market news, company profiles, analyst estimates, dividend and stock split histories, earnings data, key financial ratios, and ownership structure information.

## 2. File to be Generated

All the server logic will be contained within a single Python file:
*   `mcp_financial_server.py`

## 3. Dependencies

The following third-party Python libraries are required for this implementation:

*   `mcp`: The core library for creating the MCP server.
*   `yfinance`: To fetch financial data from Yahoo Finance.
*   `httpx`: As a standard dependency for modern asynchronous MCP servers.
*   `pandas`: `yfinance` returns data in Pandas DataFrames, which will need to be converted to a JSON-serializable format (like a list of dictionaries).

## 4. MCP Tools Plan

The server will implement the following tools, each corresponding to a specific user-requested functionality. All tools will handle potential errors, such as invalid ticker symbols, by raising appropriate exceptions. DataFrames returned by `yfinance` will be converted to JSON strings (orient='records') for the return value.

---

### **Tool: `get_income_statements`**

*   **Function Name**: `get_income_statements`
*   **Description**: Retrieves the income statements for a specified company stock ticker.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'AAPL').
    *   `period`: `str` - The reporting period. Accepts 'annual', 'quarterly'. Defaults to 'annual'.
    *   `limit`: `int` - The maximum number of recent reports to return. Defaults to 4.
*   **Return Value**: A JSON string representing a list of income statement records, sorted from most recent to oldest.

---

### **Tool: `get_balance_sheets`**

*   **Function Name**: `get_balance_sheets`
*   **Description**: Retrieves the balance sheets for a specified company stock ticker.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'MSFT').
    *   `period`: `str` - The reporting period. Accepts 'annual', 'quarterly'. Defaults to 'annual'.
    *   `limit`: `int` - The maximum number of recent reports to return. Defaults to 4.
*   **Return Value**: A JSON string representing a list of balance sheet records, sorted from most recent to oldest.

---

### **Tool: `get_cash_flows`**

*   **Function Name**: `get_cash_flows`
*   **Description**: Retrieves the cash flow statements for a specified company stock ticker.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'GOOGL').
    *   `period`: `str` - The reporting period. Accepts 'annual', 'quarterly'. Defaults to 'annual'.
    *   `limit`: `int` - The maximum number of recent reports to return. Defaults to 4.
*   **Return Value**: A JSON string representing a list of cash flow statement records, sorted from most recent to oldest.

---

### **Tool: `get_stock_prices`**

*   **Function Name**: `get_stock_prices`
*   **Description**: Retrieves historical OHLC (Open, High, Low, Close) stock price data for a specified ticker within a given time range.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'TSLA').
    *   `start_date`: `str` - The start date for the data in 'YYYY-MM-DD' format.
    *   `end_date`: `str` - The end date for the data in 'YYYY-MM-DD' format.
*   **Return Value**: A JSON string representing a list of daily price records, each containing the date, open, high, low, close, and volume.

---

### **Tool: `get_market_news`**

*   **Function Name**: `get_market_news`
*   **Description**: Retrieves recent news articles related to a specific company.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'NVDA').
*   **Return Value**: A JSON string representing a list of news articles, where each article is a dictionary containing keys like 'title', 'publisher', 'link', and 'providerPublishTime'.

---

### **Tool: `get_company_profile`**

*   **Function Name**: `get_company_profile`
*   **Description**: Retrieves the summary profile for a company, including sector, industry, employee count, and business summary.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'AMZN').
*   **Return Value**: A JSON string representing a dictionary of the company's profile information.

---

### **Tool: `get_analyst_estimates`**

*   **Function Name**: `get_analyst_estimates`
*   **Description**: Retrieves analyst recommendations and ratings for a specific stock.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'NFLX').
*   **Return Value**: A JSON string representing a list of analyst recommendation records over time.

---

### **Tool: `get_dividend_history`**

*   **Function Name**: `get_dividend_history`
*   **Description**: Retrieves the historical dividend payment data for a specific stock.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'KO').
*   **Return Value**: A JSON string representing a list of dividend payments, with date and amount for each.

---

### **Tool: `get_splits_history`**

*   **Function Name**: `get_splits_history`
*   **Description**: Retrieves the historical stock split data for a specific company.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'AAPL').
*   **Return Value**: A JSON string representing a list of stock splits, with date and ratio for each.

---

### **Tool: `get_earnings_history`**

*   **Function Name**: `get_earnings_history`
*   **Description**: Retrieves the company's historical earnings data, including reported and estimated EPS.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'META').
*   **Return Value**: A JSON string representing a list of historical earnings events, including the date, actual EPS, and estimated EPS.

---

### **Tool: `get_financial_ratios`**

*   **Function Name**: `get_financial_ratios`
*   **Description**: Retrieves key financial ratios for a company, such as P/E ratio, forward P/E, and price-to-book ratio.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'JPM').
*   **Return Value**: A JSON string representing a dictionary of selected financial ratios available from the company's summary information.

---

### **Tool: `get_ownership_data`**

*   **Function Name**: `get_ownership_data`
*   **Description**: Retrieves the company's ownership structure, including major shareholders and institutional holders.
*   **Parameters**:
    *   `ticker`: `str` - The stock ticker symbol (e.g., 'BRK-A').
*   **Return Value**: A JSON string containing two keys: 'major_holders' and 'institutional_holders', each holding a list of ownership records.