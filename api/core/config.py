"""
Configuration Management - Pydantic Settings
Load environment variables with validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    
    # Database Configuration
    database_url: str = "sqlite:///./nexsupply.db"
    database_host: Optional[str] = None
    database_port: Optional[int] = None
    database_name: Optional[str] = None
    database_user: Optional[str] = None
    database_password: Optional[str] = None
    
    # Redis Configuration (for Phase 2)
    redis_url: Optional[str] = None
    redis_host: Optional[str] = None
    redis_port: int = 6379
    
    # Application Configuration
    app_title: str = "NexSupply AI"
    app_subtitle: str = "AI 네이티브 B2B 소싱 컨설턴트"
    primary_color: str = "#0f2b46"
    background_color: str = "#f4f6f9"
    
    # Default Values
    default_volume: int = 1000
    default_market: str = "USA"
    default_channel: str = "Amazon FBA"
    default_currency: str = "USD"
    
    # Validation
    min_volume: int = 1
    min_cost: float = 0.0
    
    # Environment
    environment: str = "development"  # development, staging, production
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra environment variables
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure singleton pattern.
    
    Returns:
        Settings instance
    """
    return Settings()


# Convenience function for backward compatibility
def get_config() -> Settings:
    """Alias for get_settings()"""
    return get_settings()

