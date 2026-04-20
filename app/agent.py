from __future__ import annotations

import time
from dataclasses import dataclass

from langfuse import get_client

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import tracing_enabled


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    def run(
        self,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
        correlation_id: str | None = None,
    ) -> AgentResult:
        if not tracing_enabled():
            return self._run_without_tracing(user_id, feature, session_id, message)

        langfuse = get_client()
        started = time.perf_counter()
        user_id_hash = hash_user_id(user_id)

        with langfuse.start_as_current_span(
            name="agent-run",
            input={"message": summarize_text(message), "feature": feature},
            metadata={"correlation_id": correlation_id, "feature": feature, "model": self.model},
        ):
            langfuse.update_current_trace(
                user_id=user_id_hash,
                session_id=session_id,
                tags=["lab", feature, self.model],
                metadata={"correlation_id": correlation_id},
            )

            docs = self._trace_rag_retrieval(langfuse, message)
            prompt = self._trace_prompt_assembly(langfuse, feature, docs, message)
            response = self._trace_llm_call(langfuse, prompt)
            quality_score = self._trace_response_format(langfuse, message, response, docs)

            latency_ms = int((time.perf_counter() - started) * 1000)
            cost_usd = self._estimate_cost(
                response.usage.input_tokens, response.usage.output_tokens
            )

            langfuse.update_current_span(
                metadata={
                    "latency_ms": latency_ms,
                    "cost_usd": cost_usd,
                    "quality_score": quality_score,
                    "doc_count": len(docs),
                }
            )

            metrics.record_request(
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                quality_score=quality_score,
            )

            return AgentResult(
                answer=response.text,
                latency_ms=latency_ms,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                cost_usd=cost_usd,
                quality_score=quality_score,
            )

    def _run_without_tracing(
        self, user_id: str, feature: str, session_id: str, message: str
    ) -> AgentResult:
        started = time.perf_counter()
        docs = retrieve(message)
        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        response = self.llm.generate(prompt)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(
            response.usage.input_tokens, response.usage.output_tokens
        )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _trace_rag_retrieval(self, langfuse, message: str) -> list[str]:
        with langfuse.start_as_current_span(
            name="rag-retrieval",
            metadata={"query_preview": summarize_text(message)},
        ) as span:
            docs = retrieve(message)
            span.update(metadata={"doc_count": len(docs)})
        return docs

    def _trace_prompt_assembly(
        self, langfuse, feature: str, docs: list[str], message: str
    ) -> str:
        with langfuse.start_as_current_span(
            name="prompt-assembly",
            metadata={"feature": feature},
        ) as span:
            prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
            span.update(metadata={"prompt_length": len(prompt)})
        return prompt

    def _trace_llm_call(self, langfuse, prompt: str):
        with langfuse.start_as_current_generation(
            name="llm-call",
            model=self.model,
            input={"prompt": summarize_text(prompt)},
        ) as generation:
            response = self.llm.generate(prompt)
            generation.update(
                output={"text": summarize_text(response.text)},
                usage_details={
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                },
                metadata={
                    "model": response.model,
                },
            )
        return response

    def _trace_response_format(self, langfuse, message: str, response, docs: list[str]) -> float:
        with langfuse.start_as_current_span(name="response-format") as span:
            quality_score = self._heuristic_quality(message, response.text, docs)
            span.update(
                metadata={
                    "answer_length": len(response.text),
                    "quality_score": quality_score,
                },
            )
        return quality_score

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(
            token in answer.lower() for token in question.lower().split()[:3]
        ):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
