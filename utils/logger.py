"""
JSON Structured Logging - Main Logger Module
Alias for backward compatibility and cleaner imports.
"""

from .logging_utils import get_logger, log_error, JSONFormatter

__all__ = ["get_logger", "log_error", "JSONFormatter"]

