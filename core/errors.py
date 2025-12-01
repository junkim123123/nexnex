"""
Custom Exception Classes for NexSupply
Clear error hierarchy for better error handling and debugging.
"""

class NexSupplyError(Exception):
    """Base exception class for all NexSupply-specific errors"""
    pass

class ParsingError(NexSupplyError):
    """Raised when input parsing fails or produces invalid results"""
    pass

class AIServiceError(NexSupplyError):
    """Raised when Gemini API fails or produces invalid responses"""
    pass

class ValidationError(NexSupplyError):
    """Raised when data validation fails (Pydantic validation errors)"""
    pass

class CostingError(NexSupplyError):
    """Raised when cost calculation logic fails"""
    pass

class RateLimitExceeded(NexSupplyError):
    """Raised when rate limit is exceeded"""
    def __init__(self, retry_after: float, message: str = "Rate limit exceeded"):
        super().__init__(message)
        self.retry_after = retry_after

