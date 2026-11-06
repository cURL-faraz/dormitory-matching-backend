from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",               # where to read local values from
        env_file_encoding="utf-8",
        extra="ignore",
    )
    APP_ENV: Literal["development", "test", "production"] = "development"
    DATABASE_URL: str


@lru_cache                             # build Settings once; later calls reuse the same object
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
