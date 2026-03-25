"""
Economy Repository
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.economy import Economy
from src.database.repositories.base import BaseRepository


class EconomyRepository(BaseRepository[Economy]):
    """Economy repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Economy, session)
    
    async def get_by_user_id(self, user_id: int) -> Optional[Economy]:
        """Get economy by user ID"""
        result = await self.session.execute(
            select(Economy).where(Economy.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_for_user(self, user_id: int) -> Economy:
        """Create economy record for user"""
        return await self.create(user_id=user_id)
    
    async def add_money(self, user_id: int, amount: Decimal) -> Decimal:
        """Add money to user's balance"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(
                balance=Economy.balance + amount,
                total_earned=Economy.total_earned + amount
            )
        )
        await self.session.commit()
        
        economy = await self.get_by_user_id(user_id)
        return economy.balance
    
    async def deduct_money(self, user_id: int, amount: Decimal) -> Decimal:
        """Deduct money from user's balance"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(
                balance=Economy.balance - amount,
                total_spent=Economy.total_spent + amount
            )
        )
        await self.session.commit()
        
        economy = await self.get_by_user_id(user_id)
        return economy.balance
    
    async def deposit(self, user_id: int, amount: Decimal) -> tuple:
        """Deposit money to bank"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(
                balance=Economy.balance - amount,
                bank_balance=Economy.bank_balance + amount
            )
        )
        await self.session.commit()
        
        economy = await self.get_by_user_id(user_id)
        return economy.balance, economy.bank_balance
    
    async def withdraw(self, user_id: int, amount: Decimal) -> tuple:
        """Withdraw money from bank"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(
                balance=Economy.balance + amount,
                bank_balance=Economy.bank_balance - amount
            )
        )
        await self.session.commit()
        
        economy = await self.get_by_user_id(user_id)
        return economy.balance, economy.bank_balance
    
    async def transfer(self, from_user_id: int, to_user_id: int, amount: Decimal):
        """Transfer money between users"""
        # Deduct from sender
        await self.deduct_money(from_user_id, amount)
        # Add to receiver
        await self.add_money(to_user_id, amount)
    
    async def update_health(self, user_id: int, health: int):
        """Update user's health"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(health=health)
        )
        await self.session.commit()
    
    async def update_reputation(self, user_id: int, delta: int):
        """Update user's reputation"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(reputation=Economy.reputation + delta)
        )
        await self.session.commit()
    
    async def set_weapon(self, user_id: int, weapon_name: str):
        """Set user's equipped weapon"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(equipped_weapon=weapon_name)
        )
        await self.session.commit()
    
    async def increment_robbery_count(self, user_id: int):
        """Increment daily robbery count"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(robbery_count_today=Economy.robbery_count_today + 1)
        )
        await self.session.commit()
    
    async def increment_kill_count(self, user_id: int):
        """Increment daily kill count"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(kill_count_today=Economy.kill_count_today + 1)
        )
        await self.session.commit()
    
    async def reset_daily_limits(self, user_id: int):
        """Reset daily limits"""
        await self.session.execute(
            update(Economy)
            .where(Economy.user_id == user_id)
            .values(
                robbery_count_today=0,
                kill_count_today=0,
                last_limit_reset=datetime.utcnow()
            )
        )
        await self.session.commit()
    
    async def get_leaderboard(self, limit: int = 10) -> list:
        """Get top users by balance"""
        result = await self.session.execute(
            select(Economy, User)
            .join(User, Economy.user_id == User.id)
            .order_by(Economy.balance.desc())
            .limit(limit)
        )
        return result.all()
