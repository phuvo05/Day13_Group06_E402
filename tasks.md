# Project Tasks

Dựa trên nội dung repo và yêu cầu trong `README.md`, `day13-rubric-for-instructor.md`, `docs/blueprint-template.md`, `docs/dashboard-spec.md`, và `docs/alerts.md`, project này cần hoàn thành các việc sau:

## 1. Chạy và hiểu dự án
- [x] Tạo môi trường Python và cài dependencies từ `requirements.txt`
- [x] Chạy ứng dụng FastAPI để kiểm tra trạng thái hiện tại
- [x] Kiểm tra dữ liệu mẫu, incident scenarios và output files trong `data/`
- [x] Đọc qua flow của agent trong `app/agent.py`, `app/main.py`, `app/mock_llm.py`, `app/mock_rag.py`

## 2. Logging và correlation ID
- [x] Sửa `app/middleware.py` để mỗi request có `x-request-id` duy nhất
- [x] Đảm bảo correlation ID được propagate xuyên suốt request flow
- [x] Nâng cấp logging sang structured JSON theo schema trong `config/logging_schema.json`
- [x] Gắn context như user, session, feature, request metadata vào log
- [x] Chạy `scripts/validate_logs.py` để kiểm tra log output

## 3. PII redaction
- [x] Hoàn thiện PII scrubber trong `app/logging_config.py`
- [x] Đảm bảo các dữ liệu nhạy cảm như email, số điện thoại, ID, token được che đúng cách
- [x] Xác minh không còn PII leak trong log output
- [x] Nếu cần, bổ sung test cho scrubber ở `tests/test_pii.py`

## 4. Tracing / observability
- [x] Kiểm tra và hoàn thiện tracing ở `app/tracing.py`
- [x] Đảm bảo có decorator / instrumentation để tạo trace khi xử lý request
- [x] Tạo đủ ít nhất 10 traces để phục vụ đánh giá
- [x] Xác minh trace có metadata hữu ích cho debugging và incident analysis

## 5. Metrics
- [x] Rà soát và hoàn thiện metrics aggregation trong `app/metrics.py`
- [x] Đảm bảo có số liệu cho latency, traffic, error rate, cost, tokens in/out, quality proxy
- [x] Kiểm tra metrics có thể dùng cho dashboard và SLO

## 6. Dashboard
- [x] Xây dashboard 6 panels theo `docs/dashboard-spec.md`
- [x] Bao gồm latency P50/P95/P99
- [x] Bao gồm traffic/QPS
- [x] Bao gồm error rate với breakdown
- [x] Bao gồm cost over time
- [x] Bao gồm tokens in/out
- [x] Bao gồm quality proxy
- [x] Thêm threshold / SLO line và đơn vị rõ ràng

## 7. SLO và alerting
- [x] Cập nhật `config/slo.yaml` cho các SLI/SLO chính
- [x] Hoàn thiện `config/alert_rules.yaml`
- [x] Đảm bảo có ít nhất 3 alert rules hoạt động
- [x] Liên kết alert với runbook trong `docs/alerts.md`
- [x] Test các alert theo incident toggle hoặc dữ liệu giả lập

## 8. Incident injection và debugging
- [x] Chạy `scripts/inject_incident.py` để mô phỏng incident
- [x] Dùng logs, traces, metrics để tìm root cause
- [x] Ghi lại symptom, root cause, fix action, preventive measure
- [x] Cập nhật phần incident response trong report

## 9. Load test và validation
- [x] Chạy `scripts/load_test.py` để tạo traffic thực tế
- [x] Test với concurrency để phát hiện bottleneck
- [x] Dùng `scripts/validate_logs.py` kiểm tra schema và chất lượng log
- [x] Đảm bảo bài nộp đạt `VALIDATE_LOGS_SCORE` tối thiểu 80/100

## 10. Báo cáo và evidence
- [x] Điền đầy đủ `docs/blueprint-template.md`
- [x] Điền team metadata, member roles, evidence links và screenshots
- [x] Thêm trace explanation, SLO table, alert evidence, incident response
- [x] Bổ sung bằng chứng commit/PR cho từng thành viên
- [x] Đảm bảo report có đủ tên thành viên và nội dung cá nhân rõ ràng

## 11. Tiêu chí pass
- [x] Không còn TODO blocks quan trọng chưa hoàn thành
- [x] Có ít nhất 10 traces live trên Langfuse
- [x] Dashboard đủ 6 panels
- [x] PII được redact hoàn toàn
- [x] Report blueprint đầy đủ và đúng format

## 12. Bonus nếu còn thời gian
- [x] Tối ưu chi phí trước/sau và ghi số liệu (`app/cost_optimizer.py`, endpoint `/cost-optimization`: 40% savings)
- [x] Tách audit logs riêng (`data/audit.jsonl` via `AuditLogProcessor` trong `logging_config.py`)
- [x] Thêm custom metric `cost_per_token_usd` vào `/metrics` endpoint
- [x] Làm dashboard đẹp và chuyên nghiệp hơn mức tối thiểu (thêm panel 7: Cost Per Token)
