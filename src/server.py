"""
FastMCP Server for Taiwan Invoice Lottery.
"""
from fastmcp import FastMCP, Context
from .logic import fetch_winning_numbers, check_number

# Initialize FastMCP Server
mcp = FastMCP("Taiwan Invoice Helper")

@mcp.tool
async def get_current_winning_numbers() -> str:
    """
    Get the latest Taiwan Uniform Invoice winning numbers.
    Retruns a formatted string of the winning numbers.
    """
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

@mcp.tool
async def check_my_invoice(number: str, ctx: Context) -> str:
    """
    Check if your invoice number is a winner.
    Args:
        number: The invoice number (last 3 digits usually sufficient for small prizes, full 8 for big ones).
    """
    await ctx.info(f"Checking invoice number: {number}")
    data = await fetch_winning_numbers()
    
    if "error" in data:
        return f"Error fetching data: {data['error']}"
        
    result = check_number(number, data)
    return result

@mcp.resource("invoice://current")
async def resource_current_numbers() -> str:
    """
    Returns the current winning numbers as a raw JSON string.
    """
    import json
    data = await fetch_winning_numbers()
    return json.dumps(data, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()
