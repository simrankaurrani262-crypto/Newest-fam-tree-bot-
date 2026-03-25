"""
Garden Service
"""
from datetime import datetime, timedelta
from typing import List, Optional

from src.database.repositories.garden_repo import GardenRepository
from src.database.repositories.barn_repo import BarnRepository
from src.database.connection import get_session
from src.core.constants import CROPS, SEASON_BONUS


class GardenService:
    """Garden service"""
    
    async def get_garden(self, user_id: int) -> Optional[dict]:
        """Get garden data"""
        async for session in get_session():
            garden_repo = GardenRepository(session)
            garden = await garden_repo.get_by_user_id(user_id)
            
            if not garden:
                garden = await garden_repo.create_for_user(user_id)
            
            plots = await garden_repo.get_plots(garden.user_id)
            
            return {
                "user_id": garden.user_id,
                "slots": garden.slots,
                "max_slots": garden.max_slots,
                "season": garden.season,
                "plots": [
                    {
                        "id": p.id,
                        "plot_number": p.plot_number,
                        "crop_type": p.crop_type,
                        "is_empty": p.is_empty,
                        "is_ready": p.is_ready,
                        "time_remaining": p.time_remaining
                    }
                    for p in plots
                ]
            }
    
    async def plant_crop(
        self,
        user_id: int,
        plot_number: int,
        crop_type: str
    ) -> dict:
        """Plant a crop"""
        async for session in get_session():
            garden_repo = GardenRepository(session)
            barn_repo = BarnRepository(session)
            
            garden = await garden_repo.get_by_user_id(user_id)
            barn = await barn_repo.get_by_user_id(user_id)
            
            # Check if has seeds
            if not await barn_repo.has_item(barn.id, crop_type, 1):
                raise ValueError(f"No {crop_type} seeds in barn!")
            
            crop = CROPS[crop_type]
            
            # Calculate grow time
            grow_hours = crop["growth_hours"]
            
            # Season bonus
            if garden.season == crop["season"] or crop["season"] == "all":
                grow_hours /= SEASON_BONUS
            
            ready_at = datetime.utcnow() + timedelta(hours=grow_hours)
            
            # Remove seed from barn
            await barn_repo.remove_item(barn.id, crop_type, 1)
            
            # Plant
            plot = await garden_repo.plant_crop(
                garden.user_id,
                plot_number,
                crop_type,
                ready_at
            )
            
            return {
                "plot_id": plot.id,
                "crop_type": crop_type,
                "ready_at": ready_at
            }
    
    async def harvest_all(self, user_id: int) -> dict:
        """Harvest all ready crops"""
        async for session in get_session():
            garden_repo = GardenRepository(session)
            barn_repo = BarnRepository(session)
            
            garden = await garden_repo.get_by_user_id(user_id)
            plots = await garden_repo.get_plots(garden.user_id)
            
            harvested = {}
            
            for plot in plots:
                if plot.is_ready:
                    crop_type = plot.crop_type
                    
                    # Add to barn
                    barn = await barn_repo.get_by_user_id(user_id)
                    await barn_repo.add_item(barn.id, crop_type, 1, "crop")
                    
                    harvested[crop_type] = harvested.get(crop_type, 0) + 1
                    
                    # Remove plot
                    await garden_repo.harvest_plot(plot.id)
            
            return {"harvested": harvested}
    
    async def change_season(self, user_id: int, season: str):
        """Change garden season"""
        async for session in get_session():
            garden_repo = GardenRepository(session)
            await garden_repo.change_season(user_id, season)
