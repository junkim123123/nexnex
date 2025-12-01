"""
Secure Logging - PII Masking
Automatically detects and masks sensitive data in logs
"""

import re
import logging
import json
from typing import Any, Dict
from datetime import datetime


class SecureFormatter(logging.Formatter):
    """
    Custom formatter that masks PII (Personally Identifiable Information)
    in log messages before output.
    """
    
    # Patterns for detecting sensitive data
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    API_KEY_PATTERN = re.compile(
        r'\b(?:sk|pk|AIza|Bearer|token)[-_]?[A-Za-z0-9]{20,}\b',
        re.IGNORECASE
    )
    PHONE_PATTERN = re.compile(
        r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    )
    CREDIT_CARD_PATTERN = re.compile(
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    )
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with PII masking"""
        # Get the original message
        message = record.getMessage()
        
        # Mask sensitive data
        message = self._mask_email(message)
        message = self._mask_api_keys(message)
        message = self._mask_phone(message)
        message = self._mask_credit_cards(message)
        
        # Create a new record with masked message
        record.msg = message
        record.args = ()  # Clear args since we've formatted the message
        
        # Format using parent class
        return super().format(record)
    
    def _mask_email(self, text: str) -> str:
        """Mask email addresses"""
        def mask_email(match):
            email = match.group(0)
            parts = email.split('@')
            if len(parts) == 2:
                username, domain = parts
                masked_username = username[0] + '***' if len(username) > 1 else '***'
                return f"{masked_username}@{domain}"
            return '***@***'
        
        return self.EMAIL_PATTERN.sub(mask_email, text)
    
    def _mask_api_keys(self, text: str) -> str:
        """Mask API keys"""
        def mask_key(match):
            key = match.group(0)
            if len(key) > 10:
                return key[:4] + '****' + key[-4:]
            return '****'
        
        return self.API_KEY_PATTERN.sub(mask_key, text)
    
    def _mask_phone(self, text: str) -> str:
        """Mask phone numbers"""
        def mask_phone(match):
            phone = match.group(0)
            if len(phone) >= 4:
                return phone[:2] + '***' + phone[-2:]
            return '****'
        
        return self.PHONE_PATTERN.sub(mask_phone, text)
    
    def _mask_credit_cards(self, text: str) -> str:
        """Mask credit card numbers"""
        def mask_card(match):
            card = match.group(0)
            digits_only = re.sub(r'[-\s]', '', card)
            if len(digits_only) >= 4:
                return '****-****-****-' + digits_only[-4:]
            return '****'
        
        return self.CREDIT_CARD_PATTERN.sub(mask_card, text)


class SecureJsonFormatter(logging.Formatter):
    """
    JSON formatter with PII masking for structured logging
    """
    
    def __init__(self, mask_pii: bool = True):
        super().__init__()
        self.mask_pii = mask_pii
        self.secure_formatter = SecureFormatter() if mask_pii else None
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with PII masking"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_data and not key.startswith('_'):
                if key in ['args', 'asctime', 'created', 'exc_info', 'exc_text',
                          'filename', 'funcName', 'levelname', 'levelno', 'lineno',
                          'module', 'msecs', 'message', 'name', 'pathname', 'process',
                          'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName']:
                    continue
                log_data[key] = value
        
        # Mask PII in JSON
        if self.mask_pii and self.secure_formatter:
            log_data["message"] = self.secure_formatter._mask_email(log_data["message"])
            log_data["message"] = self.secure_formatter._mask_api_keys(log_data["message"])
            log_data["message"] = self.secure_formatter._mask_phone(log_data["message"])
            log_data["message"] = self.secure_formatter._mask_credit_cards(log_data["message"])
            
            # Mask PII in extra fields
            for key, value in log_data.items():
                if isinstance(value, str):
                    log_data[key] = self.secure_formatter._mask_email(value)
                    log_data[key] = self.secure_formatter._mask_api_keys(log_data[key])
                    log_data[key] = self.secure_formatter._mask_phone(log_data[key])
                    log_data[key] = self.secure_formatter._mask_credit_cards(log_data[key])
        
        return json.dumps(log_data, ensure_ascii=False)


def get_secure_logger(name: str = "nexsupply", level: int = logging.INFO, use_json: bool = True) -> logging.Logger:
    """
    Get a logger with secure formatting (PII masking).
    
    Args:
        name: Logger name
        level: Logging level
        use_json: Use JSON formatting (True) or text formatting (False)
        
    Returns:
        Configured logger with PII masking
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # Set formatter
    if use_json:
        formatter = SecureJsonFormatter(mask_pii=True)
    else:
        formatter = SecureFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

