from __future__ import annotations

import os
from typing import Any

from langfuse import get_client


def get_tracing_client():
    return get_client()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def get_langfuse_trace_id() -> str | None:
    langfuse = get_tracing_client()
    try:
        return langfuse.get_current_trace_id()
    except Exception:
        return None
