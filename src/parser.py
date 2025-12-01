"""
Centralized Parsing Logic - Rule-Based Parser
Fixes critical LLM parsing bugs with hard-coded Python rules.
"""

import re
from enum import Enum
from typing import Optional, Dict, Any

class Channel(Enum):
    """Sales channel enumeration"""
    AMAZON_FBA = "Amazon FBA"
    OFFLINE_RETAIL = "Offline Retail"
    SHOPIFY_DTC = "Shopify DTC"
    WHOLESALE = "Wholesale B2B"
    UNKNOWN = "Unknown"


# Country mapping - Strict rules to prevent substring matching bugs
COUNTRY_MAP = {
    # Korea variations (must come before "korea" to catch all)
    "south korea": "South Korea",
    "southkorea": "South Korea",
    "korea": "South Korea",
    "한국": "South Korea",
    "대한민국": "South Korea",
    
    # USA variations
    "united states": "USA",
    "united states of america": "USA",
    "usa": "USA",
    "us": "USA",
    "america": "USA",
    "미국": "USA",
    
    # Other common countries
    "japan": "Japan",
    "일본": "Japan",
    "china": "China",
    "중국": "China",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "영국": "United Kingdom",
    "germany": "Germany",
    "독일": "Germany",
    "france": "France",
    "프랑스": "France",
    "canada": "Canada",
    "캐나다": "Canada",
    "australia": "Australia",
    "호주": "Australia",
    "singapore": "Singapore",
    "싱가포르": "Singapore",
}


# Channel mapping - Strict rules
CHANNEL_MAP = {
    # Offline Retail (check first to prevent "retail" -> "amazon" bug)
    "retail": Channel.OFFLINE_RETAIL,
    "mart": Channel.OFFLINE_RETAIL,
    "store": Channel.OFFLINE_RETAIL,
    "매장": Channel.OFFLINE_RETAIL,
    "오프라인": Channel.OFFLINE_RETAIL,
    "월마트": Channel.OFFLINE_RETAIL,
    "walmart": Channel.OFFLINE_RETAIL,
    "target": Channel.OFFLINE_RETAIL,
    "costco": Channel.OFFLINE_RETAIL,
    
    # Amazon FBA
    "amazon": Channel.AMAZON_FBA,
    "fba": Channel.AMAZON_FBA,
    "아마존": Channel.AMAZON_FBA,
    
    # Shopify/DTC
    "shopify": Channel.SHOPIFY_DTC,
    "website": Channel.SHOPIFY_DTC,
    "d2c": Channel.SHOPIFY_DTC,
    "direct": Channel.SHOPIFY_DTC,
    "온라인": Channel.SHOPIFY_DTC,
    "웹사이트": Channel.SHOPIFY_DTC,
    
    # Wholesale
    "wholesale": Channel.WHOLESALE,
    "b2b": Channel.WHOLESALE,
    "도매": Channel.WHOLESALE,
    "도매상": Channel.WHOLESALE,
    "업체": Channel.WHOLESALE,
}


def clean_text(text: str) -> str:
    """
    Normalize text for parsing.
    
    Args:
        text: Raw input text
    
    Returns:
        Normalized text (lowercase, stripped)
    """
    if not text:
        return ""
    return text.lower().strip()


def parse_volume(text: str, llm_suggestion: Optional[int] = None) -> int:
    """
    Parse volume from text using regex. Prioritize explicit "units" pattern over other numbers.
    
    Logic:
    1. FIRST: Look for explicit "X units" or "X unit" pattern (highest priority)
    2. SECOND: Look for "Xk" or "X만" patterns
    3. THIRD: Look for standalone large numbers (> 100, not years)
    4. Fallback to llm_suggestion or default 1000
    
    Args:
        text: Input text
        llm_suggestion: Optional suggestion from LLM
    
    Returns:
        Parsed volume (int)
    """
    if not text:
        return llm_suggestion or 1000
    
    text_clean = clean_text(text)
    
    # PRIORITY 1: Explicit "units" pattern (e.g., "5,000 units", "5000 units")
    # This is the most reliable indicator of volume
    units_pattern = r'(\d{1,3}(?:,\d{3})*|\d+)\s*units?\b'
    units_match = re.search(units_pattern, text_clean, re.IGNORECASE)
    if units_match:
        volume_str = units_match.group(1).replace(',', '')
        try:
            volume = int(volume_str)
            if volume > 0:  # Valid volume
                return volume
        except (ValueError, AttributeError):
            pass
    
    # PRIORITY 2: "Xk" or "X만" patterns (e.g., "50k", "5만")
    k_pattern = r'(\d+)k\b'
    k_match = re.search(k_pattern, text_clean, re.IGNORECASE)
    if k_match:
        try:
            return int(k_match.group(1)) * 1000
        except (ValueError, AttributeError):
            pass
    
    man_pattern = r'(\d+)만\b'
    man_match = re.search(man_pattern, text_clean)
    if man_match:
        try:
            return int(man_match.group(1)) * 10000
        except (ValueError, AttributeError):
            pass
    
    # PRIORITY 3: Standalone large numbers (likely quantities, not packaging details)
    # Extract all numbers, but filter out:
    # - Years (2020-2099)
    # - Small numbers that might be packaging (e.g., "20 bags/carton")
    # - Numbers that appear in packaging context (e.g., "20 bags", "250 cartons")
    all_numbers = re.findall(r'\b(\d{1,3}(?:,\d{3})*|\d+)\b', text_clean)
    quantity_candidates = []
    year_range = range(2020, 2100)
    
    for num_str in all_numbers:
        try:
            num_val = int(num_str.replace(',', ''))
            # Accept numbers between 100 and 1,000,000 (reasonable quantity range)
            # Exclude years and very small numbers (likely packaging)
            if 100 <= num_val <= 1000000 and num_val not in year_range:
                # Check if this number appears in packaging context (e.g., "20 bags", "250 cartons")
                # If so, skip it (it's likely not the total volume)
                num_context = text_clean[max(0, text_clean.find(num_str) - 20):text_clean.find(num_str) + len(num_str) + 20]
                packaging_keywords = ['bag', 'carton', 'box', 'pack', 'piece per', 'per carton', 'per bag']
                is_packaging = any(keyword in num_context.lower() for keyword in packaging_keywords)
                if not is_packaging:
                    quantity_candidates.append(num_val)
        except (ValueError, AttributeError):
            continue
    
    if quantity_candidates:
        # Return the largest reasonable number (most likely to be the volume)
        return max(quantity_candidates)
    
    # Fallback to LLM suggestion or default
    return llm_suggestion or 1000


def parse_country(text: str) -> str:
    """
    Parse country from text using strict mapping.
    If multiple countries mentioned, return the last one (user's intent).
    
    Args:
        text: Input text
    
    Returns:
        Country name (default: "USA")
    """
    if not text:
        return "USA"
    
    text_clean = clean_text(text)
    original_text = text  # Keep original for Korean character matching
    
    found_countries = []  # List of (position, country) tuples
    
    # First pass: Check Korean keywords (don't use lowercase, Korean chars are case-sensitive)
    korean_keywords = {
        "한국": "South Korea",
        "대한민국": "South Korea",
        "미국": "USA",
        "일본": "Japan",
        "중국": "China",
        "영국": "United Kingdom",
        "독일": "Germany",
        "프랑스": "France",
        "캐나다": "Canada",
        "호주": "Australia",
        "싱가포르": "Singapore",
    }
    
    # Collect all Korean keyword matches with positions
    for keyword, country in korean_keywords.items():
        # Find all occurrences (not just first)
        start = 0
        while True:
            index = original_text.find(keyword, start)
            if index == -1:
                break
            found_countries.append((index, country))
            start = index + 1
    
    # Second pass: Check English keywords in cleaned (lowercase) text
    # Sort by length descending to match longer strings first
    sorted_countries = sorted(COUNTRY_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for keyword, country in sorted_countries:
        # Skip Korean keywords (already checked)
        if any(ord(c) > 127 for c in keyword):
            continue
            
        # Check for keyword in text (case-insensitive)
        if keyword in text_clean:
            # Find all occurrences
            start = 0
            while True:
                index = text_clean.find(keyword, start)
                if index == -1:
                    break
                
                # Check word boundaries (including Korean characters)
                before = text_clean[index-1] if index > 0 else ' '
                after = text_clean[index+len(keyword)] if index+len(keyword) < len(text_clean) else ' '
                
                # Word boundary: space, punctuation, or start/end of string
                # Also check if before/after is Korean (not alphanumeric for Korean)
                is_word_boundary = (
                    before.isspace() or 
                    not (before.isalnum() and ord(before) < 128) or  # Not English alphanumeric
                    index == 0
                ) and (
                    after.isspace() or 
                    not (after.isalnum() and ord(after) < 128) or  # Not English alphanumeric
                    index + len(keyword) >= len(text_clean)
                )
                
                if is_word_boundary:
                    # Find position in original text (approximate)
                    orig_index = original_text.lower().find(keyword, start)
                    if orig_index != -1:
                        found_countries.append((orig_index, country))
                
                start = index + 1
    
    # If multiple countries found, return the last one (user's intent)
    # Example: "미국 말고 Korea에" -> Korea is the intent
    if found_countries:
        # Sort by position and return the last one
        found_countries.sort(key=lambda x: x[0])
        return found_countries[-1][1]
    
    # Default to USA if no match
    return "USA"


def parse_channel(text: str) -> Channel:
    """
    Parse sales channel from text using strict mapping.
    
    Args:
        text: Input text
    
    Returns:
        Channel enum
    """
    if not text:
        return Channel.UNKNOWN
    
    text_clean = clean_text(text)
    original_text = text  # Keep original for Korean character matching
    
    # Priority: Check Korean keywords first
    korean_channels = {
        "매장": Channel.OFFLINE_RETAIL,
        "오프라인": Channel.OFFLINE_RETAIL,
        "월마트": Channel.OFFLINE_RETAIL,
        "아마존": Channel.AMAZON_FBA,
        "온라인": Channel.SHOPIFY_DTC,
        "웹사이트": Channel.SHOPIFY_DTC,
        "도매": Channel.WHOLESALE,
        "도매상": Channel.WHOLESALE,
        "업체": Channel.WHOLESALE,
    }
    
    for keyword, channel in korean_channels.items():
        if keyword in original_text:
            return channel
    
    # Second pass: Check English keywords in cleaned (lowercase) text
    sorted_channels = sorted(CHANNEL_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for keyword, channel in sorted_channels:
        # Skip Korean keywords (already checked)
        if any(ord(c) > 127 for c in keyword):
            continue
        
        # Use word boundary matching
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_clean):
            return channel
        
        # Also check for exact match
        if keyword in text_clean:
            index = text_clean.find(keyword)
            before = text_clean[index-1] if index > 0 else ' '
            after = text_clean[index+len(keyword)] if index+len(keyword) < len(text_clean) else ' '
            
            if before.isspace() or not before.isalnum():
                if after.isspace() or not after.isalnum():
                    return channel
    
    return Channel.UNKNOWN


def normalize_input(user_text: str, llm_parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master function: Normalize LLM output with Python rules.
    
    Takes raw text and LLM JSON, then overwrites:
    - volume (from parse_volume)
    - market/country (from parse_country)
    - channel (from parse_channel)
    
    Args:
        user_text: Original user input text
        llm_parsed_json: JSON output from LLM parser
    
    Returns:
        Normalized dictionary with Python rule-based values
    """
    result = llm_parsed_json.copy()
    
    # Parse volume (trust explicit numbers in text over LLM)
    llm_volume = None
    if 'detected_volume' in result:
        try:
            llm_volume = int(result['detected_volume'])
        except (ValueError, TypeError):
            pass
    
    parsed_volume = parse_volume(user_text, llm_volume)
    result['detected_volume'] = parsed_volume
    
    # Parse country/market
    parsed_country = parse_country(user_text)
    result['target_market'] = parsed_country
    
    # Also update in nested structures if they exist
    if 'ai_context' in result and 'assumptions' in result['ai_context']:
        result['ai_context']['assumptions']['market'] = parsed_country
        result['ai_context']['assumptions']['volume'] = parsed_volume
    
    # Parse channel
    parsed_channel = parse_channel(user_text)
    result['sales_channel'] = parsed_channel.value
    
    # Also update in nested structures if they exist
    if 'channel_strategy' in result:
        # Update channel info
        pass  # Channel strategy is separate
    
    return result

