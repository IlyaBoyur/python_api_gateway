from functools import wraps
from typing import Any

from elasticsearch import AsyncElasticsearch
from elasticsearch import exceptions as es_exceptions
from elasticsearch.helpers import async_bulk

from src.common.circuit_breaker import AsyncCircuitBreaker
from src.common.exceptions import DocumentNotFoundError, ElasticsearchDriverError, QuerySyntaxError


async def async_bulk_request(
    client: AsyncElasticsearch, actions: list[dict], **kwargs: Any
) -> None:
    """Perform a bulk index operation."""
    return await async_bulk(client=client, actions=actions, **kwargs)


def handle_es_exceptions(func):
    @wraps(func)
    async def wrapper(*args: tuple, **kwargs: dict):
        try:
            return await func(*args, **kwargs)
        except es_exceptions.NotFoundError as e:
            raise DocumentNotFoundError(kwargs.get("doc_id", "unknown"))
        except es_exceptions.RequestError as e:
            raise QuerySyntaxError(str(e.info))
        except es_exceptions.ElasticsearchException as e:
            raise ElasticsearchDriverError(str(e.info))

    return wrapper


class ElasticDatabase(AsyncElasticsearch):
    @classmethod
    def build(
        cls,
        config: dict,
        verify_certs: bool = True,
        **kwargs: Any,
    ) -> "ElasticDatabase":
        if "dsn" not in config or "timeout" not in config:
            raise ValueError(f"Missing required configuration values in {cls.__name__}")
        return cls(
            hosts=[config["dsn"]],
            request_timeout=config["timeout"],
            verify_certs=verify_certs,
            **kwargs,
        )
