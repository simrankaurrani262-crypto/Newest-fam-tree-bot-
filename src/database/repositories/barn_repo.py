"""
Barn Repository
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.barn import Barn, BarnItem
from src.database.repositories.base import BaseRepository


class BarnRepository(BaseRepository[Barn]):
    """Barn repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Barn, session)
    
    async def get_by_user_id(self, user_id: int) -> Optional[Barn]:
        """Get barn by user ID"""
        result = await self.session.execute(
            select(Barn).where(Barn.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_for_user(self, user_id: int) -> Barn:
        """Create barn for user"""
        return await self.create(user_id=user_id)
    
    async def get_item(self, barn_id: int, item_name: str) -> Optional[BarnItem]:
        """Get specific item in barn"""
        result = await self.session.execute(
            select(BarnItem)
            .where(
                BarnItem.barn_id == barn_id,
                BarnItem.item_name == item_name
            )
        )
        return result.scalar_one_or_none()
    
    async def get_items(self, barn_id: int) -> List[BarnItem]:
        """Get all items in barn"""
        result = await self.session.execute(
            select(BarnItem).where(BarnItem.barn_id == barn_id)
        )
        return result.scalars().all()
    
    async def add_item(
        self,
        barn_id: int,
        item_name: str,
        quantity: int,
        item_type: str = "crop"
    ) -> BarnItem:
        """Add item to barn"""
        # Check if item exists
        existing = await self.get_item(barn_id, item_name)
        
        if existing:
            existing.quantity += quantity
            await self.session.commit()
            return existing
        else:
            item = BarnItem(
                barn_id=barn_id,
                item_name=item_name,
                item_type=item_type,
                quantity=quantity
            )
            self.session.add(item)
            await self.session.commit()
            return item
    
    async def remove_item(self, barn_id: int, item_name: str, quantity: int) -> bool:
        """Remove item from barn"""
        item = await self.get_item(barn_id, item_name)
        
        if not item or item.quantity < quantity:
            return False
        
        item.quantity -= quantity
        
        if item.quantity == 0:
            await self.session.delete(item)
        
        await self.session.commit()
        return True
    
    async def get_quantity(self, barn_id: int, item_name: str) -> int:
        """Get quantity of specific item"""
        item = await self.get_item(barn_id, item_name)
        return item.quantity if item else 0
    
    async def has_item(self, barn_id: int, item_name: str, quantity: int = 1) -> bool:
        """Check if barn has enough of item"""
        item_qty = await self.get_quantity(barn_id, item_name)
        return item_qty >= quantity
    
    async def get_total_items(self, barn_id: int) -> int:
        """Get total number of items in barn"""
        items = await self.get_items(barn_id)
        return sum(item.quantity for item in items)
    
    async def expand_capacity(self, user_id: int, amount: int):
        """Expand barn capacity"""
        barn = await self.get_by_user_id(user_id)
        if barn:
            barn.capacity += amount
            await self.session.commit()
