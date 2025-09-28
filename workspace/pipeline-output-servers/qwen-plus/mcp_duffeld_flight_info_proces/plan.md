# MCP 服务器实施计划：Duffeld 航班信息查询

## MCP 工具计划

### 1. `search_flights` 工具
- **描述**: 根据出发地、目的地、日期、舱位等参数查询航班信息，支持单程、往返和多程航班查询
- **参数**:
  - `origin` (str): 出发地机场代码 (如 'JFK')
  - `destination` (str): 目的地机场代码 (如 'LAX')
  - `departure_date` (str): 出发日期 (格式: 'YYYY-MM-DD')
  - `return_date` (str, 可选): 返回日期 (格式: 'YYYY-MM-DD')，仅用于往返航班
  - `trip_type` (str): 航班类型 ('one-way', 'round-trip', 'multi-city')
  - `cabin_class` (str, 可选): 舱位等级 ('economy', 'business', 'first')
  - `adults` (int, 默认: 1): 成人旅客数量
  - `children` (int, 默认: 0): 儿童旅客数量
  - `infants` (int, 默认: 0): 婴儿旅客数量
- **返回值**: 包含价格、航班时间、航空公司等详细信息的 JSON 对象数组，每个对象包含:
  - `flight_number`: 航班号
  - `airline`: 航空公司名称
  - `departure_time`: 出发时间 (ISO 8601 格式)
  - `arrival_time`: 到达时间 (ISO 8601 格式)
  - `duration`: 航程时长 (分钟)
  - `price`: 总价格 (货币单位)
  - `stops`: 经停次数
  - `class`: 舱位等级

### 2. `get_offer_details` 工具
- **描述**: 获取特定航班报价的详细信息
- **参数**:
  - `offer_id` (str): 要查询的报价唯一标识符
- **返回值**: 包含完整报价详情的 JSON 对象，包括:
  - `offer_id`: 报价ID
  - `flight_details`: 完整航班信息(与 search_flights 返回结构一致)
  - `passenger_info`: 乘客信息(姓名、年龄、特殊需求等)
  - `baggage_allowance`: 行李额度
  - `cancellation_policy`: 退改签政策
  - `total_price`: 总费用明细(基础票价+税费+服务费)

### 3. `search_multi_city` 工具
- **描述**: 专门处理多城市航班查询，支持复杂的行程规划
- **参数**:
  - `segments` (list of dict): 航程段列表，每个字典包含:
    - `origin`: 出发地机场代码
    - `destination`: 目的地机场代码
    - `date`: 出发日期 (格式: 'YYYY-MM-DD')
  - `cabin_class` (str, 可选): 舱位等级 ('economy', 'business', 'first')
  - `adults` (int, 默认: 1): 成人旅客数量
  - `children` (int, 默认: 0): 儿童旅客数量
  - `infants` (int, 默认: 0): 婴儿旅客数量
- **返回值**: 多城市航班组合的详细信息，包含所有航段的连接信息和整体行程安排，结构为:
  - `itinerary_id`: 行程唯一标识
  - `segments`: 各航段详细信息数组
  - `total_duration`: 整体行程时长
  - `total_price`: 总价格
  - `layover_times`: 各中转站停留时间

## 服务器概述
实现一个基于 Duffeld API 的 MCP 服务器，提供航班信息查询功能。该服务器将提供三个主要工具：
1. 支持各种类型的航班搜索 (`search_flights`)
2. 获取特定报价的详细信息 (`get_offer_details`)
3. 处理复杂多城市行程查询 (`search_multi_city`)

## 文件生成计划
- **文件名**: `duffeld_flight_mcp_server.py`
- **内容**: 
  - FastMCP 服务器初始化代码
  - 三个工具函数的定义和实现
  - HTTP 客户端配置和 Duffeld API 集成
  - 输入验证逻辑和错误处理
  - 服务器启动代码

## 依赖项
- `mcp[cli]`: FastMCP 框架
- `httpx`: 异步 HTTP 客户端
- `python-dotenv`: 环境变量管理(Duffeld API 密钥)
- `pydantic`: 数据验证和模型定义