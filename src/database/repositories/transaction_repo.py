"""
Transaction Repository
"""
from typing import List
from datetime import datetime, timedelta

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.transaction import Transaction
from src.database.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Transaction repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Transaction, session)
    
    async def get_user_transactions(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Transaction]:
        """Get user's transaction history"""
        result = await self.session.execute(
            select(Transaction)
            .where(
                (Transaction.from_user_id == user_id) |
                (Transaction.to_user_id == user_id)
            )
            .order_by(desc(Transaction.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_transactions(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[Transaction]:
        """Get recent transactions"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.created_at >= since)
            .order_by(desc(Transaction.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_transactions_by_type(
        self,
        transaction_type: str,
        limit: int = 50
    ) -> List[Transaction]:
        """Get transactions by type"""
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.type == transaction_type)
            .order_by(desc(Transaction.created_at))
            .limit(limit)
        )
        return result.scalars().all()
