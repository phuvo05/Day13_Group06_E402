from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from statistics import mean
from time import time

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
REQUEST_TIMESTAMPS: list[float] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []


@dataclass(frozen=True)
class MetricsSnapshot:
    traffic: int
    qps: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    avg_latency_ms: float
    avg_cost_usd: float
    total_cost_usd: float
    tokens_in_total: int
    tokens_out_total: int
    error_breakdown: dict[str, int]
    error_rate: float
    quality_avg: float


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    REQUEST_TIMESTAMPS.append(time())
    QUALITY_SCORES.append(quality_score)


def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1


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


def average(values: list[int] | list[float]) -> float:
    return round(mean(values), 4) if values else 0.0


def traffic_qps() -> float:
    if len(REQUEST_TIMESTAMPS) < 2:
        return float(len(REQUEST_TIMESTAMPS))
    window_seconds = max(REQUEST_TIMESTAMPS) - min(REQUEST_TIMESTAMPS)
    if window_seconds <= 0:
        return float(len(REQUEST_TIMESTAMPS))
    return round(len(REQUEST_TIMESTAMPS) / window_seconds, 4)


def snapshot() -> dict:
    total_errors = sum(ERRORS.values())
    total_tokens = sum(REQUEST_TOKENS_IN) + sum(REQUEST_TOKENS_OUT)
    cost_per_token = round(sum(REQUEST_COSTS) / max(1, total_tokens), 8)
    return asdict(
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
    ) | {"cost_per_token_usd": cost_per_token}
