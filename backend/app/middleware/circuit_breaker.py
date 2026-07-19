"""Circuit breaker — protect against cascading failures in external API calls.

States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing recovery)
"""
import logging
import time
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """Simple circuit breaker for external API calls."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0

    @property
    def state(self) -> CircuitState:
        """Get current state, checking for recovery."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        return self._state

    def allow_request(self) -> bool:
        """Check if a request is allowed through."""
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            return True  # Allow test requests
        else:  # OPEN
            return False

    def record_success(self):
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(f"Circuit breaker '{self.name}' recovered → CLOSED")
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def record_failure(self):
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' failed in HALF_OPEN → OPEN")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker '{self.name}' tripped after {self._failure_count} failures → OPEN"
            )

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


# Global circuit breakers for platform publishers
_publisher_breakers: dict[str, CircuitBreaker] = {}


def get_publisher_breaker(platform: str) -> CircuitBreaker:
    """Get or create a circuit breaker for a platform publisher."""
    if platform not in _publisher_breakers:
        _publisher_breakers[platform] = CircuitBreaker(
            name=f"publisher:{platform}",
            failure_threshold=3,
            recovery_timeout=60.0,
        )
    return _publisher_breakers[platform]


def get_all_breakers() -> list[dict[str, Any]]:
    """Get status of all circuit breakers."""
    return [b.get_status() for b in _publisher_breakers.values()]


async def call_with_breaker(
    breaker: CircuitBreaker,
    func: Callable,
    *args,
    **kwargs,
) -> Any:
    """Execute a function through a circuit breaker."""
    if not breaker.allow_request():
        raise CircuitOpenError(
            f"Circuit breaker '{breaker.name}' is OPEN. "
            f"Retry after {breaker.recovery_timeout}s."
        )

    try:
        result = await func(*args, **kwargs)
        breaker.record_success()
        return result
    except Exception as e:
        breaker.record_failure()
        raise


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
