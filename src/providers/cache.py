import hashlib
from collections.abc import Callable
from functools import wraps
from http import HTTPStatus
from typing import Annotated, ParamSpec

from fastapi import Depends, HTTPException, Response
from loguru import logger

from src.common.coder import NoDecodeJsonCoder
from src.common.key_value_database.interfaces import IKeyValueDatabase
from src.providers.key_value_database import get_key_value_database

P = ParamSpec("P")


def build_key(
    func: Callable, namespace: str = "", args: tuple | None = None, kwargs: dict | None = None
) -> str:
    if kwargs:
        new_kwargs = {name: obj for name, obj in kwargs.items() if not isinstance(obj, Annotated)}
        kwargs = new_kwargs
    namespace = f"{namespace}:{func.__name__}" if namespace else func.__name__
    prefix = namespace
    cache_key = (
        prefix
        + hashlib.md5(  # noqa: S324
            f"{func.__module__}:{func.__name__}:{args}:{kwargs}".encode(),
        ).hexdigest()
    )
    return cache_key


def api_cache(ttl: int = 60 * 60 * 24, namespace: str = "") -> Callable:
    """Caching decorator for FastAPI endpoints.

    ttl: Time to live for the cache in seconds.
    namespace: Namespace for cache keys in key value database.
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(
            *args: P.args,
            cache_db: Annotated[IKeyValueDatabase, Depends(get_key_value_database)],
            **kwargs: P.kwargs,
        ) -> Callable:
            """Wrapper for caching decorator.

            cache_db: database dependency for request to be stored in
            """
            coder = NoDecodeJsonCoder()

            cache_key = build_key(func, namespace, args, kwargs)
            _, result = await cache_db.get_with_ttl(key=cache_key)
            headers = {"Cache-Control": f"max-age={ttl}"}
            if result is not None:
                logger.debug("CACHE HIT! key: {}", cache_key)
                return Response(
                    content=coder.decode(result),
                    status_code=HTTPStatus.OK,
                    headers=headers,
                    media_type="application/json",
                    background=None,
                )
            logger.debug("CACHE MISS! key: {}", cache_key)
            result = await func(*args, **kwargs)
            await cache_db.set(key=cache_key, value=coder.encode(result), expire=ttl)
            return result

        import inspect

        """Required to make dependency descoverable"""
        wrapper.__signature__ = inspect.Signature(
            parameters=[
                *inspect.signature(func).parameters.values(),
                *[
                    p
                    for p in inspect.signature(wrapper).parameters.values()
                    if p.kind
                    not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                ],
            ],
            return_annotation=inspect.signature(func).return_annotation,
        )
        return wrapper

    return decorator
