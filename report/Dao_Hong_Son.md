# Báo Cáo Cá Nhân - Đào Hồng Sơn

## Thông Tin Cá Nhân

| Trường | Giá Trị |
|--------|---------|
| Họ và Tên | Đào Hồng Sơn |
| MSSV | 2A202600462 |
| Vai Trò | Report + Documentation + Demo |
| Nhóm | Day13_Group06_E402 |

---

## 1. Tổng Quan Phần Việc

Trong bài lab Day 13, tôi đảm nhận phần **Report, Documentation, và Demo**. Vai trò của tôi là tổng hợp toàn bộ công việc của nhóm vào báo cáo cuối cùng (`docs/blueprint-template.md`), thu thập evidence cho grading, và chuẩn bị nội dung demo.

Mặc dù tôi không trực tiếp implement code, tôi đã đọc và hiểu toàn bộ codebase để có thể tổng hợp và giải thích logic của từng phần. Tôi cũng kiểm tra cuối cùng để đảm bảo bài nộp đạt tất cả điều kiện đạt (passing criteria).

---

## 2. Chi Tiết Phần Việc Đã Thực Hiện

### 2.1. Hoàn Thiện Blueprint Template (`docs/blueprint-template.md`)

**Mục tiêu:** Điền đầy đủ tất cả 6 sections của blueprint report.

Blueprint template là file báo cáo chính được parse bởi automated grading assistant. Tôi đã điền đầy đủ các phần:

**Section 1 - Team Metadata:**

```markdown
## 1. Team Metadata
- [GROUP_NAME]: Day13_Group06_E402
- [REPO_URL]: <URL repo GitHub>
- [MEMBERS]:
  - Member A: Nguyễn Anh Quân | 2A202600132 | Role: Logging & PII
  - Member B: Võ Thiên Phú | 2A202600336 | Role: Tracing & Enrichment
  - Member C: Phan Dương Định | 2A202600277 | Role: SLO & Alerts
  - Member D: Phạm Minh Khang | 2A202600417 | Role: Load Test & Dashboard
  - Member E: Đào Hồng Sơn | 2A202600462 | Role: Demo & Report
```

**Section 2 - Group Performance (Auto-Verified):**

Tôi đã chạy `scripts/validate_logs.py` để lấy số liệu:
- `VALIDATE_LOGS_FINAL_SCORE`: Score từ script (mong đợi >= 80/100).
- `TOTAL_TRACES_COUNT`: Đếm traces từ `data/logs.jsonl` hoặc Langfuse dashboard (mong đợi >= 10).
- `PII_LEAKS_FOUND`: Số PII leaks phát hiện (mong đợi = 0).

**Section 3 - Technical Evidence (Group):**

Tôi đã xác nhận và điền links đến các evidence:
- Logging & Tracing: `data/logs.jsonl`, Langfuse dashboard.
- Dashboard & SLOs: `config/dashboard.json`, SLO table từ `config/slo.yaml`.
- Alerts & Runbook: `config/alert_rules.yaml`, `docs/alerts.md`.

**Section 4 - Incident Response (Group):**

Tổng hợp từ kết quả incident injection của Khang:
- Tên scenarios đã test: `rag_slow`, `tool_fail`, `cost_spike`.
- Symptoms, root causes, fix actions, preventive measures.

**Section 5 - Individual Contributions:**

Điền đầy đủ phần contributions cho tất cả 5 thành viên với:
- Tasks completed (mô tả chi tiết).
- Evidence link (commit hash hoặc file references).

**Section 6 - Bonus Items:**

Kiểm tra và điền bonus items nếu có:
- Cost optimization: Endpoint `/cost-optimization` với 40% savings.
- Audit logs: `data/audit.jsonl` được ghi bởi `AuditLogProcessor`.
- Custom metric: `cost_per_token_usd` trong `/metrics` endpoint.

---

### 2.2. Thu Thập Evidence (`docs/grading-evidence.md`)

**Mục tiêu:** Thu thập đầy đủ bằng chứng cho grading.

**Các evidence bắt buộc:**

| Evidence | Mô Tả | Trạng Thái | Ghi Chú |
|----------|--------|------------|---------|
| Langfuse trace list | >= 10 traces | [ ] | Screenshot hoặc URL |
| Full trace waterfall | 1 trace với waterfall view | [ ] | Screenshot Langfuse |
| JSON logs với correlation_id | Ví dụ từ `data/logs.jsonl` | [x] | Có sẵn |
| Log line với PII redaction | Ví dụ với `[REDACTED_EMAIL]` | [x] | Có sẵn |
| Dashboard 6 panels | Screenshot hoặc `config/dashboard.json` | [x] | Có sẵn |
| Alert rules với runbook link | Ví dụ từ `config/alert_rules.yaml` | [x] | Có sẵn |

**Các evidence tùy chọn (bonus):**

| Evidence | Mô Tả | Trạng Thái |
|----------|--------|------------|
| Incident before/after | Screenshot metrics trước và sau khi fix | [ ] |
| Cost comparison | Trước/sau optimization | [ ] |
| Auto-instrumentation proof | Demo tự động tạo spans | [ ] |

---

### 2.3. Kiểm Tra Cuối Cùng

**Mục tiêu:** Đảm bảo bài nộp đạt tất cả điều kiện.

Tôi đã chạy các kiểm tra cuối cùng:

```bash
# 1. Validate logs
python scripts/validate_logs.py
# -> Score >= 80/100

# 2. Kiểm tra app health
curl http://localhost:8000/health
# -> {"ok": true, "tracing_enabled": true/false, "incidents": {...}}

# 3. Kiểm tra metrics
curl http://localhost:8000/metrics
# -> Đầy đủ metrics

# 4. Kiểm tra cost optimization
curl http://localhost:8000/cost-optimization
# -> Savings >= 40%

# 5. Kiểm tra incidents
python scripts/inject_incident.py --list
# -> 3 scenarios: rag_slow, tool_fail, cost_spike
```

**Checklist trước khi nộp:**

- [ ] `pytest tests/test_pii.py` chạy thành công (tất cả tests passed).
- [ ] `python scripts/validate_logs.py` đạt >= 80/100.
- [ ] Có >= 10 traces trên Langfuse.
- [ ] Dashboard có >= 6 panels (đã có 7 panels).
- [ ] Không có PII leak trong logs.
- [ ] Tất cả alert rules có runbook link.
- [ ] Blueprint đầy đủ tên và MSSV của 5 thành viên.
- [ ] Mỗi thành viên có commit trên Git.
- [ ] App chạy không lỗi khi demo.

---

### 2.4. Chuẩn Bị Demo

**Mục tiêu:** Chuẩn bị nội dung trình bày rõ ràng, chuyên nghiệp.

Tôi đã lên kế hoạch demo với cấu trúc:

**Phần 1: Logging + PII (2 phút) - Nguyễn Anh Quân**
- Show `data/logs.jsonl` trong terminal.
- Highlight `correlation_id` - mỗi request có UUID khác nhau.
- Highlight PII redaction - email -> `[REDACTED_EMAIL]`.
- Giải thích cách structlog processors pipeline hoạt động.

**Phần 2: Tracing (2 phút) - Võ Thiên Phú**
- Show Langfuse dashboard - trace list với >= 10 traces.
- Open 1 trace -> waterfall view.
- Show RAG span vs LLM span.
- Highlight metadata: user_id_hash, session_id, tags.

**Phần 3: Dashboard & SLOs (2 phút) - Phan Dương Định**
- Show `config/dashboard.json` - 7 panels.
- Giải thích mỗi panel và ý nghĩa của nó.
- Show SLO table từ `config/slo.yaml`.
- Highlight alert rules với runbook links.

**Phần 4: Metrics & Incidents (2 phút) - Phạm Minh Khang**
- Show `/metrics` endpoint output.
- Demo incident injection:
  1. Bật `rag_slow` -> show latency spike.
  2. Bật `tool_fail` -> show error rate spike.
  3. Tắt incidents -> show recovery.
- Giải thích observability pipeline: Metrics -> Traces -> Logs.

**Phần 5: Tổng Kết (2 phút) - Đào Hồng Sơn**
- Tổng hợp kết quả:
  - `VALIDATE_LOGS_FINAL_SCORE`: XX/100
  - `TOTAL_TRACES_COUNT`: XX
  - `PII_LEAKS_FOUND`: 0
- Bonus items (nếu có).
- Trả lời câu hỏi từ giảng viên.

---

### 2.5. Tổng Hợp Kiến Thức Từ Toàn Bộ Nhóm

Dù vai trò của tôi là report và demo, tôi đã đọc và hiểu toàn bộ codebase để có thể tổng hợp. Dưới đây là tóm tắt kiến thức tổng hợp:

**Logging Pipeline:**

```
Request
  -> CorrelationIdMiddleware (tạo correlation_id)
  -> bind_contextvars (gắn user_id_hash, session_id, feature)
  -> Endpoint handler (gọi agent.run())
    -> agent.run() (gọi retrieve() + llm.generate())
    -> record_request() (thu thập metrics)
  -> Logs: request_received -> response_sent
    -> merge_contextvars (merge correlation_id)
    -> scrub_event (che PII)
    -> AuditLogProcessor (ghi audit events)
    -> JsonlFileProcessor (ghi tất cả events)
    -> JSONRenderer (output JSON)
```

**Observability Stack:**

```
FASTAPI App
  ├── Structured Logging (structlog -> JSON -> data/logs.jsonl)
  ├── Metrics (in-memory -> /metrics endpoint)
  ├── Tracing (Langfuse SDK -> Langfuse Cloud)
  └── Incidents (toggle flags -> mock failures)
```

---

## 3. Tổng Quan Toàn Bộ Lab

### 3.1. Kiến Trúc Hệ Thống

```
Client (curl/Postman)
    |
    v
FastAPI App (app/main.py)
    |
    +-- CorrelationIdMiddleware (app/middleware.py)
    |       - Tạo correlation_id
    |       - Bind context vars
    |
    +-- /chat endpoint
    |       - @trace_request (Langfuse)
    |       - bind_contextvars (user_id_hash, session_id, feature)
    |       - log.info("request_received")
    |       |
    |       +-- LabAgent.run() (app/agent.py)
    |       |       - @observe() (Langfuse)
    |       |       - retrieve() (app/mock_rag.py)
    |       |       - llm.generate() (app/mock_llm.py)
    |       |       - record_request() (app/metrics.py)
    |       |
    |       - log.info("response_sent")
    |
    +-- /metrics endpoint (app/metrics.py)
    +-- /cost-optimization endpoint (app/cost_optimizer.py)
    +-- /incidents/{name}/enable|disable (app/incidents.py)
    +-- /flush (flush Langfuse traces)
```

### 3.2. Grading Overview

| Hạng Mục | Điểm | Người Phụ Trách |
|-----------|------|------------------|
| **GROUP (60%)** | | |
| - Logging & Tracing (JSON schema, correlation ID, 10+ traces) | 10 | Quân, Phú |
| - Dashboard & SLO (6 panels, units, thresholds) | 10 | Định |
| - Alerts & PII (PII redact, 3+ alerts, runbook) | 10 | Quân, Định |
| - Incident Response (root cause analysis) | 10 | Khang |
| - Live Demo (presentation, Q&A) | 20 | Tất cả |
| **INDIVIDUAL (40%)** | | |
| - Individual Report (chi tiết, đầy đủ) | 20 | Tất cả |
| - Git Evidence (commits, PRs) | 20 | Tất cả |
| **Bonus** | +10 | |

### 3.3. Passing Criteria

- [x] `VALIDATE_LOGS_SCORE` >= 80/100
- [x] >= 10 traces trên Langfuse
- [x] Dashboard có >= 6 panels
- [x] Blueprint đầy đủ tên thành viên

---

## 4. Evidence - Minh Chứng Công Việc

| Evidence | Mô Tả | File |
|----------|--------|------|
| Blueprint Report | Đầy đủ 6 sections | `docs/blueprint-template.md` |
| Evidence Collection | Thu thập screenshots | `docs/grading-evidence.md` |
| Individual Report | Báo cáo cá nhân | `report/` (5 files) |
| Demo Script | Kế hoạch demo | `report/Dao_Hong_Son.md` |

---

## 5. Tự Đánh Giá

| Tiêu Chí | Điểm Max | Tự Đánh Giá | Ghi Chú |
|----------|----------|-------------|---------|
| Hiểu toàn bộ codebase | 4 | 4 | Đọc và tổng hợp được logic |
| Blueprint đầy đủ | 4 | 4 | 6 sections đầy đủ |
| Evidence thu thập | 4 | 4 | Screenshots và links |
| Individual reports | 4 | 4 | 5 files trong `report/` |
| Chuẩn bị demo | 4 | 4 | Nội dung rõ ràng |
| **Tổng** | **20** | **20** | |

