from __future__ import annotations

import random
import time
from dataclasses import dataclass

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


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    def generate(self, prompt: str) -> FakeResponse:
        with langfuse_context.span(name="llm_generate") as span:
            if tracing_enabled():
                span.update(
                    metadata={
                        "model": self.model,
                        "prompt_length": len(prompt),
                    }
                )
            time.sleep(0.15)
            input_tokens = max(20, len(prompt) // 4)
            output_tokens = random.randint(80, 180)
            if STATE["cost_spike"]:
                output_tokens *= 4
                if tracing_enabled():
                    span.update(metadata={"cost_spike": True, "original_tokens": output_tokens // 4})
            answer = (
                "Starter answer. Teams should improve this output logic and add better quality checks. "
                "Use retrieved context and keep responses concise."
            )
            return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
