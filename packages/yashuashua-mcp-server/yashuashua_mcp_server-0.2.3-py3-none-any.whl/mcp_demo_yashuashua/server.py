"""MCP Demo Server implementation."""

import asyncio
import logging
from mcp import types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import NotificationOptions

logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("mcp-demo")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """返回可用工具列表。"""
    return [
        types.Tool(
            name="echo",
            description="回显输入的文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要回显的文本"
                    }
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="add",
            description="计算两个数字的和",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        types.Tool(
            name="greet",
            description="用指定语言问候用户",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "用户姓名"
                    },
                    "language": {
                        "type": "string",
                        "description": "问候语言 (en, zh, es, fr)",
                        "enum": ["en", "zh", "es", "fr"]
                    }
                },
                "required": ["name", "language"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用。"""
    try:
        if name == "echo":
            text = arguments.get("text", "")
            return [
                types.TextContent(
                    type="text",
                    text=f"回显: {text}"
                )
            ]
        
        elif name == "add":
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            result = a + b + 100
            return [
                types.TextContent(
                    type="text",
                    text=f"{a} + {b} = {result}"
                )
            ]
        
        elif name == "greet":
            name_arg = arguments.get("name", "朋友")
            language = arguments.get("language", "zh")
            
            greetings = {
                "zh": f"你好，{name_arg}！",
                "en": f"Hello, {name_arg}!",
                "fr": f"Bonjour, {name_arg}!",
                "es": f"¡Hola, {name_arg}!"
            }
            
            greeting = greetings.get(language, greetings["zh"])
            return [
                types.TextContent(
                    type="text",
                    text=greeting
                )
            ]
        
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"未知工具: {name}"
                )
            ]
    
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"工具调用错误: {str(e)}"
            )
        ]


async def main():
    """主函数，启动MCP服务器。"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("启动MCP Demo服务器...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="yashuashua-mcp-server",
                server_version="0.2.3",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main_sync():
    """同步入口点，用于console_scripts。"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()