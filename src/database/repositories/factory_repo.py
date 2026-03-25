"""
Factory Repository
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.factory import FactoryWorker
from src.database.repositories.base import BaseRepository


class FactoryRepository(BaseRepository[FactoryWorker]):
    """Factory repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(FactoryWorker, session)
    
    async def get_workers(self, owner_id: int) -> List[FactoryWorker]:
        """Get all workers for owner"""
        result = await self.session.execute(
            select(FactoryWorker).where(FactoryWorker.owner_id == owner_id)
        )
        return result.scalars().all()
    
    async def is_worker_hired(self, owner_id: int, worker_id: int) -> bool:
        """Check if worker is already hired"""
        result = await self.session.execute(
            select(FactoryWorker)
            .where(
                FactoryWorker.owner_id == owner_id,
                FactoryWorker.worker_id == worker_id
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def hire_worker(self, owner_id: int, worker_id: int, price: float):
        """Hire a worker"""
        worker = FactoryWorker(
            owner_id=owner_id,
            worker_id=worker_id,
            price=price
        )
        self.session.add(worker)
        await self.session.commit()
    
    async def start_work(self, worker_id: int, end_time: datetime):
        """Start work for a worker"""
        await self.session.execute(
            update(FactoryWorker)
            .where(FactoryWorker.id == worker_id)
            .values(
                status="working",
                work_end_time=end_time
            )
        )
        await self.session.commit()
    
    async def complete_work(self, worker_id: int):
        """Complete work for a worker"""
        await self.session.execute(
            update(FactoryWorker)
            .where(FactoryWorker.id == worker_id)
            .values(
                status="completed",
                work_end_time=None
            )
        )
        await self.session.commit()
    
    async def add_shield(self, worker_id: int, duration_hours: int = 24):
        """Add shield to worker"""
        expires = datetime.utcnow() + timedelta(hours=duration_hours)
        await self.session.execute(
            update(FactoryWorker)
            .where(FactoryWorker.id == worker_id)
            .values(shield_expires=expires)
        )
        await self.session.commit()
    
    async def fire_worker(self, worker_id: int):
        """Fire a worker"""
        await self.session.execute(
            delete(FactoryWorker).where(FactoryWorker.id == worker_id)
        )
        await self.session.commit()
