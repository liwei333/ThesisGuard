"""Redis client wrapper for cache and queue operations."""


import redis
from backend.common.config import settings


class RedisClient:
    """Redis client for caching and basic queue operations."""

    def __init__(self) -> None:
        self._cache_client: redis.Redis | None = None

    @property
    def cache(self) -> redis.Redis:
        """Get the cache Redis connection."""
        if self._cache_client is None:
            self._cache_client = redis.Redis.from_url(
                settings.redis_cache_url_resolved,
                decode_responses=True,
            )
        return self._cache_client

    def health_check(self) -> bool:
        """Check if Redis is reachable."""
        try:
            return bool(self.cache.ping())
        except Exception:
            return False

    def set_cache(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set a cache value with TTL."""
        return bool(self.cache.set(key, value, ex=ttl))

    def get_cache(self, key: str) -> str | None:
        """Get a cache value."""
        value = self.cache.get(key)
        return str(value) if value is not None else None

    def delete_cache(self, key: str) -> bool:
        """Delete a cache key."""
        return bool(self.cache.delete(key))


# Singleton instance
redis_client = RedisClient()
