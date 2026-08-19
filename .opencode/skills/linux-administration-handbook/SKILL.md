---
name: linux-administration-handbook
description: Applies Linux Administration Handbook (Evi Nemeth, Garth Snyder, Hein R. Hein & Ben Whaley) to running Linux systems in production: the classic sysadmin reference covering boot, filesystems, processes, backup, networking, DNS, security, performance, and troubleshooting. Covers user and group management, service management, monitoring, and the operational habits that keep systems healthy. Use when the user says 'administer this Linux box', 'backup strategy', 'manage users', 'troubleshoot the server', or 'run a production Linux system'.
---
# linux-administration-handbook

The Nemeth handbook is the field guide generations of administrators learned from: what a healthy Linux system looks like and how to keep it that way.
Use this skill for operational work, from daily administration to incident response.
It encodes the habits and procedures that turn ad-hoc sysadmin into a repeatable discipline.

## Core principles
- Administration is a discipline: document, automate, and verify everything you touch.
- The boot process, init, and service management define how a system comes to life.
- Filesystems, quotas, and backup form the durability layer that protects data.
- Networking and name services are infrastructure your automation depends on.
- Performance work starts with measurement, not guesses.
- A system you cannot rebuild from notes is a system you do not actually run.

## Key patterns
- Structured user and group management with consistent conventions.
- Backup and restore cycles that are tested, not just scheduled.
- Service startup and shutdown procedures that are repeatable.
- Monitoring that watches health and capacity with clear thresholds.
- Troubleshooting that walks from log evidence to root cause.
- Change records for every production alteration, large or small.

## Applying this to scripting/automation/code
- Codify account and service setup so every host is reproducible.
- Schedule and verify backups for databases and workflow state.
- Add health checks and log rotation to long-running automation services.
- Standardize naming and paths so scripts work identically everywhere.
- Keep a runbook for the operations every automation depends on.
- Measure capacity before adding load to any production service.

## Hard rules
- Never run a backup policy that has never been restored once.
- Never change a production service without a rollback path.
- Never ignore log growth and disk pressure.
- Never assume two hosts share the same configuration.
- Never perform a change without a recorded reason and a reviewer.
- Never let a monitoring gap hide a failing service.

## Pairs with
practice-of-cloud-system-administration, devops-automation, infrastructure-as-code, n8n-code-nodes-official, evidence-over-memory
