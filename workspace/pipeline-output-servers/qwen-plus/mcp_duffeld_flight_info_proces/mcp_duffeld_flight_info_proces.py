import sys
import os
import httpx
import re
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import json
import logging
from datetime import datetime

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 FastMCP 服务器
mcp = FastMCP("duffeld_flight_info")

# 设置 Duffeld API 配置
DUFFEL_API_BASE = "https://api.duffel.com/flights"
API_VERSION = "beta"
USER_AGENT = "duffeld-flight-server/1.0 (contact@example.com)"

# 获取环境变量中的 API 密钥
API_KEY = os.getenv('DUFFEL_API_KEY')
if not API_KEY:
    logger.warning("DUFFEL_API_KEY 环境变量未设置，航班查询功能将受限")

# 设置代理（如果需要）
HTTP_PROXY = os.environ.get('HTTP_PROXY')
HTTPS_PROXY = os.environ.get('HTTPS_PROXY')

# 创建异步 HTTP 客户端
client = httpx.AsyncClient(
    base_url=DUFFEL_API_BASE,
    headers={
        "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    },
    timeout=30.0,
    proxies={"http://": HTTP_PROXY, "https://": HTTPS_PROXY} if HTTP_PROXY or HTTPS_PROXY else None
)

# 数据模型定义
class FlightSegment(BaseModel):
    origin: str = Field(..., description="出发地机场代码 (如 'JFK')")
    destination: str = Field(..., description="目的地机场代码 (如 'LAX')")
    date: str = Field(..., description="出发日期 (格式: 'YYYY-MM-DD')")

class FlightDetails(BaseModel):
    flight_number: str = Field(..., description="航班号")
    airline: str = Field(..., description="航空公司名称")
    departure_time: str = Field(..., description="出发时间 (ISO 8601 格式)")
    arrival_time: str = Field(..., description="到达时间 (ISO 8601 格式)")
    duration: int = Field(..., description="航程时长 (分钟)")
    price: float = Field(..., description="总价格 (货币单位)")
    stops: int = Field(..., description="经停次数")
    class_: str = Field(..., description="舱位等级", alias="class")

class PassengerInfo(BaseModel):
    name: str = Field(..., description="乘客姓名")
    age: int = Field(..., description="乘客年龄")
    special_needs: Optional[str] = Field(None, description="特殊需求")

class OfferDetails(BaseModel):
    offer_id: str = Field(..., description="报价ID")
    flight_details: List[FlightDetails] = Field(..., description="完整航班信息")
    passenger_info: List[PassengerInfo] = Field(..., description="乘客信息")
    baggage_allowance: str = Field(..., description="行李额度")
    cancellation_policy: str = Field(..., description="退改签政策")
    total_price: float = Field(..., description="总费用明细(基础票价+税费+服务费)")

class MultiCityItinerary(BaseModel):
    itinerary_id: str = Field(..., description="行程唯一标识")
    segments: List[FlightDetails] = Field(..., description="各航段详细信息数组")
    total_duration: int = Field(..., description="整体行程时长 (分钟)")
    total_price: float = Field(..., description="总价格")
    layover_times: List[int] = Field(..., description="各中转站停留时间 (分钟)")

@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    trip_type: str,
    return_date: Optional[str] = None,
    cabin_class: Optional[str] = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0
) -> str:
    """
    根据出发地、目的地、日期、舱位等参数查询航班信息，支持单程、往返和多程航班查询

    Args:
        origin: 出发地机场代码 (如 'JFK')，必填
        destination: 目的地机场代码 (如 'LAX')，必填
        departure_date: 出发日期 (格式: 'YYYY-MM-DD')，必填
        trip_type: 航班类型 ('one-way', 'round-trip', 'multi-city')，必填
        return_date: 返回日期 (格式: 'YYYY-MM-DD')，仅用于往返航班，可选
        cabin_class: 舱位等级 ('economy', 'business', 'first')，可选
        adults: 成人旅客数量，默认1，可选
        children: 儿童旅客数量，默认0，可选
        infants: 婴儿旅客数量，默认0，可选

    Returns:
        包含价格、航班时间、航空公司等详细信息的 JSON 对象数组，每个对象包含:
        - flight_number: 航班号
        - airline: 航空公司名称
        - departure_time: 出发时间 (ISO 8601 格式)
        - arrival_time: 到达时间 (ISO 8601 格式)
        - duration: 航程时长 (分钟)
        - price: 总价格 (货币单位)
        - stops: 经停次数
        - class: 航位等级

    Raises:
        ValueError: 如果输入参数无效
        httpx.HTTPStatusError: 如果 API 请求失败
    """
    try:
        # 输入验证
        if not origin or not origin.strip():
            raise ValueError("出发地不能为空")
        if not destination or not destination.strip():
            raise ValueError("目的地不能为空")
        if not departure_date or not re.match(r'^\d{4}-\d{2}-\d{2}$', departure_date):
            raise ValueError(f"无效的出发日期格式: {departure_date}。必须为 YYYY-MM-DD 格式")
        if trip_type not in ['one-way', 'round-trip', 'multi-city']:
            raise ValueError(f"无效的航班类型: {trip_type}。必须为 'one-way', 'round-trip' 或 'multi-city'")
        if trip_type == 'round-trip' and not return_date:
            raise ValueError("往返航班必须提供返回日期")
        if return_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', return_date):
            raise ValueError(f"无效的返回日期格式: {return_date}。必须为 YYYY-MM-DD 格式")
        if cabin_class and cabin_class not in ['economy', 'business', 'first']:
            raise ValueError(f"无效的舱位等级: {cabin_class}。必须为 'economy', 'business' 或 'first'")
        if adults < 0:
            raise ValueError(f"成人数量不能为负数: {adults}")
        if children < 0:
            raise ValueError(f"儿童数量不能为负数: {children}")
        if infants < 0:
            raise ValueError(f"婴儿数量不能为负数: {infants}")

        # 构建查询参数
        params = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": [
                {"type": "adult", "count": adults} if adults > 0 else None,
                {"type": "child", "count": children} if children > 0 else None,
                {"type": "infant", "count": infants} if infants > 0 else None
            ],
            "cabin_class": cabin_class
        }

        # 移除空值
        params["passengers"] = [p for p in params["passengers"] if p is not None]

        if trip_type == "round-trip" and return_date:
            params["return_date"] = return_date

        # 发送 API 请求
        response = await client.post("/offers", json=params)
        
        # 处理响应
        response.raise_for_status()
        data = response.json()
        
        # 解析结果
        flights = []
        for offer in data.get("offers", []):
            for segment in offer.get("segments", []):
                flight = {
                    "flight_number": segment.get("flight_number"),
                    "airline": segment.get("marketing_airline_iata_code"),
                    "departure_time": segment.get("departing_at"),
                    "arrival_time": segment.get("arriving_at"),
                    "duration": segment.get("duration_minutes"),
                    "price": offer.get("total_amount"),
                    "stops": len(segment.get("intermediate_stops", [])),
                    "class": offer.get("cabin_class")
                }
                flights.append(flight)
        
        return json.dumps(flights, ensure_ascii=False)
    except Exception as e:
        logger.error(f"search_flights 方法发生错误: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def get_offer_details(offer_id: str) -> str:
    """
    获取特定航班报价的详细信息

    Args:
        offer_id: 要查询的报价唯一标识符，必填

    Returns:
        包含完整报价详情的 JSON 对象，包括:
        - offer_id: 报价ID
        - flight_details: 完整航班信息(与 search_flights 返回结构一致)
        - passenger_info: 乘客信息(姓名、年龄、特殊需求等)
        - baggage_allowance: 行李额度
        - cancellation_policy: 退改签政策
        - total_price: 总费用明细(基础票价+税费+服务费)

    Raises:
        ValueError: 如果输入参数无效
        httpx.HTTPStatusError: 如果 API 请求失败
    """
    try:
        # 输入验证
        if not offer_id or not offer_id.strip():
            raise ValueError("报价ID不能为空")

        # 发送 API 请求
        response = await client.get(f"/offers/{offer_id}")
        
        # 处理响应
        response.raise_for_status()
        data = response.json()
        
        # 解析结果
        offer_details = {
            "offer_id": data.get("id"),
            "flight_details": [],
            "passenger_info": [],
            "baggage_allowance": data.get("baggage_allowance"),
            "cancellation_policy": data.get("cancellation_policy"),
            "total_price": data.get("total_amount")
        }
        
        # 解析航班信息
        for segment in data.get("segments", []):
            flight = {
                "flight_number": segment.get("flight_number"),
                "airline": segment.get("marketing_airline_iata_code"),
                "departure_time": segment.get("departing_at"),
                "arrival_time": segment.get("arriving_at"),
                "duration": segment.get("duration_minutes"),
                "price": data.get("total_amount"),
                "stops": len(segment.get("intermediate_stops", [])),
                "class": data.get("cabin_class")
            }
            offer_details["flight_details"].append(flight)
        
        # 解析乘客信息
        for passenger in data.get("passengers", []):
            passenger_info = {
                "name": f"{passenger.get('given_name', '')} {passenger.get('family_name', '')}",
                "age": passenger.get("age"),
                "special_needs": passenger.get("special_needs")
            }
            offer_details["passenger_info"].append(passenger_info)
        
        return json.dumps(offer_details, ensure_ascii=False)
    except Exception as e:
        logger.error(f"get_offer_details 方法发生错误: {str(e)}", exc_info=True)
        raise

@mcp.tool()
async def search_multi_city(segments: List[Dict[str, Any]], cabin_class: Optional[str] = None, adults: int = 1, children: int = 0, infants: int = 0) -> str:
    """
    专门处理多城市航班查询，支持复杂的行程规划

    Args:
        segments: 航程段列表，每个字典包含:
            - origin: 出发地机场代码
            - destination: 目的地机场代码
            - date: 出发日期 (格式: 'YYYY-MM-DD')
        cabin_class: 舱位等级 ('economy', 'business', 'first')，可选
        adults: 成人旅客数量，默认1，可选
        children: 儿童旅客数量，默认0，可选
        infants: 婴儿旅客数量，默认0，可选

    Returns:
        多城市航班组合的详细信息，包含所有航段的连接信息和整体行程安排，结构为:
        - itinerary_id: 行程唯一标识
        - segments: 各航段详细信息数组
        - total_duration: 整体行程时长
        - total_price: 总价格
        - layover_times: 各中转站停留时间

    Raises:
        ValueError: 如果输入参数无效
        httpx.HTTPStatusError: 如果 API 请求失败
    """
    try:
        # 输入验证
        if not segments or len(segments) < 2:
            raise ValueError("多城市航班至少需要两个航段")
        
        for i, segment in enumerate(segments):
            if not segment.get("origin"):
                raise ValueError(f"第 {i+1} 个航段缺少出发地")
            if not segment.get("destination"):
                raise ValueError(f"第 {i+1} 个航段缺少目的地")
            if not segment.get("date") or not re.match(r'^\d{4}-\d{2}-\d{2}$', segment.get("date", "")):
                raise ValueError(f"第 {i+1} 个航段日期格式不正确。必须为 YYYY-MM-DD 格式")
        
        if cabin_class and cabin_class not in ['economy', 'business', 'first']:
            raise ValueError(f"无效的舱位等级: {cabin_class}。必须为 'economy', 'business' 或 'first'")
        
        if adults < 0:
            raise ValueError(f"成人数量不能为负数: {adults}")
        if children < 0:
            raise ValueError(f"儿童数量不能为负数: {children}")
        if infants < 0:
            raise ValueError(f"婴儿数量不能为负数: {infants}")
        
        # 构建查询参数
        params = {
            "segments": [{
                "origin": segment["origin"],
                "destination": segment["destination"],
                "departure_date": segment["date"]
            } for segment in segments],
            "passengers": [
                {"type": "adult", "count": adults} if adults > 0 else None,
                {"type": "child", "count": children} if children > 0 else None,
                {"type": "infant", "count": infants} if infants > 0 else None
            ],
            "cabin_class": cabin_class
        }
        
        # 移除空值
        params["passengers"] = [p for p in params["passengers"] if p is not None]
        
        # 发送 API 请求
        response = await client.post("/offers", json=params)
        
        # 处理响应
        response.raise_for_status()
        data = response.json()
        
        # 解析结果
        itineraries = []
        for offer in data.get("offers", []):
            itinerary = {
                "itinerary_id": offer.get("id"),
                "segments": [],
                "total_duration": 0,
                "total_price": offer.get("total_amount"),
                "layover_times": []
            }
            
            total_duration = 0
            previous_arrival_time = None
            
            for segment in offer.get("segments", []):
                flight = {
                    "flight_number": segment.get("flight_number"),
                    "airline": segment.get("marketing_airline_iata_code"),
                    "departure_time": segment.get("departing_at"),
                    "arrival_time": segment.get("arriving_at"),
                    "duration": segment.get("duration_minutes", 0),
                    "price": offer.get("total_amount"),
                    "stops": len(segment.get("intermediate_stops", [])),
                    "class": offer.get("cabin_class")
                }
                itinerary["segments"].append(flight)
                
                total_duration += segment.get("duration_minutes", 0)
                
                if previous_arrival_time:
                    # 计算中转时间（假设时间格式为 ISO 8601）
                    prev_time = datetime.fromisoformat(previous_arrival_time.replace("Z", "+00:00"))
                    dep_time = datetime.fromisoformat(segment.get("departing_at", "").replace("Z", "+00:00"))
                    layover = (dep_time - prev_time).total_seconds() / 60
                    itinerary["layover_times"].append(max(0, int(layover)))
                
                previous_arrival_time = segment.get("arriving_at")
            
            itinerary["total_duration"] = total_duration
            itineraries.append(itinerary)
        
        return json.dumps(itineraries, ensure_ascii=False)
    except Exception as e:
        logger.error(f"search_multi_city 方法发生错误: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}", exc_info=True)
        sys.exit(1)