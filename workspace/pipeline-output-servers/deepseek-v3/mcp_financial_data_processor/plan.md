### **MCP Tools Plan**  

#### **1. `get_income_statements`**  
- **Description**: Retrieves income statements for a specified company.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol (e.g., "AAPL").  
  - `period` (str, optional): Reporting period ("annual", "quarterly", "TTM"). Default: "annual".  
  - `limit` (int, optional): Maximum number of results to return. Default: 5.  
- **Return Value**: JSON-structured income statement data (revenue, expenses, net income, etc.).  

#### **2. `get_balance_sheets`**  
- **Description**: Retrieves balance sheet data for a specified company.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
  - `period` (str, optional): Reporting period. Default: "annual".  
  - `limit` (int, optional): Maximum results to return. Default: 5.  
- **Return Value**: JSON-structured balance sheet data (assets, liabilities, equity).  

#### **3. `get_cash_flows`**  
- **Description**: Retrieves cash flow statements for a specified company.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
  - `period` (str, optional): Reporting period. Default: "annual".  
  - `limit` (int, optional): Maximum results to return. Default: 5.  
- **Return Value**: JSON-structured cash flow data (operating, investing, financing activities).  

#### **4. `get_stock_prices`**  
- **Description**: Retrieves historical stock price data.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
  - `start_date` (str): Start date in `YYYY-MM-DD` format.  
  - `end_date` (str): End date in `YYYY-MM-DD` format.  
- **Return Value**: JSON-structured historical price data (date, open, high, low, close, volume).  

#### **5. `get_market_news`**  
- **Description**: Retrieves financial news related to a company or market.  
- **Parameters**:  
  - `symbol` (str, optional): Stock ticker symbol. If omitted, returns general market news.  
  - `limit` (int, optional): Maximum news items to return. Default: 10.  
- **Return Value**: JSON-structured news headlines, sources, and timestamps.  

#### **6. `get_company_profile`**  
- **Description**: Retrieves company metadata (industry, location, etc.).  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
- **Return Value**: JSON-structured company profile data.  

#### **7. `get_analyst_estimates`**  
- **Description**: Retrieves analyst estimates (target price, earnings forecasts).  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
  - `limit` (int, optional): Maximum estimates to return. Default: 5.  
- **Return Value**: JSON-structured analyst predictions.  

#### **8. `get_dividend_history`**  
- **Description**: Retrieves dividend payment history.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
  - `limit` (int, optional): Maximum dividends to return. Default: 10.  
- **Return Value**: JSON-structured dividend data (date, amount).  

#### **9. `get_splits_history`**  
- **Description**: Retrieves stock split history.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
- **Return Value**: JSON-structured split data (date, ratio).  

#### **10. `get_earnings_history`**  
- **Description**: Retrieves historical earnings reports (EPS, revenue surprises).  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
  - `limit` (int, optional): Maximum reports to return. Default: 5.  
- **Return Value**: JSON-structured earnings history.  

#### **11. `get_financial_ratios`**  
- **Description**: Retrieves financial ratios (P/E, debt-to-equity, etc.).  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
- **Return Value**: JSON-structured financial ratios.  

#### **12. `get_ownership_data`**  
- **Description**: Retrieves institutional ownership data.  
- **Parameters**:  
  - `symbol` (str): Stock ticker symbol.  
- **Return Value**: JSON-structured ownership data (institutional holders, shares held).  

---

### **Server Overview**  
A **Financial Data MCP Server** that integrates with financial APIs to provide structured data for stock analysis, including financial statements, market news, and historical prices.  

---

### **File to be Generated**  
`financial_mcp_server.py`  

---

### **Dependencies**  
- `financialdatapy` (for financial statements)  
- `yfinance` (for stock prices, dividends, splits)  
- `investpy` (for market news, analyst estimates)  
- `httpx` (for API requests)  
- `mcp[cli]` (MCP SDK)  

This plan strictly adheres to the user's request without adding extraneous functionalities.