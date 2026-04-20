from __future__ import annotations

from collections import Counter
from statistics import mean

REQUEST_LATENCIES: list[int] = []
RETRIEVAL_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []

# Baseline metrics for SLO computation
START_TIME: float | None = None
BASELINE_COST_PER_HOUR: float = 0.0


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)


def record_retrieval_latency(latency_ms: int) -> None:
    RETRIEVAL_LATENCIES.append(latency_ms)



def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    import time as _time
    global START_TIME, BASELINE_COST_PER_HOUR

    now = _time.time()
    if START_TIME is None:
        START_TIME = now
    elapsed_hours = (now - START_TIME) / 3600.0
    if elapsed_hours > 0:
        cost_per_hour = round(sum(REQUEST_COSTS) / elapsed_hours, 4)
    else:
        cost_per_hour = 0.0
    if BASELINE_COST_PER_HOUR == 0.0 and TRAFFIC > 10:
        BASELINE_COST_PER_HOUR = cost_per_hour

    total_errors = sum(ERRORS.values())
    error_rate = (total_errors / TRAFFIC) if TRAFFIC > 0 else 0.0

    return {
        # Counters
        f"# HELP app_requests_total Total number of requests received" f"\napp_requests_total": TRAFFIC,
        f"# TYPE app_requests_total counter\napp_requests_total": TRAFFIC,
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        f"app_latency_p95_seconds": round(percentile(REQUEST_LATENCIES, 95) / 1000, 3),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        f"app_tokens_in_total": sum(REQUEST_TOKENS_IN),
        f"app_tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "total_errors": total_errors,
        f"app_errors_total": total_errors,
        f"app_error_rate": round(error_rate, 4),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
        f"app_cost_per_hour_usd": cost_per_hour,
        f"app_baseline_cost_per_hour_usd": BASELINE_COST_PER_HOUR,
        f"app_retrieval_latency_p95_seconds": round(percentile(RETRIEVAL_LATENCIES, 95) / 1000, 3) if RETRIEVAL_LATENCIES else 0.0,
    }
