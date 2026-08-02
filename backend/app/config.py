from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartSearch TMA API"
    VERSION: str = "1.0.0"
    
    # DB
    DATABASE_URL: str = "postgresql+asyncpg://smartsearch_user:smartsearch_password_secure@localhost:5432/smartsearch_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Telegram Bot
    BOT_TOKEN: str = ""
    WEBHOOK_URL: Optional[str] = None
    
    # Security
    JWT_SECRET: str = "default_jwt_secret_change_in_prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Vector & Search DBs
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    MEILISEARCH_HOST: str = "http://localhost:7700"
    MEILI_MASTER_KEY: str = "master_key"
    
    # API Keys
    OZON_CLIENT_ID: Optional[str] = None
    OZON_API_KEY: Optional[str] = None
    WB_API_TOKEN: Optional[str] = None
    YANDEX_MARKET_OAUTH_TOKEN: Optional[str] = None
    YANDEX_MARKET_CAMPAIGN_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
