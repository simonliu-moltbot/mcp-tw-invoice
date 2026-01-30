"""
Core logic for fetching and checking Taiwan Uniform Invoice numbers.
"""
import httpx
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
from .config import INVOICE_URL, USER_AGENT

async def fetch_winning_numbers() -> Dict[str, str]:
    """
    Fetches the latest winning numbers from the official website.
    Returns a dictionary with prize names and numbers.
    """
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(INVOICE_URL, headers=headers, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return {"error": f"Failed to fetch data: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    
    # This selector might need adjustment based on the actual site structure.
    # The official site usually puts the latest numbers in the first area.
    # We look for the 'area1' id or similar structures. 
    # For robustness, we'll try to find the container with class "etw-on".
    
    # Note: The site structure often changes. This is a best-effort scraper.
    # A more stable approach would use the RSS feed: https://invoice.etax.nat.gov.tw/invoice.xml
    # But for this exercise we demonstrate scraping logic.
    
    # Let's try parsing the invoice.xml content if possible as it is structured?
    # Actually, let's stick to the HTML parsing as requested by prompt "Scraper".
    
    # Typical structure:
    # <div class="etw-tbiggest">12345678</div> (Special Prize)
    # <div class="etw-tbig">12345678</div> (Grand Prize)
    
    results = {}
    
    # Extract Period (Title)
    # Usually in <h2> or .etw-tit
    period_tag = soup.select_one(".etw-tit-text")
    if period_tag:
        results["period"] = period_tag.get_text(strip=True)
    else:
        results["period"] = "Unknown Period"

    # Extract Special Prize (特別獎)
    special = soup.select_one(".etw-tbiggest .etw-web .number")
    if special:
        results["special_prize"] = special.get_text(strip=True)

    # Extract Grand Prize (特獎)
    grand = soup.select_one(".etw-tbig .etw-web .number")
    if grand:
        results["grand_prize"] = grand.get_text(strip=True)

    # Extract First Prize (頭獎) - can be multiple
    # Usually in .etw-tfirst .etw-web .number
    # The text might be "123 456 789"
    first = soup.select_one(".etw-tfirst .etw-web .number")
    if first:
        raw_first = first.get_text(strip=True)
        # Split by space or non-digit
        results["first_prize"] = [n for n in re.split(r'\s+', raw_first) if n]

    return results

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
    
    # Check Special Prize (8 digits)
    sp = winning_numbers.get("special_prize")
    if sp and number == sp:
        msg.append(f"🎉 特別獎 (1,000萬): {sp}")
    elif sp and sp.endswith(number) and len(number) >= 3:
        # Partial match just for hint? Usually full match needed for big prizes.
        pass

    # Check Grand Prize (8 digits)
    gp = winning_numbers.get("grand_prize")
    if gp and number == gp:
        msg.append(f"🎉 特獎 (200萬): {gp}")

    # Check First Prize (8 digits) -> and sub-prizes
    fps = winning_numbers.get("first_prize", [])
    if isinstance(fps, list):
        for fp in fps:
            if number == fp:
                msg.append(f"🎉 頭獎 (20萬): {fp}")
            elif len(number) >= 3 and fp.endswith(number):
                # 3 to 7 digits match
                matched_len = 0
                for i in range(3, 9):
                    if number.endswith(fp[-i:]):
                        matched_len = i
                
                if matched_len >= 3:
                    prize_map = {
                        3: "六獎 (200元)",
                        4: "五獎 (1,000元)",
                        5: "四獎 (4,000元)",
                        6: "三獎 (1萬元)",
                        7: "二獎 (4萬元)"
                    }
                    if matched_len == len(number): # Exact match of suffix
                         msg.append(f"🎉 {prize_map.get(matched_len, '中獎')}: ...{number}")

    if not msg:
        return "可惜，未中獎 (Not matched)."
    
    return " | ".join(msg)
