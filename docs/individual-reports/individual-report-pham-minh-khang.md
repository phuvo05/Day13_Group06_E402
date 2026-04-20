# Individual Report — Phạm Minh Khang
**MSSV**: 2A202600417
**Work Stream**: Work Stream 4 — Incident Response + Runbooks
**Role**: Primary Owner

---

## 1. Role in the Team

I owned **Work Stream 4: Incident Response + Runbooks**. My primary responsibility was to document the runbook for each of the 3 incident scenarios, update the `docs/alerts.md` file with complete incident documentation, and enhance the `scripts/inject_incident.py` script for easier incident injection during testing.

---

## 2. Technical Contribution

### Files Modified

#### `docs/alerts.md` — Complete Runbook Documentation
Rewrote `docs/alerts.md` from the starter template into a comprehensive runbook document covering:

**For each of the 3 incident scenarios** (`rag_slow`, `tool_fail`, `cost_spike`), the runbook includes:

1. **Metadata**: Severity level, alert rule, owner, runbook section link
2. **Symptoms**: Observable indicators that the incident is occurring (e.g., P95 > 5000ms, error rate > 5%, cost 4x baseline)
3. **Detection**: Step-by-step instructions for confirming the incident via dashboard, `/metrics`, and `/health`
4. **Diagnosis Steps**: A structured workflow using the observability triad (Metrics → Traces → Logs):
   - How to find the relevant trace in Langfuse
   - Which span metadata to look for (e.g., `incident: rag_slow`, `incident: tool_fail`)
   - How to extract the correlation ID from logs and link it to traces
5. **Root Cause**: The specific code path that triggered the incident (e.g., `time.sleep(2.5)` in `mock_rag.py`)
6. **Proof**: Specific trace IDs and log line examples showing the incident
7. **Fix Action**: Exact command to disable the incident toggle (both script and HTTP approaches)
8. **Preventive Measure**: Long-term fixes to prevent recurrence

#### Incident 1: `rag_slow` (High Latency)
- **Trigger**: `time.sleep(2.5)` in `mock_rag.py::retrieve()`
- **Trace indicator**: `vector_store_lookup` span has `"incident": "rag_slow", "slowdown_ms": 2500`
- **Fix**: `POST /incidents/rag_slow/disable`
- **Prevention**: Circuit breaker for vector store calls, retrieval timeout with fallback

#### Incident 2: `tool_fail` (High Error Rate)
- **Trigger**: `raise RuntimeError("Vector store timeout")` in `mock_rag.py::retrieve()`
- **Trace indicator**: `vector_store_lookup` span ends with exception, no `rag_retrieval` span follows
- **Fix**: `POST /incidents/tool_fail/disable`
- **Prevention**: Retry with exponential backoff, graceful degradation with fallback answer

#### Incident 3: `cost_spike` (Cost Over Budget)
- **Trigger**: `output_tokens *= 4` in `mock_llm.py::generate()`
- **Trace indicator**: `llm_generate` span has `"cost_spike": true, "original_tokens": <base>`
- **Fix**: `POST /incidents/cost_spike/disable`
- **Prevention**: Per-user token budget, prompt caching, token usage alerts

#### `docs/alerts.md` — Standard Incident Response Workflow
Added a standard incident response workflow that applies to all 3 scenarios:
```
1. DETECT  --> Alert fires in Grafana or PagerDuty
2. TRIAGE  --> Check /health endpoint, identify which incident toggle is active
3. DIAGNOSE --> Use correlation_id to link metrics -> traces -> logs
4. FIX     --> POST /incidents/<name>/disable to restore service
5. VERIFY  --> Confirm metrics return to normal within 1-2 minutes
6. DOCUMENT --> Update this runbook if new patterns are discovered
7. RETRO    --> Identify preventive measures to add to this document
```

#### `docs/alerts.md` — Quick Reference Commands
Added a quick reference section at the end with all incident toggle commands for fast access during incident response.

#### `scripts/inject_incident.py` — Enhanced Script
- Added support for `--incident` as an alias for `--scenario` (to match the README's `inject_incident.py --scenario` style)
- Added `--disable` flag for disabling incidents
- Added `sys.path` manipulation to support running as `python -m scripts.inject_incident`
- Added a descriptive argparse help message

---

## 3. Challenges Faced

**Challenge 1: Connecting traces to logs during incidents**
It was not immediately obvious how to link a Langfuse trace to a log entry. I solved this by ensuring both use the same correlation ID: the middleware generates the correlation ID and stores it in `request.state.correlation_id`, which is then attached to the Langfuse trace as metadata. This creates a direct link between the trace URL and the `correlation_id` field in log entries.

**Challenge 2: Documenting the diagnostic workflow clearly**
The diagnosis steps needed to be specific enough to be actionable but general enough to apply to all incidents. I structured each runbook as: (1) open the right dashboard panel, (2) identify the affected correlation ID, (3) open the Langfuse trace, (4) look for incident metadata in spans, (5) verify via incident toggle status. This Metrics → Traces → Logs flow is the core of the observability debugging methodology.

---

## 4. Evidence

| Evidence Item | Description |
|---|---|
| `docs/alerts.md` | Complete runbook with 3 scenarios + workflow |
| `scripts/inject_incident.py` | Enhanced script with aliases and module support |
| Incident response walkthrough | All 3 incidents diagnosed and resolved |

---

## 5. Reflection

This lab taught me that **runbooks are living documents**, not one-time artifacts. The value of a runbook is not just in documenting what to do — it is in forcing you to actually think through the incident flow *before* an incident happens. When I wrote the diagnosis steps for each incident, I discovered that the observability stack only works if all three layers (metrics, traces, logs) are properly connected. If any one of them is missing, the incident response workflow breaks down.

The most important insight was the **Metrics → Traces → Logs debugging flow**:
1. Metrics tell you *something is wrong* (high latency, high errors, high cost)
2. Traces tell you *where* in the code the problem is (which span, which function)
3. Logs tell you *why* it happened (exception message, context, what the input was)

Without all three, you are guessing. With all three and a correlation ID linking them, you have a complete picture.
