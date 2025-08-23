import re
import sys
import httpx
from typing import List, Dict, Union, Optional
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("flight_info")

# 假设的航班API基础URL和用户代理
FLIGHT_API_BASE = "https://api.flightinfo.com"
USER_AGENT = "flight-info-app/1.0 (contact@example.com)"

@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    cabin_class: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants: int = 0
) -> str:
    """
    根据参数查询航班信息，支持单程、往返航班查询。

    Args:
        origin: 出发地机场代码（例如 'PEK' 表示北京首都国际机场）。
        destination: 目的地机场代码（例如 'SHA' 表示上海虹桥国际机场）。
        departure_date: 出发日期，格式为 'YYYY-MM-DD'。
        return_date: 返回日期，格式为 'YYYY-MM-DD'，仅在往返查询时提供。
        cabin_class: 舱位等级（可选值：economy, premium_economy, business, first），默认为 economy。
        adults: 成人旅客数量，默认为 1。
        children: 儿童旅客数量，默认为 0。
        infants: 婴儿旅客数量，默认为 0。

    Returns:
        包含航班详细信息的JSON字符串，包括：
        - 航班号
        - 出发时间
        - 到达时间
        - 航空公司
        - 价格详情（经济舱、商务舱等）
        - 总飞行时间
        - 中转信息（如有）

    Raises:
        ValueError: 如果输入参数不符合要求（如日期格式错误、无效的机场代码等）。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        单程查询:
        search_flights(origin="PEK", destination="SHA", departure_date="2023-12-25")
        
        往返查询:
        search_flights(
            origin="PEK", 
            destination="SHA", 
            departure_date="2023-12-25", 
            return_date="2023-12-30"
        )
    """
    # 输入验证
    if not re.match(r"^[A-Z]{3}$", origin):
        raise ValueError(f"无效的出发地机场代码: '{origin}'。必须是三个大写字母 (例如, 'PEK')。")
    
    if not re.match(r"^[A-Z]{3}$", destination):
        raise ValueError(f"无效的目的地机场代码: '{destination}'。必须是三个大写字母 (例如, 'SHA')。")
    
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, departure_date):
        raise ValueError(f"无效的出发日期: '{departure_date}'。必须是 YYYY-MM-DD 格式。")
    
    if return_date and not re.match(date_pattern, return_date):
        raise ValueError(f"无效的返回日期: '{return_date}'。必须是 YYYY-MM-DD 格式。")
    
    valid_cabin_classes = ["economy", "premium_economy", "business", "first"]
    if cabin_class not in valid_cabin_classes:
        raise ValueError(f"无效的舱位等级: '{cabin_class}'。有效值: {', '.join(valid_cabin_classes)}")
    
    if adults < 0 or children < 0 or infants < 0:
        raise ValueError("旅客数量不能为负数。")
    
    if infants > adults:
        raise ValueError("婴儿数量不能超过成人数量。")

    # 构建查询参数
    params = {
        "origin": origin,
        "destination": destination,
        "departureDate": departure_date,
        "cabinClass": cabin_class,
        "adults": adults,
        "children": children,
        "infants": infants
    }
    
    if return_date:
        params["returnDate"] = return_date

    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient(base_url=FLIGHT_API_BASE, headers=headers) as client:
        response = await client.get("/flights/search", params=params)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_offer_details(offer_id: str) -> str:
    """
    获取特定航班报价的详细信息。

    Args:
        offer_id: 航班报价唯一标识符（由 search_flights 或 search_multi_city 返回）。

    Returns:
        包含完整报价详情的JSON字符串，包括：
        - 完整的行程信息
        - 所有乘客类型的票价详情
        - 税费明细
        - 退改签政策
        - 行李额度
        - 座位选择选项
        - 餐食选项

    Raises:
        ValueError: 如果 offer_id 格式无效。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        get_offer_details(offer_id="OFFER-20231225-PEK-SHA-CZ3104-ECONOMY")
    """
    # 输入验证
    if not re.match(r"^OFFER-\d{8}-[A-Z]{3}-[A-Z]{3}-[A-Z0-9]+-[A-Za-z_]+$", offer_id):
        raise ValueError(f"无效的报价ID: '{offer_id}'。必须符合指定格式。")

    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient(base_url=FLIGHT_API_BASE, headers=headers) as client:
        response = await client.get(f"/offers/{offer_id}/details")
        response.raise_for_status()
        return response.text

@mcp.tool()
async def search_multi_city(
    route_segments: List[Dict[str, Union[str, int]]],
    cabin_class: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants: int = 0
) -> str:
    """
    处理多城市航班查询，支持复杂的行程规划。

    Args:
        route_segments: 行程段列表，每个字典包含以下字段：
            - origin: 出发地机场代码（例如 'PEK'）
            - destination: 目的地机场代码（例如 'SHA'）
            - departure_date: 出发日期，格式为 'YYYY-MM-DD'
        cabin_class: 舱位等级（可选值：economy, premium_economy, business, first），默认为 economy。
        adults: 成人旅客数量，默认为 1。
        children: 儿童旅客数量，默认为 0。
        infants: 婴儿旅客数量，默认为 0。

    Returns:
        包含多城市航班详细信息的JSON字符串，包括：
        - 整个行程的航班组合
        - 每个航段的详细信息
        - 总价格及各航段价格分配
        - 转机等待时间
        - 航空公司联盟信息
        - 共享航班信息

    Raises:
        ValueError: 如果输入参数不符合要求（如日期格式错误、无效的机场代码等）。
        httpx.HTTPStatusError: 如果API请求失败。

    示例:
        search_multi_city(
            route_segments=[
                {"origin": "PEK", "destination": "SHA", "departure_date": "2023-12-25"},
                {"origin": "SHA", "destination": "CAN", "departure_date": "2023-12-28"},
                {"origin": "CAN", "destination": "PEK", "departure_date": "2023-12-30"}
            ]
        )
    """
    # 输入验证
    if not route_segments or len(route_segments) < 2:
        raise ValueError("多城市查询至少需要两个行程段。")
    
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    for i, segment in enumerate(route_segments):
        if "origin" not in segment:
            raise ValueError(f"第 {i+1} 个行程段缺少 'origin' 字段。")
        if "destination" not in segment:
            raise ValueError(f"第 {i+1} 个行程段缺少 'destination' 字段。")
        if "departure_date" not in segment:
            raise ValueError(f"第 {i+1} 个行程段缺少 'departure_date' 字段。")
        
        if not re.match(r"^[A-Z]{3}$", segment["origin"]):
            raise ValueError(f"第 {i+1} 个行程段的出发地机场代码无效: '{segment['origin']}'。必须是三个大写字母。")
        
        if not re.match(r"^[A-Z]{3}$", segment["destination"]):
            raise ValueError(f"第 {i+1} 个行程段的目的地机场代码无效: '{segment['destination']}'。必须是三个大写字母。")
        
        if not re.match(date_pattern, segment["departure_date"]):
            raise ValueError(f"第 {i+1} 个行程段的出发日期无效: '{segment['departure_date']}'。必须是 YYYY-MM-DD 格式。")
    
    valid_cabin_classes = ["economy", "premium_economy", "business", "first"]
    if cabin_class not in valid_cabin_classes:
        raise ValueError(f"无效的舱位等级: '{cabin_class}'。有效值: {', '.join(valid_cabin_classes)}")
    
    if adults < 0 or children < 0 or infants < 0:
        raise ValueError("旅客数量不能为负数。")
    
    if infants > adults:
        raise ValueError("婴儿数量不能超过成人数量。")

    # 构建查询参数
    params = {
        "cabinClass": cabin_class,
        "adults": adults,
        "children": children,
        "infants": infants
    }
    
    # 添加行程段参数
    for i, segment in enumerate(route_segments):
        params[f"origin{i+1}"] = segment["origin"]
        params[f"destination{i+1}"] = segment["destination"]
        params[f"departureDate{i+1}"] = segment["departure_date"]

    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient(base_url=FLIGHT_API_BASE, headers=headers) as client:
        response = await client.get("/flights/multi-city", params=params)
        response.raise_for_status()
        return response.text

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run("stdio")