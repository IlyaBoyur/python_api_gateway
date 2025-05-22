import pytest
from pydantic import BaseModel

from src.common.exceptions import ServiceError
from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.models.genre import Genre, GenreFilterSchema
from src.services.genre import GenreService
from tests.factories.genre import GenreFactory


@pytest.fixture
def genre_entity() -> Genre:
    return GenreFactory()


@pytest.fixture
def genre_service(
    key_value_database_mock: IKeyValueDatabase,
    search_engine_mock: ISearchEngine,
) -> GenreService:
    return GenreService(key_value_database_mock, search_engine_mock)


@pytest.mark.asyncio
async def test_get_by_id_cache_hit(
    genre_service: GenreService,
    key_value_database_mock: IKeyValueDatabase,
    genre_entity: Genre,
) -> None:
    key_value_database_mock.get.return_value = genre_entity.json()

    entity = await genre_service.get_by_id("1")

    assert entity == genre_entity
    key_value_database_mock.get.assert_awaited_once_with("1")


@pytest.mark.asyncio
async def test_get_by_id_cache_miss_fetches_from_search_engine(
    genre_service: GenreService,
    key_value_database_mock: IKeyValueDatabase,
    search_engine_mock: ISearchEngine,
    genre_entity: Genre,
) -> None:
    key_value_database_mock.get.return_value = None
    search_engine_mock.get_document.return_value = genre_entity.dict()

    result = await genre_service.get_by_id("1")

    assert result == genre_entity
    search_engine_mock.get_document.assert_awaited_once_with(index="genres", doc_id="1")


@pytest.mark.asyncio
async def test_get_multi_returns_filtered_results(
    genre_service: GenreService,
    search_engine_mock: ISearchEngine,
    genre_entity: Genre,
) -> None:
    search_engine_mock.search.return_value = [genre_entity.dict()]
    filters = GenreFilterSchema()

    result = await genre_service.get_multi(filters)

    assert result == [genre_entity]
    search_engine_mock.search.assert_awaited_once()
