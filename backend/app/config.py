import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict  # ✅ Required for Pydantic v2

class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    GENAI_MODEL: str = "gemini-pro"
    REDIS_URL: str = "redis://localhost:6379"

    # ✅ Replaces old `Config` class
    model_config = ConfigDict(env_file=".env")  # Automatically loads from .env

# ✅ Singleton instance to be imported across the app
settings = Settings()
