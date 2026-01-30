"""
Core logic for fetching and checking Taiwan Uniform Invoice numbers.
"""
import httpx
import xml.etree.ElementTree as ET
import re
from typing import Dict, List
from config import USER_AGENT

# Official RSS Feed
INVOICE_XML_URL = "https://invoice.etax.nat.gov.tw/invoice.xml"

async def fetch_winning_numbers() -> Dict[str, str]:
    """
    Fetches the latest winning numbers from the official XML RSS feed.
    """
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(INVOICE_XML_URL, headers=headers, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return {"error": f"Failed to fetch data: {str(e)}"}

    try:
        # Parse XML
        root = ET.fromstring(response.text)
        # Get the first item (latest period)
        item = root.find(".//item")
        if item is None:
            return {"error": "No data found in XML feed"}
        
        title = item.find("title").text # e.g. 114年 11~12月
        description = item.find("description").text # Contains HTML-like string with numbers
        
        # Parse numbers from description
        # Format: <p>特別獎：97023797</p><p>特獎：00507588</p><p>頭獎：92377231、05232592、78125249</p>
        
        results = {
            "period": title,
            "first_prize": []
        }
        
        # Regex to extract numbers
        special_match = re.search(r"特別獎：(\d+)", description)
        if special_match:
            results["special_prize"] = special_match.group(1)
            
        grand_match = re.search(r"特獎：(\d+)", description)
        if grand_match:
            results["grand_prize"] = grand_match.group(1)
            
        first_match = re.search(r"頭獎：([0-9、]+)", description)
        if first_match:
            # Split by '、' which is the separator in the XML
            nums = first_match.group(1).split("、")
            results["first_prize"] = [n.strip() for n in nums if n.strip()]
            
        return results

    except Exception as e:
        return {"error": f"Failed to parse XML: {str(e)}"}

def check_number(number: str, winning_numbers: Dict) -> str:
    """
    Checks if a given invoice number matches any prize.
    number: Last 3 digits or full 8 digits.
    """
    if not number or not number.isdigit():
        return "Invalid input: Please enter 3 to 8 digits."
        
    if "error" in winning_numbers:
        return winning_numbers["error"]

    msg = []
    
    # Helper to check match length from end
    def get_match_len(target, user_num):
        match_len = 0
        for i in range(1, min(len(target), len(user_num)) + 1):
            if user_num[-i:] == target[-i:]:
                match_len = i
            else:
                break
        return match_len
    
    # Check Special Prize (1000萬) - Needs Full Match
    sp = winning_numbers.get("special_prize")
    if sp:
        if number == sp:
            msg.append(f"🎉 特別獎 (1,000萬): {sp}")
        elif len(number) >= 3 and sp.endswith(number):
             msg.append(f"⚠️ 特別獎潛在號碼 (需8碼全中): ...{sp[-3:]} (您輸入: {number})")

    # Check Grand Prize (200萬) - Needs Full Match
    gp = winning_numbers.get("grand_prize")
    if gp:
        if number == gp:
            msg.append(f"🎉 特獎 (200萬): {gp}")
        elif len(number) >= 3 and gp.endswith(number):
             msg.append(f"⚠️ 特獎潛在號碼 (需8碼全中): ...{gp[-3:]} (您輸入: {number})")

    # Check First Prize (20萬) & Sub-prizes (六獎 to 二獎)
    fps = winning_numbers.get("first_prize", [])
    if isinstance(fps, list):
        for fp in fps:
            match_len = get_match_len(fp, number)
            
            # Check for full match (Head Prize)
            if number == fp:
                msg.append(f"🎉 頭獎 (20萬): {fp}")
                continue
                
            # Check for sub-prizes (need at least 3 digits matching from end)
            if match_len >= 3:
                # User's number matches at least 3 digits from the end
                prize_map = {
                    3: "六獎 (200元)",
                    4: "五獎 (1,000元)",
                    5: "四獎 (4,000元)",
                    6: "三獎 (1萬元)",
                    7: "二獎 (4萬元)",
                    8: "頭獎 (20萬)" 
                }
                # If it's a full match of 8 digits, it's covered by the "head prize" check above usually,
                # but if we removed that explicit check or want to be safe:
                if match_len == 8:
                    msg.append(f"🎉 頭獎 (20萬): {fp}")
                else:
                    prize_name = prize_map.get(match_len, "中獎")
                    msg.append(f"🎉 {prize_name}: ...{fp[-match_len:]}")

    if not msg:
        return "可惜，未中獎 (Not matched)."
    
    return "\n".join(msg)
