# Báo Cáo Cá Nhân - Võ Thiên Phú

## Thông Tin Cá Nhân

| Trường | Giá Trị |
|--------|---------|
| Họ và Tên | Võ Thiên Phú |
| MSSV | 2A202600336 |
| Vai Trò | Tracing + Observability |
| Nhóm | Day13_Group06_E402 |

---

## 1. Tổng Quan Phần Việc

Trong bài lab Day 13, tôi đảm nhận phần **Tracing và Observability**. Mục tiêu chính là kích hoạt Langfuse tracing cho ứng dụng FastAPI, đảm bảo có ít nhất 10 traces được ghi lại với đầy đủ metadata phục vụ debug và phân tích incident.

Observability bao gồm ba trụ cột: **Logs**, **Metrics**, và **Traces**. Trong khi logs cho biết "điều gì đã xảy ra" và metrics cho biết "hệ thống đang hoạt động như thế nào", thì traces cho biết "tại sao nó xảy ra" - đặc biệt quan trọng trong các hệ thống phân tán nơi một request đi qua nhiều thành phần.

---

## 2. Chi Tiết Phần Việc Đã Thực Hiện

### 2.1. Tracing Pipeline - Langfuse (`app/tracing.py`)

**Mục tiêu:** Cấu hình Langfuse để ghi lại traces của các request.

**Cách hoạt động:**

Tôi đã đọc và hiểu `app/tracing.py`. Đây là module trung tâm cho việc tracing với Langfuse.

**Kiểm tra availability:**

```python
try:
    from langfuse import observe, Langfuse
    if tracing_enabled():
        langfuse_context = Langfuse()
    else:
        langfuse_context = None
    _langfuse_available = True
except ImportError:
    _langfuse_available = False
    langfuse_context = None

    def observe(*args, **kwargs):
        def decorator(func):
            @wraps(func)
            def wrapper(*a, **kw):
                return func(*a, **kw)
            return wrapper
        return decorator
```

Điểm đáng chú ý: Nếu Langfuse không được cài đặt hoặc không được cấu hình (thiếu keys), các decorators `@observe` sẽ trở thành no-op decorators - không làm gì cả nhưng cũng không gây lỗi. Điều này đảm bảo app vẫn chạy được dù không có tracing.

**Hàm `tracing_enabled()`:**

```python
def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
```

Chỉ cần đặt cả hai biến môi trường `LANGFUSE_PUBLIC_KEY` và `LANGFUSE_SECRET_KEY` là tracing được kích hoạt.

**Decorator `@trace_request`:**

```python
def trace_request(name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        if not _langfuse_available or not tracing_enabled():
            return func
        return observe(name=name, capture_input=True, capture_output=True)(func)
    return decorator
```

Decorator này wrap một async function, ghi lại input và output của function đó vào Langfuse.

---

### 2.2. Kích Hoạt Tracing trên Chat Endpoint (`app/main.py`)

**Mục tiêu:** Đảm bảo `/chat` endpoint được trace.

**Cách hoạt động:**

Trong `app/main.py`, endpoint `/chat` đã được decorate với `@trace_request(name="chat_request")`:

```python
@app.post("/chat", response_model=ChatResponse)
@trace_request(name="chat_request")
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # ... xử lý request ...
```

Khi một request POST đến `/chat` được gửi:
1. `CorrelationIdMiddleware` tạo `correlation_id`.
2. `@trace_request` bắt đầu một trace trong Langfuse.
3. Code xử lý request chạy.
4. Kết quả (input/output) được capture bởi Langfuse.

---

### 2.3. Tracing trong Agent (`app/agent.py`)

**Mục tiêu:** Gắn thêm metadata vào trace.

**Cách hoạt động:**

Trong `app/agent.py`, class `LabAgent` có method `run()` được decorate với `@observe()`:

```python
class LabAgent:
    @observe()
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        with propagate_attributes(
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", feature, self.model],
        ):
            # ... xử lý ...
            langfuse_context.update_current_span(
                metadata={"doc_count": len(docs), "query_preview": summarize_text(message)},
            )
```

**Điểm quan trọng:**

- **`@observe()` decorator:** Tự động tạo một trace span cho method này. Traces trong Langfuse sẽ có cấu trúc hierarchical - trace của `/chat` endpoint chứa trace của `LabAgent.run()`.
- **`propagate_attributes`:** Gắn các attributes vào trace context:
  - `user_id`: Được hash để không lộ PII (dùng `hash_user_id`).
  - `session_id`: ID của phiên làm việc.
  - `tags`: Labels phục vụ filter/grouping trong Langfuse (ví dụ: `["lab", "qa", "claude-sonnet-4-5"]`).
- **`update_current_span`:** Cập nhật metadata bổ sung sau khi xử lý:
  - `doc_count`: Số lượng documents retrieved từ RAG.
  - `query_preview`: Câu hỏi đã được scrub và cắt ngắn.

**Waterfall của một trace:**

```
/chat (root span)
  └── LabAgent.run (child span)
        ├── RAG retrieval (grandchild span - trong mock_rag.py)
        └── LLM generation (grandchild span - trong mock_llm.py)
```

---

### 2.4. Cấu Hình Langfuse (`.env`)

**Mục tiêu:** Kích hoạt tracing bằng cách cấu hình credentials.

Tôi đã tạo/cấu hình file `.env` với các biến cần thiết:

```
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
APP_NAME=day13-observability-lab
APP_ENV=dev
```

**Cách lấy Langfuse keys:**
1. Đăng ký tài khoản tại https://cloud.langfuse.com (free tier có 50k traces/tháng).
2. Tạo một project mới.
3. Copy Public Key và Secret Key từ project settings.
4. Paste vào file `.env`.

---

### 2.5. Tạo Traces - Gửi Request

**Mục tiêu:** Tạo ít nhất 10 traces để đáp ứng điều kiện đạt của bài lab.

Tôi đã gửi 15-20 request để tạo traces:

**Cách 1 - Dùng load test script:**

```bash
python scripts/load_test.py --concurrency 1
```

**Cách 2 - Dùng curl:**

```bash
for i in {1..15}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":\"user_$i\",\"session_id\":\"sess_$i\",\"feature\":\"qa\",\"message\":\"Question $i\"}"
done
```

**Kết quả:** Có >= 15 traces trên Langfuse dashboard.

---

### 2.6. Flush Traces

**Mục tiêu:** Đảm bảo tất cả traces được gửi lên Langfuse server.

Sau khi gửi request, tôi gọi endpoint `/flush`:

```bash
curl -X POST http://localhost:8000/flush
```

Điều này gọi `langfuse_context.flush()` để đảm bảo tất cả buffered traces được gửi lên server trước khi đóng app.

---

## 3. Kiến Thức Về Observability

### 3.1. Three Pillars of Observability

**Logs:** Nhật ký sự kiện, cho biết "điều gì đã xảy ra". Ví dụ: "User John gửi câu hỏi về observability lúc 10:30:15".

**Metrics:** Các số liệu định lượng, cho biết "hệ thống đang hoạt động như thế nào". Ví dụ: "P95 latency = 2500ms", "Error rate = 0.5%".

**Traces:** Chuỗi các spans cho biết "tại sao nó xảy ra và ở đâu". Ví dụ: "Request mất 2500ms vì RAG retrieval mất 2000ms, LLM generation mất 400ms, network mất 100ms".

### 3.2. Tại sao cần Distributed Tracing?

Trong kiến trúc microservices, một request đơn lẻ có thể đi qua:
1. API Gateway
2. Authentication Service
3. Rate Limiter
4. RAG Retrieval Service
5. LLM Service
6. Response Formatter

Nếu không có distributed tracing, việc xác định "tại sao request này chậm?" rất khó khăn. Với distributed tracing, ta có thể thấy waterfall và xác định chính xác span nào gây chậm.

### 3.3. OpenTelemetry vs Langfuse

- **OpenTelemetry (OTel):** Standard industry cho distributed tracing. Vendor-neutral, hỗ trợ nhiều backends (Jaeger, Zipkin, Datadog, ...).
- **Langfuse:** Một SaaS platform xây trên OpenTelemetry, tập trung vào LLM tracing. Có giao diện đẹp, hỗ trợ prompt versioning, evaluation, và cost tracking.

Trong bài lab này, ta dùng Langfuse vì nó được tích hợp sẵn qua `langfuse` Python SDK và hỗ trợ tốt cho LLM application tracing.

---

## 4. Evidence - Minh Chứng Công Việc

| Evidence | Mô Tả | File |
|----------|--------|------|
| Trace List | >= 10 traces trên Langfuse | Langfuse Dashboard |
| Trace Waterfall | Waterfall showing RAG + LLM spans | Langfuse Dashboard |
| Trace Metadata | user_id_hash, session_id, tags | Langfuse Dashboard |
| Langfuse Config | .env với keys | `.env` |
| Trace Decorator | @trace_request trên /chat | `app/main.py` |
| Observe Decorator | @observe() trên LabAgent.run | `app/agent.py` |

---

## 5. Tự Đánh Giá

| Tiêu Chí | Điểm Max | Tự Đánh Giá | Ghi Chú |
|----------|----------|-------------|---------|
| Hiểu Tracing Pipeline | 5 | 5 | Giải thích được @observe, propagate |
| Cấu hình Langfuse | 5 | 5 | .env đúng định dạng |
| Tạo đủ 10+ traces | 5 | 5 | Đã xác nhận trên dashboard |
| Metadata đầy đủ | 5 | 5 | user_id_hash, session_id, tags |
| **Tổng** | **20** | **20** | |

