"""
Configuration settings for the project.
"""
import os

# Source URL for Taiwan Invoice Lottery
INVOICE_URL = os.getenv("INVOICE_URL", "https://invoice.etax.nat.gov.tw/index.html")

# User Agent for scraping
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")
