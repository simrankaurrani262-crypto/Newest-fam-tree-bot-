"""
Friendship Repository
"""
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.friendship import Friendship
from src.database.repositories.base import BaseRepository


class FriendshipRepository(BaseRepository[Friendship]):
    """Friendship repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Friendship, session)
    
    async def get_friends(self, user_id: int) -> List[Friendship]:
        """Get all friends of user"""
        result = await self.session.execute(
            select(Friendship).where(Friendship.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_friends_count(self, user_id: int) -> int:
        """Get number of friends"""
        result = await self.session.execute(
            select(Friendship).where(Friendship.user_id == user_id)
        )
        return len(result.scalars().all())
    
    async def are_friends(self, user_id1: int, user_id2: int) -> bool:
        """Check if two users are friends"""
        result = await self.session.execute(
            select(Friendship)
            .where(
                Friendship.user_id == user_id1,
                Friendship.friend_id == user_id2
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def create_friendship(self, user_id1: int, user_id2: int):
        """Create bidirectional friendship"""
        # Create both directions
        friend1 = Friendship(user_id=user_id1, friend_id=user_id2)
        friend2 = Friendship(user_id=user_id2, friend_id=user_id1)
        
        self.session.add(friend1)
        self.session.add(friend2)
        await self.session.commit()
    
    async def remove_friendship(self, user_id1: int, user_id2: int):
        """Remove bidirectional friendship"""
        await self.session.execute(
            delete(Friendship)
            .where(
                Friendship.user_id == user_id1,
                Friendship.friend_id == user_id2
            )
        )
        await self.session.execute(
            delete(Friendship)
            .where(
                Friendship.user_id == user_id2,
                Friendship.friend_id == user_id1
            )
        )
        await self.session.commit()
