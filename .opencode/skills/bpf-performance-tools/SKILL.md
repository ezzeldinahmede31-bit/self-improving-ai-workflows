---
name: bpf-performance-tools
description: Applies BPF Performance Tools (Brendan Gregg) to observability and performance analysis on Linux: using eBPF and bpftrace to inspect the kernel and applications safely and live. Covers the USE method, on-CPU and off-CPU analysis, flame graphs, latency histograms, and drilling from metrics to code paths. Use when the user says 'why is this slow', 'bpftrace', 'eBPF', 'flame graph', 'on CPU vs off CPU', or 'trace a syscall path'.
---
# bpf-performance-tools

Gregg's book turns eBPF into a superpower for performance work: live kernel and application tracing without restarting or instrumenting source.
Use this skill when a slowdown must be traced to its cause with hard evidence.
It replaces guessing about performance with direct observation of the running system.

## Core principles
- eBPF lets a safe program run inside the kernel at probe points, capturing events with negligible overhead.
- The USE method checks every resource for Utilization, Saturation, and Errors before guessing.
- Performance problems split into on-CPU and off-CPU causes; each needs its own tool.
- Flame graphs turn stacks into readable evidence of where time goes.
- Metrics lead to hypotheses, and traces confirm them.
- Histograms capture the real distribution that averages hide.

## Key patterns
- bpftrace one-liners for syscall and function tracing.
- BCC tools for scheduler, block, and network analysis.
- On-CPU flame graph generation for CPU-bound workloads.
- Off-CPU and wakeup analysis for lock and I/O waits.
- Latency histograms for request and syscall durations.
- Drilling from a metric to the exact code path that causes it.

## Applying this to scripting/automation/code
- Trace where a slow pipeline script spends its time before optimizing.
- Confirm disk or network saturation in automation hosts with a single tool pass.
- Attach flame graphs to agent workers to find hot code paths.
- Verify lock contention in multi-threaded code nodes with off-CPU analysis.
- Use syscall tracing to prove whether time is lost in the kernel or in user code.
- Baseline normal behavior so regressions become visible when they appear.

## Hard rules
- Never optimize on averages; capture histograms.
- Never trace production without knowing the tool's overhead and scope.
- Never skip the USE method and jump straight to a guess.
- Never ship an eBPF program that lacks privilege and version checks.
- Never change code on a performance lead that a trace has not confirmed.
- Never stop tracing at the first plausible explanation.

## Pairs with
systems-performance-profiling, computer-systems-programmers-perspective, operating-systems-three-easy-pieces, code-execution-guided-swemaster, evidence-over-memory
