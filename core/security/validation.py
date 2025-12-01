"""
Input Validation & Sanitization - Injection Defense
Prevents XSS, SQL Injection, and Prompt Injection attacks
"""

import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from core.models import TargetMarket, SalesChannel


class SanitizedInput(BaseModel):
    """Validated and sanitized user input"""
    text: str = Field(..., min_length=1, max_length=10000)
    market: Optional[TargetMarket] = None
    volume: Optional[int] = Field(None, ge=1, le=1000000000)
    channel: Optional[SalesChannel] = None
    
    @field_validator('text')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize text input"""
        return sanitize_input(v)


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw user input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags (XSS prevention)
    text = _remove_html_tags(text)
    
    # Remove SQL injection patterns
    text = _remove_sql_injection_patterns(text)
    
    # Remove script tags and event handlers
    text = _remove_script_patterns(text)
    
    # Strip excessive whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def _remove_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    # Simple regex-based removal (bleach can be added for more robust handling)
    html_pattern = re.compile(r'<[^>]+>')
    text = html_pattern.sub('', text)
    return text


def _remove_sql_injection_patterns(text: str) -> str:
    """Detect and block common SQL injection patterns"""
    sql_patterns = [
        r"('|(\\')|(;)|(\-{2,})|(\/\*)|(\*\/))",  # SQL comment patterns
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+",
        r"(\bor\b|\band\b)\s+\d+\s*=\s*\d+",  # OR/AND 1=1 patterns
    ]
    
    for pattern in sql_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text


def _remove_script_patterns(text: str) -> str:
    """Remove JavaScript event handlers and script patterns"""
    script_patterns = [
        r"javascript:",
        r"on\w+\s*=",  # onclick, onerror, etc.
        r"<script[^>]*>.*?</script>",
        r"eval\s*\(",
        r"expression\s*\(",
    ]
    
    for pattern in script_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text


def wrap_for_llm(user_input: str) -> str:
    """
    Wrap user input in delimiters to prevent prompt injection.
    
    Args:
        user_input: User input text
        
    Returns:
        Wrapped text safe for LLM processing
    """
    # Use clear delimiters to separate user input from system prompt
    return f"""```USER_INPUT
{user_input}
```USER_INPUT_END"""


def validate_input(input_data: Dict[str, Any]) -> SanitizedInput:
    """
    Validate and sanitize user input using Pydantic.
    
    Args:
        input_data: Raw input dictionary
        
    Returns:
        Validated SanitizedInput model
        
    Raises:
        ValidationError: If input validation fails
    """
    return SanitizedInput(**input_data)

