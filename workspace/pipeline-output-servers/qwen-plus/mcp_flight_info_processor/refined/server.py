import sys
import os
import httpx
import asyncio
import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# 设置代理（如果需要）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 初始化 FastMCP 服务器
mcp = FastMCP("duffel_flight_info_processor")
API_KEY = os.environ.get('DUFFEL_API_KEY')
# 创建异步HTTP客户端
client = httpx.AsyncClient(
    base_url="https://api.duffel.com/air/",
    headers={
        "Accept-Encoding": "gzip",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
        "Duffel-Version": "v1.0"  # 更新为当前支持的版本
    }
)

def validate_iata_code(code: str) -> bool:
    """验证IATA机场代码是否符合格式（3个大写字母）"""
    return isinstance(code, str) and len(code) == 3 and code.isalpha() and code.isupper()

def validate_date(date_str: str) -> bool:
    """验证日期格式是否为YYYY-MM-DD"""
    if not isinstance(date_str, str) or len(date_str) != 10:
        return False
    parts = date_str.split('-')
    if len(parts) != 3:
        return False
    try:
        year, month, day = map(int, parts)
        if not (1900 <= year <= 2100):
            return False
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        return True
    except ValueError:
        return False

def validate_cabin_class(cabin_class: Optional[str]) -> bool:
    """验证舱位等级是否为允许的值"""
    allowed_classes = ['economy', 'premium_economy', 'business', 'first']
    return cabin_class is None or cabin_class in allowed_classes

def format_flight_data(flight_data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化航班数据为标准格式"""
    try:
        segments = flight_data.get('segments', [])
        
        # 计算总时长（分钟）
        total_duration = sum(segment.get('duration_mins', 0) for segment in segments)
        
        # 获取价格信息
        price_info = flight_data.get('total_amount', 'N/A')
        currency = flight_data.get('total_currency', 'USD')
        
        # 获取航空公司信息
        operating_carrier = segments[0].get('operating_carrier', {}) if segments else {}
        airline_name = operating_carrier.get('name', 'Unknown')
        
        # 格式化航班号
        flight_number = segments[0].get('flight_number', 'N/A') if segments else 'N/A'
        
        # 计算经停次数
        stops = max(0, len(segments) - 1)
        
        return {
            "flight_number": flight_number,
            "airline": airline_name,
            "departure_time": segments[0].get('departing_at', 'N/A') if segments else 'N/A',
            "arrival_time": segments[-1].get('arriving_at', 'N/A') if segments else 'N/A',
            "duration": total_duration,
            "price": f"{price_info} {currency}" if price_info != 'N/A' else 'N/A',
            "stops": stops,
            "cabin_class": flight_data.get('cabin_class', 'N/A')
        }
    except Exception as e:
        # 如果格式化失败，返回错误信息
        return {
            "error": f"格式化航班数据失败: {str(e)}",
            "raw_data": flight_data
        }

def format_offer_details(offer_data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化报价详细信息"""
    try:
        # 获取报价ID
        offer_id = offer_data.get('id', 'N/A')
        
        # 获取航班号
        slices = offer_data.get('slices', [])
        flight_number = slices[0].get('segments', [{}])[0].get('flight_number', 'N/A') if slices else 'N/A'
        
        # 获取航空公司信息
        operating_carrier = slices[0].get('segments', [{}])[0].get('operating_carrier', {}) if slices else {}
        airline_name = operating_carrier.get('name', 'Unknown')
        airline_iata = operating_carrier.get('iata_code', 'N/A')
        
        # 格式化航段信息
        segments = []
        for slice in slices:
            for segment in slice.get('segments', []):
                segments.append({
                    "origin": segment.get('origin', {}).get('iata_code', 'N/A'),
                    "destination": segment.get('destination', {}).get('iata_code', 'N/A'),
                    "departure_time": segment.get('departing_at', 'N/A'),
                    "arrival_time": segment.get('arriving_at', 'N/A'),
                    "flight_number": segment.get('flight_number', 'N/A')
                })
        
        # 格式化价格明细
        price_breakdown = {
            "base_price": f"{offer_data.get('base_amount', 'N/A')} {offer_data.get('base_currency', 'N/A')}",
            "taxes": f"{offer_data.get('tax_amount', 'N/A')} {offer_data.get('tax_currency', 'N/A')}",
            "service_fee": "0 USD",  # Duffel API中没有直接的服务费信息
            "total_price": f"{offer_data.get('total_amount', 'N/A')} {offer_data.get('total_currency', 'N/A')}"
        }
        
        # 格式化行李额度
        baggage_allowance = []
        for baggage in offer_data.get('bags', []):
            allowance = {
                "type": baggage.get('type', 'N/A'),
                "quantity": baggage.get('quantity', 'N/A'),
                "weight": baggage.get('weight_kg', 'N/A')
            }
            baggage_allowance.append(allowance)
        
        # 格式化预订条件
        booking_conditions = {
            "changeable": offer_data.get('changeable', False),
            "refundable": offer_data.get('refundable', False),
            "change_penalty": "根据航空公司政策",  # Duffel API中没有直接的信息
            "refund_penalty": "根据航空公司政策"  # Duffel API中没有直接的信息
        }
        
        return {
            "offer_id": offer_id,
            "flight_number": flight_number,
            "airline": {
                "name": airline_name,
                "iata_code": airline_iata
            },
            "segments": segments,
            "price_breakdown": price_breakdown,
            "baggage_allowance": baggage_allowance,
            "booking_conditions": booking_conditions
        }
    except Exception as e:
        # 如果格式化失败，返回错误信息
        return {
            "error": f"格式化报价详细信息失败: {str(e)}",
            "raw_data": offer_data
        }

def format_multi_city_data(journey_data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化多城市行程数据"""
    try:
        journey_id = journey_data.get('id', 'N/A')
        
        # 获取总价格信息
        total_price = f"{journey_data.get('total_amount', 'N/A')} {journey_data.get('total_currency', 'N/A')}"
        
        # 格式化各航段信息
        segments = []
        slices = journey_data.get('slices', [])
        for slice in slices:
            for segment in slice.get('segments', []):
                segments.append({
                    "flight_number": segment.get('flight_number', 'N/A'),
                    "airline": segment.get('operating_carrier', {}).get('name', 'Unknown'),
                    "departure_time": segment.get('departing_at', 'N/A'),
                    "arrival_time": segment.get('arriving_at', 'N/A')
                })
        
        # 获取中转停留信息
        layover_info = []
        for i in range(len(slices) - 1):
            current_slice = slices[i]
            next_slice = slices[i + 1]
            
            # 获取当前航段的到达时间和下一个航段的出发时间
            current_segments = current_slice.get('segments', [])
            next_segments = next_slice.get('segments', [])
            
            if current_segments and next_segments:
                current_arrival = current_segments[-1].get('arriving_at')
                next_departure = next_segments[0].get('departing_at')
                
                if current_arrival and next_departure:
                    # 计算中转时间（分钟）
                    from datetime import datetime
                    arrival_time = datetime.fromisoformat(current_arrival.replace('Z', '+00:00'))
                    departure_time = datetime.fromisoformat(next_departure.replace('Z', '+00:00'))
                    layover_minutes = (departure_time - arrival_time).total_seconds() / 60
                    
                    layover_info.append({
                        "from": current_slice.get('destination', {}).get('iata_code', 'N/A'),
                        "to": next_slice.get('origin', {}).get('iata_code', 'N/A'),
                        "layover_time_minutes": int(layover_minutes)
                    })
        
        # 计算总旅行时间（分钟）
        first_departure = None
        last_arrival = None
        
        if slices and slices[0].get('segments'):
            first_departure = slices[0]['segments'][0].get('departing_at')
        if slices and slices[-1].get('segments'):
            last_arrival = slices[-1]['segments'][-1].get('arriving_at')
        
        travel_duration = 'N/A'
        if first_departure and last_arrival:
            from datetime import datetime
            arrival_time = datetime.fromisoformat(last_arrival.replace('Z', '+00:00'))
            departure_time = datetime.fromisoformat(first_departure.replace('Z', '+00:00'))
            travel_duration = (arrival_time - departure_time).total_seconds() / 60
        
        return {
            "journey_id": journey_id,
            "total_price": total_price,
            "segments": segments,
            "travel_duration": travel_duration,
            "layover_info": layover_info
        }
    except Exception as e:
        # 如果格式化失败，返回错误信息
        return {
            "error": f"格式化多城市行程数据失败: {str(e)}",
            "raw_data": journey_data
        }

@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    cabin_class: Optional[str] = None,
    trip_type: str = "one_way",
    max_results: int = 5
) -> str:
    """
    根据出发地、目的地、日期、舱位等参数查询航班信息，支持单程、往返和多程航班查询。

    Args:
        origin: 出发地机场代码 (IATA格式，3个字母)。
        destination: 目的地机场代码 (IATA格式，3个字母)。
        departure_date: 出发日期 (格式: YYYY-MM-DD)。
        return_date: 返回日期 (格式: YYYY-MM-DD)，仅往返航班需要。
        cabin_class: 航位等级 ('economy', 'premium_economy', 'business', 'first')。
        trip_type: 航班类型 ('one_way', 'round_trip', 'multi_city')。
        max_results: 最大返回结果数 (默认: 5, 最大: 20)。

    Returns:
        JSON 格式字符串，包含以下字段的航班信息列表：
        - flight_number: 航班号
        - airline: 航空公司名称
        - departure_time: 出发时间 (ISO 8601 格式)
        - arrival_time: 到达时间 (ISO 8601 格式)
        - duration: 航班时长 (分钟)
        - price: 价格 (货币单位根据出发地自动确定)
        - stops: 经停次数
        - cabin_class: 航位等级

    Raises:
        ValueError: 如果参数验证失败。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    try:
        # 参数验证
        if not validate_iata_code(origin):
            raise ValueError(f"无效的出发地机场代码: '{origin}'。必须是3个字母的大写IATA代码。")
        if not validate_iata_code(destination):
            raise ValueError(f"无效的目的地机场代码: '{destination}'。必须是3个字母的大写IATA代码。")
        if not validate_date(departure_date):
            raise ValueError(f"无效的出发日期: '{departure_date}'。必须是格式为YYYY-MM-DD的有效日期。")
        if return_date and not validate_date(return_date):
            raise ValueError(f"无效的返回日期: '{return_date}'。必须是格式为YYYY-MM-DD的有效日期。")
        if not validate_cabin_class(cabin_class):
            raise ValueError(f"无效的舱位等级: '{cabin_class}'。有效值为: economy, premium_economy, business, first。")
        if trip_type not in ['one_way', 'round_trip', 'multi_city']:
            raise ValueError(f"无效的航班类型: '{trip_type}'。有效值为: one_way, round_trip, multi_city。")
        if not isinstance(max_results, int) or not 1 <= max_results <= 20:
            raise ValueError(f"无效的最大结果数: '{max_results}'。必须是1到20之间的整数。")
        
        # 构建请求数据
        data = {
            "cabin_class": cabin_class,
            "max_connections": 0,  # 不允许经停
            "return_date": return_date,
            "slices": [{
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date
            }],
            "passengers": [{
                "type": "adult"
            }],
            "max_results": max_results
        }
        
        # 如果是往返航班，添加返程信息
        if trip_type == "round_trip":
            if not return_date:
                raise ValueError("往返航班必须提供返回日期。")
            data["slices"].append({
                "origin": destination,
                "destination": origin,
                "departure_date": return_date
            })
        
        # 发送请求
        response = await client.post("offer_requests", json=data)
        response.raise_for_status()
        
        # 解析响应数据
        offers = response.json().get("data", [])
        
        # 格式化航班信息
        formatted_results = []
        for offer in offers:
            formatted_results.append(format_flight_data(offer))
        
        return json.dumps(formatted_results, ensure_ascii=False)
    except httpx.HTTPStatusError as e:
        # 处理HTTP错误
        error_msg = f"Duffel API请求失败: {str(e)}\n状态码: {e.response.status_code}\n响应内容: {e.response.text}"
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except Exception as e:
        # 处理其他错误
        error_msg = f"搜索航班时发生错误: {str(e)}"
        return json.dumps({"error": error_msg}, ensure_ascii=False)

@mcp.tool()
async def get_offer_details(offer_id: str) -> str:
    """
    获取特定航班报价的详细信息。

    Args:
        offer_id: 航班报价唯一标识符 (从 search_flights 结果中获取)。

    Returns:
        JSON 格式字符串，包含以下字段的详细信息：
        - offer_id: 报价ID
        - flight_number: 航班号
        - airline: 航空公司信息 (名称、IATA代码)
        - segments: 航段详细信息 (出发地、目的地、出发时间、到达时间)
        - price_breakdown: 价格明细 (基础票价、税费、手续费等)
        - baggage_allowance: 行李额度 (手提行李和托运行李限制)
        - booking_conditions: 预订条件 (改签政策、退票政策)

    Raises:
        ValueError: 如果参数验证失败。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    try:
        # 参数验证
        if not isinstance(offer_id, str) or not offer_id.strip():
            raise ValueError("无效的报价ID。报价ID不能为空或仅包含空白字符。")
        
        # 发送请求
        response = await client.get(f"offers/{offer_id}")
        response.raise_for_status()
        
        # 解析响应数据
        offer_data = response.json().get("data", {})
        
        # 格式化报价详细信息
        formatted_data = format_offer_details(offer_data)
        
        return json.dumps(formatted_data, ensure_ascii=False)
    except httpx.HTTPStatusError as e:
        # 处理HTTP错误
        error_msg = f"Duffel API请求失败: {str(e)}\n状态码: {e.response.status_code}\n响应内容: {e.response.text}"
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except Exception as e:
        # 处理其他错误
        error_msg = f"获取报价详细信息时发生错误: {str(e)}"
        return json.dumps({"error": error_msg}, ensure_ascii=False)

@mcp.tool()
async def search_multi_city(itinerary: List[Dict[str, str]], cabin_class: Optional[str] = None, max_results: int = 5) -> str:
    """
    处理多城市航班查询，支持复杂的行程规划。

    Args:
        itinerary: 包含多个行程段的列表，每个行程段为一个字典，包含：
                   - origin: 出发地机场代码 (IATA格式)
                   - destination: 目的地机场代码 (IATA格式)
                   - date: 出发日期 (格式: YYYY-MM-DD)
        cabin_class: 航班舱位等级。
        max_results: 最大返回结果数 (默认: 5, 最大: 20)。

    Returns:
        JSON 格式字符串，包含以下字段的航班信息列表：
        - journey_id: 行程唯一标识
        - total_price: 总价格
        - segments: 各航段详细信息 (航班号、航空公司、出发时间、到达时间)
        - travel_duration: 总旅行时间 (分钟)
        - layover_info: 中转停留信息 (各中转地停留时间)

    Raises:
        ValueError: 如果参数验证失败。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    try:
        # 参数验证
        if not isinstance(itinerary, list) or len(itinerary) < 2:
            raise ValueError("无效的行程列表。必须是至少包含两个行程段的列表。")
        
        for i, segment in enumerate(itinerary):
            if not isinstance(segment, dict):
                raise ValueError(f"无效的行程段: 第{i+1}个行程段必须是一个字典。")
            
            origin = segment.get('origin')
            destination = segment.get('destination')
            date = segment.get('date')
            
            if not validate_iata_code(origin):
                raise ValueError(f"无效的出发地机场代码: '{origin}'（第{i+1}个行程段）。必须是3个字母的大写IATA代码。")
            if not validate_iata_code(destination):
                raise ValueError(f"无效的目的地机场代码: '{destination}'（第{i+1}个行程段）。必须是3个字母的大写IATA代码。")
            if not validate_date(date):
                raise ValueError(f"无效的出发日期: '{date}'（第{i+1}个行程段）。必须是格式为YYYY-MM-DD的有效日期。")
        
        if not validate_cabin_class(cabin_class):
            raise ValueError(f"无效的舱位等级: '{cabin_class}'。有效值为: economy, premium_economy, business, first。")
        
        if not isinstance(max_results, int) or not 1 <= max_results <= 20:
            raise ValueError(f"无效的最大结果数: '{max_results}'。必须是1到20之间的整数。")
        
        # 构建请求数据
        data = {
            "cabin_class": cabin_class,
            "max_connections": 0,  # 不允许经停
            "slices": [],
            "passengers": [{
                "type": "adult"
            }],
            "max_results": max_results
        }
        
        # 添加行程段信息
        for segment in itinerary:
            data["slices"].append({
                "origin": segment.get('origin'),
                "destination": segment.get('destination'),
                "departure_date": segment.get('date')
            })
        
        # 发送请求
        response = await client.post("offer_requests", json=data)
        response.raise_for_status()
        
        # 解析响应数据
        journeys = response.json().get("data", [])
        
        # 格式化多城市行程信息
        formatted_results = []
        for journey in journeys:
            formatted_results.append(format_multi_city_data(journey))
        
        return json.dumps(formatted_results, ensure_ascii=False)
    except httpx.HTTPStatusError as e:
        # 处理HTTP错误
        error_msg = f"Duffel API请求失败: {str(e)}\n状态码: {e.response.status_code}\n响应内容: {e.response.text}"
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except Exception as e:
        # 处理其他错误
        error_msg = f"搜索多城市行程时发生错误: {str(e)}"
        return json.dumps({"error": error_msg}, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()