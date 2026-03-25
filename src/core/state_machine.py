"""
State Machine for Multi-Step Commands
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from redis import asyncio as aioredis

from src.config.settings import settings

logger = logging.getLogger(__name__)


class UserState(Enum):
    """User states for state machine"""
    IDLE = "idle"
    WAITING_MARRIAGE_CONFIRMATION = "waiting_marriage_confirmation"
    WAITING_ADOPTION_CONFIRMATION = "waiting_adoption_confirmation"
    WAITING_DIVORCE_CONFIRMATION = "waiting_divorce_confirmation"
    PLANTING_MODE = "planting_mode"
    TRADING_MODE = "trading_mode"
    COOKING_MODE = "cooking_mode"
    GAME_IN_PROGRESS = "game_in_progress"
    WAITING_PAYMENT_CONFIRMATION = "waiting_payment_confirmation"
    WAITING_FRIEND_CONFIRMATION = "waiting_friend_confirmation"


class StateManager:
    """Manages user states for multi-step commands"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._local_states: Dict[int, Dict[str, Any]] = {}
        self.state_timeout = 300  # 5 minutes
    
    async def init(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            logger.info("StateManager: Redis connected")
        except Exception as e:
            logger.warning(f"StateManager: Redis connection failed, using local storage: {e}")
            self.redis = None
    
    def _get_key(self, user_id: int) -> str:
        """Generate Redis key for user state"""
        return f"user_state:{user_id}"
    
    async def set_state(
        self,
        user_id: int,
        state: UserState,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = None
    ):
        """
        Set user state with optional data
        
        Args:
            user_id: Telegram user ID
            state: New state
            data: Optional state data
            timeout: State timeout in seconds (default: 300)
        """
        timeout = timeout or self.state_timeout
        
        state_data = {
            "state": state.value,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.redis:
            key = self._get_key(user_id)
            await self.redis.setex(
                key,
                timeout,
                str(state_data)
            )
        else:
            self._local_states[user_id] = state_data
        
        logger.debug(f"Set state for user {user_id}: {state.value}")
    
    async def get_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user current state
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            State data or None if no state
        """
        if self.redis:
            key = self._get_key(user_id)
            data = await self.redis.get(key)
            if data:
                import ast
                return ast.literal_eval(data)
            return None
        else:
            return self._local_states.get(user_id)
    
    async def clear_state(self, user_id: int):
        """Clear user state"""
        if self.redis:
            key = self._get_key(user_id)
            await self.redis.delete(key)
        else:
            self._local_states.pop(user_id, None)
        
        logger.debug(f"Cleared state for user {user_id}")
    
    async def is_in_state(self, user_id: int, state: UserState) -> bool:
        """Check if user is in specific state"""
        current_state = await self.get_state(user_id)
        if not current_state:
            return False
        return current_state.get("state") == state.value
    
    async def get_state_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get state data for user"""
        state = await self.get_state(user_id)
        if state:
            return state.get("data", {})
        return None
    
    async def update_state_data(self, user_id: int, data: Dict[str, Any]):
        """Update state data while keeping the same state"""
        current = await self.get_state(user_id)
        if current:
            current["data"].update(data)
            await self.set_state(
                user_id,
                UserState(current["state"]),
                current["data"]
            )
    
    async def check_timeout(self, user_id: int) -> bool:
        """Check if user state has timed out"""
        state = await self.get_state(user_id)
        if not state:
            return True
        
        timestamp = datetime.fromisoformat(state["timestamp"])
        elapsed = (datetime.utcnow() - timestamp).total_seconds()
        
        return elapsed > self.state_timeout


# Global state manager instance
state_manager = StateManager()
        
