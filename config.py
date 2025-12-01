"""
Configuration Module - Constants and Environment Variables
Single source of truth for all configuration values.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Database Configuration
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "nexsupply.db")

# UI Configuration
APP_TITLE: str = "NexSupply AI"
APP_SUBTITLE: str = "AI 네이티브 B2B 소싱 컨설턴트"
PRIMARY_COLOR: str = "#0f2b46"
BACKGROUND_COLOR: str = "#f4f6f9"

# Default Values
DEFAULT_VOLUME: int = 1000
DEFAULT_MARKET: str = "USA"
DEFAULT_CHANNEL: str = "Amazon FBA"
DEFAULT_CURRENCY: str = "USD"

# Validation
MIN_VOLUME: int = 1
MIN_COST: float = 0.0

