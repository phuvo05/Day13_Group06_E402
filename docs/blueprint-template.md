# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Day13_Group06_E402
- [REPO_URL]: Local repository (`/home/pmkhang/Desktop/VinUni/Lab/Day13_Group06_E402`)
- [MEMBERS]:
  - Member A: TBD_A | Role: Logging & PII
  - Member B: TBD_B | Role: Tracing & Enrichment
  - Member C: TBD_C | Role: SLO & Alerts
  - Member D: TBD_D | Role: Load Test & Dashboard
  - Member E: TBD_E | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 80/100
- [TOTAL_TRACES_COUNT]: 48 (counted from `request_received` events in `data/logs.jsonl`)
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: `data/logs.jsonl` (multiple unique `correlation_id` values, 64 unique IDs)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: `data/logs.jsonl` (redacted tokens: `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: N/A in repo (trace instrumentation active via `@trace_request(name="chat_request")` on `/chat`)
- [TRACE_WATERFALL_EXPLANATION]: In the `rag_slow` scenario, request processing latency jumps while request flow remains successful (HTTP 200), proving slowdown happens in dependency path and not in request parsing/validation. This aligns with high tail latency (`latency_p95_ms` rose to 2650.0ms) while error rate stayed 0 in that phase.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: `config/dashboard.json`
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2650.0 ms |
| Error Rate | < 2% | 28d | 33.33% (during injected `tool_fail`) |
| Cost Budget | < $2.5/day | 1d | $0.1138 cumulative run |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: `config/alert_rules.yaml`
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#1-high-latency-p95`

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow + tool_fail + cost_spike
- [SYMPTOMS_OBSERVED]: `rag_slow` increased request time to 7-13s on client side and raised `latency_p95_ms` to 2650.0ms; `tool_fail` caused 10 consecutive HTTP 500 responses and `error_rate` up to 0.5; `cost_spike` increased average/total request cost while traffic recovered with HTTP 200.
- [ROOT_CAUSE_PROVED_BY]: Logs in `data/logs.jsonl` show `request_failed` with `error_type=RuntimeError` and detail `Vector store timeout` during `tool_fail`; metrics snapshots after each scenario confirm symptom shifts (`latency_p95_ms`, `error_rate`, `total_cost_usd`).
- [FIX_ACTION]: Disable incident toggles with `python scripts/inject_incident.py --scenario <name> --disable`, then re-run load test to verify metric recovery.
- [PREVENTIVE_MEASURE]: Add pre-deploy canary checks for alert thresholds, enforce circuit breaker/retry fallback on vector store calls, and set budget guardrails to auto-throttle expensive paths.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: Logging schema, correlation ID, PII redaction verification.
- [EVIDENCE_LINK]: `9ac5e22`

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: Trace instrumentation and metadata checks.
- [EVIDENCE_LINK]: `350e2f0`

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: SLO and alert rules completion.
- [EVIDENCE_LINK]: `9ac5e22`

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: Load testing, incident injection, runtime validation.
- [EVIDENCE_LINK]: Local execution evidence (`scripts/load_test.py`, `scripts/inject_incident.py`, `scripts/validate_logs.py`)

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: Report completion and evidence collation.
- [EVIDENCE_LINK]: `docs/blueprint-template.md` updates in current working tree

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
