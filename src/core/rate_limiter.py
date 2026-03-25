"""
Rate Limiting System
"""
import logging
from typing import Tuple
from datetime import datetime, timedelta

import aioredis

from src.config.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Redis sliding window"""
    
    def __init__(self):
        self.redis: aioredis.Redis = None
    
    async def init(self):
        """Initialize Redis connection"""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        logger.info("RateLimiter: Redis connected")
    
    def _get_key(self, user_id: int, command: str) -> str:
        """Generate Redis key for rate limit"""
        return f"rate_limit:{user_id}:{command}"
    
    async def is_allowed(
        self,
        user_id: int,
        command: str,
        max_requests: int = 30,
        window: int = 60
    ) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit
        
        Args:
            user_id: Telegram user ID
            command: Command name
            max_requests: Maximum requests in window
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, retry_after)
        """
        key = self._get_key(user_id, command)
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start.timestamp())
        
        # Count current requests
        current_count = await self.redis.zcard(key)
        
        if current_count >= max_requests:
            # Get oldest request to calculate retry_after
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_timestamp = oldest[0][1]
                retry_after = int(window - (now.timestamp() - oldest_timestamp))
                return False, max(1, retry_after)
            return False, window
        
        # Add current request
        await self.redis.zadd(key, {str(now.timestamp()): now.timestamp()})
        await self.redis.expire(key, window)
        
        return True, 0
    
    async def get_remaining(
        self,
        user_id: int,
        command: str,
        max_requests: int = 30
    ) -> int:
        """Get remaining requests for user"""
        key = self._get_key(user_id, command)
        current = await self.redis.zcard(key)
        return max(0, max_requests - current)
    
    async def reset(self, user_id: int, command: str = None):
        """Reset rate limit for user"""
        if command:
            key = self._get_key(user_id, command)
            await self.redis.delete(key)
        else:
            # Reset all commands for user
            pattern = f"rate_limit:{user_id}:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)


# Global rate limiter instance
rate_limiter = RateLimiter()
