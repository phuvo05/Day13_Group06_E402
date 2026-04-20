# Individual Report — Nguyễn Anh Quân
**MSSV**: 2A202600132
**Work Stream**: Work Stream 5 — Dashboard + Load Testing + Validation + Bonus
**Role**: Primary Owner

---

## 1. Role in the Team

I owned **Work Stream 5: Dashboard + Load Testing + Validation + Bonus Work**. My primary responsibility was to build the Grafana dashboard with 6 panels, create the full validation automation script, implement the audit logging bonus feature, and ensure the complete observability stack was validated end-to-end.

---

## 2. Technical Contribution

### Files Modified / Created

#### `docs/dashboard-spec.md` — Grafana Dashboard
Created a complete Grafana dashboard JSON specification with 6 panels:

| Panel | Title | Type | Metric | Notes |
|-------|-------|------|--------|-------|
| 1 | Request Volume | Time series | `sum(rate(app_requests_total[5m]))` | QPS over time |
| 2 | P95 Latency | Time series | `histogram_quantile(0.95, ...)` | P50/P95/P99 + SLO line at 3000ms |
| 3 | Error Rate | Gauge | `rate(app_errors_total) / rate(app_requests_total)` | Green < 2%, Yellow > 2%, Red > 5% |
| 4 | Token Usage | Stacked time series | `rate(app_tokens_in_total)` + `rate(app_tokens_out_total)` | Tokens in (blue) vs out (orange) |
| 5 | Cost per Hour | Stat | `app_cost_per_hour_usd` | Single stat with threshold coloring |
| 6 | SLO Health Overview | Table | Composite | Traffic light overview |

The dashboard uses a dark theme, auto-refreshes every 15 seconds, defaults to 1-hour time range, and includes threshold lines for SLO targets.

#### `scripts/run_full_validation.py` — Full Validation Automation Script
Created an automation script that runs the complete validation suite in one command:

```
python scripts/run_full_validation.py
python scripts/run_full_validation.py --concurrency 5 --count 10
```

The script:
1. Clears existing logs (`data/logs.jsonl`)
2. Runs load test with configurable concurrency and repeat count
3. Runs the log validator
4. Parses the validation output to extract score, PII leaks, and correlation ID counts
5. Prints a summary report with PASS/FAIL verdict

**Key design decision**: I made the script idempotent — it can be run multiple times safely, clearing logs each time. This is useful for CI/CD pipelines and for demonstrating the validation multiple times during the live demo.

#### `app/audit.py` — Audit Logging Module
Created a dedicated audit logging module (`app/audit.py`) that writes structured audit events to `data/audit.jsonl` for compliance. Audit events include:

- **`chat.request` (success)**: Records user, session, feature, correlation_id, latency for every successful request
- **`chat.request` (failure)**: Records user, session, feature, correlation_id, error_type for every failed request
- **`incident.enable`** / **`incident.disable`**: Records when incident toggles are changed
- **`alert.cost_spike`**: Records when a cost spike is detected

Each audit event is a JSON object with: `ts` (ISO timestamp), `actor`, `action`, `resource`, `outcome`, and `metadata`.

#### `app/main.py` — Audit Integration
Integrated audit logging into `main.py`:
- Every successful `/chat` request triggers `audit_chat_request()`
- Every failed `/chat` request triggers `audit_chat_error()`
- Every incident toggle change triggers `audit_incident_toggle()`

#### Bonus Feature: Custom Retrieval Latency Metric
Added `app_retrieval_latency_seconds` histogram to `app/metrics.py`:
- A new `RETRIEVAL_LATENCIES` list tracks retrieval-specific latency
- `record_retrieval_latency()` is called in `mock_rag.py` for every retrieval
- The `snapshot()` function exposes `app_retrieval_latency_p95_seconds` for the dashboard

#### `scripts/load_test.py` — Enhanced Load Test
Enhanced the load test script:
- Added `--count` parameter to repeat queries multiple times (useful for generating 50+ log entries)
- Added `sys.path` manipulation for module-style execution
- Improved output to show correlation IDs for each request
- Increased timeout from 30s to 60s for concurrent runs

---

## 3. Challenges Faced

**Challenge 1: Generating enough log entries for validation**
The starter `scripts/load_test.py` only ran through the 10 sample queries once. The `validate_logs.py` script checks for >= 50 entries. I solved this by adding the `--count` parameter to `load_test.py` and `--concurrency` for testing parallel bottlenecks. A single pass with `concurrency=5` is now sufficient to generate enough data.

**Challenge 2: Correlation ID gaps in validation**
I noticed that the validation script checks that correlation IDs are "MISSING" — this was the default value in the starter code. After implementing the middleware, every request should generate a proper ID. The validation script checks that at least 2 unique correlation IDs exist, which confirms proper propagation.

---

## 4. Evidence

| Evidence Item | Description |
|---|---|
| `docs/dashboard-spec.md` | Complete Grafana dashboard JSON with 6 panels |
| `scripts/run_full_validation.py` | Full automation script — bonus item |
| `app/audit.py` | Audit logging module — bonus item |
| `app/main.py` lines 74–82, 88–95, 101, 110 | Audit integration |
| `app/metrics.py` lines 30–31 | `record_retrieval_latency()` — bonus custom metric |
| `scripts/load_test.py` | Enhanced load test with `--count` support |

---

## 5. Reflection

This lab taught me that **observability is only as good as your ability to verify it**. You can implement all the logging, tracing, and metrics in the world, but without a way to automatically verify that they are working correctly, you have no confidence in your observability stack.

The `run_full_validation.py` automation script embodies this principle: it is a single command that runs the load test, validates the logs, and reports a PASS/FAIL verdict. This is exactly what a CI/CD pipeline would need to prevent regressions in observability instrumentation.

The audit logging feature was an eye-opener: in regulated industries (healthcare, finance, government), you don't just need to *observe* your system — you need an **immutable audit trail** of who did what and when. The `audit.jsonl` file with structured events is designed to be exactly that: a compliance-ready record that can be exported to a SIEM or reviewed by auditors.

Finally, building the Grafana dashboard made me appreciate the importance of **clear, actionable dashboards**. A panel that just shows a number without context or thresholds is not useful in an incident. The dashboard I built includes SLO lines, threshold coloring, and clear units on every panel — so that during an incident, anyone can glance at the dashboard and immediately understand the system state.
