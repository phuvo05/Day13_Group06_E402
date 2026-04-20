from __future__ import annotations

import time

from .incidents import STATE

try:
    from langfuse.decorators import langfuse_context
except Exception:
    class _DummyContext:
        def span(self, **kwargs):
            class DummySpan:
                def update(self, **kwargs): pass
                def __enter__(self): return self
                def __exit__(self, *args): pass
            return DummySpan()
    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    import os as _os
    return bool(_os.getenv("LANGFUSE_PUBLIC_KEY") and _os.getenv("LANGFUSE_SECRET_KEY"))

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


def retrieve(message: str) -> list[str]:
    from . import metrics
    retrieval_started = time.perf_counter()

    with langfuse_context.span(name="vector_store_lookup") as span:
        if STATE["tool_fail"]:
            if tracing_enabled():
                span.update(metadata={"error": "Vector store timeout", "incident": "tool_fail"})
            raise RuntimeError("Vector store timeout")
        if STATE["rag_slow"]:
            time.sleep(2.5)
            if tracing_enabled():
                span.update(metadata={"incident": "rag_slow", "slowdown_ms": 2500})
        lowered = message.lower()
        for key, docs in CORPUS.items():
            if key in lowered:
                if tracing_enabled():
                    span.update(
                        metadata={
                            "top_k": 1,
                            "matched_key": key,
                            "source_doc_ids": [f"doc_{key}"],
                        }
                    )
                retrieval_ms = int((time.perf_counter() - retrieval_started) * 1000)
                metrics.record_retrieval_latency(retrieval_ms)
                return docs
        if tracing_enabled():
            span.update(metadata={"top_k": 0, "matched_key": None, "source_doc_ids": []})
        retrieval_ms = int((time.perf_counter() - retrieval_started) * 1000)
        metrics.record_retrieval_latency(retrieval_ms)
        return ["No domain document matched. Use general fallback answer."]
