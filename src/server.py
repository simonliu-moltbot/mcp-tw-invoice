"""
Standard MCP Server for Taiwan Invoice Lottery.
Uses official 'mcp' SDK to avoid stdout pollution.
"""
import sys
import os

# Add current directory to sys.path so we can import logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
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

async def main():
    # Run the server using stdin/stdout
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
            raise_exceptions=True,
        )

if __name__ == "__main__":
    asyncio.run(main())
