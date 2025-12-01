"""
Response Cache - Simple in-memory cache for AI responses
Reduces API calls by caching identical requests
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta


class ResponseCache:
    """
    Simple in-memory cache for AI analysis responses.
    Uses hash of input text/image to identify identical requests.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, text: Optional[str] = None, image_data: Optional[bytes] = None) -> str:
        """
        Generate a cache key from input text and/or image data.
        
        Args:
            text: Input text
            image_data: Image data bytes (or list of image bytes)
            
        Returns:
            Cache key string (SHA256 hash)
        """
        # Handle list of images
        if isinstance(image_data, list):
            # Hash all images together
            combined = (text or "").encode('utf-8')
            for img_bytes in image_data:
                combined += img_bytes[:1000]  # Use first 1KB as fingerprint
            key_input = combined
        elif image_data:
            # Single image
            key_input = ((text or "") + image_data[:1000].hex()).encode('utf-8')
        else:
            # Text only
            key_input = (text or "").encode('utf-8')
        
        return hashlib.sha256(key_input).hexdigest()
    
    def get(self, text: Optional[str] = None, image_data: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response if available and not expired.
        
        Args:
            text: Input text
            image_data: Image data bytes (or list)
            
        Returns:
            Cached response dict, or None if not found/expired
        """
        key = self._generate_key(text, image_data)
        
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            
            # Check if expired
            if time.time() - timestamp < self.ttl:
                return cached_data
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    def set(self, text: Optional[str] = None, image_data: Optional[bytes] = None, response: Dict[str, Any] = None) -> None:
        """
        Store response in cache.
        
        Args:
            text: Input text
            image_data: Image data bytes (or list)
            response: Response dictionary to cache
        """
        if response is None:
            return
        
        key = self._generate_key(text, image_data)
        self.cache[key] = (response, time.time())
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def clear_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        current_time = time.time()
        valid_entries = sum(
            1 for _, timestamp in self.cache.values()
            if current_time - timestamp < self.ttl
        )
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries,
            "ttl_seconds": self.ttl
        }


# Global cache instance (1 hour TTL)
response_cache = ResponseCache(ttl_seconds=3600)

