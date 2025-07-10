import hashlib
import json
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from .local_tools_registry import ToolRegistry
import asyncio


class CacheEntry:
    """A cache entry for tool results"""
    
    def __init__(self, result: Any, timestamp: float, ttl: Optional[float] = None):
        self.result = result
        self.timestamp = timestamp
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "result": self.result,
            "timestamp": self.timestamp,
            "ttl": self.ttl
        }


class ToolCache:
    """Caching system for tool results"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, float] = {}
    
    def _generate_key(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Generate a cache key for tool execution"""
        # Create a deterministic string representation of parameters
        param_str = json.dumps(parameters, sort_keys=True)
        key_data = f"{tool_name}:{param_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Get a cached result for tool execution"""
        key = self._generate_key(tool_name, parameters)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired():
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        
        return entry.result
    
    def set(self, tool_name: str, parameters: Dict[str, Any], result: Any, ttl: Optional[float] = None) -> None:
        """Cache a tool result"""
        key = self._generate_key(tool_name, parameters)
        
        # Use default TTL if not specified
        if ttl is None:
            ttl = self.default_ttl
        
        # Check cache size and evict if necessary
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        # Store the entry
        self.cache[key] = CacheEntry(result, time.time(), ttl)
        self.access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Evict the least recently used cache entry"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
        self.access_times.clear()
    
    def clear_expired(self) -> int:
        """Clear expired entries and return count of cleared entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        expired_count = len([entry for entry in self.cache.values() if entry.is_expired()])
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "valid_entries": len(self.cache) - expired_count,
            "max_size": self.max_size,
            "default_ttl": self.default_ttl
        }


class CachedToolRegistry(ToolRegistry):
    """Tool registry with caching capabilities"""
    
    def __init__(self, cache: ToolCache = None):
        super().__init__()
        self.cache = cache or ToolCache()
        self.tool_ttls: Dict[str, Optional[float]] = {}
    
    def set_tool_ttl(self, tool_name: str, ttl: Optional[float]) -> None:
        """Set TTL for a specific tool"""
        self.tool_ttls[tool_name] = ttl
    
    def get_tool_ttl(self, tool_name: str) -> Optional[float]:
        """Get TTL for a specific tool"""
        return self.tool_ttls.get(tool_name, self.cache.default_ttl)
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with caching"""
        # Check cache first
        cached_result = self.cache.get(tool_name, parameters)
        if cached_result is not None:
            return cached_result
        
        # Execute tool
        result = await super().execute_tool(tool_name, parameters)
        
        # Cache the result
        ttl = self.get_tool_ttl(tool_name)
        self.cache.set(tool_name, parameters, result, ttl)
        
        return result
    
    def clear_cache(self) -> None:
        """Clear the tool cache"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()


def cache_tool_result(ttl: Optional[float] = None, cache: ToolCache = None):
    """Decorator to cache tool results"""
    def decorator(func: Callable) -> Callable:
        tool_cache = cache or ToolCache()
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            param_dict = {}
            if args:
                param_dict["args"] = args
            if kwargs:
                param_dict.update(kwargs)
            
            # Check cache
            cached_result = tool_cache.get(func.__name__, param_dict)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Cache result
            tool_cache.set(func.__name__, param_dict, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator


# Global cached tool registry
cached_tool_registry = CachedToolRegistry()


# Example usage with caching decorator
@cache_tool_result(ttl=300)  # Cache for 5 minutes
async def expensive_calculation(data: str) -> str:
    """An expensive calculation that should be cached"""
    # Simulate expensive operation
    await asyncio.sleep(1)
    return f"Processed: {data}"


# Cache configuration for different tool types
def configure_tool_caching():
    """Configure caching for different types of tools"""
    
    # Data processing tools - cache for 1 hour
    cached_tool_registry.set_tool_ttl("csv_to_json", 3600)
    cached_tool_registry.set_tool_ttl("json_to_csv", 3600)
    cached_tool_registry.set_tool_ttl("filter_data", 3600)
    
    # File operations - no caching (always fresh)
    cached_tool_registry.set_tool_ttl("read_text_file", None)
    cached_tool_registry.set_tool_ttl("write_text_file", None)
    
    # Web scraping - cache for 30 minutes
    cached_tool_registry.set_tool_ttl("fetch_url", 1800)
    cached_tool_registry.set_tool_ttl("extract_text", 1800)
    
    # Math operations - cache for 1 hour
    cached_tool_registry.set_tool_ttl("calculate", 3600)
    cached_tool_registry.set_tool_ttl("statistics", 3600) 