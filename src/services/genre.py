from functools import lru_cache

from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.common.search_engine.filter_fields import (
    Filter,
    InFilter,
    LimitOffsetFilter,
    NotInFilter,
    OrderingField,
    OrderingFilter,
    RangeFilter,
    SearchFilter,
)
from src.common.search_engine.filtersets import AsyncFilterSet
from src.models.base import BaseSchema
from src.models.genre import Genre, GenreFilterSchema

from .base import BaseEntityService

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5
GENRE_INDEX = "genres"


class GenreFilterSet(AsyncFilterSet):
    id = Filter("id")
    ids = InFilter("id")
    excluded_ids = NotInFilter("id")
    name = SearchFilter("name")
    description = SearchFilter("description")
    pagination = LimitOffsetFilter("pagination")
    order = OrderingFilter(
        id=OrderingField("id"),
        name=OrderingField("name.raw"),
    )


class GenreService(BaseEntityService[Genre, GenreFilterSchema]):
    """Cодержит бизнес-логику по работе с жанрами."""

    schema: type[BaseSchema] = Genre
    filter_set: AsyncFilterSet = GenreFilterSet
    index_name: str = GENRE_INDEX
    cache_expire_secs: int = GENRE_CACHE_EXPIRE_IN_SECONDS

    def __init__(self, key_value_database: IKeyValueDatabase, search_engine: ISearchEngine) -> None:
        super().__init__(key_value_database, search_engine, self.index_name, self.cache_expire_secs)
