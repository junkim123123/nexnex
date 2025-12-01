"""
Formatting utilities for display
Currency formatting, number formatting, etc.
"""

from typing import Union


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency for display.
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, KRW, etc.)
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "KRW":
        return f"₩{amount:,.0f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_volume(volume: int) -> str:
    """
    Format volume for display.
    
    Args:
        volume: Volume number
        
    Returns:
        Formatted volume string with commas
    """
    return f"{volume:,}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"

