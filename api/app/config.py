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
    BOT_USERNAME: str = "pvzNT_bot"
    WEBAPP_URL: str = "https://smartsearch-tma.vercel.app"
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
    
    # API Keys & Credentials
    OZON_CLIENT_ID: Optional[str] = None
    OZON_API_KEY: Optional[str] = None
    WB_API_TOKEN: Optional[str] = None
    YANDEX_MARKET_OAUTH_TOKEN: Optional[str] = None
    YANDEX_MARKET_CAMPAIGN_ID: Optional[str] = None
    
    # Southeast Asia & Vietnam Marketplaces (Shopee, Lazada, Shein)
    SHOPEE_PARTNER_ID: Optional[str] = None
    SHOPEE_PARTNER_KEY: Optional[str] = None
    LAZADA_APP_KEY: Optional[str] = None
    LAZADA_APP_SECRET: Optional[str] = None
    SHEIN_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
