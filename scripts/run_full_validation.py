"""
Full Validation Automation Script
==================================
Runs the complete observability stack validation in one shot:
  1. Start the app in the background (or verify it's running)
  2. Run load test with concurrency=5
  3. Validate logs with the validator
  4. Generate a summary report

Usage:
    python scripts/run_full_validation.py
    python scripts/run_full_validation.py --app-url http://127.0.0.1:8000 --concurrency 5 --count 10
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple

# Allow running as `python -m scripts.run_full_validation`
sys.path.insert(0, str(Path(__file__).parent.parent))


class ValidationResult(NamedTuple):
    load_test_ok: bool
    log_count: int
    validate_score: int
    pii_leaks: int
    correlation_ids: int


def clear_logs() -> None:
    log_path = Path("data/logs.jsonl")
    if log_path.exists():
        log_path.unlink()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch()
    print("[1/3] Cleared existing logs.")


def run_load_test(concurrency: int, count: int, app_url: str) -> bool:
    print(f"[2/3] Running load test (concurrency={concurrency}, count={count})...")
    try:
        result = subprocess.run(
            [
                sys.executable, "scripts/load_test.py",
                "--concurrency", str(concurrency),
                "--count", str(count),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"  Load test FAILED (exit {result.returncode}):")
            print(result.stdout)
            print(result.stderr)
            return False
        print(f"  Load test completed successfully.")
        return True
    except subprocess.TimeoutExpired:
        print("  Load test TIMED OUT after 120s.")
        return False
    except Exception as e:
        print(f"  Load test ERROR: {e}")
        return False


def run_log_validation() -> tuple[int, int, int]:
    print("[3/3] Validating logs...")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/validate_logs.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Parse score from output
        score = 0
        pii_leaks = 0
        correlation_ids = 0
        log_count = 0
        for line in result.stdout.splitlines():
            if "Total log records analyzed:" in line:
                log_count = int(line.split(":")[-1].strip())
            if "Estimated Score:" in line:
                score = int(line.split("/")[0].split(":")[-1].strip())
            if "Potential PII leaks detected:" in line:
                pii_leaks = int(line.split(":")[-1].strip())
            if "Unique correlation IDs found:" in line:
                correlation_ids = int(line.split(":")[-1].strip())

        return log_count, score, pii_leaks, correlation_ids
    except subprocess.TimeoutExpired:
        print("  Validation TIMED OUT.")
        return 0, 0, 0, 0
    except Exception as e:
        print(f"  Validation ERROR: {e}")
        return 0, 0, 0, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full observability validation suite.")
    parser.add_argument("--concurrency", type=int, default=5, help="Load test concurrency")
    parser.add_argument("--count", type=int, default=10, help="Number of times to repeat sample queries")
    parser.add_argument("--skip-clear", action="store_true", help="Skip log clearing")
    args = parser.parse_args()

    total_queries = 10 * args.count
    print("=" * 60)
    print("  Day 13 Full Validation Suite")
    print("=" * 60)
    print(f"  Concurrency : {args.concurrency}")
    print(f"  Query pass  : {args.count} ({total_queries} total requests)")
    print(f"  Expected    : {total_queries} log entries")
    print("=" * 60)

    if not args.skip_clear:
        clear_logs()
    else:
        print("[1/3] Skipping log clear.")

    load_ok = run_load_test(args.concurrency, args.count, "http://127.0.0.1:8000")
    log_count, score, pii_leaks, correlation_ids = run_log_validation()

    # Summary
    print("\n" + "=" * 60)
    print("  VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Load test        : {'PASS' if load_ok else 'FAIL'}")
    print(f"  Log entries      : {log_count} (expected ~{total_queries})")
    print(f"  Validation score : {score}/100")
    print(f"  PII leaks        : {pii_leaks}")
    print(f"  Correlation IDs  : {correlation_ids}")
    print("=" * 60)

    # Pass/Fail
    if score >= 80 and pii_leaks == 0 and correlation_ids >= 2 and log_count >= total_queries // 2:
        print("  RESULT: PASS - System is observability-ready.")
        return 0
    else:
        print("  RESULT: FAIL - Review the validation output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
