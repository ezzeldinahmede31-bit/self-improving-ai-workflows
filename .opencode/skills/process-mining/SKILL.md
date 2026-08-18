---
name: process-mining
description: Applies Wil van der Aalst's Process Mining to extract real process behavior from event logs — discovery (automatically building the actual process model from events), conformance checking (finding where reality deviates from the intended model), and enhancement (repairing or extending the model with frequencies and times). Covers the alpha and inductive mining families, event-log quality, and the honest limits of the field. Use when the user says 'process mining', 'event log', 'discovery algorithm', 'conformance checking', 'van der Aalst process mining', 'alpha miner', 'inductive miner', 'deviation analysis', 'process enhancement', or when a running process leaves event data and the actual, data-driven behavior must be understood instead of assumed. Pairs with: business-process-management-weske, fundamentals-of-bpm, workflow-management-van-der-aalst, data-analysis, thinking-map-territory, evidence-over-memory.
---
# Process Mining (van der Aalst)

Transfers van der Aalst's process-mining discipline so the actual behavior of a running process is extracted from event logs, checked against the intended model, and improved with evidence instead of assumption.

## When to use
- Understanding what a process actually does from its recorded events.
- Finding where reality deviates from the documented process.
- Enriching a process model with real frequencies and times for better analysis.

## The three pillars
1. Discovery: mine the event log to build the process model as it really runs, free of the documented-fiction bias.
2. Conformance: replay the log against the intended model to locate deviations — skipped steps, unexpected paths, loops, extra work.
3. Enhancement: repair the model to match reality or extend it with performance data (durations, frequencies, bottlenecks).

## The method
1. Ensure event-log quality: every event has a case id, an activity, and a timestamp; clean and filter before mining.
2. Choose the miner to the data: inductive miners handle noise and loops well; simpler families show basic structure.
3. Interpret deviations as signals: they reveal control gaps, resource problems, or processes that outgrew their model.

## Verification discipline
- Validate the mined model against a hold-out of the log; an overfit model explains noise, not behavior.
- Confirm conformance findings with the people who run the process before acting on them.
- Report the log's quality and coverage alongside any conclusion; a thin log cannot prove a complex process.

## Pairs with
business-process-management-weske, fundamentals-of-bpm, workflow-management-van-der-aalst, data-analysis, thinking-map-territory, evidence-over-memory.