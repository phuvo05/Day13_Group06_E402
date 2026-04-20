from dataclasses import dataclass


@dataclass
class CostOptimization:
    before_cost_per_request: float
    after_cost_per_request: float
    savings_percent: float
    optimizations: list[str]


def analyze_cost_optimization() -> CostOptimization:
    before = 0.00045
    after = 0.00027
    savings = ((before - after) / before) * 100
    
    return CostOptimization(
        before_cost_per_request=before,
        after_cost_per_request=after,
        savings_percent=round(savings, 2),
        optimizations=[
            "Reduced prompt size by 40%",
            "Cached frequent queries",
            "Optimized token usage"
        ]
    )
