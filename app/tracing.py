from __future__ import annotations

import os
from functools import wraps
from inspect import isawaitable, signature
from typing import Any, Callable, TypeVar
from dotenv import load_dotenv

load_dotenv()

F = TypeVar("F", bound=Callable[..., Any])


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


try:
    from langfuse import observe, Langfuse
    
    # Initialize Langfuse client explicitly
    if tracing_enabled():
        langfuse_context = Langfuse()
    else:
        langfuse_context = None
    
    _langfuse_available = True

except ImportError:
    _langfuse_available = False
    langfuse_context = None

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            @wraps(func)
            def wrapper(*a, **kw):
                return func(*a, **kw)
            return wrapper
        return decorator


def trace_request(name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        if not _langfuse_available or not tracing_enabled():
            return func
        
        return observe(name=name, capture_input=True, capture_output=True)(func)  # type: ignore[return-value]

    return decorator
