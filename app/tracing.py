from __future__ import annotations

import os
from inspect import isawaitable, signature
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

try:
    from langfuse.decorators import observe, langfuse_context
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            @wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any):
                return func(*f_args, **f_kwargs)

            return wrapper

        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def trace_request(name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        observed = observe(name=name, capture_input=True, capture_output=True)(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            result = observed(*args, **kwargs)
            if isawaitable(result):
                return await result
            return result

        # Keep FastAPI endpoint parameter inspection stable after decoration.
        wrapper.__signature__ = signature(func)  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
