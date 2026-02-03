"""
Taiwan Invoice Lottery MCP Server.
Supports both STDIO and HTTP (SSE) transport modes.
"""
import sys
import os
import asyncio
import argparse

# Add current directory to sys.path so we can import logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import mcp.types as types
from logic import fetch_winning_numbers, check_number

# Initialize Server
server = Server("mcp-tw-invoice")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_current_winning_numbers",
            description="Get the latest Taiwan Uniform Invoice winning numbers.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="check_my_invoice",
            description="Check if your invoice number is a winner.",
            inputSchema={
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "The invoice number (last 3 digits or full 8 digits).",
                    },
                },
                "required": ["number"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "get_current_winning_numbers":
        data = await fetch_winning_numbers()
        if "error" in data:
            return [types.TextContent(type="text", text=data["error"])]
        
        output = [f"📅 期別: {data.get('period', 'Unknown')}"]
        if "special_prize" in data:
            output.append(f"特別獎 (1000萬): {data['special_prize']}")
        if "grand_prize" in data:
            output.append(f"特獎 (200萬): {data['grand_prize']}")
        if "first_prize" in data:
            fps = "、".join(data["first_prize"])
            output.append(f"頭獎 (20萬): {fps}")
            
        return [types.TextContent(type="text", text="\n".join(output))]

    elif name == "check_my_invoice":
        if not arguments or "number" not in arguments:
            return [types.TextContent(type="text", text="Missing 'number' argument.")]
            
        number = str(arguments["number"])
        data = await fetch_winning_numbers()
        
        if "error" in data:
            return [types.TextContent(type="text", text=f"Error fetching data: {data['error']}")]
            
        result = check_number(number, data)
        return [types.TextContent(type="text", text=result)]

    raise ValueError(f"Unknown tool: {name}")

async def run_stdio():
    """Run the server using stdin/stdout (for Claude Desktop)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
            raise_exceptions=True,
        )

async def run_http(port: int):
    """Run the server using HTTP SSE (for Docker/Remote)."""
    from mcp.server.models import InitializationOptions
    import mcp.types as types

    # SseServerTransport needs a path where it will receive POST messages.
    # We'll use /mcp/messages for this.
    sse = SseServerTransport("/mcp/messages")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request.send) as (read, write):
            await server.run(
                read, 
                write, 
                InitializationOptions(
                    server_name="mcp-tw-invoice",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                )
            )

    app = Starlette(
        debug=True,
        routes=[
            Route("/mcp", endpoint=handle_sse, methods=["GET"]),
            # This handles the POST requests from the client to the address provided in the SSE stream
            Mount("/mcp/messages", app=sse.handle_post_message),
        ],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["*"],
                expose_headers=["*"],
            )
        ]
    )
    
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server_http = uvicorn.Server(config)
    await server_http.serve()

async def main():
    parser = argparse.ArgumentParser(description="Taiwan Invoice MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (only for http mode)")
    args = parser.parse_args()

    if args.mode == "stdio":
        await run_stdio()
    else:
        print(f"Starting HTTP server on port {args.port}...", file=sys.stderr)
        await run_http(args.port)

if __name__ == "__main__":
    asyncio.run(main())
