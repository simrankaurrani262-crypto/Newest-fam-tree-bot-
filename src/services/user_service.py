"""
User Service
"""
from typing import Optional

from src.database.models.user import User
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.economy_repo import EconomyRepository
from src.database.repositories.garden_repo import GardenRepository
from src.database.repositories.barn_repo import BarnRepository
from src.database.connection import get_session


class UserService:
    """User service"""
    
    async def get_or_create_user(self, tg_user) -> User:
        """Get existing user or create new one"""
        async for session in get_session():
            repo = UserRepository(session)
            
            user = await repo.get_by_telegram_id(tg_user.id)
            
            if not user:
                # Create user
                user = await repo.create_from_telegram_user(tg_user)
                
                # Create related records
                economy_repo = EconomyRepository(session)
                await economy_repo.create_for_user(user.id)
                
                garden_repo = GardenRepository(session)
                await garden_repo.create_for_user(user.id)
                
                barn_repo = BarnRepository(session)
                await barn_repo.create_for_user(user.id)
            
            # Update last active
            await repo.update_last_active(tg_user.id)
            
            return user
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        async for session in get_session():
            repo = UserRepository(session)
            return await repo.get_by_telegram_id(telegram_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        async for session in get_session():
            repo = UserRepository(session)
            return await repo.get_by_username(username)
    
    async def set_language(self, telegram_id: int, language: str):
        """Set user's language"""
        async for session in get_session():
            repo = UserRepository(session)
            await repo.set_language(telegram_id, language)
    
    async def set_profile_pic(self, telegram_id: int, url: str):
        """Set user's profile picture"""
        async for session in get_session():
            repo = UserRepository(session)
            await repo.set_profile_pic(telegram_id, url)
    
    async def ban_user(self, telegram_id: int, reason: str = None):
        """Ban a user"""
        async for session in get_session():
            repo = UserRepository(session)
            await repo.ban_user(telegram_id, reason)
    
    async def unban_user(self, telegram_id: int):
        """Unban a user"""
        async for session in get_session():
            repo = UserRepository(session)
            await repo.unban_user(telegram_id)
