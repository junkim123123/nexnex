"""
JSON Structured Logging Utilities
Outputs logs in JSON format with timestamp, log level, function name, and line number.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import traceback


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str = "nexsupply", level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger configured for JSON structured logging.
    
    Includes timestamp, log level, function name, and line number in every log entry.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance with JSON formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Use JSON formatter
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """
    Log error with context in JSON format.
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Optional context string
    """
    extra_fields = {}
    if context:
        extra_fields["context"] = context
    
    logger.error(
        f"{error.__class__.__name__}: {str(error)}",
        exc_info=True,
        extra={"extra_fields": extra_fields}
    )

