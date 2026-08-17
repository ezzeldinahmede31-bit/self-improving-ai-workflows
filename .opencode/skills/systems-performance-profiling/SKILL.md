---
name: systems-performance-profiling
description: "Applies Brendan Gregg's Systems Performance methodology to find and fix real bottlenecks: the USE method (Utilization, Saturation, Errors) for every resource, latency-based analysis, profiling the CPU/memory/disk/network path, benchmarking with correct methodology, and evidence-based tuning. Use when the user says 'the system is slow', 'find the bottleneck', 'why is CPU at 100%', 'high latency', 'memory pressure', 'which component is saturated', 'USE method', 'profile this', 'benchmark methodology', 'hot spot', 'perf', 'eBPF', 'trace this slow path', or when an n8n workflow or server endpoint needs performance investigation. Pairs with: rate-limit-and-cost-guard, database-internals-engines, code-execution-guided-swemaster, n8n-debugging-official."
---

# Systems Performance — Bottleneck Analysis

Gregg's book turns "it's slow" into a method: enumerate every resource, ask three
questions per resource (utilization, saturation, errors), then drill into the one
that is saturated with the right tool. Optimizing anything else is wasted effort.

## When to use

- Any performance complaint: slow endpoint, high CPU, memory pressure, I/O stalls,
  network latency.
- Before and after any tuning or scaling change (measure both sides).
- When a workflow (n8n or otherwise) is slower than expected and the cause is unknown.

## Step 1 — The USE method (resource by resource)
For each resource — CPU, memory, storage, network, plus application-level resources
(pools, queues, locks) — answer:
1. **Utilization**: what fraction of the resource is busy over the interval?
2. **Saturation**: how much work is queued waiting for the resource? (Queues are the
   signal that demand exceeds capacity.)
3. **Errors**: are any errors being returned? (Error counts dominate everything.)

Start with a system-wide sweep (top/vmstat/iostat/sar, cloud provider metrics), find
the saturated resource, and only then drill in. Do NOT jump to a suspect.

## Step 2 — Latency analysis and the critical path
- Profile the request path and find where latency is spent (p50/p99/p999, not just
  average — averages hide outliers).
- Break the latency into components (network, queueing, service, database) and
  optimize the largest component first.
- Trace the hot path with the right tool for the layer: perf/eBPF on the kernel,
  application profilers (py-spy, async-profiler, go tool pprof) for userland, DB
  query plans for the data layer.

## Step 3 — Benchmarking methodology (before trusting any number)
- One variable at a time; fixed workload and environment; warm-up runs.
- Report the distribution (p50/p99) not just the mean, with sample size and machine.
- Never extrapolate a micro-benchmark to a production claim.

## Step 4 — Evidence-based tuning
- Make one change, re-measure, and keep it only if the measured target improved.
- Guardrails: cap work, add backpressure/retry policy with bounded queues, and
  monitor saturation after the change (see `rate-limit-and-cost-guard`).

## Verification
- State the before and after numbers for the target metric (latency/throughput/CPU)
  with the exact measurement command.
- Confirm the saturated resource from Step 1 is no longer saturated.
- If a claimed fix did not move the measured number, revert it and re-diagnose.

## Pairs with
- `rate-limit-and-cost-guard` — rate/cost ceilings and backpressure in workflows.
- `database-internals-engines` — root-cause the database-side of a slow path.
- `code-execution-guided-swemaster` — execution-evidence loop for code fixes.
- `n8n-debugging-official` — workflow-specific failure investigation.