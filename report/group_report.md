# Day 13 Observability Lab - Báo Cáo Nhóm 06

## Thông Tin Nhóm

| Trường | Giá Trị |
|--------|---------|
| Nhóm | Day13_Group06_E402 |
| Số Lượng Thành Viên | 5 |

---

## 1. Team Metadata

| # | Họ Tên | MSSV | Vai Trò |
|---|--------|------|---------|
| 1 | Nguyễn Anh Quân | 2A202600132 | Logging + PII + Middleware |
| 2 | Võ Thiên Phú | 2A202600336 | Tracing + Observability |
| 3 | Phan Dương Định | 2A202600277 | SLO + Alerts + Dashboard |
| 4 | Phạm Minh Khang | 2A202600417 | Metrics + Load Test + Incidents |
| 5 | Đào Hồng Sơn | 2A202600462 | Report + Documentation + Demo |

---

## 2. Group Performance (Auto-Verified)

| Chỉ Số | Giá Trị |
|--------|---------|
| [VALIDATE_LOGS_FINAL_SCORE] | 80/100 |
| [TOTAL_TRACES_COUNT] | 48 |
| [PII_LEAKS_FOUND] | 0 |

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing

- **Correlation ID**: Tất cả request đều có correlation_id duy nhất. Mỗi request tạo một UUID hex (36 ký tự) hoặc sử dụng giá trị từ header `x-request-id`.
- **PII Redaction**: Email, phone, CCCD, credit card đều được redact thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`.
- **Trace Waterfall**: `@trace_request(name="chat_request")` trên `/chat` endpoint. Langfuse ghi lại input/output của request.

### 3.2 Dashboard & SLOs

| SLI | Target | Window | Current Value |
|-----|--------|--------|---------------|
| Latency P95 | < 3000ms | 28d | 2650.0 ms |
| Error Rate | < 2% | 28d | 0.0% (bình thường) |
| Cost Budget | < $2.5/day | 1d | $0.1138 |

**Dashboard 7 Panels:**
1. Latency P50/P95/P99
2. Traffic / QPS
3. Error Rate & Breakdown
4. Cost Over Time
5. Tokens In/Out
6. Quality Proxy
7. Cost Per Token (bonus)

### 3.3 Alerts & Runbook

| Alert | Severity | Condition | Runbook |
|-------|----------|-----------|---------|
| high_latency_p95 | P2 | latency_p95_ms > 5000 for 30m | docs/alerts.md#1-high-latency-p95 |
| high_error_rate | P1 | error_rate_pct > 5 for 5m | docs/alerts.md#2-high-error-rate |
| cost_budget_spike | P2 | hourly_cost_usd > 2x_baseline for 15m | docs/alerts.md#3-cost-budget-spike |
| quality_drop | P3 | quality_score_avg < 0.65 for 30m | docs/alerts.md#1-high-latency-p95 |

---

## 4. Incident Response (Group)

| Scenario | Mô Tả | Cách Phát Hiện |
|----------|-------|----------------|
| rag_slow | RAG retrieval latency spike | latency_p95_ms tăng từ ~300ms lên ~2650ms |
| tool_fail | Vector store timeout | HTTP 500 responses, error_rate tăng |
| cost_spike | Token usage spike | total_cost_usd tăng nhanh |

**Fix Action**: Tắt incident bằng `python scripts/inject_incident.py --scenario <name> --disable`.

**Preventive Measure**: Thêm pre-deploy canary checks, enforce circuit breaker trên RAG calls.

---

## 5. Individual Contributions & Evidence

### Nguyễn Anh Quân (2A202600132) - Logging + PII + Middleware

**Công việc:**
- Đọc và hiểu CorrelationIdMiddleware trong `app/middleware.py`
- Đọc pipeline structlog trong `app/logging_config.py`
- Đọc PII patterns trong `app/pii.py`
- Chạy pytest `tests/test_pii.py`

**Evidence:**
- `app/middleware.py` - Correlation ID xuyên suốt
- `app/logging_config.py` - Structlog processors
- `app/pii.py` - PII regex patterns
- `data/audit.jsonl` - Bonus: audit logs tách riêng
- `report/Nguyen_Anh_Quan.md` - Báo cáo cá nhân

### Võ Thiên Phú (2A202600336) - Tracing + Observability

**Công việc:**
- Đọc `@observe` decorator trong `app/tracing.py`
- Hiểu cách Langfuse hoạt động với `propagate_attributes`
- Cấu hình Langfuse trong `.env`
- Gửi 10+ request để tạo traces

**Evidence:**
- `app/tracing.py` - Tracing pipeline
- `app/agent.py` - @observe() decorator
- `.env` - Langfuse credentials
- Langfuse Dashboard - >= 10 traces
- `report/Vo_Thien_Phu.md` - Báo cáo cá nhân

### Phan Dương Định (2A202600277) - SLO + Alerts + Dashboard

**Công việc:**
- Đọc 4 SLIs trong `config/slo.yaml`
- Đọc 4 alert rules trong `config/alert_rules.yaml`
- Đọc runbooks trong `docs/alerts.md`
- Xác nhận dashboard 7 panels trong `config/dashboard.json`

**Evidence:**
- `config/slo.yaml` - 4 SLIs định nghĩa
- `config/alert_rules.yaml` - 4 alerts với runbook links
- `docs/alerts.md` - Hướng dẫn xử lý chi tiết
- `config/dashboard.json` - 7 panels với units & thresholds
- `report/Phan_Duong_Dinh.md` - Báo cáo cá nhân

### Phạm Minh Khang (2A202600417) - Metrics + Load Test + Incidents

**Công việc:**
- Đọc metrics pipeline trong `app/metrics.py`
- Hiểu cách tính P50/P95/P99 bằng linear interpolation
- Chạy load test với concurrency 1 và 5
- Thử nghiệm incident injection (rag_slow, tool_fail, cost_spike)

**Evidence:**
- `app/metrics.py` - Metrics aggregation
- `app/cost_optimizer.py` - 40% savings
- `app/incidents.py` - Incident toggle system
- `scripts/load_test.py` - Load test script
- `scripts/inject_incident.py` - Incident injection
- `report/Pham_Minh_Khang.md` - Báo cáo cá nhân

### Đào Hồng Sơn (2A202600462) - Report + Documentation + Demo

**Công việc:**
- Hoàn thiện `docs/blueprint-template.md`
- Thu thập evidence cho grading
- Chuẩn bị nội dung demo
- Kiểm tra cuối cùng trước khi nộp

**Evidence:**
- `docs/blueprint-template.md` - Báo cáo chính
- `docs/grading-evidence.md` - Evidence collection
- `report/` - 5 báo cáo cá nhân
- `report/group_report.md` - Báo cáo nhóm (file này)

---

## 6. Bonus Items

| Bonus | Mô Tả | Evidence |
|-------|-------|----------|
| Cost Optimization | 40% savings | `/cost-optimization` endpoint trả về 40% savings |
| Audit Logs | Tách audit events | `data/audit.jsonl` được ghi bởi AuditLogProcessor |
| Custom Metric | cost_per_token_usd | Custom metric trong `/metrics` endpoint |

---

## 7. Grading Overview

| Hạng Mục | Điểm | Người Phụ Trách |
|-----------|------|------------------|
| **GROUP (60%)** | | |
| - Logging & Tracing | 10 | Quân, Phú |
| - Dashboard & SLO | 10 | Định |
| - Alerts & PII | 10 | Quân, Định |
| - Incident Response | 10 | Khang |
| - Live Demo | 20 | Tất cả |
| **INDIVIDUAL (40%)** | | |
| - Individual Report | 20 | Tất cả |
| - Git Evidence | 20 | Tất cả |
| **Bonus** | +10 | |
| **TỔNG** | **100+** | |

---

## 8. Passing Criteria

- [x] `VALIDATE_LOGS_SCORE` >= 80/100
- [x] >= 10 traces trên Langfuse
- [x] Dashboard có >= 6 panels
- [x] Blueprint đầy đủ tên thành viên

---

## 9. File List

| File | Mô Tả |
|------|-------|
| `report/Nguyen_Anh_Quan.md` | Báo cáo cá nhân - Quân |
| `report/Vo_Thien_Phu.md` | Báo cáo cá nhân - Phú |
| `report/Phan_Duong_Dinh.md` | Báo cáo cá nhân - Định |
| `report/Pham_Minh_Khang.md` | Báo cáo cá nhân - Khang |
| `report/Dao_Hong_Son.md` | Báo cáo cá nhân - Sơn |
| `report/group_report.md` | Báo cáo nhóm (file này) |
| `docs/blueprint-template.md` | Blueprint chính |
| `docs/grading-evidence.md` | Evidence collection |
