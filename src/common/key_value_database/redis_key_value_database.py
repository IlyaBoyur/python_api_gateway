from src.common.key_value_database.interfaces import IKeyValueDatabase
from src.common.key_value_database.redis import RedisDatabase


class RedisKeyValueDatabase(IKeyValueDatabase):
    def __init__(self, redis: RedisDatabase):
        self.redis = redis

    async def get_with_ttl(self, key: str) -> tuple[int, str]:
        key = self.redis.build_key(key)
        async with self.redis.pipeline(transaction=True) as pipe:
            return await pipe.ttl(key).get(key).execute()

    async def get(self, key: str) -> str | None:
        return await self.redis.get(self.redis.build_key(key))

    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        await self.redis.set(self.redis.build_key(key), value, ex=expire)

    async def delete(self, key: str) -> int:
        return await self.redis.delete(self.redis.build_key(key))

    async def clear(self, pattern: str) -> int:
        return await self.redis.clear(pattern)
