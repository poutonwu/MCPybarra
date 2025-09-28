# MCP 服务器实现计划 - Duffeld 航班信息查询

## MCP Tools Plan

### 1. `search_flights` 工具
- **描述**: 根据出发地、目的地、日期、舱位等参数查询航班信息，支持单程、往返和多程航班查询
- **参数**:
  - `origin` (str): 出发地机场代码 (IATA格式，3个字母)
  - `destination` (str): 目的地机场代码 (IATA格式，3个字母)
  - `departure_date` (str): 出发日期 (格式: YYYY-MM-DD)
  - `return_date` (str, 可选): 返回日期 (格式: YYYY-MM-DD)，仅往返航班需要
  - `cabin_class` (str, 可选): 舱位等级 ('economy', 'premium_economy', 'business', 'first')
  - `trip_type` (str): 航班类型 ('one_way', 'round_trip', 'multi_city')
  - `max_results` (int, 可选): 最大返回结果数 (默认: 5, 最大: 20)
- **返回值**: JSON 格式字符串，包含以下字段的航班信息列表：
  - `flight_number`: 航班号 (如: AF123)
  - `airline`: 航空公司名称
  - `departure_time`: 出发时间 (ISO 8601 格式)
  - `arrival_time`: 到达时间 (ISO 8601 格式)
  - `duration`: 航班时长 (分钟)
  - `price`: 价格 (货币单位根据出发地自动确定)
  - `stops`: 经停次数
  - `cabin_class`: 舱位等级

### 2. `get_offer_details` 工具
- **描述**: 获取特定航班报价的详细信息
- **参数**:
  - `offer_id` (str): 航班报价唯一标识符 (从 search_flights 结果中获取)
- **返回值**: JSON 格式字符串，包含以下字段的详细信息：
  - `offer_id`: 报价ID
  - `flight_number`: 航班号
  - `airline`: 航空公司信息 (名称、IATA代码)
  - `segments`: 航段详细信息 (出发地、目的地、出发时间、到达时间、航班号)
  - `price_breakdown`: 价格明细 (基础票价、税费、手续费等)
  - `baggage_allowance`: 行李额度 (手提行李和托运行李限制)
  - `booking_conditions`: 预订条件 (改签政策、退票政策)

### 3. `search_multi_city` 工具
- **描述**: 处理多城市航班查询，支持复杂的行程规划
- **参数**:
  - `itinerary` (list): 包含多个行程段的列表，每个行程段为一个字典，包含：
    - `origin`: 出发地机场代码 (IATA格式)
    - `destination`: 目的地机场代码 (IATA格式)
    - `date`: 出发日期 (格式: YYYY-MM-DD)
  - `cabin_class` (str, 可选): 航班舱位等级
  - `max_results` (int, 可选): 最大返回结果数 (默认: 5, 最大: 20)
- **返回值**: JSON 格式字符串，包含以下字段的航班信息列表：
  - `journey_id`: 行程唯一标识
  - `total_price`: 总价格
  - `segments`: 各航段详细信息 (航班号、航空公司、出发时间、到达时间)
  - `travel_duration`: 总旅行时间 (分钟)
  - `layover_info`: 中转停留信息 (各中转地停留时间)

## 服务器概述
该MCP服务器专门用于自动化处理Duffel平台的航班信息查询，提供三个核心功能：标准航班查询（支持单程/往返）、特定报价详情获取以及复杂多城市行程查询。服务器将使用Duffel API获取实时航班数据，并按照MCP协议规范返回结构化结果。

## 文件生成计划
- 主文件: `duffel_flight_server.py`

## 依赖项
- `mcp[cli]`: MCP 协议支持
- `httpx`: 异步 HTTP 客户端
- `python-dotenv`: 环境变量管理 (可选)