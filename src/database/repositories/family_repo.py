"""
Family Repository
"""
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.family import Family, FamilyRelation, RelationType
from src.database.repositories.base import BaseRepository


class FamilyRepository(BaseRepository[Family]):
    """Family repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Family, session)
    
    async def get_relations(self, user_id: int) -> List[FamilyRelation]:
        """Get all family relations for user"""
        result = await self.session.execute(
            select(FamilyRelation).where(FamilyRelation.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_spouses(self, user_id: int) -> List[FamilyRelation]:
        """Get user's spouses"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.SPOUSE
            )
        )
        return result.scalars().all()
    
    async def get_children(self, user_id: int) -> List[FamilyRelation]:
        """Get user's children"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.CHILD
            )
        )
        return result.scalars().all()
    
    async def get_parents(self, user_id: int) -> List[FamilyRelation]:
        """Get user's parents"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.PARENT
            )
        )
        return result.scalars().all()
    
    async def get_siblings(self, user_id: int) -> List[FamilyRelation]:
        """Get user's siblings"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.SIBLING
            )
        )
        return result.scalars().all()
    
    async def has_parent(self, user_id: int) -> bool:
        """Check if user has a parent"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.PARENT
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_children_count(self, user_id: int) -> int:
        """Get number of children"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.CHILD
            )
        )
        return len(result.scalars().all())
    
    async def get_spouses_count(self, user_id: int) -> int:
        """Get number of spouses"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.relation_type == RelationType.SPOUSE
            )
        )
        return len(result.scalars().all())
    
    async def are_married(self, user_id1: int, user_id2: int) -> bool:
        """Check if two users are married"""
        result = await self.session.execute(
            select(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id1,
                FamilyRelation.related_user_id == user_id2,
                FamilyRelation.relation_type == RelationType.SPOUSE
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def create_relation(
        self,
        user_id: int,
        related_user_id: int,
        relation_type: RelationType
    ) -> FamilyRelation:
        """Create a family relation"""
        relation = FamilyRelation(
            user_id=user_id,
            related_user_id=related_user_id,
            relation_type=relation_type
        )
        self.session.add(relation)
        await self.session.commit()
        return relation
    
    async def create_bidirectional_relation(
        self,
        user_id1: int,
        user_id2: int,
        relation_type: RelationType
    ):
        """Create bidirectional relation (spouse, sibling)"""
        # Create both directions
        await self.create_relation(user_id1, user_id2, relation_type)
        await self.create_relation(user_id2, user_id1, relation_type)
    
    async def remove_relation(self, user_id: int, related_user_id: int):
        """Remove a family relation"""
        await self.session.execute(
            delete(FamilyRelation)
            .where(
                FamilyRelation.user_id == user_id,
                FamilyRelation.related_user_id == related_user_id
            )
        )
        await self.session.commit()
    
    async def remove_bidirectional_relation(self, user_id1: int, user_id2: int):
        """Remove bidirectional relation"""
        await self.remove_relation(user_id1, user_id2)
        await self.remove_relation(user_id2, user_id1)
    
    async def divorce(self, user_id: int, spouse_id: int):
        """Divorce two users"""
        await self.remove_bidirectional_relation(user_id, spouse_id)
