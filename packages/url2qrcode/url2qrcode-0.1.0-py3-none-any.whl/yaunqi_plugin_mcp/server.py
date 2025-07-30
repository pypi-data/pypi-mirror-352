import os
import sys
import logging
import base64
from typing import Any
from qrcode import QRCode

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

def url2qrcode(arguments: dict[str, Any]) -> str:
       
    data = arguments.get("url", "")
    if data == "":
        raise ValueError("url不能为空")
    qr = QRCode("qrcode", data, image_format="PNG", options={"module_color": "black", "background": "white"})
    return base64.b64encode(qr).decode('utf-8')
    
    
async def main():
    logging.info("Starting YuanQi Plugin MCP Server.")
    
    server = Server("url2qrcode", "0.1.0", "mcp server to change url to qrcode")
    
    # Register handlers
    logging.debug("Registering handlers")
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="url2qrcode",
                description="将url转换成二维码图片",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string", 
                            "description": "需要转换成二维码图片的url地址"
                        }
                    },
                    "required": ["url"],
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "url2qrcode":
                result = url2qrcode(arguments)
                return [types.ImageContent(type="image", data=str(result), mimeType='image/png')]
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
                server_name="url2qrcode", 
                server_version="0.1.0",
                server_instructions="mcp server to change url to qrcode",
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