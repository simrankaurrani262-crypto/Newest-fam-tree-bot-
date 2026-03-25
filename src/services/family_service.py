"""
Family Service
"""
import random
from typing import List, Optional

from src.database.models.family import FamilyRelation, RelationType
from src.database.models.user import User
from src.database.repositories.family_repo import FamilyRepository
from src.database.repositories.user_repo import UserRepository
from src.database.connection import get_session
from src.core.constants import SYSTEM_LIMITS
from src.core.exceptions import (
    FamilyError,
    AlreadyMarriedError,
    MaxChildrenError,
    MaxPartnersError,
    HasParentError,
    SelfRelationError,
    BlockedError
)


class FamilyService:
    """Family service"""
    
    async def validate_adoption(self, parent_id: int, child_id: int):
        """Validate adoption request"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            # Check self-adoption
            if parent_id == child_id:
                raise SelfRelationError("You cannot adopt yourself!")
            
            # Check if child already has parent
            if await family_repo.has_parent(child_id):
                raise HasParentError("This user already has a parent!")
            
            # Check max children limit
            children_count = await family_repo.get_children_count(parent_id)
            if children_count >= SYSTEM_LIMITS["max_children"]:
                raise MaxChildrenError(
                    f"You already have {SYSTEM_LIMITS['max_children']} children (max limit)!"
                )
    
    async def adopt(self, parent_id: int, child_id: int) -> FamilyRelation:
        """Adopt a user as child"""
        await self.validate_adoption(parent_id, child_id)
        
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            # Create parent-child relation
            relation = await family_repo.create_relation(
                parent_id, child_id, RelationType.CHILD
            )
            
            # Create child-parent relation (reverse)
            await family_repo.create_relation(
                child_id, parent_id, RelationType.PARENT
            )
            
            return relation
    
    async def validate_marriage(self, user_id: int, partner_id: int):
        """Validate marriage request"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            # Check self-marriage
            if user_id == partner_id:
                raise SelfRelationError("You cannot marry yourself!")
            
            # Check if already married to each other
            if await family_repo.are_married(user_id, partner_id):
                raise AlreadyMarriedError("You are already married to this user!")
            
            # Check max partners limit
            spouses_count = await family_repo.get_spouses_count(user_id)
            if spouses_count >= SYSTEM_LIMITS["max_partners"]:
                raise MaxPartnersError(
                    f"You already have {SYSTEM_LIMITS['max_partners']} partners (max limit)!"
                )
            
            partner_spouses = await family_repo.get_spouses_count(partner_id)
            if partner_spouses >= SYSTEM_LIMITS["max_partners"]:
                raise MaxPartnersError(
                    "This user has reached the maximum number of partners!"
                )
    
    async def marry(self, user_id: int, partner_id: int):
        """Marry two users"""
        await self.validate_marriage(user_id, partner_id)
        
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            # Create bidirectional spouse relation
            await family_repo.create_bidirectional_relation(
                user_id, partner_id, RelationType.SPOUSE
            )
    
    async def divorce(self, user_id: int, spouse_id: int):
        """Divorce two users"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            await family_repo.divorce(user_id, spouse_id)
    
    async def get_spouses(self, user_id: int) -> List[FamilyRelation]:
        """Get user's spouses"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            return await family_repo.get_spouses(user_id)
    
    async def get_children(self, user_id: int) -> List[FamilyRelation]:
        """Get user's children"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            return await family_repo.get_children(user_id)
    
    async def get_parents(self, user_id: int) -> List[FamilyRelation]:
        """Get user's parents"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            return await family_repo.get_parents(user_id)
    
    async def get_siblings(self, user_id: int) -> List[FamilyRelation]:
        """Get user's siblings"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            return await family_repo.get_siblings(user_id)
    
    async def get_family_tree(self, user_id: int) -> dict:
        """Get family tree data"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            user_repo = UserRepository(session)
            
            tree = {
                "user": user_id,
                "spouses": [],
                "children": [],
                "parents": [],
                "siblings": []
            }
            
            # Get spouses
            spouses = await family_repo.get_spouses(user_id)
            for s in spouses:
                user = await user_repo.get_by_id(s.related_user_id)
                if user:
                    tree["spouses"].append({
                        "id": user.id,
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "name": user.display_name
                    })
            
            # Get children
            children = await family_repo.get_children(user_id)
            for c in children:
                user = await user_repo.get_by_id(c.related_user_id)
                if user:
                    tree["children"].append({
                        "id": user.id,
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "name": user.display_name
                    })
            
            # Get parents
            parents = await family_repo.get_parents(user_id)
            for p in parents:
                user = await user_repo.get_by_id(p.related_user_id)
                if user:
                    tree["parents"].append({
                        "id": user.id,
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "name": user.display_name
                    })
            
            # Get siblings
            siblings = await family_repo.get_siblings(user_id)
            for s in siblings:
                user = await user_repo.get_by_id(s.related_user_id)
                if user:
                    tree["siblings"].append({
                        "id": user.id,
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "name": user.display_name
                    })
            
            return tree
    
    async def disown(self, parent_id: int, child_id: int):
        """Disown a child"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            # Remove both directions
            await family_repo.remove_relation(parent_id, child_id)
            await family_repo.remove_relation(child_id, parent_id)
    
    async def runaway(self, child_id: int):
        """Self-disown from parent"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            # Get parents
            parents = await family_repo.get_parents(child_id)
            
            # Remove relations with all parents
            for parent in parents:
                await family_repo.remove_relation(child_id, parent.related_user_id)
                await family_repo.remove_relation(parent.related_user_id, child_id)
    
    async def make_siblings(self, user_id1: int, user_id2: int):
        """Make two users siblings"""
        async for session in get_session():
            family_repo = FamilyRepository(session)
            
            await family_repo.create_bidirectional_relation(
                user_id1, user_id2, RelationType.SIBLING
            )
