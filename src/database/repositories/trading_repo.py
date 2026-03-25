"""
Trading Repository
"""
from typing import List, Optional

from sqlalchemy import select, update, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.trading import Stand
from src.database.repositories.base import BaseRepository


class TradingRepository(BaseRepository[Stand]):
    """Trading repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Stand, session)
    
    async def get_all_stands(self) -> List[Stand]:
        """Get all active stands"""
        result = await self.session.execute(
            select(Stand).order_by(Stand.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_user_stands(self, seller_id: int) -> List[Stand]:
        """Get stands by seller"""
        result = await self.session.execute(
            select(Stand).where(Stand.seller_id == seller_id)
        )
        return result.scalars().all()
    
    async def find_cheapest(self, crop_type: str, quantity: int) -> Optional[Stand]:
        """Find cheapest stand with enough quantity"""
        result = await self.session.execute(
            select(Stand)
            .where(
                Stand.crop_type == crop_type,
                Stand.quantity >= quantity
            )
            .order_by(asc(Stand.price_per_unit))
        )
        return result.scalar_one_or_none()
    
    async def create_stand(
        self,
        seller_id: int,
        crop_type: str,
        quantity: int,
        price_per_unit: float
    ) -> Stand:
        """Create a new stand"""
        stand = Stand(
            seller_id=seller_id,
            crop_type=crop_type,
            quantity=quantity,
            price_per_unit=price_per_unit
        )
        self.session.add(stand)
        await self.session.commit()
        return stand
    
    async def update_quantity(self, stand_id: int, new_quantity: int):
        """Update stand quantity"""
        await self.session.execute(
            update(Stand)
            .where(Stand.id == stand_id)
            .values(quantity=new_quantity)
        )
        await self.session.commit()
    
    async def delete_stand(self, stand_id: int):
        """Delete a stand"""
        await self.session.execute(
            delete(Stand).where(Stand.id == stand_id)
        )
        await self.session.commit()
