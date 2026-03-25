"""
User Repository
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user import User
from src.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(User, session)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username (case-insensitive)"""
        result = await self.session.execute(
            select(User).where(User.username.ilike(username))
        )
        return result.scalar_one_or_none()
    
    async def create_from_telegram_user(self, tg_user) -> User:
        """Create user from Telegram user object"""
        return await self.create(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            is_premium=getattr(tg_user, 'is_premium', False)
        )
    
    async def update_last_active(self, telegram_id: int):
        """Update user's last active timestamp"""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_active=datetime.utcnow())
        )
        await self.session.commit()
    
    async def ban_user(self, telegram_id: int, reason: str = None, until: datetime = None):
        """Ban a user"""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                is_banned=True,
                ban_reason=reason,
                banned_until=until
            )
        )
        await self.session.commit()
    
    async def unban_user(self, telegram_id: int):
        """Unban a user"""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                is_banned=False,
                ban_reason=None,
                banned_until=None
            )
        )
        await self.session.commit()
    
    async def set_language(self, telegram_id: int, language: str):
        """Set user's language preference"""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language=language)
        )
        await self.session.commit()
    
    async def set_profile_pic(self, telegram_id: int, url: str):
        """Set user's profile picture URL"""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(profile_pic_url=url)
        )
        await self.session.commit()
        
