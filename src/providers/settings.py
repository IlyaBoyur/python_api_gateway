from functools import lru_cache

from pydantic import BaseSettings

from src.core.config import Settings

app_settings = Settings()


@lru_cache
def get_settings() -> BaseSettings:
    return app_settings
