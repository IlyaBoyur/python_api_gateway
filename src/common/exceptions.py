from typing import Any


class BaseError(Exception):
    """Base class for all custom exceptions.
    Allows formatting via message template defined at the class level or during instantiation.
    """

    message: str = "Internal Server Error"
    message_template: str = ""

    def __init__(self, message: str | None = None, **kwargs: Any) -> None:
        self.kwargs = kwargs

        if message:
            self.message = message
        elif self.message_template:
            try:
                self.message = self.message_template.format(**kwargs)
            except KeyError as e:
                missing_key = e.args[0]
                raise ValueError(
                    f"Missing keyword '{missing_key}' for formatting {self.__class__.__name__}"
                ) from e
        else:
            self.message = self.__class__.__name__

        super().__init__(self.message)

    def __str__(self):
        return self.message



class ServiceError(BaseError):
    message: str = "Internal Service Error"
    status: int = 500


class ValidationServiceError(ServiceError):
    message: str = "Validation error"
    status: int = 422


class CircuitBreakerOpenError(ServiceError):
    message: str = "Circuit breaker is open, rejecting request."
    status: int = 403


class RepositoryError(BaseError):
    message: str = "Internal Service Error"
    status: int = 500


class DocumentNotFoundError(RepositoryError):
    message_template: str = "Document with ID '{doc_id}' not found."
    status: int = 404


class ElasticsearchDriverError(RepositoryError):
    message_template: str = "Unexpected Elasticsearch error: {detail}"
    status: int = 500


class QuerySyntaxError(ElasticsearchDriverError):
    message_template: str = "Query syntax error: {detail}"
    status: int = 400



