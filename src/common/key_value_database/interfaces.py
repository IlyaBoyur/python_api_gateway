import abc


class IKeyValueDatabase(abc.ABC):
    @abc.abstractmethod
    async def get_with_ttl(self, key: str) -> tuple[int, str | None]:
        ...

    @abc.abstractmethod
    async def get(self, key: str) -> str | None:
        ...

    @abc.abstractmethod
    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        ...

    @abc.abstractmethod
    async def delete(self, key: str) -> int:
        ...

    @abc.abstractmethod
    async def clear(self, pattern: str) -> int:
        ...
