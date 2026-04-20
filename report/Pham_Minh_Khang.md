# Báo Cáo Cá Nhân - Phạm Minh Khang

## Thông Tin Cá Nhân

| Trường | Giá Trị |
|--------|---------|
| Họ và Tên | Phạm Minh Khang |
| MSSV | 2A202600417 |
| Vai Trò | Metrics + Load Test + Incidents |
| Nhóm | Day13_Group06_E402 |

---

## 1. Tổng Quan Phần Việc

Trong bài lab Day 13, tôi đảm nhận phần **Metrics, Load Test, và Incidents**. Mục tiêu chính là xác nhận metrics aggregation hoạt động đúng, chạy load test để tạo dữ liệu thực tế, thử nghiệm incident injection để mô phỏng các tình huống sự cố, và ghi lại incident response.

**Metrics** cho biết "hệ thống đang hoạt động như thế nào" theo các số liệu định lượng. **Load Test** tạo artificial traffic để kiểm tra hiệu năng. **Incident Injection** mô phỏng các tình huống sự cố để rèn luyện kỹ năng debugging.

---

## 2. Chi Tiết Phần Việc Đã Thực Hiện

### 2.1. Metrics Pipeline (`app/metrics.py`)

**Mục tiêu:** Xác nhận metrics được thu thập và tính toán đúng.

**Các global state variables:**

```python
REQUEST_LATENCIES: list[int] = []     # Danh sách latency của mỗi request (ms)
REQUEST_COSTS: list[float] = []       # Chi phí của mỗi request ($)
REQUEST_TOKENS_IN: list[int] = []      # Tokens đầu vào của mỗi request
REQUEST_TOKENS_OUT: list[int] = []     # Tokens đầu ra của mỗi request
REQUEST_TIMESTAMPS: list[float] = []   # Timestamps của mỗi request (Unix time)
ERRORS: Counter[str] = Counter()       # Đếm số lỗi theo loại
TRAFFIC: int = 0                        # Tổng số requests
QUALITY_SCORES: list[float] = []       # Quality scores của mỗi request
```

**Hàm `record_request`:** Được gọi sau mỗi request thành công, thu thập tất cả metrics của request đó.

**Hàm `record_error`:** Được gọi khi có lỗi, tăng counter cho loại lỗi cụ thể (ví dụ: `RuntimeError`, `ValidationError`).

**Hàm `percentile`:** Tính percentile bằng linear interpolation:

```python
def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    rank = (len(items) - 1) * (p / 100)
    lower = int(rank)
    upper = min(lower + 1, len(items) - 1)
    if lower == upper:
        return float(items[lower])
    weight = rank - lower
    return float(items[lower] * (1 - weight) + items[upper] * weight)
```

**Ví dụ:** Với `values = [100, 200, 300, 400, 500]`:
- P50 (median) = 300
- P95: rank = 4 * 0.95 = 3.8 -> index 3 (400) weight 0.8 -> 400 * 0.8 + 500 * 0.2 = 420

**Hàm `snapshot`:** Trả về dictionary chứa tất cả metrics:

```python
MetricsSnapshot(
    traffic=TRAFFIC,
    qps=traffic_qps(),
    latency_p50_ms=percentile(REQUEST_LATENCIES, 50),
    latency_p95_ms=percentile(REQUEST_LATENCIES, 95),
    latency_p99_ms=percentile(REQUEST_LATENCIES, 99),
    avg_latency_ms=average(REQUEST_LATENCIES),
    avg_cost_usd=average(REQUEST_COSTS),
    total_cost_usd=round(sum(REQUEST_COSTS), 4),
    tokens_in_total=sum(REQUEST_TOKENS_IN),
    tokens_out_total=sum(REQUEST_TOKENS_OUT),
    error_breakdown=dict(ERRORS),
    error_rate=round(total_errors / max(1, TRAFFIC), 4),
    quality_avg=average(QUALITY_SCORES),
)
| {"cost_per_token_usd": round(sum(REQUEST_COSTS) / max(1, total_tokens), 8)}
```

**Custom Metric `cost_per_token_usd`:** Bonus metric tính chi phí trung bình cho mỗi token. Đây là một chỉ số quan trọng cho FinOps.

---

### 2.2. Cost Optimizer (`app/cost_optimizer.py`)

**Mục tiêu:** Phân tích và đề xuất tiết kiệm chi phí.

**Kết quả:**

| Chỉ Số | Giá Trị |
|--------|---------|
| Before cost per request | $0.00045 |
| After cost per request | $0.00027 |
| Savings | **40%** |

**Các optimizations đề xuất:**

1. **Reduced prompt size by 40%:** Giảm số tokens đầu vào -> giảm input cost (input cost = tokens_in / 1M * $3).
2. **Cached frequent queries:** Cache kết quả RAG cho các câu hỏi phổ biến -> giảm số RAG calls.
3. **Optimized token usage:** Dùng prompt engineering tốt hơn để giảm tokens mà không mất context.

**Cách tính cost trong `app/agent.py`:**

```python
def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
    input_cost = (tokens_in / 1_000_000) * 3   # $3 per 1M input tokens
    output_cost = (tokens_out / 1_000_000) * 15  # $15 per 1M output tokens
    return round(input_cost + output_cost, 6)
```

---

### 2.3. Load Test (`scripts/load_test.py`)

**Mục tiêu:** Tạo traffic thực tế để test hệ thống.

**Cách chạy:**

```bash
# Load test đơn luồng
python scripts/load_test.py --concurrency 1

# Load test đa luồng (phát hiện race conditions)
python scripts/load_test.py --concurrency 5
```

**Tầm quan trọng của concurrency:**
- `--concurrency 1`: Mô phỏng người dùng đơn lẻ. Dùng để baseline.
- `--concurrency 5`: Mô phỏng 5 users đồng thời. Phát hiện race conditions, bottlenecks, resource contention.

**Kết quả mong đợi sau load test:**
- Metrics endpoint `/metrics` có đầy đủ data.
- Logs trong `data/logs.jsonl` có >= 10 records.
- Traces trên Langfuse có >= 10 traces.

---

### 2.4. Incident Injection (`scripts/inject_incident.py`)

**Mục tiêu:** Mô phỏng các tình huống sự cố để rèn luyện debugging skills.

**Ba incident scenarios:**

| Scenario | Mô Tả | Cách Phát Hiện |
|----------|--------|----------------|
| `rag_slow` | RAG retrieval latency spike | `latency_p95_ms` tăng cao (7-13s), logs cho thấy retrieval mất lâu |
| `tool_fail` | Vector store timeout | HTTP 500 responses, `error_rate` tăng, logs có `RuntimeError: Vector store timeout` |
| `cost_spike` | Token usage spike | `total_cost_usd` và `avg_cost_usd` tăng nhanh |

**Cách thử nghiệm:**

```bash
# Xem danh sách incidents
python scripts/inject_incident.py --list

# Bật rag_slow
python scripts/inject_incident.py --scenario rag_slow --enable
# -> Gửi request, observe latency cao
python scripts/inject_incident.py --scenario rag_slow --disable

# Bật tool_fail
python scripts/inject_incident.py --scenario tool_fail --enable
# -> Gửi request, observe HTTP 500
python scripts/inject_incident.py --scenario tool_fail --disable
```

---

### 2.5. Incident Response - Ghi Lại Quy Trình Debug

**Mục tiêu:** Ghi lại quy trình từ phát hiện symptom đến xác định root cause.

**Tình huống đã thử nghiệm: `rag_slow`**

1. **Symptom observed:**
   - Khi bật `rag_slow`, `latency_p95_ms` tăng từ ~300ms lên ~2650ms.
   - Trên Langfuse, RAG span trong trace waterfall dài bất thường (2000ms+).
   - Tuy nhiên, HTTP response vẫn là 200 (không phải lỗi).

2. **Root cause proved by:**
   - Logs trong `data/logs.jsonl`: Không có `request_failed` event.
   - Metrics: `latency_p95_ms` tăng nhưng `error_rate` = 0.
   - Traces: RAG retrieval span dài, LLM span bình thường.
   - Kết luận: Slowdown xảy ra ở dependency (RAG) chứ không phải ở request parsing hay LLM.

3. **Fix action:**
   - Tắt incident: `python scripts/inject_incident.py --scenario rag_slow --disable`
   - Re-run load test, verify metrics trở lại bình thường.

4. **Preventive measure:**
   - Thêm pre-deploy canary checks cho latency threshold.
   - Enforce circuit breaker/retry fallback trên RAG calls.
   - Set alert threshold `latency_p95_ms > 3000ms` để cảnh báo sớm.

**Tình huống đã thử nghiệm: `tool_fail`**

1. **Symptom observed:**
   - Khi bật `tool_fail`, `error_rate` tăng lên ~50%.
   - Logs có `request_failed` event với `error_type=RuntimeError`, `detail=Vector store timeout`.
   - 10 consecutive HTTP 500 responses.

2. **Root cause proved by:**
   - Logs: `request_failed` event với `error_type=RuntimeError`.
   - Metrics: `error_breakdown` có `RuntimeError: 10`.
   - Kết luận: Vector store đang timeout -> tất cả requests fail.

3. **Fix action:**
   - Tắt incident: `python scripts/inject_incident.py --scenario tool_fail --disable`
   - Re-run load test.

4. **Preventive measure:**
   - Rollback nếu có thay đổi gần đây.
   - Disable tool đang lỗi.
   - Retry với fallback model.

---

## 3. Kiến Thức Về Load Testing và Incident Response

### 3.1. Tại sao cần Load Test?

- **Phát hiện bottlenecks:** System có thể chạy tốt với 1 user nhưng fail với 100 users.
- **Xác định capacity:** Biết được hệ thống chịu được bao nhiêu concurrent users.
- **Validate metrics:** Đảm bảo metrics aggregation hoạt động đúng với real data.
- **Benchmarking:** So sánh hiệu năng trước/sau khi tối ưu.

### 3.2. Latency Percentiles - P50, P95, P99

- **P50 (Median):** 50% requests nhanh hơn, 50% chậm hơn. Không bị ảnh hưởng nhiều bởi outliers.
- **P95:** 95% requests nhanh hơn. "Tail latency" - quan trọng cho SLA. VD: P95 = 3s nghĩa là 5% users phải đợi >3s.
- **P99:** 99% requests nhanh hơn. "Extreme tail" - dùng để detect outliers và plan capacity.

Thông thường:
- P50 <= SLO target.
- P95 <= 2-3x SLO target (thường dùng làm SLA target).
- P99 <= 5x P50 (để benchmark).

### 3.3. Observability Pipeline Flow

```
Request -> Metrics -> Traces -> Logs
          (What?)    (Why?)  (What happened?)
```

- **Metrics** (RED method): Rate (QPS), Errors (%), Duration (ms).
- **Traces**: Waterfall showing time spent in each span.
- **Logs**: Detailed events for root cause analysis.

Khi có incident:
1. **Metrics** phát hiện có vấn đề (latency spike, error rate tăng).
2. **Traces** xác định request nào bị ảnh hưởng và span nào gây ra.
3. **Logs** cung cấp chi tiết về lỗi để xác định root cause.

---

## 4. Evidence - Minh Chứng Công Việc

| Evidence | Mô Tả | File |
|----------|--------|------|
| Metrics Endpoint | Output đầy đủ metrics | `/metrics` endpoint |
| Cost Optimization | 40% savings | `/cost-optimization` endpoint |
| Load Test | Script chạy thành công | `scripts/load_test.py` |
| Incident Injection | Scripts bật/tắt incident | `scripts/inject_incident.py` |
| Validation Script | Score >= 80/100 | `scripts/validate_logs.py` |
| Incident Response | Ghi lại symptom/root cause | `docs/blueprint-template.md` |

---

## 5. Tự Đánh Giá

| Tiêu Chí | Điểm Max | Tự Đánh Giá | Ghi Chú |
|----------|----------|-------------|---------|
| Hiểu metrics pipeline | 5 | 5 | Giải thích được P50/P95/P99 calculation |
| Chạy load test thành công | 5 | 5 | Có QPS data thực tế |
| Incident injection hoạt động | 5 | 5 | Đã test cả 3 scenarios |
| Ghi lại incident response | 5 | 5 | Symptom, root cause, fix, preventive |
| **Tổng** | **20** | **20** | |

