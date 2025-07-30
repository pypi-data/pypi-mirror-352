"""
In-memory cache implementation for the Test Intelligence Engine.

This module provides a simple in-memory cache with TTL support.
"""
import time
import threading
from typing import Any, Dict, Optional, Tuple, Union


class MemoryCache:
    """
    Simple in-memory cache with TTL support.
    
    This cache stores key-value pairs in memory with optional time-to-live (TTL)
    for each entry. It also supports periodic cleanup of expired entries.
    """
    
    def __init__(self, default_ttl: Optional[int] = None, cleanup_interval: int = 60):
        """
        Initialize a new in-memory cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: None, no expiration)
            cleanup_interval: Interval in seconds for cleaning up expired entries (default: 60)
        """
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._lock = threading.RLock()
        self._default_ttl = default_ttl
        self._cleanup_interval = cleanup_interval
        self._cleanup_timer: Optional[threading.Timer] = None
        
        # Start the cleanup timer if cleanup is enabled
        if cleanup_interval > 0:
            self._start_cleanup_timer()
    
    def _start_cleanup_timer(self) -> None:
        """Start the cleanup timer."""
        self._cleanup_timer = threading.Timer(self._cleanup_interval, self._cleanup)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _cleanup(self) -> None:
        """Clean up expired entries."""
        current_time = time.time()
        
        with self._lock:
            # Find expired keys
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry is not None and expiry <= current_time
            ]
            
            # Remove expired keys
            for key in expired_keys:
                del self._cache[key]
        
        # Restart the cleanup timer
        self._start_cleanup_timer()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (default: None, use default_ttl)
        """
        # Calculate expiry time if TTL is specified
        expiry = None
        if ttl is not None:
            expiry = time.time() + ttl
        elif self._default_ttl is not None:
            expiry = time.time() + self._default_ttl
        
        # Store value and expiry time
        with self._lock:
            self._cache[key] = (value, expiry)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value to return if key not found (default: None)
            
        Returns:
            Cached value or default if key not found or expired
        """
        with self._lock:
            if key not in self._cache:
                return default
            
            value, expiry = self._cache[key]
            
            # Check if the value has expired
            if expiry is not None and expiry <= time.time():
                del self._cache[key]
                return default
            
            return value
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all values from the cache."""
        with self._lock:
            self._cache.clear()
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is not expired, False otherwise
        """
        with self._lock:
            if key not in self._cache:
                return False
            
            _, expiry = self._cache[key]
            
            # Check if the value has expired
            if expiry is not None and expiry <= time.time():
                del self._cache[key]
                return False
            
            return True
    
    def keys(self) -> list:
        """
        Get all non-expired keys in the cache.
        
        Returns:
            List of non-expired keys
        """
        current_time = time.time()
        
        with self._lock:
            return [
                key for key, (_, expiry) in self._cache.items()
                if expiry is None or expiry > current_time
            ]
    
    def __del__(self) -> None:
        """Clean up resources when the cache is destroyed."""
        if self._cleanup_timer is not None:
            self._cleanup_timer.cancel() 