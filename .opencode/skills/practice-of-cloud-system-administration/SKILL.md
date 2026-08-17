---
name: practice-of-cloud-system-administration
description: "Applies Limoncelli, Chalup & Hogan's The Practice of Cloud System Administration to run services on the cloud reliably: the core duties of a sysadmin as a service (time to repair, monitoring, launch, failover, restart), scalable practices that do not collapse under dozens of systems (automation, configuration as code, runbooks, change management), and the design principle that the system must run itself so humans can sleep. Covers monitoring and alerting, configuration management and versioning, backups and recovery, security and access control, capacity, and the operational handoff. Use when the user says 'run a service on the cloud', 'system administration', 'sysadmin', 'production ops', 'monitoring', 'runbook', 'configuration management', 'change management', 'failover', 'service launch', 'manage many servers', 'how do I keep this running', or when a service must be operated reliably by a small team. Pairs with: infrastructure-as-code, devops-automation, n8n-self-hosting, sre-reliability-engineering, kubernetes-operations."
---

# The Practice of Cloud System Administration — Running Services That Survive

Limoncelli's trilogy distills sysadmin into a craft: the goal is not perfect
machines but **time to repair** — how fast the service is back when it breaks.
The discipline scales because it is engineered: everything repeatable is
automated and documented so a small team runs many systems.

## When to use

- Launching or operating a service in the cloud (web, database, queue, agent).
- Turning a manually-managed system into one that runs itself.
- Building runbooks, monitoring, backups, or change processes for production.

## The core: time to repair
- Name the metric that matters: minutes from failure to service restored. Optimize
  that, not uptime percentages.
- Failures are normal; design for them (detection, restart, failover) and practice
  recovery until it is routine.

## The systems-engineering mindset
- The system must run itself: if a human must intervene to keep it alive, the
  job is half-done. Automate the restart, the config, the deploy.
- Everything is documented as the thing that actually runs — the runbook is the
  interface for the next operator (including future you).
- One person scaling: automation is not a luxury for a cloud fleet, it is the
  only way a small team stays small and healthy.

## The five core duties (scaled to any size)
1. **Launch**: a documented, repeatable way to bring the service up — from bare
   config to healthy traffic (see `infrastructure-as-code` and `n8n-self-hosting`).
2. **Monitoring**: check what keeps the service alive (health endpoints, capacity,
   error rates) and alert on the things that require a human decision — never on
   noise. Alert fatigue kills real alarms.
3. **Change management**: every change is reviewed, scheduled, and reversible.
   A change that cannot be rolled back is a gamble, not a deployment.
4. **Backup and restore**: backups are worthless until a restore has been
   exercised. Run recovery drills; verify the restored data actually serves.
5. **Failover and restart**: define what "down" means and what happens next —
   restart, failover to a standby, or a page. Test the path, not just the theory.

## Configuration as code
- Version all configuration in a repo; every machine is built from code, never
  drifted by hand (see `infrastructure-as-code`).
- Environments (dev/staging/prod) promote the same artifact; differences are
  configuration values, not separate snowflakes.
- Access control follows least privilege, with a review trail for every change.

## Verification
- The service survived a forced failure with a measured time to repair.
- A restore drill ran recently and produced verified, serving data.
- Every operational task has a runbook that a newcomer can follow to completion.

## Pairs with
- `infrastructure-as-code` — the provisioning/config machinery this skill runs.
- `devops-automation` — automating the operations workflow itself.
- `n8n-self-hosting` — applying the craft to the self-hosted n8n stack.
- `sre-reliability-engineering` — SLIs/SLOs for the same operational discipline.
- `kubernetes-operations` — running the service on a managed cluster.