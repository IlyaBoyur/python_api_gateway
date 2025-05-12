from functools import lru_cache

from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.common.search_engine.filter_fields import (
    Filter,
    InFilter,
    LimitOffsetFilter,
    OrderingField,
    OrderingFilter,
    RangeFilter,
    SearchFilter,
)
from src.common.search_engine.filtersets import AsyncFilterSet
from src.models.base import BaseSchema
from src.models.film import Film, FilmFilterSchema

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


MOVIES_INDEX = "movies"


class FilmFilterSet(AsyncFilterSet):
    id = Filter("id")
    title = SearchFilter("title")
    description = SearchFilter("description")
    imdb_rating = RangeFilter("imdb_rating")
    pagination = LimitOffsetFilter("pagination")
    order = OrderingFilter(
        id=OrderingField("id"),
        imdb_rating=OrderingField("imdb_rating"),
        created=OrderingField("created"),
        title=OrderingField("title.raw"),
    )


class FilmService:
    """Cодержит бизнес-логику по работе с фильмами."""

    filter_set: AsyncFilterSet = FilmFilterSet

    def __init__(self, key_value_database: IKeyValueDatabase, search_engine: ISearchEngine) -> None:
        self.key_value_database = key_value_database
        self.search_engine = search_engine

    async def get_by_id(self, film_id: str) -> Film | None:
        """Вернуть объект фильма. Он опционален, так как фильм может отсутствовать в базе."""
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_search_engine(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def filter(self, params: FilmFilterSchema) -> list[Film]:
        filter_set = self.filter_set()
        es_query = filter_set.filter_query(params.dict(exclude_none=True))
        result = await self.search_engine.search(index=MOVIES_INDEX, params=es_query)
        return [Film(**doc["_source"]) for doc in result["hits"]["hits"]]

    async def _get_film_from_search_engine(self, film_id: str) -> Film | None:
        doc = await self.search_engine.get_document(index=MOVIES_INDEX, doc_id=film_id)
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Film | None:
        data = await self.key_value_database.get(film_id)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film) -> None:
        await self.key_value_database.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)
