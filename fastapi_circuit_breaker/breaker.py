"""
fastapi-circuit-breaker: Lightweight async circuit breaker decorator for FastAPI.
Prevents cascading service failures when external dependencies (OpenAI, Stripe, 3rd-party APIs) stall or crash.
"""

import functools
import inspect
import time
from enum import Enum
from typing import Any, Callable, Optional
from fastapi import HTTPException, status

class CircuitState(Enum):
    CLOSED = "CLOSED" # Normal operation: traffic flows through
    OPEN = "OPEN" # Circuit tripped: calls fail fast
    HALF_OPEN = "HALF_OPEN" # Testing if downstream service has recovered

class CircuitBreakerOpenError(HTTPException):
    def __init__(self, detail: str = "Service temporarily unavailable due to downstream failure."):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)

class CircuitBreaker:
    """Manages circuit state and failure counting."""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_state_change = time.time()
        self.state = CircuitState.CLOSED

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False
        return True

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    fallback: Optional[Callable[..., Any]] = None
):
    """
    Decorator that wraps an async function with circuit breaker protection.

    Usage:
        @app.get("/external-data")
        @circuit_breaker(failure_threshold=3, recovery_timeout=15.0)
        async def fetch_external():
            return await call_unstable_api()
    """
    breaker = CircuitBreaker(failure_threshold=failure_threshold, recovery_timeout=recovery_timeout)

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not breaker.allow_request():
                if fallback:
                    if inspect.iscoroutinefunction(fallback):
                        return await fallback(*args, **kwargs)
                    return fallback(*args, **kwargs)
                raise CircuitBreakerOpenError()

            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                if fallback and breaker.state == CircuitState.OPEN:
                    if inspect.iscoroutinefunction(fallback):
                        return await fallback(*args, **kwargs)
                    return fallback(*args, **kwargs)
                raise e

        return wrapper
    return decorator
