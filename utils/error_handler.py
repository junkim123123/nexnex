"""
Error Handler - User-friendly error messages and retry logic
Provides better error handling and user experience
"""

from typing import Optional, Callable, Any
import time
import logging
from functools import wraps
from core.errors import (
    NexSupplyError,
    ParsingError,
    AIServiceError,
    ValidationError,
    CostingError,
    RateLimitExceeded
)

logger = logging.getLogger(__name__)


def get_user_friendly_message(error: Exception, lang: str = "en") -> tuple[str, str, Optional[str]]:
    """
    Convert technical errors to user-friendly messages.
    
    Args:
        error: The exception that occurred
        lang: Language code ("en" or "ko")
        
    Returns:
        Tuple of (title, message, suggestion)
    """
    error_messages = {
        "en": {
            ParsingError: (
                "⚠️ Input Parsing Error",
                "We couldn't understand your product description. Please try again with more details.",
                "💡 Tip: Include product name, quantity (e.g., '1000 units'), and target market (e.g., 'USA')"
            ),
            AIServiceError: (
                "🤖 AI Service Error",
                "The AI analysis service is temporarily unavailable. Please try again in a moment.",
                "💡 Tip: Check your API key or wait a few seconds and retry"
            ),
            ValidationError: (
                "📋 Validation Error",
                "The input data format is invalid. Please check your entries.",
                "💡 Tip: Ensure all required fields are filled correctly"
            ),
            CostingError: (
                "💰 Cost Calculation Error",
                "We couldn't calculate the costs for this product. Please verify your inputs.",
                "💡 Tip: Make sure retail price and volume are valid numbers"
            ),
            RateLimitExceeded: (
                "🚫 Rate Limit Exceeded",
                "You've made too many requests. Please wait before trying again.",
                None  # retry_after is shown separately
            ),
            Exception: (
                "❌ Unexpected Error",
                "Something went wrong. Our team has been notified.",
                "💡 Tip: Try refreshing the page or contact support if the issue persists"
            )
        },
        "ko": {
            ParsingError: (
                "⚠️ 입력 파싱 오류",
                "제품 설명을 이해할 수 없습니다. 더 자세한 정보를 포함하여 다시 시도해주세요.",
                "💡 팁: 제품명, 수량(예: '1000개'), 타겟 시장(예: '미국')을 포함하세요"
            ),
            AIServiceError: (
                "🤖 AI 서비스 오류",
                "AI 분석 서비스가 일시적으로 사용 불가능합니다. 잠시 후 다시 시도해주세요.",
                "💡 팁: API 키를 확인하거나 몇 초 기다린 후 재시도하세요"
            ),
            ValidationError: (
                "📋 검증 오류",
                "입력 데이터 형식이 올바르지 않습니다. 입력 항목을 확인해주세요.",
                "💡 팁: 모든 필수 항목이 올바르게 입력되었는지 확인하세요"
            ),
            CostingError: (
                "💰 비용 계산 오류",
                "이 제품의 비용을 계산할 수 없습니다. 입력값을 확인해주세요.",
                "💡 팁: 소매 가격과 수량이 유효한 숫자인지 확인하세요"
            ),
            RateLimitExceeded: (
                "🚫 요청 제한 초과",
                "너무 많은 요청을 하셨습니다. 잠시 기다린 후 다시 시도해주세요.",
                None
            ),
            Exception: (
                "❌ 예상치 못한 오류",
                "문제가 발생했습니다. 우리 팀에 알림이 전송되었습니다.",
                "💡 팁: 페이지를 새로고침하거나 문제가 계속되면 지원팀에 문의하세요"
            )
        }
    }
    
    messages = error_messages.get(lang, error_messages["en"])
    
    # Find matching error type
    error_type = type(error)
    for exc_type, (title, msg, suggestion) in messages.items():
        if isinstance(error, exc_type) or (error_type == exc_type):
            return title, msg, suggestion
    
    # Default fallback
    default = messages[Exception]
    return default[0], f"{default[1]}\n\nError details: {str(error)}", default[2]


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (AIServiceError, Exception)
):
    """
    Decorator to retry a function on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}")
            
            # All retries exhausted
            raise last_exception
        return wrapper
    return decorator


def handle_error_with_retry_button(
    error: Exception,
    retry_callback: Optional[Callable] = None,
    lang: str = "en"
) -> dict:
    """
    Handle error and return structured error information for UI display.
    
    Args:
        error: The exception that occurred
        retry_callback: Optional function to call on retry
        lang: Language code
        
    Returns:
        Dictionary with error information for UI
    """
    title, message, suggestion = get_user_friendly_message(error, lang)
    
    error_info = {
        "title": title,
        "message": message,
        "suggestion": suggestion,
        "error_type": type(error).__name__,
        "can_retry": isinstance(error, (AIServiceError, Exception)) and not isinstance(error, (ValidationError, ParsingError)),
        "retry_callback": retry_callback
    }
    
    # Add retry_after for RateLimitExceeded
    if isinstance(error, RateLimitExceeded):
        error_info["retry_after"] = getattr(error, "retry_after", 60)
    
    return error_info

