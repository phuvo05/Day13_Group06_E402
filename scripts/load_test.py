import argparse
import concurrent.futures
import json
import sys
import time
from pathlib import Path

# Allow running as `python -m scripts.load_test`
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

BASE_URL = "http://127.0.0.1:8002"
QUERIES = Path("data/sample_queries.jsonl")


def send_request(client: httpx.Client, payload: dict) -> dict | None:
    try:
        start = time.perf_counter()
        r = client.post(f"{BASE_URL}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000
        cid = r.json().get("correlation_id", "MISSING")
        print(f"[{r.status_code}] {cid} | {payload['feature']} | {latency:.1f}ms")
        return {"status": r.status_code, "correlation_id": cid, "latency_ms": latency}
    except Exception as e:
        print(f"Error: {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Load test the /chat endpoint.")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent workers")
    parser.add_argument("--count", type=int, default=0, help="Repeat the queries this many times (0 = one pass)")
    args = parser.parse_args()

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]

    if args.count > 0:
        lines = lines * args.count

    print(f"Sending {len(lines)} requests (concurrency={args.concurrency})...")

    with httpx.Client(timeout=60.0) as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [executor.submit(send_request, client, json.loads(line)) for line in lines]
                concurrent.futures.wait(futures)
        else:
            for line in lines:
                send_request(client, json.loads(line))

    print("Load test complete.")


if __name__ == "__main__":
    main()
