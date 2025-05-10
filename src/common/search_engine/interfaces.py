import abc


class ISearchEngine:
    @abc.abstractmethod
    def search(self, index: str, query: dict) -> dict:
        """Search for documents in the specified index using the provided query."""
        ...

    @abc.abstractmethod
    def get_document(self, index: str, doc_id: str) -> dict:
        """Get a document by its ID from the specified index."""
        ...
