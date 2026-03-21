import os
from flask_caching import Cache
from flask import request

cache = Cache()

CACHE_TTL = 300  # 5 minutes default

def init_cache(app):
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    try:
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_URL'] = redis_url
        app.config['CACHE_DEFAULT_TIMEOUT'] = CACHE_TTL
        app.config['CACHE_KEY_PREFIX'] = 'pq:'
        cache.init_app(app)
        # test connection
        with app.app_context():
            cache.set('_ping', 1, timeout=5)
            cache.delete('_ping')
    except Exception:
        # Redis unreachable → fall back to in-process simple cache
        app.config['CACHE_TYPE'] = 'SimpleCache'
        app.config['CACHE_DEFAULT_TIMEOUT'] = CACHE_TTL
        cache.init_app(app)

def make_search_cache_key():
    return f"pq:search:{request.full_path}"
