from typing import Any


class BaseError(Exception):
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None, *args: Any, **kwargs: Any):
        if message:
            self.message = message
        super().__init__(self.message, *args, **kwargs)


class ServiceError(BaseError):
    message: str = "Internal Service Error"
    status: int = 500


class ValidationServiceError(ServiceError):
    message: str = "Validation error"
    status: int = 422


class RepositoryError(BaseError):
    message: str = "Internal Service Error"
    status: int = 500


class ElasticsearchDriverError(RepositoryError):
    message: str = "Unexpected Elasticsearch error"
    status: int = 500


class DocumentNotFoundError(ElasticsearchDriverError):
    message: str = "Document with ID '{doc_id}' not found."
    status: int = 404


class QuerySyntaxError(ElasticsearchDriverError):
    message: str = "Query syntax error: {detail}"
    status: int = 400


class CircuitBreakerOpenError(ElasticsearchDriverError):
    message: str = "Circuit breaker is open, rejecting request."
    status: int = 403
