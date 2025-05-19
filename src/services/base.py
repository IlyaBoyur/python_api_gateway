import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from json import JSONDecodeError
from typing import Generic, Protocol, TypeVar

from loguru import logger
from pydantic import BaseModel, ValidationError, parse_obj_as

from src.common.exceptions import ServiceError
from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.common.search_engine.filtersets import AsyncFilterSet

T = TypeVar("T", bound=BaseModel)
FilterSchema = TypeVar("FilterSchema", bound=BaseModel, contravariant=True)  # noqa: PLC0105


ERROR_FAILED_TO_PARSE_CACHE_DATA = "Failed to parse Cache data for object_id: {object_id}"
ERROR_FAILED_TO_WRITE_TO_CACHE = "Failed to write to Cache for object_id: {object_id}"


class IEntityService(ABC, Generic[T, FilterSchema]):
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        ...

    @abstractmethod
    async def get_multi(self, filters: FilterSchema) -> list[T]:
        ...


class BaseEntityService(IEntityService[T, FilterSchema], Generic[T, FilterSchema]):
    """Base entity service class."""

    schema: type[T]
    filter_set: AsyncFilterSet

    def __init__(
        self,
        key_value_database: IKeyValueDatabase,
        search_engine: ISearchEngine,
        index: str,
        cache_expire_secs: int,
    ):
        self.key_value_database = key_value_database
        self.search_engine = search_engine
        self.index = index
        self.cache_expire_secs = cache_expire_secs

    async def get_by_id(self, entity_id: str) -> T | None:
        entity = await self._entity_from_cache(entity_id)
        if not entity:
            entity = await self._get_entity_from_search_engine(entity_id)
            if not entity:
                return None
            await self._put_entity_to_cache(entity, self.cache_expire_secs)
        return entity

    async def get_multi(self, filters: FilterSchema) -> list[T]:
        filter_set = self.filter_set()
        search_query = filter_set.filter_query(filters.dict(exclude_none=True))
        result = await self.search_engine.search(index=self.index, params=search_query)
        return [self.schema(**doc) for doc in result]

    async def _get_entity_from_search_engine(self, entity_id: str) -> T | None:
        doc = await self.search_engine.get_document(index=self.index, doc_id=entity_id)
        if doc:
            return self.schema(**doc)
        return None

    async def _entity_from_cache(self, entity_id: str) -> T | None:
        raw = await self.key_value_database.get(entity_id)
        if not raw:
            return None
        try:
            return parse_obj_as(self.schema, raw)
        except (JSONDecodeError, KeyError, TypeError, ValidationError) as error:
            logger.error(ERROR_FAILED_TO_PARSE_CACHE_DATA, object_id=entity_id)
            raise ServiceError from error
        return None

    async def _put_entity_to_cache(self, entity: T, expire_secs: int) -> None:
        try:
            await self.key_value_database.set(entity.id, entity.json(), expire=expire_secs)
        except Exception as error:
            logger.error(ERROR_FAILED_TO_WRITE_TO_CACHE, object_id=entity.id)
            raise ServiceError from error
