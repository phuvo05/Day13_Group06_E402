# Individual Report — Phan Dương Định
**MSSV**: 2A202600277
**Work Stream**: Work Stream 3 — Metrics + SLO + Alert Rules
**Role**: Primary Owner

---

## 1. Role in the Team

I owned **Work Stream 3: Metrics + SLO + Alert Rules**. My primary responsibility was to ensure the application exposes Prometheus-compatible metrics via the `/metrics` endpoint, define clear SLOs in `config/slo.yaml`, and configure 3 alert rules in `config/alert_rules.yaml` with runbook links. Metrics are the quantitative backbone of observability — they tell you *how* the system is performing, while logs and traces tell you *why*.

---

## 2. Technical Contribution

### Files Modified

#### `app/metrics.py` — Enhanced Metrics with Prometheus-Compatible Naming
Extended the in-memory metrics module with:

- **`RETRIEVAL_LATENCIES` list**: Tracks retrieval-specific latency separately from total request latency. This enables the bonus custom metric `app_retrieval_latency_seconds`.
- **`START_TIME` and `BASELINE_COST_PER_HOUR`**: Tracks the server start time and establishes a cost baseline after the first 10 requests. This allows the `cost_budget_spike` alert to compare current cost against a learned baseline rather than a hardcoded value.
- **`record_retrieval_latency()` function**: Records retrieval-specific latency for the bonus custom metric.
- **Prometheus-formatted keys in `snapshot()`**: Added keys prefixed with `app_` following Prometheus naming conventions:
  - `app_latency_p95_seconds` (latency in seconds for Prometheus histograms)
  - `app_tokens_in_total`, `app_tokens_out_total` (counters)
  - `app_errors_total` (counter)
  - `app_error_rate` (gauge 0-1)
  - `app_cost_per_hour_usd` (gauge)
  - `app_baseline_cost_per_hour_usd` (gauge, set after 10 requests)
  - `app_retrieval_latency_p95_seconds` (custom retrieval histogram)

The cost-per-hour formula: `total_cost_usd / elapsed_hours`, where `elapsed_hours = (now - START_TIME) / 3600`.

#### `app/mock_rag.py` — Retrieval Latency Recording
- Added `record_retrieval_latency()` call at the end of every `retrieve()` execution (both the normal path and the fallback path).
- The retrieval latency is measured from just before the corpus lookup to just after, capturing the total time spent in the vector store.

#### `config/slo.yaml` — SLO Definitions
Defined 4 Service Level Indicators (SLIs) with objectives and targets:

| SLI | Objective | Target | Metric |
|-----|-----------|--------|--------|
| Latency P95 | < 3000ms | 99.5% availability | `app_latency_p95_seconds` |
| Error Rate | < 2% | 99.0% availability | `app_error_rate` |
| Daily Cost | < $2.50/day | 100% budget | `app_cost_per_hour_usd` |
| Quality Score | > 0.75 avg | 95% of requests | `app_quality_score_avg` |

Each SLO includes a 28-day measurement window consistent with industry best practices.

#### `config/alert_rules.yaml` — Alert Rules
Configured 3 alert rules:

| Alert | Severity | Condition | Window |
|-------|----------|-----------|--------|
| `high_latency_p95` | P2 | `app_latency_p95_seconds > 5` | 30 minutes |
| `high_error_rate` | P1 | `app_error_rate > 0.05` | 5 minutes |
| `cost_budget_spike` | P2 | `app_cost_per_hour_usd > 2 * baseline` | 15 minutes |

Each rule includes: severity, owner, runbook link, impact description, and dashboard panel reference.

---

## 3. Challenges Faced

**Challenge 1: Baseline cost estimation**
I initially used a hardcoded baseline cost, but this didn't account for different traffic patterns. I solved this by implementing an adaptive baseline: after 10 requests, the system learns its current cost-per-hour and uses that as the baseline. The `cost_budget_spike` alert then compares against this learned baseline rather than a fixed value.

**Challenge 2: Retrieval latency as a separate metric**
The total request latency includes both retrieval and LLM time. To create the `app_retrieval_latency_p95_seconds` bonus metric, I needed to record retrieval latency separately. I solved this by adding `record_retrieval_latency()` directly in `mock_rag.py`, which keeps the retrieval-specific timing logic close to where the work happens.

---

## 4. Evidence

| Evidence Item | Description |
|---|---|
| `app/metrics.py` | Full metrics module with Prometheus-compatible naming |
| `app/mock_rag.py` line 31 | `record_retrieval_latency()` call |
| `config/slo.yaml` | 4 SLOs with objectives and targets |
| `config/alert_rules.yaml` | 3 alert rules with runbook links |
| `GET /metrics` output | Shows all Prometheus-formatted metrics after load test |

---

## 5. Reflection

The metrics work taught me that **"you can't manage what you can't measure"** is especially true for LLM-powered applications. Unlike traditional software where latency is predictable, LLM responses have variable token counts and costs. By tracking `tokens_in`, `tokens_out`, `cost_usd`, and `latency_ms` together, we get a complete picture of both performance and economics.

The SLO design exercise was valuable: choosing the right thresholds (3000ms for P95, 2% for error rate) requires understanding both user expectations and system capacity. Too strict and you get alert fatigue; too lenient and you miss real problems.

I also learned the importance of **alert severity classification**. A P1 alert for error rate > 5% should wake someone up at 3am, while a P2 latency alert can wait until business hours. The `config/alert_rules.yaml` with severity levels and runbook links makes this explicit and auditable.
