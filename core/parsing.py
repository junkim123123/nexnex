"""
Strict Input Normalization - Single Source of Truth
Handles parsing logic to fix critical bugs (Korea mapping, Volume parsing, Retail mapping)
"""

import re

COUNTRY_MAP = {
    "korea": "South Korea", "south korea": "South Korea", "한국": "South Korea",
    "usa": "USA", "united states": "USA", "america": "USA", "미국": "USA",
    "china": "China", "중국": "China"
}

CHANNEL_MAP = {
    "retail": "Offline Retail", "mart": "Offline Retail", "store": "Offline Retail",
    "amazon": "Amazon FBA", "fba": "Amazon FBA",
    "shopify": "Shopify DTC", "d2c": "Shopify DTC"
}

def clean_text(text: str) -> str:
    return text.lower().strip()

def parse_volume(text: str, default: int = 1000) -> int:
    text_clean = text.replace(",", "")
    # Handle '만' (Korean 10k unit)
    man_match = re.search(r'(\d+(?:\.\d+)?)\s*만', text_clean)
    if man_match: return int(float(man_match.group(1)) * 10000)
    # Handle 'k'
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*k', text_clean, re.IGNORECASE)
    if k_match: return int(float(k_match.group(1)) * 1000)
    # Handle raw numbers (Filter out years like 2024, 2025)
    numbers = [int(n) for n in re.findall(r'\d+', text_clean)]
    candidates = [n for n in numbers if n > 100 and n not in [2024, 2025]]
    return max(candidates) if candidates else default

def parse_market(text: str, default: str = "USA") -> str:
    text_lower = clean_text(text)
    for key, value in COUNTRY_MAP.items():
        if key in text_lower: return value
    return default

def parse_channel(text: str, default: str = "Amazon FBA") -> str:
    text_lower = clean_text(text)
    for key, value in CHANNEL_MAP.items():
        if key in text_lower: return value
    return default

