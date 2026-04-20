# Individual Report — Đào Hồng Sơn
**MSSV**: 2A202600462
**Work Stream**: Work Stream 2 — Langfuse Distributed Tracing
**Role**: Primary Owner

---

## 1. Role in the Team

I owned **Work Stream 2: Langfuse Distributed Tracing**. My primary responsibility was to ensure that every agent run produces a complete distributed trace in Langfuse with meaningful spans for each sub-step: retrieval, prompt assembly, LLM call, and response formatting. Good traces allow the team to pinpoint exactly which part of the pipeline is slow or failing.

---

## 2. Technical Contribution

### Files Modified

#### `app/agent.py` — Child Spans for Each Pipeline Stage
The starter `agent.run()` was a single monolithic function. I instrumented it with 4 explicit child spans using Langfuse's `langfuse_context.span()` context manager:

1. **`rag_retrieval`** (via `mock_rag.retrieve()`): Wraps the retrieval call and updates the span with `doc_count` and `query_preview`.
2. **`prompt_assembly`**: Wraps the string formatting of the prompt with `prompt_length` and `feature`.
3. **`llm_call`** (via `mock_llm.generate()`): Wraps the LLM call and updates the span with `model`, `tokens_in`, and `tokens_out`.
4. **`response_format`**: Wraps the `_heuristic_quality()` call and records `answer_length` and `quality_score`.

After all spans are complete, I call `langfuse_context.update_current_trace()` and `update_current_observation()` to attach the top-level trace metadata (hashed `user_id`, `session_id`, tags, usage details). The `@observe()` decorator (already present in the starter code) wraps the entire `run()` method.

**Key design decision**: I chose to use `langfuse_context.span()` as a context manager rather than manual `span.start()`/`span.end()` because it automatically handles the span lifecycle — including exception handling — even though we don't currently raise from within the spans.

#### `app/mock_llm.py` — LLM Span Tagging
- Added an inner `llm_generate` span within the `FakeLLM.generate()` method. This span captures:
  - `model`: The model name used
  - `prompt_length`: Length of the input prompt
  - `cost_spike`: Boolean flag when the `cost_spike` incident is active
  - `original_tokens`: Token count before multiplication (for cost spike cases)

#### `app/mock_rag.py` — RAG Span Tagging
- Added a `vector_store_lookup` span within the `retrieve()` function. This span captures:
  - `incident`: Set to `"rag_slow"` or `"tool_fail"` when the respective incident toggle is active
  - `slowdown_ms`: Set to `2500` when `rag_slow` is active
  - `error`: Set to `"Vector store timeout"` when `tool_fail` is active
  - `top_k`: Number of documents matched
  - `matched_key`: The corpus key that was matched
  - `source_doc_ids`: IDs of retrieved documents

The span is attached before the incident check so that even failed retrievals have a trace entry.

---

## 3. Challenges Faced

**Challenge 1: Exception propagation through spans**
When the `tool_fail` incident is enabled, `mock_rag.py` raises `RuntimeError("Vector store timeout")`. I needed to ensure this exception still creates a trace entry (with the error metadata) rather than silently failing. I solved this by updating the span metadata *before* re-raising the exception — the span is created via context manager, so even if an exception propagates, the span is closed with the error attached.

**Challenge 2: PII in trace metadata**
The `user_id` is visible in the raw request. I recommended and helped implement the `hash_user_id()` function in `pii.py` which hashes the user ID to a 12-character hex string before attaching it to the Langfuse trace. This preserves traceability without exposing raw user identifiers.

---

## 4. Evidence

| Evidence Item | Description |
|---|---|
| `app/agent.py` lines 29–92 | All 4 child spans + trace/observation updates |
| `app/mock_llm.py` lines 46–64 | `llm_generate` span with model/cost metadata |
| `app/mock_rag.py` lines 26–47 | `vector_store_lookup` span with incident tagging |
| `app/tracing.py` | `@observe()` decorator and `tracing_enabled()` check |
| Langfuse dashboard | >= 10 traces visible after load test |

---

## 5. Reflection

Before this lab, I thought of "tracing" as just adding a few log lines. This lab showed me that distributed tracing is a **causality graph** — each span has a start time, end time, parent, and metadata, forming a tree that lets you see not just *that* something was slow, but *where* in the call stack the slowness occurred.

The Langfuse waterfall view is particularly powerful: you can see at a glance that `rag_retrieval` took 2500ms (because `rag_slow` was on) while `llm_call` took ~150ms. Without tracing, you would only know that the total request took 2650ms — you would have no idea which component was responsible.

I also learned that tracing and logging are complementary: traces give you the *structure* (which spans, how long), while logs give you the *context* (why did this happen, what was the input). The correlation ID bridges both — it appears in both the Langfuse trace metadata and in every structlog log line.
