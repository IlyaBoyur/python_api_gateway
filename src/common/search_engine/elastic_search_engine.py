from typing import Any

from src.common.circuit_breaker import AsyncCircuitBreaker, circuit_breaker
from src.common.retry import retry_async
from src.common.search_engine.elastic import (
    ElasticDatabase,
    async_bulk_request,
    handle_es_exceptions,
)
from src.common.search_engine.interfaces import ISearchEngine


class ElasticSearchEngine(ISearchEngine):
    def __init__(self, client: ElasticDatabase) -> None:
        self._client = client
        self._cb = AsyncCircuitBreaker()

    @circuit_breaker(lambda self: self._cb)
    @retry_async()
    @handle_es_exceptions
    async def index_document(self, index: str, doc_id: str | None, document: dict) -> Any:
        return await self._client.index(index=index, id=doc_id, document=document)

    @circuit_breaker(lambda self: self._cb)
    @retry_async()
    @handle_es_exceptions
    async def get_document(self, index: str, doc_id: str) -> Any:
        return await self._client.get(index=index, id=doc_id)

    @circuit_breaker(lambda self: self._cb)
    @retry_async()
    @handle_es_exceptions
    async def search(self, index: str, query: dict) -> Any:
        """Search for documents in the specified index using the provided query."""
        return await self._client.search(index=index, query=query)

    @circuit_breaker(lambda self: self._cb)
    @retry_async()
    @handle_es_exceptions
    async def delete_document(self, index: str, doc_id: str) -> Any:
        return await self._client.delete(index=index, id=doc_id)

    @circuit_breaker(lambda self: self._cb)
    @retry_async()
    @handle_es_exceptions
    async def bulk_index(self, actions: list[dict]) -> Any:
        return await async_bulk_request(client=self._client, actions=actions)

    async def close(self):
        await self._client.close()
