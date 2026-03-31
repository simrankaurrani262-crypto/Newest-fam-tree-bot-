"""
Rate Limiting System
"""
import logging
from typing import Tuple
from datetime import datetime, timedelta

from redis import asyncio as aioredis

from src.config.settings import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter using Redis sliding window with local fallback"""
    
    def __init__(self):
        self.redis: aioredis.Redis = None
        self._local_storage: dict = {}  # Fallback local storage
        self._initialized = False
    
    async def init(self):
        """Initialize Redis connection"""
        if self._initialized:
            return
            
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("RateLimiter: Redis connected")
        except Exception as e:
            logger.warning(f"RateLimiter: Redis connection failed, using local storage: {e}")
            self.redis = None
        
        self._initialized = True
    
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
        # Initialize if not already done
        if not self._initialized:
            await self.init()
        
        if self.redis:
            return await self._is_allowed_redis(user_id, command, max_requests, window)
        else:
            return await self._is_allowed_local(user_id, command, max_requests, window)
    
    async def _is_allowed_redis(
        self,
        user_id: int,
        command: str,
        max_requests: int,
        window: int
    ) -> Tuple[bool, int]:
        """Redis-based rate limiting"""
        key = self._get_key(user_id, command)
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        try:
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
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fallback to local storage on Redis error
            return await self._is_allowed_local(user_id, command, max_requests, window)
    
    async def _is_allowed_local(
        self,
        user_id: int,
        command: str,
        max_requests: int,
        window: int
    ) -> Tuple[bool, int]:
        """Local memory-based rate limiting (fallback)"""
        key = self._get_key(user_id, command)
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        # Initialize storage for this key
        if key not in self._local_storage:
            self._local_storage[key] = []
        
        # Remove old entries
        self._local_storage[key] = [
            ts for ts in self._local_storage[key]
            if ts > window_start
        ]
        
        # Check limit
        if len(self._local_storage[key]) >= max_requests:
            if self._local_storage[key]:
                oldest = self._local_storage[key][0]
                retry_after = int(window - (now - oldest).total_seconds())
                return False, max(1, retry_after)
            return False, window
        
        # Add current request
        self._local_storage[key].append(now)
        
        return True, 0
    
    async def get_remaining(
        self,
        user_id: int,
        command: str,
        max_requests: int = 30
    ) -> int:
        """Get remaining requests for user"""
        if not self._initialized:
            await self.init()
            
        key = self._get_key(user_id, command)
        
        if self.redis:
            try:
                current = await self.redis.zcard(key)
                return max(0, max_requests - current)
            except Exception as e:
                logger.error(f"Redis error in get_remaining: {e}")
        
        # Local fallback
        if key in self._local_storage:
            return max(0, max_requests - len(self._local_storage[key]))
        return max_requests
    
    async def reset(self, user_id: int, command: str = None):
        """Reset rate limit for user"""
        if not self._initialized:
            await self.init()
            
        if command:
            key = self._get_key(user_id, command)
            if self.redis:
                try:
                    await self.redis.delete(key)
                except Exception as e:
                    logger.error(f"Redis error in reset: {e}")
            # Also clear local
            self._local_storage.pop(key, None)
        else:
            # Reset all commands for user
            pattern = f"rate_limit:{user_id}:"
            if self.redis:
                try:
                    keys = await self.redis.keys(pattern + "*")
                    if keys:
                        await self.redis.delete(*keys)
                except Exception as e:
                    logger.error(f"Redis error in reset all: {e}")
            # Also clear local
            keys_to_remove = [k for k in self._local_storage.keys() if k.startswith(pattern)]
            for k in keys_to_remove:
                self._local_storage.pop(k, None)


# Global rate limiter instance
rate_limiter = RateLimiter()
                 
