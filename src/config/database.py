"""
Database Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DatabaseSettings(BaseSettings):
    """Database-specific settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Connection Pool
    POOL_SIZE: int = Field(default=20, alias="DB_POOL_SIZE")
    MAX_OVERFLOW: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    POOL_TIMEOUT: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    POOL_RECYCLE: int = Field(default=3600, alias="DB_POOL_RECYCLE")
    
    # Query Timeout
    QUERY_TIMEOUT: int = Field(default=30, alias="DB_QUERY_TIMEOUT")
    
    # Echo SQL (debug)
    ECHO: bool = Field(default=False, alias="DB_ECHO")


database_settings = DatabaseSettings()
