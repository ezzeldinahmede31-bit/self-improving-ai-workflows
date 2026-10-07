"""bench_common.py — shared helpers for device latency/concurrency benchmarks."""
import json
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SCRIPTS = HERE / "scripts"
sys.path.insert(0, str(SCRIPTS))


def pct(data, q):
    if not data:
        return 0.0
    s = sorted(data)
    i = min(len(s) - 1, max(0, int(q * len(s))))
    return float(s[i])


def summarize(samples):
    s = sorted(samples)
    return {
        "n": len(s),
        "min": round(min(s), 4) if s else 0,
        "max": round(max(s), 4) if s else 0,
        "p50": round(pct(s, 0.50), 4),
        "p90": round(pct(s, 0.90), 4),
        "p95": round(pct(s, 0.95), 4),
        "p99": round(pct(s, 0.99), 4),
        "mean": round(statistics.mean(s), 4) if s else 0,
    }


def make_plan(work, tag):
    return {"task": f"bench-{tag}", "steps": [
        {"id": "a", "tool": "bash", "args": ["ls", str(work)]},
        {"id": "b", "tool": "read", "path": str(work / "probe.txt")},
    ]}
