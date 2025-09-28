### MCP Tools Plan

#### Tool: `get_income_statements`
- **Description**: Fetches income statements for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
  - `report_period` (str): The reporting period (e.g., annual, quarterly, TTM).
  - `limit` (int): The maximum number of results to return.
- **Return Value**: A JSON-formatted string containing the income statement data.

#### Tool: `get_balance_sheets`
- **Description**: Retrieves balance sheets for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
  - `report_period` (str): The reporting period (e.g., annual, quarterly, TTM).
  - `limit` (int): The maximum number of results to return.
- **Return Value**: A JSON-formatted string containing the balance sheet data.

#### Tool: `get_cash_flows`
- **Description**: Extracts cash flow statements for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
  - `report_period` (str): The reporting period (e.g., annual, quarterly, TTM).
  - `limit` (int): The maximum number of results to return.
- **Return Value**: A JSON-formatted string containing the cash flow statement data.

#### Tool: `get_stock_prices`
- **Description**: Queries historical stock price data for a specified stock using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
  - `start_date` (str): The start date of the historical data range.
  - `end_date` (str): The end date of the historical data range.
- **Return Value**: A JSON-formatted string containing historical stock prices.

#### Tool: `get_market_news`
- **Description**: Fetches the latest financial news related to a company or market using the financialdatasets API.
- **Parameters**:
  - `company_name` (str): The name of the company.
- **Return Value**: A JSON-formatted string containing the latest financial news articles.

#### Tool: `get_company_profile`
- **Description**: Retrieves a company profile including industry and location information using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing the company’s profile.

#### Tool: `get_analyst_estimates`
- **Description**: Gets analyst estimates such as target prices and earnings forecasts for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing analyst estimates.

#### Tool: `get_dividend_history`
- **Description**: Retrieves dividend history records for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing the dividend history.

#### Tool: `get_splits_history`
- **Description**: Queries stock split history for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing the stock split history.

#### Tool: `get_earnings_history`
- **Description**: Fetches historical earnings data, such as EPS, for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing historical earnings data.

#### Tool: `get_financial_ratios`
- **Description**: Gets financial ratios such as P/E and debt-to-equity for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing financial ratios.

#### Tool: `get_ownership_data`
- **Description**: Retrieves ownership structure data, such as institutional holding percentages, for a specified company using the financialdatasets API.
- **Parameters**:
  - `stock_code` (str): The stock code of the company.
- **Return Value**: A JSON-formatted string containing ownership structure data.

### Server Overview
The server will be designed to handle financial data queries and analysis through an MCP interface. It will provide tools that fetch various types of financial data from the financialdatasets API, including income statements, balance sheets, cash flow statements, stock prices, market news, company profiles, analyst estimates, dividend history, stock splits history, earnings history, financial ratios, and ownership data.

### File to be Generated
- **File Name**: `mcp_server.py`

### Dependencies
- `financialdatasets-api`: The Python client library for accessing the financialdatasets API.
- `httpx`: For making asynchronous HTTP requests to the financialdatasets API.