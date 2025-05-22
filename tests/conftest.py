from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from src.common.key_value_database import IKeyValueDatabase
from src.common.search_engine import ISearchEngine


@pytest.fixture
def key_value_database_mock() -> IKeyValueDatabase:
    """Returns an async mock of the IKeyValueDatabase interface."""
    return AsyncMock(spec=IKeyValueDatabase)


@pytest.fixture
def search_engine_mock() -> ISearchEngine:
    """Returns an async mock of the ISearchEngine interface."""
    return AsyncMock(spec=ISearchEngine)
