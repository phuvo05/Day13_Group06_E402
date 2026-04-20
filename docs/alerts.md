# Alert Rules and Runbooks

> This document contains the alert rules and runbooks for the Day 13 Observability Lab.
> Each incident is documented with: symptoms, detection method, diagnosis steps, fix action, and preventive measure.

---

## Alert Rule Reference

| Name | Severity | Condition | Owner | Runbook Section |
|------|----------|-----------|-------|-----------------|
| `high_latency_p95` | P2 | `latency_p95_ms > 5000` for 30m | team-oncall | [#1-high-latency-p95](#1-high-latency-p95) |
| `high_error_rate` | P1 | `error_rate_pct > 5` for 5m | team-oncall | [#2-high-error-rate](#2-high-error-rate) |
| `cost_budget_spike` | P2 | `hourly_cost_usd > 2x_baseline` for 15m | finops-owner | [#3-cost-budget-spike](#3-cost-budget-spike) |

---

## 1. High latency P95

### Metadata
- **Severity**: P2
- **Alert Rule**: `app_latency_p95_seconds > 5` for 30 minutes
- **Owner**: team-oncall
- **Runbook**: `docs/alerts.md#1-high-latency-p95`

### Symptoms
- P95 latency observed > 5000ms on the Grafana dashboard
- Users report slow response times from the `/chat` endpoint
- Latency spike visible in the `app_latency_p95_seconds` metric panel

### Detection
1. Open Grafana dashboard Panel 2 (P95 Latency)
2. Confirm P95 > 5000ms sustained for at least 5 minutes
3. Check `/metrics` endpoint for `latency_p95` value
4. Verify incident toggle status via `GET /health`

### Diagnosis Steps
1. **Step 1**: Open Langfuse trace list and sort by latency (descending)
2. **Step 2**: Open the slowest trace -- look at the waterfall view
3. **Step 3**: Identify which child span is the bottleneck:
   - If `rag_retrieval` or `vector_store_lookup` span > 2000ms -> RAG slow
   - If `llm_call` span > 1000ms -> LLM slow
   - If `prompt_assembly` span > 500ms -> prompt too long
4. **Step 4**: Check logs for `correlation_id` matching the slow trace
5. **Step 5**: Look for `incident: rag_slow` metadata in the trace span
6. **Step 6**: Verify if the `rag_slow` incident toggle is enabled via `GET /health`

### Root Cause
- The `rag_slow` incident was enabled via `POST /incidents/rag_slow/enable`
- This triggered a `time.sleep(2.5)` in `app/mock_rag.py`'s `retrieve()` function
- The vector store lookup span in Langfuse shows `incident: rag_slow, slowdown_ms: 2500`

### Proof
- **Trace ID**: Found in Langfuse, `vector_store_lookup` span metadata contains `"incident": "rag_slow"`
- **Log line**: `data/logs.jsonl` contains event `request_received` with `feature: qa` followed by `response_sent` with `latency_ms > 2500`

### Fix Action
```bash
# Disable the incident toggle to restore normal latency
python scripts/inject_incident.py --scenario rag_slow --disable
```

Or via HTTP:
```bash
curl -X POST http://127.0.0.1:8000/incidents/rag_slow/disable
```

### Preventive Measure
- Add a circuit breaker for vector store calls that opens after 3 consecutive timeouts
- Implement timeout with fallback: if retrieval > 2s, return empty docs and proceed with general answer
- Add `app_retrieval_latency_seconds` histogram to dashboard with alerting at P95 > 1500ms

---

## 2. High Error Rate

### Metadata
- **Severity**: P1
- **Alert Rule**: `app_error_rate > 0.05` for 5 minutes
- **Owner**: team-oncall
- **Runbook**: `docs/alerts.md#2-high-error-rate`

### Symptoms
- Error rate gauge on Grafana dashboard shows > 5%
- Users receive HTTP 500 responses from `/chat` endpoint
- `error_breakdown` in `/metrics` shows `RuntimeError` count increasing

### Detection
1. Open Grafana dashboard Panel 3 (Error Rate)
2. Confirm error rate > 5% sustained for at least 5 minutes
3. Check `/metrics` for `error_breakdown` with `RuntimeError` > 0
4. Verify incident toggle status via `GET /health`

### Diagnosis Steps
1. **Step 1**: Group logs in `data/logs.jsonl` by `error_type`
2. **Step 2**: Find recent error log entries -- look for `event: request_failed`
3. **Step 3**: Extract the `correlation_id` from failed log entries
4. **Step 4**: Open Langfuse trace using the same `correlation_id` (stored as `trace_id` in Langfuse)
5. **Step 5**: The trace waterfall will end abruptly at the `vector_store_lookup` span
6. **Step 6**: Look for `incident: tool_fail` in the span metadata
7. **Step 7**: Check if the `tool_fail` incident toggle is enabled

### Root Cause
- The `tool_fail` incident was enabled via `POST /incidents/tool_fail/enable`
- This triggered `raise RuntimeError("Vector store timeout")` in `app/mock_rag.py`'s `retrieve()` function
- All requests matching keywords in the corpus fail because the vector store throws before returning docs

### Proof
- **Log line**: `data/logs.jsonl` contains `"event": "request_failed", "error_type": "RuntimeError", "payload": {"detail": "Vector store timeout"}`
- **Trace**: Langfuse trace shows `vector_store_lookup` span ending with `RuntimeError`, no `rag_retrieval` span

### Fix Action
```bash
# Disable the incident toggle to restore normal service
python scripts/inject_incident.py --scenario tool_fail --disable
```

Or via HTTP:
```bash
curl -X POST http://127.0.0.1:8000/incidents/tool_fail/disable
```

### Preventive Measure
- Add retry logic with exponential backoff for vector store calls (max 3 retries)
- Implement graceful degradation: if retrieval fails, return a "service temporarily degraded" answer with no docs
- Add dead-letter queue for failed retrieval events for later analysis

---

## 3. Cost Budget Spike

### Metadata
- **Severity**: P2
- **Alert Rule**: `app_cost_per_hour_usd > 2 * baseline` for 15 minutes
- **Owner**: finops-owner
- **Runbook**: `docs/alerts.md#3-cost-budget-spike`

### Symptoms
- Cost per hour on Grafana dashboard shows > 2x the established baseline
- `app_cost_per_hour_usd` in `/metrics` is significantly elevated
- `tokens_out_total` increases disproportionately to `tokens_in_total`

### Detection
1. Open Grafana dashboard Panel 5 (Cost per Hour)
2. Compare current value against `app_baseline_cost_per_hour_usd`
3. If `cost_per_hour > 2 * baseline`, the alert fires
4. Check `/metrics` for `tokens_out_total` and `total_cost_usd`

### Diagnosis Steps
1. **Step 1**: Split traces by feature in Langfuse -- compare `tokens_out` across features
2. **Step 2**: Look for traces where `usage.output` is unusually high (normal: 80-180 tokens)
3. **Step 3**: Compare `tokens_in` vs `tokens_out` ratio in affected traces
4. **Step 4**: Check if `llm_generate` span metadata shows `cost_spike: true`
5. **Step 5**: Look for `incident: cost_spike` in span metadata
6. **Step 6**: Verify if the `cost_spike` incident toggle is enabled

### Root Cause
- The `cost_spike` incident was enabled via `POST /incidents/cost_spike/enable`
- This multiplied `output_tokens` by 4 in `app/mock_llm.py`'s `FakeLLM.generate()` method
- Cost formula: `input_cost = tokens_in / 1M * $3` + `output_cost = tokens_out / 1M * $15`
- With 4x output tokens, cost per request increases ~3-4x

### Proof
- **Metric**: `/metrics` shows `tokens_out_total` at approximately 4x expected value
- **Trace**: Langfuse `llm_generate` span metadata contains `"cost_spike": true, "original_tokens": <base_token_count>`
- **Log**: `response_sent` log entries show `tokens_out` and `cost_usd` both 4x baseline

### Fix Action
```bash
# Disable the incident toggle to restore normal cost
python scripts/inject_incident.py --scenario cost_spike --disable
```

Or via HTTP:
```bash
curl -X POST http://127.0.0.1:8000/incidents/cost_spike/disable
```

### Preventive Measure
- Implement per-user or per-session token budgets with graceful degradation (fall back to shorter responses)
- Add token usage alerts at 2x and 3x baseline thresholds for earlier warning
- Consider prompt caching to reduce redundant token usage

---

## Incident Response Workflow

For each incident, follow this standard workflow:

```
1. DETECT  --> Alert fires in Grafana or PagerDuty
2. TRIAGE  --> Check /health endpoint, identify which incident toggle is active
3. DIAGNOSE --> Use correlation_id to link metrics -> traces -> logs
4. FIX     --> POST /incidents/<name>/disable to restore service
5. VERIFY  --> Confirm metrics return to normal within 1-2 minutes
6. DOCUMENT --> Update this runbook if new patterns are discovered
7. RETRO    --> Identify preventive measures to add to this document
```

---

## Quick Reference: Incident Toggle Commands

```bash
# Enable an incident
python scripts/inject_incident.py --scenario <rag_slow|tool_fail|cost_spike>
python -m scripts.inject_incident --scenario <rag_slow|tool_fail|cost_spike>

# Disable an incident
python scripts/inject_incident.py --scenario <rag_slow|tool_fail|cost_spike> --disable
python -m scripts.inject_incident --scenario <rag_slow|tool_fail|cost_spike> --disable

# Check current status
curl http://127.0.0.1:8000/health
```
