# MCP Tools Plan

### 1. Tool: `search_flights`

*   **Function Name**: `search_flights`
*   **Description**: 根据出发地、目的地、日期和舱位等参数查询单程或往返航班信息。要执行往返搜索，请同时提供 `departure_date` 和 `return_date`。如果只提供 `departure_date`，则执行单程搜索。
*   **Parameters**:
    *   `origin` (str): 出发机场的 IATA 代码 (例如, "LHR")。
    *   `destination` (str): 目的地机场的 IATA 代码 (例如, "JFK")。
    *   `departure_date` (str): 出发日期，格式为 "YYYY-MM-DD"。
    *   `cabin_class` (str): 舱位等级。可选值为 "economy", "premium_economy", "business", "first"。默认为 "economy"。
    *   `return_date` (str, optional): 返程日期，格式为 "YYYY-MM-DD"。如果提供此参数，将执行往返查询。如果省略，则执行单程查询。
*   **Return Value**: 返回一个 JSON 字符串，其中包含航班报价列表。每个报价都包括价格、航班时刻、航空公司和行程摘要。如果未找到航班，则返回一个空列表。

### 2. Tool: `get_offer_details`

*   **Function Name**: `get_offer_details`
*   **Description**: 获取特定航班报价的完整详细信息。这包括乘客定价、行李限额、退改签政策以及完整的航段信息。
*   **Parameters**:
    *   `offer_id` (str): 从 `search_flights` 或 `search_multi_city` 返回的航班报价的唯一标识符。
*   **Return Value**: 返回一个 JSON 字符串，其中包含指定航班报价的全部详细信息。如果 ID 无效或已过期，则会引发错误。

### 3. Tool: `search_multi_city`

*   **Function Name**: `search_multi_city`
*   **Description**: 专门处理包含多个航段的复杂多城市行程查询。
*   **Parameters**:
    *   `slices` (list[dict]): 一个描述行程中每个航段的字典列表。每个字典应包含以下键：`origin` (出发机场 IATA 代码), `destination` (目的地机场 IATA 代码), 和 `departure_date` (该航段的出发日期，格式为 "YYYY-MM-DD")。
    *   `cabin_class` (str): 适用于所有航段的舱位等级。可选值为 "economy", "premium_economy", "business", "first"。默认为 "economy"。
*   **Return Value**: 返回一个 JSON 字符串，其中包含符合整个多城市行程的航班报价列表。如果无法满足行程要求，则返回一个空列表。

# Server Overview

该 MCP 服务器旨在提供一个自动化的航班信息查询接口。它利用 Duffel API 的强大功能，允许用户通过一系列定义的工具来执行不同类型的航班搜索。服务器支持单程、往返和复杂的多城市行程查询，并能获取特定航班报价的详细信息，为航班预订和行程规划提供全面的数据支持。

# File to be Generated

`mcp_duffel_server.py`

# Dependencies

*   `mcp[cli]`
*   `duffel-api`