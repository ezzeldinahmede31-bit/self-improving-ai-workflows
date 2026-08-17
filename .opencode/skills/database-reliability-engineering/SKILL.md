---
name: database-reliability-engineering
description: "Applies the principles behind Google's Database Reliability Engineering (Campbell & Majors) to run databases like a production service: the SRE mindset applied to data — capacity planning, schema and query review gates, change management and migrations, backup/restore and drill-tested recovery, monitoring and alerting for the data path, and the 'one team owns the DB experience' operating model. Use when the user says 'database reliability', 'DBRE', 'capacity planning for the database', 'schema review', 'migration runbook', 'backup drill', 'restore test', 'database monitoring', 'why is the database down', 'run the database safely', 'data loss prevention', or when a database needs SRE-grade operational discipline, not just tuning. Pairs with: database-internals-engines, systems-performance-profiling, n8n-self-hosting, infrastructure-as-code, devops-handbook-flow."
---

# Database Reliability Engineering — Running Data as a Service

Campbell & Majors distilled Google's practice: a database is a critical
production service, and reliability is engineered — capacity planned, changes
gated, recovery drilled, and the data path monitored like any SLO. The role is
the DBRE, owning the database experience end to end.

## When to use

- A database (SQL, NoSQL, vector store, cache) is part of a production system.
- Planning capacity, migrations, backups, or monitoring for a data store.
- Responding to (or preventing) database outages and data-loss incidents.

## The operating model
- One team owns the database experience: availability, performance, schema,
  access, and recovery. Splitting ownership across teams guarantees gaps.
- Treat schema and queries as production code: versioned, reviewed, and tested
  against the real data shape.

## Capacity planning
- Measure the real data path, then project: growth rate of data, read/write mix,
  peak and trend. Size for the trend, with headroom for spikes.
- Plan for partitions, shards, or collections before the store is full — a
  resize under pressure is an incident.
- Confirm the engine's amplification behavior (see `database-internals-engines`)
  so capacity forecasts match reality.

## Change management for the data path
- Every migration has a runbook with a rollback path, a time-box, and a
  verification step. Rehearse it before the change window.
- Prefer online, reversible migrations over big-bang ones; test on a copy first.
- Schema and query changes go through review with the owners of the traffic
  they affect — a hot-query rewrite is a performance event.

## Backup and recovery (the part nobody skips twice)
- Backups exist to make restores work, not to be files: restore to a clean target
  and verify the data before declaring success.
- Schedule recovery drills on a cadence; a restore that has never run will fail
  at the worst moment.
- Test both the data restore and the access path (users, credentials, app) that
  depends on it.

## Monitoring and alerting for data
- Watch the reliability signals: availability, latency, error rate, and capacity
  (disk, connections, load). Alert on SLO breach risk, not on every metric twitch.
- Bake in the amplification and replication metrics from the engine itself so
  slow degradation shows up before the outage (see `systems-performance-profiling`).

## Verification
- A restore is proven by a real, recent drill with a verified target, not by a
  file existing.
- Every schema/migration change has a reviewed runbook with rollback and a
  post-change verification result.
- Capacity plans are written, trend-based, and reviewed on a cadence.

## Pairs with
- `database-internals-engines` — the mechanics behind the reliability decisions.
- `systems-performance-profiling` — measuring the real bottleneck and SLO health.
- `n8n-self-hosting` — applying this discipline to the self-hosted stack.
- `infrastructure-as-code` — versioning the environment and its data plane.