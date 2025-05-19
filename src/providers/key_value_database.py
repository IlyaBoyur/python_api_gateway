from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.common.key_value_database.interfaces import IKeyValueDatabase
from src.common.key_value_database.redis_key_value_database import (
    RedisDatabase,
    RedisKeyValueDatabase,
)

redis_database: RedisDatabase = None


@lru_cache
def get_redis_database() -> RedisDatabase:
    return redis_database


@lru_cache
def get_key_value_database(
    redis: Annotated[RedisDatabase, Depends(get_redis_database)],
) -> IKeyValueDatabase:
    return RedisKeyValueDatabase(redis=redis)
