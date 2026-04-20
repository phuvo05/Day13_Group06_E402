from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python -m scripts.inject_incident`
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    parser = argparse.ArgumentParser(description="Toggle incident scenarios in the running app.")
    parser.add_argument(
        "--scenario",
        "--incident",
        dest="scenario",
        required=True,
        choices=["rag_slow", "tool_fail", "cost_spike"],
        help="Incident scenario to toggle",
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable the incident (enable by default)",
    )
    args = parser.parse_args()

    path = f"/incidents/{args.scenario}/disable" if args.disable else f"/incidents/{args.scenario}/enable"
    r = httpx.post(f"{BASE_URL}{path}", timeout=10.0)
    print(r.status_code, r.json())


if __name__ == "__main__":
    main()
