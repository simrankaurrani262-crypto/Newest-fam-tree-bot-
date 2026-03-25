"""
Base Repository Pattern
"""
from typing import TypeVar, Generic, Type, List, Optional, Any

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession = None):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> ModelType:
        """Create new entity"""
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        """Update entity by ID"""
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: Any) -> bool:
        """Delete entity by ID"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def exists(self, id: Any) -> bool:
        """Check if entity exists"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None
