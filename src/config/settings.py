"""
Main Settings Configuration
"""
import os
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with proper environment variable loading"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
        case_sensitive=False
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", alias="ENVIRONMENT")
    DEBUG: bool = Field(default=True, alias="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Bot
    BOT_TOKEN_ALPHA: str = Field(default="", alias="BOT_TOKEN_ALPHA")
    BOT_TOKEN_BETA: str = Field(default="", alias="BOT_TOKEN_BETA")
    BOT_NAME_ALPHA: str = Field(default="fam_tree_bot", alias="BOT_NAME_ALPHA")
    BOT_NAME_BETA: str = Field(default="famtreebbot", alias="BOT_NAME_BETA")
    
    # Database - Use environment variable first, fallback to constructed URL
    DATABASE_URL: str = Field(default="", alias="DATABASE_URL")
    DB_HOST: str = Field(default="localhost", alias="DB_HOST")
    DB_PORT: int = Field(default=5432, alias="DB_PORT")
    DB_NAME: str = Field(default="famtreebot", alias="DB_NAME")
    DB_USER: str = Field(default="famtree_user", alias="DB_USER")
    DB_PASSWORD: str = Field(default="", alias="DB_PASSWORD")
    
    # Database SSL (required for Render PostgreSQL)
    DB_SSL_MODE: str = Field(default="require", alias="DB_SSL_MODE")
    DB_SSL_ROOT_CERT: Optional[str] = Field(default=None, alias="DB_SSL_ROOT_CERT")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(default=0, alias="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND")
    CELERY_WORKER_CONCURRENCY: int = Field(default=4, alias="CELERY_WORKER_CONCURRENCY")
    
    # Webhook
    WEBHOOK_HOST: str = Field(default="", alias="WEBHOOK_HOST")
    WEBHOOK_PATH: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    WEBHOOK_PORT: int = Field(default=8443, alias="WEBHOOK_PORT")
    WEBHOOK_SECRET: str = Field(default="", alias="WEBHOOK_SECRET")
    
    # AI/ML
    OPENAI_API_KEY: str = Field(default="", alias="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: str = Field(default="", alias="HUGGINGFACE_API_KEY")
    AI_ENABLED: bool = Field(default=False, alias="AI_ENABLED")
    
    # Blockchain
    ETHEREUM_RPC_URL: str = Field(default="", alias="ETHEREUM_RPC_URL")
    POLYGON_RPC_URL: str = Field(default="", alias="POLYGON_RPC_URL")
    SOLANA_RPC_URL: str = Field(default="", alias="SOLANA_RPC_URL")
    BLOCKCHAIN_ENABLED: bool = Field(default=False, alias="BLOCKCHAIN_ENABLED")
    NFT_CONTRACT_ETH: str = Field(default="", alias="NFT_CONTRACT_ETH")
    NFT_CONTRACT_POLYGON: str = Field(default="", alias="NFT_CONTRACT_POLYGON")
    
    def model_post_init(self, __context):
        """Post-initialization to construct DATABASE_URL if not provided"""
        super().model_post_init(__context)
        
        # If DATABASE_URL is not set, construct it from individual components
        if not self.DATABASE_URL:
            if self.DB_PASSWORD:
                self.DATABASE_URL = (
                    f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
                    f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                )
            else:
                # Fallback for local development
                self.DATABASE_URL = (
                    f"postgresql+asyncpg://{self.DB_USER}@{self.DB_HOST}"
                    f":{self.DB_PORT}/{self.DB_NAME}"
                )
        
        # Add SSL parameters for Render PostgreSQL if needed
        if "render.com" in self.DATABASE_URL and "ssl" not in self.DATABASE_URL:
            ssl_param = "?ssl=require"
            if self.DB_SSL_ROOT_CERT:
                ssl_param = f"?sslmode=verify-ca&sslrootcert={self.DB_SSL_ROOT_CERT}"
            self.DATABASE_URL += ssl_param


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
    
