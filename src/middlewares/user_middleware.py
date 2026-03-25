"""
User Middleware
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.database.repositories.user_repo import UserRepository
from src.database.connection import get_session


class UserMiddleware(BaseMiddleware):
    """Ensure user exists in database"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        user = None
        
        if isinstance(event, (Message, CallbackQuery)):
            tg_user = event.from_user
            
            async for session in get_session():
                repo = UserRepository(session)
                user = await repo.get_by_telegram_id(tg_user.id)
                
                if not user:
                    # Create new user
                    user = await repo.create_from_telegram_user(tg_user)
                    
                    # Create related records
                    from src.database.repositories.economy_repo import EconomyRepository
                    from src.database.repositories.garden_repo import GardenRepository
                    from src.database.repositories.barn_repo import BarnRepository
                    
                    economy_repo = EconomyRepository(session)
                    await economy_repo.create_for_user(user.id)
                    
                    garden_repo = GardenRepository(session)
                    await garden_repo.create_for_user(user.id)
                    
                    barn_repo = BarnRepository(session)
                    await barn_repo.create_for_user(user.id)
                
                # Update last active
                await repo.update_last_active(tg_user.id)
        
        # Add user to data
        data["db_user"] = user
        
        return await handler(event, data)
