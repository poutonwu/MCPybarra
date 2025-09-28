# MCP 服务器实施计划：Financial Datasets API 集成

## MCP Tools Plan

### `get_income_statements`
**描述**: 获取指定公司的财务报表数据
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
- `report_period` (str): 报告周期 ('annual', 'quarterly', 'ttm') (必填)
- `limit` (int): 返回记录数量限制 (可选, 默认10)
**返回值**: JSON 格式包含收入声明数据，包括报告日期、总收入、成本、净利润等字段

### `get_balance_sheets`
**描述**: 获取公司资产负债表
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
- `report_period` (str): 报告周期 ('annual', 'quarterly', 'ttm') (必填)
- `limit` (int): 返回记录数量限制 (可选, 默认10)
**返回值**: JSON 格式包含资产负债表数据，包括资产、负债和股东权益详细信息

### `get_cash_flows`
**描述**: 获取公司现金流量表
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
- `report_period` (str): 报告周期 ('annual', 'quarterly', 'ttm') (必填)
- `limit` (int): 返回记录数量限制 (可选, 默认10)
**返回值**: JSON 格式包含现金流量数据，分为经营、投资和融资活动现金流

### `get_stock_prices`
**描述**: 查询指定股票的历史价格
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
- `start_date` (str): 开始日期 (格式YYYY-MM-DD) (可选)
- `end_date` (str): 结束日期 (格式YYYY-MM-DD) (可选)
**返回值**: JSON 格式包含日期范围内的历史价格数据（开盘价、收盘价、最高价、最低价、成交量）

### `get_market_news`
**描述**: 获取与公司或市场相关的金融新闻
**参数**:
- `stock_symbol` (str): 股票代码 (可选)
- `topic` (str): 新闻主题 (可选)
**返回值**: JSON 格式包含最新金融新闻，包括标题、来源、摘要和相关链接

### `get_company_profile`
**描述**: 获取公司简介信息
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含公司基本信息，如名称、行业、所在地、市值、上市交易所等

### `get_analyst_estimates`
**描述**: 获取分析师预测数据
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含分析师预测，包括目标价格范围、收益预测、评级变化等

### `get_dividend_history`
**描述**: 获取公司股息历史
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含股息历史记录，包括除息日、支付日和股息金额

### `get_splits_history`
**描述**: 获取股票分割历史
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含股票分割记录，包括分割日期和分割比例

### `get_earnings_history`
**描述**: 获取公司历史财报数据
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含每股收益(EPS)数据及其他关键财务指标的历史记录

### `get_financial_ratios`
**描述**: 获取公司财务比率
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含市盈率(P/E)、负债权益比、流动比率等关键财务比率

### `get_ownership_data`
**描述**: 获取公司股权结构数据
**参数**:
- `stock_symbol` (str): 股票代码 (必填)
**返回值**: JSON 格式包含机构持股比例、内部人士持股比例等所有权信息

## 服务器概述
该 MCP 服务器将集成 financialdatasets API，提供全面的金融市场数据查询和分析功能。服务器将实现用户请求中列出的所有数据访问功能，支持灵活的参数配置和结构化数据返回。

## 文件生成计划
- **文件名**: `financial_datasets_mcp_server.py`

## 依赖项
- `mcp[cli]` - MCP SDK
- `httpx` - 异步HTTP客户端
- `python-dotenv` - 环境变量管理（如果API需要认证）