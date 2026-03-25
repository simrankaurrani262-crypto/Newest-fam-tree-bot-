"""
Economy Service
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Tuple

from src.database.repositories.economy_repo import EconomyRepository
from src.database.repositories.transaction_repo import TransactionRepository
from src.database.connection import get_session
from src.core.constants import (
    DAILY_BASE_REWARD,
    DAILY_FAMILY_BONUS,
    DAILY_STREAK_BONUS,
    GEMSTONES,
    MEDICAL_COST,
    SYSTEM_LIMITS
)
from src.core.exceptions import (
    InsufficientFundsError,
    LimitExceededError,
    UserDeadError
)


class EconomyService:
    """Economy service"""
    
    async def get_balance(self, user_id: int) -> Decimal:
        """Get user's balance"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.balance if economy else Decimal("0")
    
    async def get_bank_balance(self, user_id: int) -> Decimal:
        """Get user's bank balance"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.bank_balance if economy else Decimal("0")
    
    async def get_net_worth(self, user_id: int) -> Decimal:
        """Get user's net worth"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.net_worth if economy else Decimal("0")
    
    async def add_money(self, user_id: int, amount: Decimal) -> Decimal:
        """Add money to user's balance"""
        async for session in get_session():
            repo = EconomyRepository(session)
            return await repo.add_money(user_id, amount)
    
    async def deduct_money(self, user_id: int, amount: Decimal) -> Decimal:
        """Deduct money from user's balance"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            
            if economy.balance < amount:
                raise InsufficientFundsError(
                    f"Insufficient funds! You have ${economy.balance}, need ${amount}"
                )
            
            return await repo.deduct_money(user_id, amount)
    
    async def transfer(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: Decimal,
        description: str = None
    ):
        """Transfer money between users"""
        async for session in get_session():
            repo = EconomyRepository(session)
            
            # Check balance
            from_economy = await repo.get_by_user_id(from_user_id)
            if from_economy.balance < amount:
                raise InsufficientFundsError("Insufficient funds!")
            
            # Transfer
            await repo.transfer(from_user_id, to_user_id, amount)
            
            # Log transaction
            trans_repo = TransactionRepository(session)
            await trans_repo.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                amount=amount,
                type="transfer",
                description=description
            )
    
    async def deposit(self, user_id: int, amount: Decimal) -> Tuple[Decimal, Decimal]:
        """Deposit money to bank"""
        async for session in get_session():
            repo = EconomyRepository(session)
            
            economy = await repo.get_by_user_id(user_id)
            if economy.balance < amount:
                raise InsufficientFundsError("Insufficient funds!")
            
            return await repo.deposit(user_id, amount)
    
    async def withdraw(self, user_id: int, amount: Decimal) -> Tuple[Decimal, Decimal]:
        """Withdraw money from bank"""
        async for session in get_session():
            repo = EconomyRepository(session)
            
            economy = await repo.get_by_user_id(user_id)
            if economy.bank_balance < amount:
                raise InsufficientFundsError("Insufficient bank balance!")
            
            return await repo.withdraw(user_id, amount)
    
    async def get_daily_reward(
        self,
        user_id: int,
        family_count: int = 0,
        streak: int = 0
    ) -> dict:
        """Calculate and give daily reward"""
        async for session in get_session():
            repo = EconomyRepository(session)
            
            # Calculate reward
            base = DAILY_BASE_REWARD
            family_bonus = family_count * DAILY_FAMILY_BONUS
            streak_bonus = streak * DAILY_STREAK_BONUS
            total = base + family_bonus + streak_bonus
            
            # Assign random gemstone
            gemstone = random.choice(list(GEMSTONES.keys()))
            
            # Update economy
            await repo.add_money(user_id, Decimal(str(total)))
            
            return {
                "base": base,
                "family_bonus": family_bonus,
                "streak_bonus": streak_bonus,
                "total": total,
                "gemstone": gemstone
            }
    
    async def get_health(self, user_id: int) -> int:
        """Get user's health"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.health if economy else 5
    
    async def is_alive(self, user_id: int) -> bool:
        """Check if user is alive"""
        health = await self.get_health(user_id)
        return health > 0
    
    async def kill(self, user_id: int):
        """Kill a user (set health to 0)"""
        async for session in get_session():
            repo = EconomyRepository(session)
            await repo.update_health(user_id, 0)
    
    async def revive(self, user_id: int, health: int = 5):
        """Revive a user"""
        async for session in get_session():
            repo = EconomyRepository(session)
            await repo.update_health(user_id, health)
    
    async def medical(self, user_id: int) -> int:
        """Self-revive using medical"""
        async for session in get_session():
            repo = EconomyRepository(session)
            
            # Check if dead
            economy = await repo.get_by_user_id(user_id)
            if economy.health > 0:
                return economy.health  # Already alive
            
            # Check funds
            if economy.balance < MEDICAL_COST:
                raise InsufficientFundsError(
                    f"Medical costs ${MEDICAL_COST}. You only have ${economy.balance}"
                )
            
            # Deduct money and revive
            await repo.deduct_money(user_id, Decimal(str(MEDICAL_COST)))
            await repo.update_health(user_id, 5)
            
            return 5
    
    async def get_reputation(self, user_id: int) -> int:
        """Get user's reputation"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.reputation if economy else 100
    
    async def update_reputation(self, user_id: int, delta: int):
        """Update user's reputation"""
        async for session in get_session():
            repo = EconomyRepository(session)
            await repo.update_reputation(user_id, delta)
    
    async def can_rob(self, user_id: int) -> bool:
        """Check if user can rob today"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.robbery_count_today < SYSTEM_LIMITS["max_robbery_per_day"]
    
    async def can_kill(self, user_id: int) -> bool:
        """Check if user can kill today"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            return economy.kill_count_today < SYSTEM_LIMITS["max_kills_per_day"]
    
    async def increment_robbery(self, user_id: int):
        """Increment robbery count"""
        async for session in get_session():
            repo = EconomyRepository(session)
            await repo.increment_robbery_count(user_id)
    
    async def increment_kill(self, user_id: int):
        """Increment kill count"""
        async for session in get_session():
            repo = EconomyRepository(session)
            await repo.increment_kill_count(user_id)
    
    async def get_leaderboard(self, limit: int = 10) -> list:
        """Get money leaderboard"""
        async for session in get_session():
            repo = EconomyRepository(session)
            return await repo.get_leaderboard(limit)
