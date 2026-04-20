from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import observe, propagate_attributes, get_client
except Exception:  # pragma: no cover

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    def propagate_attributes(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    def get_client(*args: Any, **kwargs: Any):
        return None


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
