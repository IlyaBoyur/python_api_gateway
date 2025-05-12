from collections.abc import Sequence
from typing import Any

from src.common.circuit_breaker import AsyncCircuitBreaker, circuit_breaker
from src.common.exceptions import DocumentNotFoundError, ElasticsearchDriverError
from src.common.retry import retry_async
from src.common.search_engine.elastic import (
    ElasticDatabase,
    async_bulk_index,
    handle_es_exceptions,
)
from src.common.search_engine.interfaces import ISearchEngine


class ElasticSearchEngine(ISearchEngine):
    def __init__(self, client: ElasticDatabase) -> None:
        self._client = client
        self._cb = AsyncCircuitBreaker()

    @circuit_breaker(lambda self: self._cb)
    @retry_async(retriable_exceptions=(ElasticsearchDriverError,))
    @handle_es_exceptions
    async def index_document(self, index: str, doc_id: str | None, document: dict) -> Any:
        return await self._client.index(index=index, id=doc_id, document=document)

    async def get_document(self, index: str, doc_id: str) -> Any:
        return await self.call_with_params(self._client.get, index=index, id=doc_id)

    @circuit_breaker(lambda self: self._cb)
    @retry_async(retriable_exceptions=(ElasticsearchDriverError,))
    @handle_es_exceptions
    async def search(self, index: str, params: dict) -> Any:
        """Search for documents in the specified index using the provided query."""
        if not params.get("query"):
            params["query"] = {"match_all": {}}
        return await self._client.search(index=index, **params)

    @circuit_breaker(lambda self: self._cb)
    @retry_async(retriable_exceptions=(ElasticsearchDriverError,))
    @handle_es_exceptions
    async def delete_document(self, index: str, doc_id: str) -> Any:
        return await self._client.delete(index=index, id=doc_id)

    async def bulk_index(self, actions: list[dict]) -> Any:
        return await self.call_with_params(async_bulk_index, client=self._client, actions=actions)

    @circuit_breaker(lambda self: self._cb)
    @retry_async(retriable_exceptions=(ElasticsearchDriverError,))
    @handle_es_exceptions
    async def call_with_params(self, callable, **params: dict) -> Any:
        """Call a function with parameters."""
        return await callable(**params)

    async def close(self) -> None:
        await self._client.close()
