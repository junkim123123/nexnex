"""
Rate Limiting - Abuse Prevention
Token Bucket algorithm implementation for request throttling
"""

import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from core.errors import RateLimitExceeded


class RateLimiter:
    """
    Rate Limiter using Token Bucket algorithm.
    
    Allows a certain number of requests per time window.
    Uses in-memory storage (session_state) or Redis if available.
    """
    
    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 60,
        redis_client: Optional[Any] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_client = redis_client
        self._local_buckets: Dict[str, Dict] = {}  # For in-memory storage
    
    def is_allowed(self, identifier: str) -> tuple[bool, float]:
        """
        Check if request is allowed and return retry_after if not.
        
        Args:
            identifier: Unique identifier (IP, session ID, user ID)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Use Redis if available (distributed rate limiting)
        if self.redis_client:
            return self._check_redis_rate_limit(identifier, now)
        
        # Use in-memory storage (local rate limiting)
        return self._check_local_rate_limit(identifier, now)
    
    def _check_local_rate_limit(self, identifier: str, now: float) -> tuple[bool, float]:
        """Check rate limit using local in-memory storage"""
        if identifier not in self._local_buckets:
            self._local_buckets[identifier] = {
                'tokens': self.max_requests,
                'last_refill': now
            }
        
        bucket = self._local_buckets[identifier]
        
        # Refill tokens based on elapsed time
        elapsed = now - bucket['last_refill']
        tokens_to_add = int(elapsed / self.window_seconds) * self.max_requests
        
        if tokens_to_add > 0:
            bucket['tokens'] = min(self.max_requests, bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = now
        
        # Check if request is allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True, 0.0
        
        # Calculate retry_after
        next_refill = bucket['last_refill'] + self.window_seconds
        retry_after = max(0.0, next_refill - now)
        
        return False, retry_after
    
    def _check_redis_rate_limit(self, identifier: str, now: float) -> tuple[bool, float]:
        """Check rate limit using Redis (distributed rate limiting)"""
        try:
            key = f"rate_limit:{identifier}"
            
            # Get current count
            current_count = self.redis_client.get(key)
            if current_count is None:
                # First request in window
                self.redis_client.setex(key, self.window_seconds, 1)
                return True, 0.0
            
            current_count = int(current_count)
            
            if current_count < self.max_requests:
                # Increment counter
                self.redis_client.incr(key)
                # Refresh TTL
                ttl = self.redis_client.ttl(key)
                if ttl <= 0:
                    self.redis_client.expire(key, self.window_seconds)
                return True, 0.0
            
            # Rate limit exceeded
            ttl = self.redis_client.ttl(key)
            retry_after = max(0.0, float(ttl) if ttl > 0 else self.window_seconds)
            return False, retry_after
            
        except Exception as e:
            # If Redis fails, fall back to local rate limiting
            return self._check_local_rate_limit(identifier, now)
    
    def check_or_raise(self, identifier: str) -> None:
        """
        Check rate limit and raise exception if exceeded.
        
        Args:
            identifier: Unique identifier
            
        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        is_allowed, retry_after = self.is_allowed(identifier)
        if not is_allowed:
            raise RateLimitExceeded(
                retry_after=retry_after,
                message=f"Rate limit exceeded. Please try again in {retry_after:.1f} seconds."
            )
    
    def allow_request(self, identifier: str) -> bool:
        """
        Compatibility method - Check if request is allowed.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            True if request is allowed, False otherwise
        """
        is_allowed, _ = self.is_allowed(identifier)
        return is_allowed
    
    def get_retry_after(self, identifier: str) -> float:
        """
        Compatibility method - Get retry after time in seconds.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Retry after time in seconds
        """
        _, retry_after = self.is_allowed(identifier)
        return retry_after


def get_rate_limiter(
    max_requests: int = 10,
    window_seconds: int = 60,
    redis_client: Optional[Any] = None
) -> RateLimiter:
    """
    Get rate limiter instance.
    
    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        redis_client: Optional Redis client
        
    Returns:
        RateLimiter instance
    """
    return RateLimiter(
        max_requests=max_requests,
        window_seconds=window_seconds,
        redis_client=redis_client
    )

