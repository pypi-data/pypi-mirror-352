import os
import sys
import logging
import httpx
from typing import Any

from mcp.server import InitializationOptions
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

if sys.platform == "win32" and os.environ.get('PYTHONIOENCODING') is None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.info("Starting Hunyuan Plugin MCP Server")

def siteList(arguments: dict[str, Any],api_key) -> str:
    aiSearchUrl = "https://arsenalgw.qa.ly.com/gwai/gw/ai_datasets_qa1/yuanbao/site_list_rt"
    
    qryDetail = arguments.get("qryDetail", None)
    if qryDetail is None:
        raise ValueError("qryDetail不能为空")
    
    payload = {
        "qryDetail": qryDetail
    }

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": api_key
    }

    logging.info("start to call tc travel site_list_rt api:", payload)
    timeout = httpx.Timeout(90.0, connect=10.0)
    response = httpx.post(aiSearchUrl, headers=headers, json=payload, timeout=timeout)
    response_json = response.json()
    return(response_json)
    # if response.code == 401:
    #     raise SystemError("token验证失败")
    # if response.status_code != 200:
    #     error_info = response_json.get("error", None)
    #     if error_info is None:
    #         raise SystemError(f"请求服务器失败，错误码{response.status_code}")
    #     else:
    #         err_msg = error_info.get("message", "未知错误")
    #         raise SystemError(f"请求服务器失败，{err_msg}")
        
    # logging.info("openapi response:", response_json)
    # err_code = response_json.get("code", 0)
    # if err_code != 0:
    #     raise SystemError(f"服务器异常，{err_code}")
    # return str(response.content, encoding='utf-8')

def trainRealTime(arguments: dict[str, Any],api_key) -> str:
    aiSearchUrl = "https://arsenalgw.qa.ly.com/gwai/gw/ai_datasets_qa1/yuanbao/flyRealTime"
    
    depCityName = arguments.get("depCityName", None)
    if depCityName is None:
        raise ValueError("qryDetail不能为空")
    arrCityName = arguments.get("arrCityName", None)
    if arrCityName is None:
        raise ValueError("arrCityName不能为空")
    depDate = arguments.get("depDate", None)
    if depDate is None:
        raise ValueError("depDate不能为空")
    

    payload = {
        "qryDetail": depCityName,
        "arrCityName": arrCityName,
        "depDate": depDate,
    }

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": api_key
    }

    logging.info("start to call tc travel trainRealTime api:", payload)
    timeout = httpx.Timeout(90.0, connect=10.0)
    response = httpx.post(aiSearchUrl, headers=headers, json=payload, timeout=timeout)
    response_json = response.json()
    return response_json
    # if response.status_code == 401:
    #     raise SystemError("token验证失败")
    # if response.status_code != 200:
    #     error_info = response_json.get("error", None)
    #     if error_info is None:
    #         raise SystemError(f"请求服务器失败，错误码{response.status_code}")
    #     else:
    #         err_msg = error_info.get("message", "未知错误")
    #         raise SystemError(f"请求服务器失败，{err_msg}")
        
    # logging.info("openapi response:", response_json)
    # err_code = response_json.get("code", 0)
    # if err_code != 0:
    #     raise SystemError(f"服务器异常，{err_code}")
    # return str(response.content, encoding='utf-8')

def hotelList(arguments: dict[str, Any],api_key) -> str:
    aiSearchUrl = "https://arsenalgw.qa.ly.com/gwai/gw/ai_datasets_qa1/yuanbao/main_bot/hotel_list_rt"
    
    city= arguments.get("city", None)
    if city is None:
        raise ValueError("city不能为空")
    brand = arguments.get("brand", None)
    
    payload = {
        "city": city,
    }

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": api_key
    }

    logging.info("start to call tc travel hotelList api:", payload)
    timeout = httpx.Timeout(90.0, connect=10.0)
    response = httpx.post(aiSearchUrl, headers=headers, json=payload, timeout=timeout)
    response_json = response.json()
    return response_json
    # if response.status_code == 401:
    #     raise SystemError("token验证失败")
    # if response.status_code != 200:
    #     error_info = response_json.get("error", None)
    #     if error_info is None:
    #         raise SystemError(f"请求服务器失败，错误码{response.status_code}")
    #     else:
    #         err_msg = error_info.get("message", "未知错误")
    #         raise SystemError(f"请求服务器失败，{err_msg}")
        
    # logging.info("openapi response:", response_json)
    # err_code = response_json.get("code", 0)
    # if err_code != 0:
    #     raise SystemError(f"服务器异常，{err_code}")
    # return str(response.content, encoding='utf-8')

async def main():
    logging.info("Starting Hunyuan Plugin MCP Server.")
    
    server = Server("hunyuan-mcp-tc-travel", "2", "mcp server to invoke hunyuan tc travel")
    
    # Register handlers
    logging.debug("Registering handlers")
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="siteList",
                description="根据条件查询景点列表。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "qryDetail": {
                            "type": "array",
                            "description": "用户的查询详情。查询词不能为空。",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "keyword": {
                                        "type": "string",
                                        "description": "搜索词，目前支持景点名（城市名称和搜索词不能同时为空）"
                                    },
                                    "cityName": {
                                        "type": "string",
                                        "description": "城市名称（城市名称和搜索词不能同时为空）"
                                    }
                                },
                                "required": []
                            }
                        }
                    },
                    "required": ["qryDetail"]
                }
            ),
            types.Tool(
                name="hotelList",
                description="根据条件查询酒店列表。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string", 
                            "description": "城市名称【简称和全称都可以】"
                        },
                         "brand": {
                            "type": "string", 
                            "description": "酒店品牌【只支持品牌不支持酒店名称查询】"
                        }
                    },
                    "required": ["city"],
                },
            ),
            types.Tool(
                name="trainRealTime",
                description="根据条件查询酒店列表。",
                inputSchema={
                   "type": "object",
                    "properties": {
                        "depCityName": {
                            "type": "string",
                            "description": "出发城市名称",
                        },
                        "arrCityName": {
                            "type": "string",
                            "description": "到达城市名称"
                        },
                        "depDate": {
                            "type": "string",
                            "description": "出发日期",
                            "format": "date"
                        },
                        "trainNumber": {
                            "type": "string",
                            "description": "车次"
                        },
                        "trainType": {
                            "type": "string",
                            "description": "列车类型"
                        },
                        "depStation": {
                            "type": "string",
                            "description": "出发站",
                            "examples": ["广州南站"]
                        },
                        "arrStation": {
                            "type": "string",
                            "description": "到达站",
                            "examples": ["北京西站"]
                        },
                        "minPrice": {
                            "type": "number",
                            "description": "最小价格"
                        },
                        "maxPrice": {
                            "type": "number",
                            "description": "最大价格"
                        },
                        "hasTicket": {
                            "type": "boolean",
                            "description": "是否有票"
                        },
                        "earliestDepTime": {
                            "type": "string",
                            "description": "最早出发时间"
                        },
                        "latestDepTime": {
                            "type": "string",
                            "description": "最晚出发时间"
                        },
                        "earliestArrTime": {
                            "type": "string",
                            "description": "最早到达时间"
                        },
                        "latestArrTime": {
                            "type": "string",
                            "description": "最晚到达时间"
                        },
                        "seatType": {
                            "type": "string",
                            "description": "座位类型"
                        },
                        "sortField": {
                            "type": "string",
                            "description": "排序字段",
                            "enum": ["depTime", "arrTime"]
                        },
                        "sortOrder": {
                            "type": "string",
                            "description": "排序规则",
                            "enum": ["asc", "desc"]
                        }
                    },
                    "required": ["depCityName", "arrCityName"]
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "siteList":
                 api_key = os.getenv("SITE_API_KEY", None)
                 if api_key is None:
                     return ValueError("环境变量SITE_API_KEY没有设置")
                 results = siteList(arguments,api_key)
                 return [types.TextContent(type="text", text=str(results))]
            elif name == "hotelList":
                 api_key = os.getenv("HOTEL_API_KEY", None)
                 if api_key is None:
                     return ValueError("环境变量HOTEL_API_KEY没有设置")
                 results = hotelList(arguments,api_key)
                 return [types.TextContent(type="text", text=str(results))]
            elif name == "trainRealTime":
                 api_key = os.getenv("REAL_API_KEY", None)
                 if api_key is None:
                     return ValueError("环境变量REAL_API_KEY没有设置")
                 results = trainRealTime(arguments,api_key)
                 return [types.TextContent(type="text", text=str(results))]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            raise e # [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with stdio_server() as (read_stream, write_stream):
        logging.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hunyuan-mcp-tc-travel", 
                server_version="2",
                server_instructions="mcp server to invoke tc travel",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

class ServerWrapper():
    """A wrapper to compat with mcp[cli]"""
    def run(self):
        import asyncio
        asyncio.run(main())


wrapper = ServerWrapper()