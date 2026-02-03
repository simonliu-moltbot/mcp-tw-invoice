"""
Taiwan Invoice Lottery MCP Server using FastMCP.
Supports both STDIO and Streamable HTTP transport modes.
"""
import sys
import os
import argparse
import asyncio

# Add current directory to sys.path so we can import logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
from logic import fetch_winning_numbers, check_number

# Initialize FastMCP
mcp = FastMCP("mcp-tw-invoice")

@mcp.tool()
async def get_current_winning_numbers() -> str:
    """Get the latest Taiwan Uniform Invoice winning numbers."""
    data = await fetch_winning_numbers()
    if "error" in data:
        return data["error"]
    
    output = [f"📅 期別: {data.get('period', 'Unknown')}"]
    if "special_prize" in data:
        output.append(f"特別獎 (1000萬): {data['special_prize']}")
    if "grand_prize" in data:
        output.append(f"特獎 (200萬): {data['grand_prize']}")
    if "first_prize" in data:
        fps = "、".join(data["first_prize"])
        output.append(f"頭獎 (20萬): {fps}")
        
    return "\n".join(output)

@mcp.tool()
async def check_my_invoice(number: str) -> str:
    """
    Check if your invoice number is a winner.
    Args:
        number: The invoice number (last 3 digits or full 8 digits).
    """
    data = await fetch_winning_numbers()
    
    if "error" in data:
        return f"Error fetching data: {data['error']}"
        
    result = check_number(str(number), data)
    return result

def main():
    parser = argparse.ArgumentParser(description="Taiwan Invoice MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (only for http mode)")
    args = parser.parse_args()

    if args.mode == "stdio":
        # Default run is stdio
        mcp.run()
    else:
        # Use streamable-http for remote/Docker access
        print(f"Starting FastMCP in streamable-http mode on port {args.port}...", file=sys.stderr)
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=args.port,
            path="/mcp"
        )

if __name__ == "__main__":
    main()
