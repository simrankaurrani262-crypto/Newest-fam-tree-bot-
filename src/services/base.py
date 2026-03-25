"""
Base Service Class
"""
from typing import Generic, TypeVar

from src.database.connection import get_session

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Base service with common functionality"""
    
    def __init__(self):
        pass
    
    async def get_session(self):
        """Get database session"""
        async for session in get_session():
            return session
