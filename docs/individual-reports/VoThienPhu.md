# Individual Report — Võ Thiên Phú
**MSSV**: 2A202600336
**Work Stream**: Work Stream 1 — Structured Logging + PII Scrubbing
**Role**: Primary Owner

---

## 1. Role in the Team

I owned **Work Stream 1: Structured Logging + PII Scrubbing**. My primary responsibility was to implement the observability logging pipeline so that every application event is emitted as structured JSON with correlation ID propagation and PII redaction. This formed the foundation for the entire observability stack — all other components (tracing, metrics, alerting) depend on well-structured logs.

---

## 2. Technical Contribution

### Files Modified

#### `app/middleware.py` — Correlation ID Middleware
Implemented the `CorrelationIdMiddleware` class which intercepts every incoming HTTP request:

- **Clear contextvars** (`clear_contextvars()`): Called at the start of each request to prevent data leakage between concurrent requests. This is critical for async applications where one request's context must not bleed into another's.
- **Generate/extract correlation ID**: If the client sends an `X-Request-ID` header, it is used; otherwise a new ID in format `req-<8-char-hex>` is generated using `uuid.uuid4().hex[:8]`.
- **Bind to structlog contextvars**: The correlation ID is bound using `bind_contextvars(correlation_id=correlation_id)` so it is automatically included in every log entry for that request.
- **Add to response headers**: Both `X-Request-ID` and `X-Response-Time-Ms` are added to the HTTP response for client-side tracing.

Key design decision: I chose to generate the correlation ID in the middleware rather than in individual endpoints so that **every** request — including `/health`, `/metrics`, and incident toggle endpoints — gets a correlation ID automatically, without each endpoint having to duplicate this logic.

#### `app/logging_config.py` — Structlog Pipeline
- Registered the `scrub_event` PII processor in the structlog processor chain. It sits after `TimeStamper` and before `StackInfoRenderer`, ensuring PII is scrubbed before the log entry is written.
- The pipeline outputs JSON to `data/logs.jsonl` via a custom `JsonlFileProcessor` class, which renders each event as a JSON line and appends it to the file.

#### `app/pii.py` — PII Pattern Definitions
Extended `PII_PATTERNS` with the following patterns beyond the starter template:

| Pattern Name | Regex | Example |
|---|---|---|
| `email` | `[\w\.-]+@[\w\.-]+\.\w+` | `student@vinuni.edu.vn` |
| `phone_vn` | `(?:\+84\|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}` | `090 123 4567`, `+84 987654321` |
| `cccd` | `\b\d{12}\b` | Vietnamese citizen ID number |
| `credit_card` | `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b` | `4111 1111 1111 1111` |
| `passport` | `\b[A-Z]{1,2}\d{6,9}\b` | `A1234567`, `B123456789` |
| `national_id_vn` | `\b\d{9,12}\b` | 9 or 12 digit national ID |
| `vietnamese_address` | `\b\d{1,5}\s+[\w\s]+\s+(đường\|phố\|...)` | `123 Nguyễn Trãi, đường...` |

All patterns are applied via `scrub_text()`, which replaces each match with `[REDACTED_<PATTERN_NAME>]`. This function is called by both `summarize_text()` (for log payloads) and the structlog `scrub_event` processor (for all log event fields).

#### `app/main.py` — Log Enrichment
- Added `bind_contextvars(user_id_hash, session_id, feature)` at the start of the `/chat` handler so all subsequent log entries in that request include user context automatically.
- Applied `bind_contextvars(service, env)` in the startup event.
- Applied `bind_contextvars(service="control")` to incident toggle endpoints.

---

## 3. Challenges Faced

**Challenge 1: Async contextvar isolation**
I initially forgot to call `clear_contextvars()` between requests. In a production async app, this could cause correlation IDs from one request to leak into another when multiple requests are handled concurrently. I fixed this by adding `clear_contextvars()` at the start of the middleware's `dispatch` method.

**Challenge 2: PII scrubbing ordering**
I had to decide where in the structlog pipeline to place `scrub_event`. If placed before `TimeStamper`, the timestamp wouldn't be in the output. If placed after `JSONRenderer`, we'd be scrubbing the rendered string. I placed it after `TimeStamper` and before `StackInfoRenderer` — this way all structured fields (including nested `payload`) are scrubbed before rendering.

---

## 4. Evidence

| Evidence Item | Description |
|---|---|
| `app/middleware.py` lines 13–36 | Full correlation ID implementation |
| `app/logging_config.py` line 46 | `scrub_event` registered in pipeline |
| `app/pii.py` lines 6–14 | All PII patterns defined |
| `app/main.py` lines 27–31, 48–52 | `bind_contextvars` calls |
| `data/logs.jsonl` (generated) | JSON log entries with `correlation_id` field |

---

## 5. Reflection

This lab taught me that logging is not just `print()` statements — it is a carefully designed pipeline where **what you log, how you structure it, and what you redact** directly determines how quickly you can debug production issues. The correlation ID pattern is especially powerful: by propagating a single ID through middleware → handler → agent → child spans → logs, you create a "thread" that lets you jump from a user complaint directly to the exact trace and log entries for that request.

The PII scrubbing exercise was a reminder that **security and observability must be designed together**. It is easy to add logging everywhere and then discover PII in your logs during a compliance audit. Building redaction into the logging pipeline from day one is the right approach.
