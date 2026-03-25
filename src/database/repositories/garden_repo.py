"""
Garden Repository
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.garden import Garden, GardenPlot
from src.database.repositories.base import BaseRepository


class GardenRepository(BaseRepository[Garden]):
    """Garden repository"""
    
    def __init__(self, session: AsyncSession = None):
        super().__init__(Garden, session)
    
    async def get_by_user_id(self, user_id: int) -> Optional[Garden]:
        """Get garden by user ID"""
        result = await self.session.execute(
            select(Garden).where(Garden.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_for_user(self, user_id: int) -> Garden:
        """Create garden for user"""
        return await self.create(user_id=user_id)
    
    async def get_plot(self, garden_id: int, plot_number: int) -> Optional[GardenPlot]:
        """Get specific plot in garden"""
        result = await self.session.execute(
            select(GardenPlot)
            .where(
                GardenPlot.garden_id == garden_id,
                GardenPlot.plot_number == plot_number
            )
        )
        return result.scalar_one_or_none()
    
    async def get_plots(self, garden_id: int) -> List[GardenPlot]:
        """Get all plots in garden"""
        result = await self.session.execute(
            select(GardenPlot).where(GardenPlot.garden_id == garden_id)
        )
        return result.scalars().all()
    
    async def get_ready_plots(self, garden_id: int) -> List[GardenPlot]:
        """Get plots with ready crops"""
        result = await self.session.execute(
            select(GardenPlot)
            .where(
                GardenPlot.garden_id == garden_id,
                GardenPlot.ready_at <= datetime.utcnow()
            )
        )
        return result.scalars().all()
    
    async def plant_crop(
        self,
        garden_id: int,
        plot_number: int,
        crop_type: str,
        ready_at: datetime
    ) -> GardenPlot:
        """Plant a crop in a plot"""
        plot = GardenPlot(
            garden_id=garden_id,
            plot_number=plot_number,
            crop_type=crop_type,
            planted_at=datetime.utcnow(),
            ready_at=ready_at
        )
        self.session.add(plot)
        await self.session.commit()
        return plot
    
    async def harvest_plot(self, plot_id: int):
        """Remove crop from plot (harvest)"""
        await self.session.execute(
            delete(GardenPlot).where(GardenPlot.id == plot_id)
        )
        await self.session.commit()
    
    async def fertilize_plot(self, plot_id: int, new_ready_at: datetime):
        """Fertilize a plot to reduce grow time"""
        plot = await self.session.get(GardenPlot, plot_id)
        if plot:
            plot.ready_at = new_ready_at
            plot.is_fertilized = True
            await self.session.commit()
    
    async def expand_garden(self, user_id: int, slots: int = 1):
        """Expand garden slots"""
        garden = await self.get_by_user_id(user_id)
        if garden:
            garden.slots = min(garden.slots + slots, garden.max_slots)
            await self.session.commit()
    
    async def change_season(self, user_id: int, season: str):
        """Change garden season"""
        garden = await self.get_by_user_id(user_id)
        if garden:
            garden.season = season
            garden.last_season_change = datetime.utcnow()
            await self.session.commit()
