"""
Combat Service
"""
import random
from decimal import Decimal
from typing import Optional

from src.database.repositories.economy_repo import EconomyRepository
from src.database.repositories.weapon_repo import WeaponRepository
from src.database.connection import get_session
from src.core.constants import WEAPONS
from src.core.exceptions import (
    CombatError,
    UserDeadError,
    WeaponNotOwnedError,
    LimitExceededError
)


class CombatService:
    """Combat service for PvP"""
    
    async def get_equipped_weapon(self, user_id: int) -> Optional[dict]:
        """Get user's equipped weapon"""
        async for session in get_session():
            repo = EconomyRepository(session)
            economy = await repo.get_by_user_id(user_id)
            
            if not economy or not economy.equipped_weapon:
                return WEAPONS["punch"]  # Default weapon
            
            return WEAPONS.get(economy.equipped_weapon, WEAPONS["punch"])
    
    async def equip_weapon(self, user_id: int, weapon_name: str):
        """Equip a weapon"""
        async for session in get_session():
            weapon_repo = WeaponRepository(session)
            
            # Check if user owns weapon
            if not await weapon_repo.has_weapon(user_id, weapon_name):
                raise WeaponNotOwnedError("You don't own this weapon!")
            
            # Unequip current weapon
            await weapon_repo.unequip_all(user_id)
            
            # Equip new weapon
            await weapon_repo.equip_weapon(user_id, weapon_name)
            
            # Update economy
            economy_repo = EconomyRepository(session)
            await economy_repo.set_weapon(user_id, weapon_name)
    
    async def buy_weapon(self, user_id: int, weapon_name: str):
        """Buy a weapon"""
        async for session in get_session():
            weapon_repo = WeaponRepository(session)
            economy_repo = EconomyRepository(session)
            
            # Get weapon info
            weapon = WEAPONS.get(weapon_name)
            if not weapon:
                raise CombatError("Invalid weapon!")
            
            # Check if already owned
            if await weapon_repo.has_weapon(user_id, weapon_name):
                raise CombatError("You already own this weapon!")
            
            # Check funds
            economy = await economy_repo.get_by_user_id(user_id)
            if economy.balance < Decimal(str(weapon["price"])):
                raise CombatError("Insufficient funds!")
            
            # Deduct money and add weapon
            await economy_repo.deduct_money(user_id, Decimal(str(weapon["price"])))
            await weapon_repo.add_weapon(user_id, weapon_name)
    
    async def rob(
        self,
        robber_id: int,
        target_id: int
    ) -> dict:
        """
        Attempt to rob a user
        
        Returns:
            dict with success, amount, message
        """
        async for session in get_session():
            economy_repo = EconomyRepository(session)
            
            # Check if robber is alive
            robber = await economy_repo.get_by_user_id(robber_id)
            if robber.health <= 0:
                raise UserDeadError("You are dead! Use /medical to revive.")
            
            # Check daily limit
            if robber.robbery_count_today >= 8:
                raise LimitExceededError("You've used all 8 robbery attempts today!")
            
            # Get equipped weapon
            weapon = await self.get_equipped_weapon(robber_id)
            
            # Calculate success chance
            base_chance = 50
            weapon_bonus = weapon["rob_power"] / 10
            success_chance = min(95, base_chance + weapon_bonus)
            
            # Roll for success
            roll = random.randint(1, 100)
            
            if roll <= success_chance:
                # Success!
                target = await economy_repo.get_by_user_id(target_id)
                
                # Calculate steal amount (10% or $200 max, $1000 if rich)
                steal_percent = Decimal("0.1")
                steal_amount = min(
                    Decimal("200"),
                    target.balance * steal_percent
                )
                
                if target.balance > 10000:  # Rich target
                    steal_amount = min(Decimal("1000"), target.balance * steal_percent)
                
                # Transfer money
                await economy_repo.transfer(target_id, robber_id, steal_amount)
                
                # Increment robbery count
                await economy_repo.increment_robbery_count(robber_id)
                
                return {
                    "success": True,
                    "amount": steal_amount,
                    "message": f"You successfully robbed ${steal_amount}!"
                }
            else:
                # Failed
                await economy_repo.increment_robbery_count(robber_id)
                
                return {
                    "success": False,
                    "amount": Decimal("0"),
                    "message": "Robbery failed! The target got away."
                }
    
    async def kill(
        self,
        killer_id: int,
        target_id: int
    ) -> dict:
        """
        Attempt to kill a user
        
        Returns:
            dict with success, reward, message
        """
        async for session in get_session():
            economy_repo = EconomyRepository(session)
            
            # Check if killer is alive
            killer = await economy_repo.get_by_user_id(killer_id)
            if killer.health <= 0:
                raise UserDeadError("You are dead! Use /medical to revive.")
            
            # Check daily limit
            if killer.kill_count_today >= 5:
                raise LimitExceededError("You've used all 5 kill attempts today!")
            
            # Get equipped weapon
            weapon = await self.get_equipped_weapon(killer_id)
            
            # Calculate kill chance
            base_chance = 30
            weapon_bonus = weapon["kill_power"] / 10
            success_chance = min(95, base_chance + weapon_bonus)
            
            # Roll for success
            roll = random.randint(1, 100)
            
            if roll <= success_chance:
                # Success!
                reward = Decimal("100")
                
                # Kill target
                await economy_repo.update_health(target_id, 0)
                
                # Give reward
                await economy_repo.add_money(killer_id, reward)
                
                # Increment kill count
                await economy_repo.increment_kill_count(killer_id)
                
                return {
                    "success": True,
                    "reward": reward,
                    "message": f"You killed the target and got ${reward}!"
                }
            else:
                # Failed - reputation loss
                await economy_repo.update_reputation(killer_id, -5)
                await economy_repo.increment_kill_count(killer_id)
                
                return {
                    "success": False,
                    "reward": Decimal("0"),
                    "message": "Kill failed! You lost some reputation."
                }
    
    async def donate_blood(
        self,
        donor_id: int,
        target_id: int
    ) -> dict:
        """Donate blood to revive someone"""
        async for session in get_session():
            economy_repo = EconomyRepository(session)
            
            # Check if donor is alive
            donor = await economy_repo.get_by_user_id(donor_id)
            if donor.health <= 0:
                raise UserDeadError("You are dead! Use /medical to revive.")
            
            # Check if target is dead
            target = await economy_repo.get_by_user_id(target_id)
            if target.health > 0:
                return {
                    "success": False,
                    "message": "Target is already alive!"
                }
            
            # Revive target with 1 health
            await economy_repo.update_health(target_id, 1)
            
            # Give donor reputation
            await economy_repo.update_reputation(donor_id, 10)
            
            return {
                "success": True,
                "message": "You donated blood and revived the target! +10 reputation"
            }
