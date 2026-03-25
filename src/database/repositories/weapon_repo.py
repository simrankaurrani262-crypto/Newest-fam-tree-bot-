"""
Weapon Repository
"""
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.weapon import Weapon, UserWeapon
from src.database.repositories.base import BaseRepository


class WeaponRepository(BaseRepository[Weapon]):
    """Weapon repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Weapon, session)
    
    async def get_by_name(self, name: str) -> Optional[Weapon]:
        """Get weapon by name"""
        result = await self.session.execute(
            select(Weapon).where(Weapon.name == name)
        )
        return result.scalar_one_or_none()
    
    async def has_weapon(self, user_id: int, weapon_name: str) -> bool:
        """Check if user has weapon"""
        result = await self.session.execute(
            select(UserWeapon)
            .join(Weapon)
            .where(
                UserWeapon.user_id == user_id,
                Weapon.name == weapon_name
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def add_weapon(self, user_id: int, weapon_name: str):
        """Add weapon to user"""
        weapon = await self.get_by_name(weapon_name)
        if weapon:
            user_weapon = UserWeapon(
                user_id=user_id,
                weapon_id=weapon.id
            )
            self.session.add(user_weapon)
            await self.session.commit()
    
    async def equip_weapon(self, user_id: int, weapon_name: str):
        """Equip a weapon"""
        weapon = await self.get_by_name(weapon_name)
        if weapon:
            await self.session.execute(
                update(UserWeapon)
                .where(
                    UserWeapon.user_id == user_id,
                    UserWeapon.weapon_id == weapon.id
                )
                .values(equipped=True)
            )
            await self.session.commit()
    
    async def unequip_all(self, user_id: int):
        """Unequip all weapons for user"""
        await self.session.execute(
            update(UserWeapon)
            .where(UserWeapon.user_id == user_id)
            .values(equipped=False)
        )
        await self.session.commit()
    
    async def get_user_weapons(self, user_id: int) -> List[UserWeapon]:
        """Get all user's weapons"""
        result = await self.session.execute(
            select(UserWeapon)
            .where(UserWeapon.user_id == user_id)
        )
        return result.scalars().all()
