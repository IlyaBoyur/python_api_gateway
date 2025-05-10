import asyncio
import logging
from functools import wraps

from loguru import logger


def retry_async(
    retries: int = 5, backoff_factor: float = 0.5, retriable_exceptions: tuple = (Exception,)
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args: tuple, **kwargs: dict):
            attempt = 0
            while attempt <= retries:
                try:
                    return await func(*args, **kwargs)
                except retriable_exceptions as e:
                    delay = backoff_factor * (2**attempt)
                    logger.warning(
                        f"[{func.__name__}] Attempt {attempt+1} failed: {e}. Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
            raise Exception(f"[{func.__name__}] Max retry attempts exceeded")

        return wrapper

    return decorator
