from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",          # untuk lokal saja
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def Config() -> Settings:
    return Settings()
