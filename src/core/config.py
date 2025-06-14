import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import AnyUrl, BaseSettings, RedisDsn, validator

# Project Root Setting
BASE_DIR = Path(__file__).parent.parent.parent


class EnvBaseSettings(BaseSettings):
    class Config(BaseSettings.Config):
        env_file = ".env"
        case_sensitive = False


class AppSettings(EnvBaseSettings):
    name: str = "backend"
    debug: bool = True

    class Config(EnvBaseSettings.Config):
        env_prefix = "app_"


class RedisSettings(EnvBaseSettings):
    scheme: str = "redis"
    user: str = ""
    password: str = ""
    host: str = "localhost"
    port: str = "6379"
    path: str = ""
    dsn: RedisDsn | str = ""
    prefix: str = "main"

    class Config(EnvBaseSettings.Config):
        env_prefix = "redis_"

    @validator("dsn", pre=True)
    def assemble_dsn(cls, v: str | None, values: dict[str, Any]) -> str:
        if isinstance(v, str) and len(v) > 1:
            return v
        return RedisDsn.build(
            scheme=values["scheme"],
            user=values.get("user"),
            password=values.get("password"),
            host=values["host"],
            port=values.get("port"),
            path=f"/{values.get('path')}",
        )


class ElasticsearchDsn(AnyUrl):
    allowed_schemes = {"http", "https"}
    user_required = True


class ElasticsearchSettings(EnvBaseSettings):
    scheme: str = "http"
    host: str = "127.0.0.1"
    port: str = "9200"
    dsn: ElasticsearchDsn | str = ""
    timeout: int = 25

    class Config(EnvBaseSettings.Config):
        env_prefix = "elastic_"

    @validator("dsn", pre=True)
    def assemble_dsn(cls, v: str | None, values: dict[str, Any]) -> str:
        if isinstance(v, str) and len(v) > 1:
            return v
        return ElasticsearchDsn.build(
            scheme=values["scheme"],
            host=values["host"],
            port=values["port"],
        )


class LoggingSettings(EnvBaseSettings):
    serializer: bool = False
    level: str = "INFO"

    class Config(EnvBaseSettings.Config):
        env_prefix = "logging_"


class Settings(EnvBaseSettings):
    app: AppSettings = AppSettings()
    base_dir: Path = BASE_DIR
    redis: RedisSettings = RedisSettings()
    es: ElasticsearchSettings = ElasticsearchSettings()
    logger: LoggingSettings = LoggingSettings()
