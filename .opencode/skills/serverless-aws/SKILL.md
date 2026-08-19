---
name: serverless-aws
description: Applies Sbarski's Serverless Architectures on AWS to build event-driven systems from managed services: functions that are stateless, short-lived, and event-triggered, fronted by API Gateway and backed by Step Functions, queues, and databases. Covers the patterns for fan-out, workflows, dead-lettering, and the BFF layer. Use when the user says 'design a serverless app', 'use AWS Lambda', or 'build with step functions'.
---
# serverless-aws

Sbarski's book shows how to compose AWS managed services into systems that scale without provisioning servers. A Lambda function is a unit of work, not an application; the application is the event flow that connects units. Use this skill to design serverless flows and to mirror the same thinking in event-driven automation.

## Core principles
- Functions are stateless and short-lived; durable state lives in a service (database, queue, or object store).
- Everything runs on events: an API call, a file landing, a message in a queue, or a schedule triggers work.
- Managed services are the building blocks; the team writes only the thin logic that connects them.
- Scale is implicit: design for many concurrent invocations, never for a single long process.
- Failure is handled by design: retries, dead-letter queues, and idempotent handlers are standard.
- Cost follows usage; idle systems cost nothing, so bursts are affordable.

## Key patterns
- Fan-out and fan-in: one event triggers parallel workers, and results are aggregated afterward.
- Step Functions for orchestrated workflows with human approval steps and timeouts.
- Dead-letter queues to park messages that failed after retries so nothing is silently lost.
- Idempotent handlers keyed by an event ID so replays never double-apply side effects.
- The BFF (backend-for-frontend) pattern to shape data per client while keeping domain services generic.
- Stateless workers that read state from a store, making horizontal scaling trivial.

## Applying this to n8n/automation/code
- Split long automations into small idempotent units with a durable queue as the handoff point.
- Use the Wait node and execution persistence so a flow can pause and resume across service outages.
- Make webhook handlers reply fast and do heavy work asynchronously, echoing status later.
- Add a dead-letter path for failed executions so failures are visible and replayable, not silent.
- Model cross-flow orchestration as explicit states with retries, timeouts, and approval gates.

## Hard rules
- Never hold conversational state inside a stateless handler; persist it explicitly.
- Never process a message without idempotency or deduplication on replay.
- Always attach a dead-letter destination to every queue and event source.
- Never build synchronous chains that block on slow services; use async patterns.

## Pairs with
cloud-native-patterns, enterprise-integration-patterns, infrastructure-as-code, release-it-production-hardening, agent-arch-system-design
