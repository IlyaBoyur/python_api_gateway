import abc
from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel


class ISearchEngine(abc.ABC):
    @abc.abstractmethod
    async def search(self, index: str, query: dict[str, Any]) -> list[dict[str, Any]]:
        """Search for documents in the specified index using the provided query."""
        ...

    @abc.abstractmethod
    async def get_document(self, index: str, doc_id: str) -> dict:
        """Get a document by its ID from the specified index."""
        ...
