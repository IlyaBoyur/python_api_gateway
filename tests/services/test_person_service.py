import pytest
from pydantic import BaseModel

from src.common.exceptions import ServiceError
from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine
from src.models.person import Person, PersonFilterSchema
from src.services.person import PersonService
from tests.factories.person import PersonFactory


@pytest.fixture
def person_entity() -> Person:
    return PersonFactory()


@pytest.fixture
def person_service(
    key_value_database_mock: IKeyValueDatabase,
    search_engine_mock: ISearchEngine,
) -> PersonService:
    return PersonService(key_value_database_mock, search_engine_mock)


@pytest.mark.asyncio
async def test_get_by_id_cache_hit(
    person_service: PersonService,
    key_value_database_mock: IKeyValueDatabase,
    person_entity: Person,
) -> None:
    key_value_database_mock.get.return_value = person_entity.json()

    entity = await person_service.get_by_id("1")

    assert entity == person_entity
    key_value_database_mock.get.assert_awaited_once_with("1")


@pytest.mark.asyncio
async def test_get_by_id_cache_miss_fetches_from_search_engine(
    person_service: PersonService,
    key_value_database_mock: IKeyValueDatabase,
    search_engine_mock: ISearchEngine,
    person_entity: Person,
) -> None:
    key_value_database_mock.get.return_value = None
    search_engine_mock.get_document.return_value = person_entity.dict()

    result = await person_service.get_by_id("1")

    assert result == person_entity
    search_engine_mock.get_document.assert_awaited_once_with(index="persons", doc_id="1")


@pytest.mark.asyncio
async def test_get_multi_returns_filtered_results(
    person_service: PersonService,
    search_engine_mock: ISearchEngine,
    person_entity: Person,
) -> None:
    search_engine_mock.search.return_value = [person_entity.dict()]
    filters = PersonFilterSchema()

    result = await person_service.get_multi(filters)

    assert result == [person_entity]
    search_engine_mock.search.assert_awaited_once()
