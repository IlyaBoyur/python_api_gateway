import pytest
from pydantic import BaseModel

from src.common.exceptions import ServiceError
from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.models.film import Film, FilmFilterSchema
from src.services.film import FilmService
from tests.factories.film import FilmFactory


@pytest.fixture
def film_entity() -> Film:
    return FilmFactory()


@pytest.fixture
def film_service(
    key_value_database_mock: IKeyValueDatabase,
    search_engine_mock: ISearchEngine,
) -> FilmService:
    return FilmService(key_value_database_mock, search_engine_mock)


@pytest.mark.asyncio
async def test_get_by_id_cache_hit(
    film_service: FilmService,
    key_value_database_mock: IKeyValueDatabase,
    film_entity: Film,
) -> None:
    key_value_database_mock.get.return_value = film_entity.json()

    entity = await film_service.get_by_id("1")

    assert entity == film_entity
    key_value_database_mock.get.assert_awaited_once_with("1")


@pytest.mark.asyncio
async def test_get_by_id_cache_miss_fetches_from_search_engine(
    film_service: FilmService,
    key_value_database_mock: IKeyValueDatabase,
    search_engine_mock: ISearchEngine,
    film_entity: Film,
) -> None:
    key_value_database_mock.get.return_value = None
    search_engine_mock.get_document.return_value = film_entity.dict()

    result = await film_service.get_by_id("1")

    assert result == film_entity
    search_engine_mock.get_document.assert_awaited_once_with(index="movies", doc_id="1")


@pytest.mark.asyncio
async def test_get_multi_returns_filtered_results(
    film_service: FilmService,
    search_engine_mock: ISearchEngine,
    film_entity: Film,
) -> None:
    search_engine_mock.search.return_value = [film_entity.dict()]
    filters = FilmFilterSchema()

    result = await film_service.get_multi(filters)

    assert result == [film_entity]
    search_engine_mock.search.assert_awaited_once()