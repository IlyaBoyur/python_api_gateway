import asyncio
import time
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from src.common.exceptions import CircuitBreakerOpenError


class AsyncCircuitBreaker:
    def __init__(self, max_failures: int = 5, reset_timeout: int = 30):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        self._lock = asyncio.Lock()

    async def allow(self) -> bool:
        async with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time >= self.reset_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            return True

    async def record_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.max_failures:
                self.state = "OPEN"

    async def record_success(self):
        async with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"


def circuit_breaker(
    cb_getter: Callable,
    recorded_exceptions: tuple[BaseException, ...] = (Exception,),
) -> Callable:
    def decorator(func: Coroutine) -> Coroutine:
        @wraps(func)
        async def wrapper(self, *args: tuple, **kwargs: dict) -> Any:
            cb: AsyncCircuitBreaker = cb_getter(self)
            if not await cb.allow():
                raise CircuitBreakerOpenError
            try:
                result = await func(self, *args, **kwargs)
                await cb.record_success()
                return result
            except recorded_exceptions:
                await cb.record_failure()
                raise

        return wrapper

    return decorator
