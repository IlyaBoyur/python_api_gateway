from typing import Any

from redis.asyncio import ConnectionPool, Redis


class RedisDatabase(Redis):
    def __init__(self, prefix: str, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.prefix = prefix

    @classmethod
    def build(
        cls,
        config: dict,
        encoding: str = "utf8",
        decode_responses: bool = True,
        **kwargs: Any,
    ) -> "RedisDatabase":
        if "dsn" not in config or "prefix" not in config:
            raise ValueError("Missing required configuration values in RedisDatabase")

        connection_pool: ConnectionPool = ConnectionPool.from_url(
            url=config["dsn"],
            encoding=encoding,
            decode_responses=decode_responses,
            **kwargs,
        )
        return cls(prefix=config["prefix"], connection_pool=connection_pool)

    async def clear(self, pattern: str) -> int:
        script = f"""
        local count = 0;
        for i, name in ipairs(redis.call('KEYS', '{self.prefix}:{pattern}'))
        do
            redis.call('DEL', name);
            count = count + 1;
        end
        return count
        """
        return await self.eval(script, numkeys=0)  # type: ignore

    def build_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"
