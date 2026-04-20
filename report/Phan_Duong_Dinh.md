# Báo Cáo Cá Nhân - Phan Dương Định

## Thông Tin Cá Nhân

| Trường | Giá Trị |
|--------|---------|
| Họ và Tên | Phan Dương Định |
| MSSV | 2A202600277 |
| Vai Trò | SLO + Alerts + Dashboard |
| Nhóm | Day13_Group06_E402 |

---

## 1. Tổng Quan Phần Việc

Trong bài lab Day 13, tôi đảm nhận phần **SLO (Service Level Objectives), Alerts, và Dashboard**. Mục tiêu chính là xây dựng các định nghĩa SLO hợp lý, cấu hình alert rules với runbook, và tạo dashboard 6 panels phục vụ giám sát hệ thống theo thời gian thực.

**SLO** là cam kết về mức độ service mà team phải đạt được. **Alert** là cảnh báo khi SLO bị vi phạm. **Dashboard** là giao diện trực quan hóa các metrics để theo dõi SLO.

---

## 2. Chi Tiết Phần Việc Đã Thực Hiện

### 2.1. SLO Definitions (`config/slo.yaml`)

**Mục tiêu:** Định nghĩa các SLI (Service Level Indicator) và SLO (Service Level Objective) hợp lý cho hệ thống.

**Service Level Objective (SLO)** là cam kết về hiệu suất service. Nó gồm:
- **SLI** (Service Level Indicator): Chỉ số đo lường cụ thể.
- **Target**: Giá trị mục tiêu cần đạt.
- **Window**: Khoảng thời gian đo lường.

**Bốn SLIs đã được định nghĩa:**

| SLI | Indicator | Objective | Target | Window | Giải Thích |
|-----|-----------|-----------|--------|--------|------------|
| Latency P95 | `latency_p95_ms` | < 3000ms | 99.5% | 28 ngày | Tail latency (P95) là chỉ số quan trọng nhất cho trải nghiệm người dùng. 95% requests phải hoàn thành trong 3 giây. Target 99.5% nghĩa là cho phép 0.5% outliers. |
| Error Rate | `error_rate_pct` | < 2% | 99.0% | 28 ngày | Tỷ lệ request thất bại (HTTP 500) phải dưới 2%. Target 99% nghĩa là 99% requests phải thành công. |
| Daily Cost | `daily_cost_usd` | < $2.5 | 100% | 1 ngày | Chi phí hàng ngày không vượt quá $2.5 (giới hạn của bài assignment). |
| Quality Score | `quality_score_avg` | >= 0.75 | 95% | 28 ngày | Điểm chất lượng câu trả lời trung bình (heuristic) phải >= 0.75. Target 95% nghĩa là 95% requests phải có quality score >= 0.75. |

**Cách hoạt động của Quality Score (`app/agent.py`):**

```python
def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
    score = 0.5
    if docs:
        score += 0.2        # +0.2 nếu có retrieved documents
    if len(answer) > 40:
        score += 0.1        # +0.1 nếu câu trả lời đủ dài (>40 chars)
    if any(token in answer.lower() for token in question.lower().split()[:3]):
        score += 0.1        # +0.1 nếu câu trả lời chứa keywords từ câu hỏi
    if "[REDACTED" in answer:
        score -= 0.2        # -0.2 nếu có PII leak trong câu trả lời
    return round(max(0.0, min(1.0, score)), 2)
```

---

### 2.2. Alert Rules (`config/alert_rules.yaml`)

**Mục tiêu:** Cấu hình các alert rules để cảnh báo khi hệ thống có vấn đề.

**Bốn alert rules đã được định nghĩa:**

| Alert | Severity | Condition | Owner | Runbook |
|-------|----------|-----------|-------|---------|
| `high_latency_p95` | P2 | `latency_p95_ms > 5000` for 30m | team-oncall | `docs/alerts.md#1-high-latency-p95` |
| `high_error_rate` | P1 | `error_rate_pct > 5` for 5m | team-oncall | `docs/alerts.md#2-high-error-rate` |
| `cost_budget_spike` | P2 | `hourly_cost_usd > 2x_baseline` for 15m | finops-owner | `docs/alerts.md#3-cost-budget-spike` |
| `quality_drop` | P3 | `quality_score_avg < 0.65` for 30m | product-oncall | `docs/alerts.md#1-high-latency-p95` |

**Phân biệt Severity:**

- **P1 (Critical):** Người dùng bị ảnh hưởng nghiêm trọng. Cần phản hồi ngay lập tức. Ví dụ: Error rate > 5% -> users không nhận được câu trả lời.
- **P2 (Warning):** Có vấn đề nhưng không nghiêm trọng. Cần theo dõi và có kế hoạch xử lý. Ví dụ: Latency tăng cao nhưng vẫn có response.
- **P3 (Info):** Cảnh báo sớm (early warning). Không cần hành động ngay nhưng cần theo dõi xu hướng. Ví dụ: Quality score giảm dần.

**Runbook:** Mỗi alert cần có link đến runbook để on-call engineer biết phải làm gì khi nhận cảnh báo.

---

### 2.3. Runbooks (`docs/alerts.md`)

**Mục tiêu:** Cung cấp hướng dẫn xử lý chi tiết cho từng alert.

Tôi đã đọc và hiểu các runbooks trong `docs/alerts.md`:

**Alert 1 - High Latency P95:**

- **Trigger:** `latency_p95_ms > 5000ms` trong 30 phút.
- **Impact:** Tail latency vượt SLO, trải nghiệm người dùng kém.
- **First checks:**
  1. Mở top slow traces trong 1 giờ gần nhất trên Langfuse.
  2. So sánh thời gian RAG span vs LLM span.
  3. Kiểm tra xem incident toggle `rag_slow` có được bật không.
- **Mitigation:**
  - Truncate câu hỏi quá dài.
  - Fallback sang retrieval source khác.
  - Giảm prompt size.

**Alert 2 - High Error Rate:**

- **Trigger:** `error_rate_pct > 5%` trong 5 phút.
- **Impact:** Users nhận failed responses.
- **First checks:**
  1. Group logs theo `error_type`.
  2. Inspect các failed traces.
  3. Xác định lỗi thuộc LLM, tool, hay schema.
- **Mitigation:**
  - Rollback thay đổi gần nhất.
  - Disable tool đang lỗi.
  - Retry với fallback model.

**Alert 3 - Cost Budget Spike:**

- **Trigger:** `hourly_cost_usd > 2x_baseline` trong 15 phút.
- **Impact:** Chi phí tăng nhanh hơn dự kiến.
- **First checks:**
  1. Split traces theo feature và model.
  2. So sánh `tokens_in` vs `tokens_out`.
  3. Kiểm tra xem incident `cost_spike` có được bật không.
- **Mitigation:**
  - Rút gọn prompts.
  - Route requests đơn giản sang model rẻ hơn.
  - Bật prompt cache.

---

### 2.4. Dashboard 6 Panels (`config/dashboard.json`)

**Mục tiêu:** Tạo dashboard trực quan với 6 panels theo spec.

**Cấu trúc dashboard:**

```json
{
  "title": "Day 13 Observability Dashboard",
  "timeRange": "1h",
  "refresh": "15s",
  "layout": "6-panel",
  "panels": [ ... ]
}
```

**Bảy panels (6 required + 1 bonus):**

| # | Title | Type | Unit | Threshold | Mô Tả |
|---|-------|------|------|-----------|--------|
| 1 | Latency P50/P95/P99 | timeseries | ms | SLO P95 < 3000ms | Ba đường cong latency cho thấy phân bố thời gian phản hồi. P50 = median, P95 = 95th percentile, P99 = 99th percentile. |
| 2 | Traffic / QPS | timeseries | req/min | Target throughput | Số request trên phút. QPS = Queries Per Second. Giúp phát hiện traffic spike. |
| 3 | Error Rate & Breakdown | bar+timeseries | % | SLO < 2% | Tỷ lệ lỗi theo thời gian + breakdown theo error type. Giúp xác định loại lỗi phổ biến nhất. |
| 4 | Cost Over Time | timeseries | $ | Budget < $2.5/day | Chi phí tích lũy theo thời gian. Giúp theo dõi burn rate. |
| 5 | Tokens In/Out | timeseries | tokens | - | Số tokens đầu vào và đầu ra. Giúp ước tính chi phí LLM. |
| 6 | Quality Proxy | timeseries | score | Target >= 0.8 | Điểm chất lượng câu trả lời (heuristic). Giúp phát hiện quality drop. |
| 7 (bonus) | Cost Per Token | stat | $/token | Budget < $0.000005/token | Chi phí trung bình cho mỗi token. Custom metric phục vụ cost optimization. |

**Các thuộc tính quan trọng của mỗi panel:**

- **`timeRange: "1h"`:** Mặc định hiển thị 1 giờ gần nhất - phù hợp cho lab demo.
- **`refresh: "15s"`:** Tự động refresh mỗi 15 giây - đủ nhanh để thấy thay đổi mà không gây lag.
- **`thresholds`:** Đường thẳng đứng hiển thị SLO target trên chart - giúp trực quan thấy đang trên hay dưới SLO.
- **`unit`:** Đơn vị rõ ràng (ms, %, $, tokens) - tránh confusion.

---

## 3. Kiến Thức Về SLO và Alerting

### 3.1. Error Budget

Error Budget = `1 - Target SLO`. Ví dụ: Nếu SLO là 99.9%, error budget là 0.1%.

- **Error budget > 0:** Team có thể deploy thay đổi mới (vì vẫn còn budget để "tiêu").
- **Error budget = 0 hoặc âm:** Team phải dừng deploy, tập trung cải thiện reliability.

Trong bài lab này, Error Budget của error_rate SLO = `1 - 99% = 1%`. Nghĩa là trong 28 ngày, hệ thống được phép có tối đa ~6.7 giờ downtime/error time.

### 3.2. Toil vs Feature Work

Alert fatigue là vấn đề lớn. Nếu alert quá nhạy (false positive cao), engineers sẽ bỏ qua alerts -> miss real incidents. Nếu alert quá ít nhạy (false negative cao), incidents xảy ra mà không được alert -> users bị ảnh hưởng.

Cách tốt nhất:
- Alert trên **symptom-based** metrics (latency cao, error rate cao) thay vì **cause-based** metrics (RAG slow, LLM timeout).
- Symptom-based alerts ít bị false positive hơn vì chúng chỉ trigger khi users thực sự bị ảnh hưởng.

### 3.3. Dashboard Design Principles

1. **Tập trung vào SLO:** Dashboard nên hiển thị metrics liên quan trực tiếp đến SLO, không phải mọi metrics có thể có.
2. **USE Method:** Đối với resources: **U**tilization, **S**aturation, **E**rrors.
3. **RED Method:** Đối với services: **R**ate (QPS), **E**rrors (error rate), **D**uration (latency).
4. **Đơn vị rõ ràng:** Không có unit ambiguity. "100" có thể là bytes, ms, requests - cần ghi rõ.

---

## 4. Evidence - Minh Chứng Công Việc

| Evidence | Mô Tả | File |
|----------|--------|------|
| SLO Config | 4 SLIs định nghĩa đầy đủ | `config/slo.yaml` |
| Alert Rules | 4 alerts với runbook links | `config/alert_rules.yaml` |
| Runbooks | Hướng dẫn xử lý chi tiết | `docs/alerts.md` |
| Dashboard | 7 panels với units & thresholds | `config/dashboard.json` |
| SLO Table | Bảng SLO trong blueprint | `docs/blueprint-template.md` |

---

## 5. Tự Đánh Giá

| Tiêu Chí | Điểm Max | Tự Đánh Giá | Ghi Chú |
|----------|----------|-------------|---------|
| Hiểu SLO config | 5 | 5 | Giải thích được 4 SLIs, error budget |
| Alert rules đầy đủ | 5 | 5 | 4 alerts với runbook links |
| Dashboard 6+ panels | 5 | 5 | 7 panels (6 required + 1 bonus) |
| Cập nhật blueprint | 5 | 5 | SLO table + Member C section |
| **Tổng** | **20** | **20** | |

