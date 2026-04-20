# Evidence Collection Sheet

## Required Screenshots

| # | Evidence Item | File Path | Status |
|---|--------------|-----------|--------|
| 1 | Langfuse trace list showing >= 10 traces | `docs/evidence/langfuse-trace-list.png` | To be captured after running load test |
| 2 | One full trace waterfall with 4+ spans | `docs/evidence/langfuse-waterfall.png` | To be captured after running load test |
| 3 | JSON logs showing `correlation_id` in every entry | `docs/evidence/correlation-id-logs.png` | To be captured from `data/logs.jsonl` |
| 4 | Log line with PII redaction (email/phone/CC) | `docs/evidence/pii-redaction.png` | To be captured from `data/logs.jsonl` |
| 5 | Dashboard with 6 panels all populated | `docs/evidence/grafana-dashboard.png` | To be captured from Grafana |
| 6 | Alert rules with runbook links | `docs/evidence/alert-rules.png` | To be captured from alert manager |

## Optional Screenshots

| # | Evidence Item | File Path |
|---|--------------|-----------|
| 7 | Incident before/after fix (e.g., latency before vs. after disabling rag_slow) | `docs/evidence/incident-before-after.png` |
| 8 | Cost comparison before/after optimization | `docs/evidence/cost-comparison.png` |
| 9 | Audit log entries (`data/audit.jsonl`) | `docs/evidence/audit-logs.png` |

## How to Capture Screenshots

### 1. Langfuse Trace List
1. Open Langfuse dashboard at `https://cloud.langfuse.com`
2. Navigate to your project
3. Run `python scripts/load_test.py --concurrency 5`
4. Take screenshot of the traces list panel

### 2. Trace Waterfall
1. Click on any trace in the Langfuse list
2. Take screenshot of the waterfall view showing all spans

### 3. Correlation ID in Logs
```bash
# Show first 5 log entries with correlation_id
head -n 5 data/logs.jsonl | python -m json.tool
```
Screenshot the formatted JSON output.

### 4. PII Redaction
```bash
# Show a log entry that would have contained PII
grep -i "student@vinuni.edu.vn\|4111\|090" data/logs.jsonl || echo "No PII found - redaction working!"
```
Screenshot the output.

### 5. Grafana Dashboard
1. Import dashboard JSON from `docs/dashboard-spec.md`
2. Run load test
3. Take screenshot of all 6 panels

### 6. Alert Rules
1. Open your alert management tool (Grafana Alerts, PagerDuty, etc.)
2. Screenshot showing all 3 alert rules with runbook links

## Validation Commands

```bash
# Run load test to generate traces
python scripts/load_test.py --concurrency 5 --count 10

# Validate logs
python scripts/validate_logs.py

# Run full validation (bonus script)
python scripts/run_full_validation.py --concurrency 5 --count 10
```

## Expected Results

After running `python scripts/load_test.py --concurrency 5`:
- `data/logs.jsonl` should contain ~50+ entries
- Langfuse should show ~50 traces
- `python scripts/validate_logs.py` should report:
  - Score: >= 80/100
  - PII leaks: 0
  - Correlation ID gaps: 0
  - Unique correlation IDs: >= 10
