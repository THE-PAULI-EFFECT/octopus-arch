"""
Redis client for caching and rate limiting
"""

import redis.asyncio as redis
from api.config import settings
import structlog

logger = structlog.get_logger()


class RedisClient:
    """Async Redis client wrapper"""

    def __init__(self):
        self.client = None

    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise

    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    async def get(self, key: str):
        """Get value from Redis"""
        if not self.client:
            await self.connect()
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        """Set value in Redis with optional expiry"""
        if not self.client:
            await self.connect()
        return await self.client.set(key, value, ex=ex)

    async def incr(self, key: str):
        """Increment value in Redis"""
        if not self.client:
            await self.connect()
        return await self.client.incr(key)

    async def expire(self, key: str, seconds: int):
        """Set expiry on key"""
        if not self.client:
            await self.connect()
        return await self.client.expire(key, seconds)

    async def delete(self, key: str):
        """Delete key from Redis"""
        if not self.client:
            await self.connect()
        return await self.client.delete(key)

    async def ping(self):
        """Ping Redis server"""
        if not self.client:
            await self.connect()
        return await self.client.ping()


# Global Redis client instance
redis_client = RedisClient()
