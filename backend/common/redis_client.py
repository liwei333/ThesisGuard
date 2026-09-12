"""Redis client wrapper for cache and queue operations."""

from typing import Optional

import redis

from backend.common.config import settings


class RedisClient:
    """Redis client for caching and basic queue operations."""

    def __init__(self) -> None:
        self._cache_client: Optional[redis.Redis] = None

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
            return self.cache.ping()
        except Exception:
            return False

    def set_cache(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set a cache value with TTL."""
        return self.cache.set(key, value, ex=ttl)

    def get_cache(self, key: str) -> Optional[str]:
        """Get a cache value."""
        return self.cache.get(key)

    def delete_cache(self, key: str) -> bool:
        """Delete a cache key."""
        return bool(self.cache.delete(key))


# Singleton instance
redis_client = RedisClient()
