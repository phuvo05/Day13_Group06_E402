"""
Audit Logging Module
====================
Structured audit events written to `data/audit.jsonl` for compliance.
Each audit record captures who did what and when, with full context.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))


def write_audit_event(
    actor: str,
    action: str,
    resource: str,
    outcome: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append a structured audit event to the audit log file."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "resource": resource,
        "outcome": outcome,
        "metadata": metadata or {},
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(__import__("json").dumps(event) + "\n")


def audit_chat_request(user_id: str, session_id: str, feature: str, correlation_id: str, latency_ms: int) -> None:
    """Audit a completed chat request."""
    write_audit_event(
        actor=user_id,
        action="chat.request",
        resource="agent",
        outcome="success",
        metadata={
            "session_id": session_id,
            "feature": feature,
            "correlation_id": correlation_id,
            "latency_ms": latency_ms,
        },
    )


def audit_chat_error(user_id: str, session_id: str, feature: str, correlation_id: str, error_type: str) -> None:
    """Audit a failed chat request."""
    write_audit_event(
        actor=user_id,
        action="chat.request",
        resource="agent",
        outcome="failure",
        metadata={
            "session_id": session_id,
            "feature": feature,
            "correlation_id": correlation_id,
            "error_type": error_type,
        },
    )


def audit_incident_toggle(name: str, action: str, triggered_by: str = "system") -> None:
    """Audit an incident toggle change."""
    write_audit_event(
        actor=triggered_by,
        action=f"incident.{action}",
        resource=f"incident/{name}",
        outcome="applied",
        metadata={"incident_name": name},
    )


def audit_cost_alert(current_cost: float, baseline: float, spike_factor: float) -> None:
    """Audit a cost spike alert."""
    write_audit_event(
        actor="system",
        action="alert.cost_spike",
        resource="metrics",
        outcome="triggered",
        metadata={
            "current_cost_per_hour": current_cost,
            "baseline_cost_per_hour": baseline,
            "spike_factor": spike_factor,
        },
    )
