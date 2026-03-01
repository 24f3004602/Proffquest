"""
Redis caching utilities for API performance optimization.
Provides decorators for caching endpoints and cache management functions.
"""
import os
import json
import functools
import hashlib
from datetime import datetime
import redis
from flask import request

# Redis configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Initialize Redis client
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except (redis.ConnectionError, redis.RedisError):
    redis_client = None
    REDIS_AVAILABLE = False

# Cache TTL configurations (in seconds)
CACHE_TTL = {
    'short': 60,           # 1 minute - for rapidly changing data
    'medium': 300,         # 5 minutes - for moderately changing data
    'long': 900,           # 15 minutes - for slowly changing data
    'very_long': 3600,     # 1 hour - for rarely changing data
    'daily': 86400,        # 24 hours - for static data
}

# Cache key prefixes
CACHE_PREFIXES = {
    'drives': 'pq:drives',
    'companies': 'pq:companies',
    'students': 'pq:students',
    'analytics': 'pq:analytics',
    'public_stats': 'pq:public_stats',
    'search': 'pq:search',
}


def get_cache_key(*args, **kwargs):
    """Generate a unique cache key from arguments."""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(prefix, ttl_type='medium', key_builder=None):
    """
    Decorator to cache API responses.
    
    Args:
        prefix: Cache key prefix (use CACHE_PREFIXES)
        ttl_type: TTL type from CACHE_TTL dict
        key_builder: Optional function to build custom cache key
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE:
                return func(*args, **kwargs)
            
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key includes request args and JSON body
                request_args = dict(request.args) if request else {}
                cache_key = f"{prefix}:{func.__name__}:{get_cache_key(request_args)}"
            
            try:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                
                # Handle tuple responses (data, status_code)
                if isinstance(result, tuple):
                    data, status_code = result[0], result[1] if len(result) > 1 else 200
                    # Only cache successful responses
                    if status_code == 200:
                        redis_client.setex(
                            cache_key,
                            CACHE_TTL.get(ttl_type, 300),
                            json.dumps(data, default=str)
                        )
                else:
                    redis_client.setex(
                        cache_key,
                        CACHE_TTL.get(ttl_type, 300),
                        json.dumps(result, default=str)
                    )
                
                return result
            except (redis.RedisError, json.JSONDecodeError) as e:
                print(f"Cache error: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def invalidate_cache(patterns):
    """
    Invalidate cache entries matching patterns.
    
    Args:
        patterns: List of patterns to match (e.g., ['pq:drives:*', 'pq:analytics:*'])
    """
    if not REDIS_AVAILABLE:
        return
    
    try:
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
    except redis.RedisError as e:
        print(f"Cache invalidation error: {e}")


def invalidate_drives_cache():
    """Invalidate all drives-related caches."""
    invalidate_cache([
        f"{CACHE_PREFIXES['drives']}:*",
        f"{CACHE_PREFIXES['analytics']}:*",
        f"{CACHE_PREFIXES['public_stats']}:*",
    ])


def invalidate_company_cache(company_id=None):
    """Invalidate company-related caches."""
    patterns = [f"{CACHE_PREFIXES['companies']}:*"]
    if company_id:
        patterns.append(f"{CACHE_PREFIXES['companies']}:{company_id}:*")
    invalidate_cache(patterns)


def invalidate_student_cache(student_id=None):
    """Invalidate student-related caches."""
    patterns = [f"{CACHE_PREFIXES['students']}:*"]
    if student_id:
        patterns.append(f"{CACHE_PREFIXES['students']}:{student_id}:*")
    invalidate_cache(patterns)


def invalidate_application_cache():
    """Invalidate application-related caches (triggers analytics refresh)."""
    invalidate_cache([
        f"{CACHE_PREFIXES['analytics']}:*",
        f"{CACHE_PREFIXES['public_stats']}:*",
    ])


def get_cached_value(key):
    """Get a value from cache."""
    if not REDIS_AVAILABLE:
        return None
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except (redis.RedisError, json.JSONDecodeError):
        return None


def set_cached_value(key, value, ttl_type='medium'):
    """Set a value in cache."""
    if not REDIS_AVAILABLE:
        return False
    try:
        redis_client.setex(key, CACHE_TTL.get(ttl_type, 300), json.dumps(value, default=str))
        return True
    except (redis.RedisError, TypeError, ValueError):
        return False


def get_cache_stats():
    """Get cache statistics."""
    if not REDIS_AVAILABLE:
        return {'available': False}
    
    try:
        info = redis_client.info()
        keys_count = {prefix: len(redis_client.keys(f"{CACHE_PREFIXES[prefix]}:*")) 
                      for prefix in CACHE_PREFIXES}
        
        return {
            'available': True,
            'connected_clients': info.get('connected_clients', 0),
            'used_memory_human': info.get('used_memory_human', 'N/A'),
            'total_keys': sum(keys_count.values()),
            'keys_by_prefix': keys_count,
            'hits': info.get('keyspace_hits', 0),
            'misses': info.get('keyspace_misses', 0),
        }
    except redis.RedisError:
        return {'available': False}
