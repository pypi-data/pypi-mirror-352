import os
import sys
import logging
import httpx
from typing import Any

from mcp.server import InitializationOptions
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

# reconfigure UnicodeEncodeError prone default (i.e. windows-1252) to utf-8
if sys.platform == "win32" and os.environ.get('PYTHONIOENCODING') is None:
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.info("Starting YuanQi Plugin MCP Server")

def aiSearch(arguments: dict[str, Any],api_key) -> str:
    aiSearchUrl = "http://120.241.140.192/openapi/betav1/tools/ai_search"
    
    query_list = arguments.get("query_list", None)
    if query_list is None:
        raise ValueError("query_list不能为空")
    
    payload = {
        "query_list": query_list
    }
    # api_key = os.getenv("API_KEY", None)
    # if api_key is None:
    #     raise ValueError("环境变量API_KEY没有设置")
    headers = {
        "X-Source": "mcp-server",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }

    logging.info("start to call yuanqi plugin api:", payload)
    timeout = httpx.Timeout(90.0, connect=10.0)
    response = httpx.post(aiSearchUrl, headers=headers, json=payload, timeout=timeout)
    return(response)

    # response_json = response.json()
    # if response.status_code == 401:
    #     raise SystemError("token验证失败")
    # if response.status_code != 200:
    #     error_info = response_json.get("error", None)
    #     if error_info is None:
    #         raise SystemError(f"请求服务器失败，错误码{response.status_code}")
    #     else:
    #         err_msg = error_info.get("message", "未知错误")
    #         raise SystemError(f"请求服务器失败，{err_msg}")
        
    # logging.info("yuanqi openapi response:", response_json)
    # err_code = response_json.get("code", 0)
    # if err_code != 0:
    #     raise SystemError(f"AI搜索异常，请稍后重试{err_code}")
    # return str(response.content, encoding='utf-8')
    
    
async def main():
    logging.info("Starting YuanQi Plugin MCP Server.")
    
    server = Server("hunyuan-mcp-aiSearch", "0.1.6", "mcp server to invoke hunyuan search")
    
    # Register handlers
    logging.debug("Registering handlers")
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="bingSearch",
                description="必应搜索引擎。当你需要搜索你不知道的信息，比如天气、汇率、时事等，这个工具非常有用。但是绝对不要在用户想要翻译的时候使用它。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query_list": {
                            "type": "array", 
                            "description": "用户的搜索查询词列表。查询词不能为空。",
                            "items": {
                                "type": "string",
                                "description": "用户的搜索查询词"
                            }
                    
                        }
                    },
                    "required": ["query_list"],
                },
            ),
            types.Tool(
                name="aiSearchQuote",
                description="搜索引擎。当你需要搜索你不知道的信息，比如天气、汇率、时事等，这个工具非常有用。但是绝对不要在用户想要翻译的时候使用它。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query_list": {
                            "type": "array", 
                            "description": "用户的搜索查询词列表。查询词不能为空。",
                            "items": {
                                "type": "string",
                                "description": "用户的搜索查询词"
                            }
                    
                        }
                    },
                    "required": ["query_list"],
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "bingSearch":
                 api_key = os.getenv("BING_API_KEY", None)
                 if api_key is None:
                     return ValueError("环境变量BING_API_KEY没有设置")
                 results = aiSearch(arguments,api_key)
                 return [types.TextContent(type="text", text=str(results))]
            elif name == "aiSearchQuote":
                 api_key = os.getenv("QUOTE_API_KEY", None)
                 if api_key is None:
                     return ValueError("环境变量QUOTE_API_KEY没有设置")
                 results = aiSearch(arguments,api_key)
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
                server_name="hunyuan-mcp-search", 
                server_version="0.1.6",
                server_instructions="mcp server to invoke hunyuan search",
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