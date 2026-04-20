# Evidence Collection Sheet

## Required Evidence

### 1. Langfuse Trace List (>= 10 traces)
- **Status**: [ ] Screenshot required
- **Evidence**: Langfuse Dashboard at `https://cloud.langfuse.com`
- **Files**: `app/tracing.py`, `app/agent.py`

### 2. One Full Trace Waterfall
- **Status**: [ ] Screenshot required
- **Evidence**: Langfuse Dashboard - open any trace to see waterfall
- **Files**: `app/main.py` (`@trace_request(name="chat_request")`)

### 3. JSON Logs with Correlation ID
- **Status**: [x] Available
- **Evidence**: `data/logs.jsonl`
- **Example**:
```json
{"ts": "2026-04-20T10:30:15.123Z", "level": "info", "event": "request_received", "correlation_id": "abc123def456..."}
```
- **Files**: `app/middleware.py`, `app/logging_config.py`

### 4. Log Line with PII Redaction
- **Status**: [x] Available
- **Evidence**: `data/logs.jsonl`
- **Example**:
```json
{"msg": "Email me at [REDACTED_EMAIL] or call [REDACTED_PHONE_VN]", "pii_scrubbed": true}
```
- **Files**: `app/pii.py`

### 5. Dashboard with 6 Panels
- **Status**: [x] Available
- **Evidence**: `config/dashboard.json` (7 panels)
- **Panels**:
  1. Latency P50/P95/P99
  2. Traffic / QPS
  3. Error Rate & Breakdown
  4. Cost Over Time
  5. Tokens In/Out
  6. Quality Proxy
  7. Cost Per Token (bonus)
- **Files**: `config/dashboard.json`, `docs/alerts.md`

### 6. Alert Rules with Runbook Link
- **Status**: [x] Available
- **Evidence**: `config/alert_rules.yaml`
- **Alerts**:
  - `high_latency_p95` -> `docs/alerts.md#1-high-latency-p95`
  - `high_error_rate` -> `docs/alerts.md#2-high-error-rate`
  - `cost_budget_spike` -> `docs/alerts.md#3-cost-budget-spike`
  - `quality_drop` -> `docs/alerts.md#1-high-latency-p95`

---

## Optional Evidence (Bonus)

### 1. Incident Before/After Fix
- **Status**: [ ] Screenshot required (optional)
- **Evidence**: Run `scripts/inject_incident.py` with `--enable` and `--disable`

### 2. Cost Comparison Before/After Optimization
- **Status**: [x] Available
- **Evidence**: `/cost-optimization` endpoint returns 40% savings
- **Before**: $0.00045 per request
- **After**: $0.00027 per request
- **Savings**: 40%

### 3. Auto-Instrumentation Proof
- **Status**: [x] Available
- **Evidence**: `@trace_request` and `@observe` decorators auto-create spans
- **Files**: `app/tracing.py`, `app/agent.py`, `app/main.py`

---

## Bonus Items Evidence

| Bonus | Description | Evidence File |
|-------|-------------|---------------|
| Cost Optimization | 40% savings | `app/cost_optimizer.py`, `/cost-optimization` endpoint |
| Audit Logs | Separated audit events | `data/audit.jsonl`, `app/logging_config.py` |
| Custom Metric | cost_per_token_usd | `app/metrics.py`, `/metrics` endpoint |

---

## Grading Checklist

### Group Level (60%)
- [x] Logging schema with JSON format
- [x] Correlation ID in every request
- [x] PII redaction (email, phone, CCCD, credit card)
- [x] >= 10 Langfuse traces
- [x] Dashboard with 6+ panels
- [x] 3+ alert rules with runbook links
- [x] Incident response documented
- [ ] Live Demo presentation

### Individual Level (40%)
- [x] Individual report for each member
- [ ] Git commits for each member

### Bonus (+10)
- [x] Cost optimization (40% savings)
- [x] Audit logs separated
- [x] Custom metric (cost_per_token_usd)
