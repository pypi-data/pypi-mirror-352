"""
Cache Manager - Handle caching of SDK data for performance
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional
import aiofiles
import asyncio
from datetime import datetime, timedelta
from ..config import config

class CacheManager:
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache manager with optional cache directory"""
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use config cache directory
            self.cache_dir = config.cache_dir
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._max_size_bytes = config.cache_max_size_mb * 1024 * 1024
        self._default_ttl = config.cache_ttl_hours * 3600
    
    async def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds (None = use default TTL)
        
        Returns:
            Cached value or None if not found/expired
        """
        if not config.enable_caching:
            return None
            
        # Use default TTL if not specified
        if ttl is None:
            ttl = self._default_ttl
            
        # Check memory cache first
        if key in self._memory_cache:
            cached = self._memory_cache[key]
            if time.time() - cached["timestamp"] < ttl:
                return cached["value"]
            else:
                # Expired in memory
                del self._memory_cache[key]
        
        # Check disk cache
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                async with aiofiles.open(cache_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                
                if time.time() - data["timestamp"] < ttl:
                    # Store in memory for faster access
                    self._memory_cache[key] = data
                    return data["value"]
                else:
                    # Expired on disk
                    cache_file.unlink()
            except Exception:
                # Corrupted cache file
                cache_file.unlink(missing_ok=True)
        
        return None
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        if not config.enable_caching:
            return
            
        async with self._lock:
            # Check cache size limit
            cache_info = await self.get_cache_info()
            if cache_info["total_size_bytes"] > self._max_size_bytes:
                # Clean up old entries
                await self.cleanup_expired(self._default_ttl // 2)
            
            data = {
                "value": value,
                "timestamp": time.time()
            }
            
            # Store in memory
            self._memory_cache[key] = data
            
            # Store on disk
            cache_file = self._get_cache_file(key)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        # Remove from memory
        self._memory_cache.pop(key, None)
        
        # Remove from disk
        cache_file = self._get_cache_file(key)
        cache_file.unlink(missing_ok=True)
    
    async def clear(self) -> None:
        """Clear all cache"""
        self._memory_cache.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.rglob("*.json"):
            cache_file.unlink()
    
    async def get_or_compute(self, key: str, compute_fn, ttl: Optional[int] = None) -> Any:
        """
        Get from cache or compute if not found.
        
        Args:
            key: Cache key
            compute_fn: Async function to compute value if not cached
            ttl: Time to live in seconds
        
        Returns:
            Cached or computed value
        """
        value = await self.get(key, ttl)
        if value is not None:
            return value
        
        # Compute value
        value = await compute_fn()
        await self.set(key, value)
        return value
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        # Use config method for safe key generation
        return config.get_cache_path(key)
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cache usage"""
        total_size = 0
        file_count = 0
        
        for cache_file in self.cache_dir.rglob("*.json"):
            total_size += cache_file.stat().st_size
            file_count += 1
        
        return {
            "cache_dir": str(self.cache_dir),
            "memory_entries": len(self._memory_cache),
            "disk_entries": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "max_size_mb": config.cache_max_size_mb,
            "usage_percent": round((total_size / self._max_size_bytes) * 100, 2) if self._max_size_bytes > 0 else 0
        }
    
    async def cleanup_expired(self, ttl: Optional[int] = None) -> int:
        """
        Clean up expired cache entries.
        
        Args:
            ttl: TTL in seconds (None = use default from config)
        
        Returns:
            Number of entries cleaned
        """
        if ttl is None:
            ttl = self._default_ttl
        cleaned = 0
        current_time = time.time()
        
        # Clean memory cache
        expired_keys = []
        for key, data in self._memory_cache.items():
            if current_time - data["timestamp"] > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_cache[key]
            cleaned += 1
        
        # Clean disk cache
        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                async with aiofiles.open(cache_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                
                if current_time - data["timestamp"] > ttl:
                    cache_file.unlink()
                    cleaned += 1
            except Exception:
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                cleaned += 1
        
        return cleaned