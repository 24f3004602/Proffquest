import os
from flask_caching import Cache
from flask import request

cache = Cache()

CACHE_TTL = int(os.environ.get('CACHE_TTL', '300'))
SIMPLE_CACHE_THRESHOLD = int(os.environ.get('SIMPLE_CACHE_THRESHOLD', '1000'))
REDIS_CONNECT_TIMEOUT = float(os.environ.get('REDIS_CONNECT_TIMEOUT', '0.5'))
REDIS_SOCKET_TIMEOUT = float(os.environ.get('REDIS_SOCKET_TIMEOUT', '0.5'))

def init_cache(app):
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CACHE_DEFAULT_TIMEOUT'] = CACHE_TTL
    app.config['CACHE_KEY_PREFIX'] = 'pq:'
    try:
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_URL'] = redis_url
        app.config['CACHE_OPTIONS'] = {
            'socket_connect_timeout': REDIS_CONNECT_TIMEOUT,
            'socket_timeout': REDIS_SOCKET_TIMEOUT,
            'retry_on_timeout': True,
        }
        cache.init_app(app)
        # test connection
        with app.app_context():
            cache.set('_ping', 1, timeout=5)
            if cache.get('_ping') != 1:
                raise RuntimeError('Redis ping check failed')
            cache.delete('_ping')
        app.logger.info('Cache backend initialized: RedisCache (%s)', redis_url)
    except Exception as exc:
        app.config['CACHE_TYPE'] = 'SimpleCache'
        app.config.pop('CACHE_REDIS_URL', None)
        app.config.pop('CACHE_OPTIONS', None)
        app.config['CACHE_THRESHOLD'] = SIMPLE_CACHE_THRESHOLD
        cache.init_app(app)
        app.logger.warning(
            'Redis cache unavailable (%s). Falling back to SimpleCache (threshold=%s).',
            exc,
            SIMPLE_CACHE_THRESHOLD,
        )

def make_search_cache_key(*args, **kwargs):
    return f"pq:search:{request.full_path}"
