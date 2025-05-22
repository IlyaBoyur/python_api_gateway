import json
import pytest
from pydantic import BaseModel
from pytest_mock.plugin import MockerFixture

from src.common.exceptions import ServiceError
from src.services.base import BaseEntityService, IEntityService


class DummyModel(BaseModel):
    id: str
    name: str


class DummyFilter(BaseModel):
    name: str | None = None


class DummyFilterSet:
    def filter_query(self, data: dict) -> dict:
        # Simulate a filter query
        return {"query": data}


@pytest.fixture
def fake_search_result() -> list[dict]:
    return [{"id": "1", "name": "Test"}]


@pytest.fixture
def dummy_service(mocker: MockerFixture, fake_search_result: list[dict]) -> IEntityService:
    kv_db = mocker.AsyncMock()
    search = mocker.AsyncMock()
    search.search.return_value = fake_search_result
    search.get_document.return_value = fake_search_result[0]

    class DummyService(BaseEntityService[DummyModel, DummyFilter]):
        schema = DummyModel
        filter_set = DummyFilterSet

    return DummyService(kv_db, search, "test-index", 60)


@pytest.mark.asyncio
async def test_get_by_id_from_cache(dummy_service: IEntityService) -> None:
    dummy_service.key_value_database.get.return_value = b'{"id": "1", "name": "FromCache"}'

    result = await dummy_service.get_by_id("1")

    assert isinstance(result, DummyModel)
    assert result.id == "1"
    assert result.name == "FromCache"
    dummy_service.key_value_database.get.assert_called_once_with("1")
    assert not dummy_service.search_engine.called


@pytest.mark.asyncio
async def test_get_by_id_from_search(dummy_service: IEntityService) -> None:
    dummy_service.key_value_database.get.return_value = None

    result = await dummy_service.get_by_id("1")

    assert isinstance(result, DummyModel)
    assert result.id == "1"
    assert result.name == "Test"
    dummy_service.search_engine.get_document.assert_called_once_with(index="test-index", doc_id="1")
    dummy_service.key_value_database.set.assert_called_once_with(
        "1", json.dumps({"id": "1", "name": "Test"}), expire=60
    )


@pytest.mark.asyncio
async def test_get_by_id_cache_parse_failure(dummy_service: IEntityService) -> None:
    dummy_service.key_value_database.get.return_value = "INVALID"

    with pytest.raises(ServiceError):
        await dummy_service.get_by_id("1")


@pytest.mark.asyncio
async def test_get_multi(dummy_service: IEntityService) -> None:
    result = await dummy_service.get_multi(DummyFilter(name="Test"))

    assert isinstance(result, list)
    assert result[0].id == "1"
