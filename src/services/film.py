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
from src.models.film import Film, FilmFilterSchema

from .base import BaseEntityService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5
FILM_INDEX = "movies"


class FilmFilterSet(AsyncFilterSet):
    id = Filter("id")
    ids = InFilter("id")
    excluded_ids = NotInFilter("id")
    title = SearchFilter("title")
    description = SearchFilter("description")
    imdb_rating = RangeFilter("imdb_rating")
    pagination = LimitOffsetFilter("pagination")
    order = OrderingFilter(
        id=OrderingField("id"),
        imdb_rating=OrderingField("imdb_rating"),
        title=OrderingField("title.raw"),
    )


class FilmService(BaseEntityService[Film, FilmFilterSchema]):
    """Cодержит бизнес-логику по работе с фильмами."""

    schema: type[BaseSchema] = Film
    filter_set: AsyncFilterSet = FilmFilterSet
    index_name: str = FILM_INDEX
    cache_expire_secs: int = FILM_CACHE_EXPIRE_IN_SECONDS

    def __init__(self, key_value_database: IKeyValueDatabase, search_engine: ISearchEngine) -> None:
        super().__init__(key_value_database, search_engine, self.index_name, self.cache_expire_secs)
