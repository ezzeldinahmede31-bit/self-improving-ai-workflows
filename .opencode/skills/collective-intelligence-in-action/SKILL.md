---
name: collective-intelligence-in-action
description: Applies Satnam Alag's Collective Intelligence in Action to build commercial collective-intelligence systems on real infrastructure: the collective-intelligence lifecycle (data acquisition, storage, processing, presentation), profiles, taxonomies and tags, recommendation engines, reputation and trust, and the practical web-application patterns that ship such systems. Use when the user says 'collective intelligence', 'recommendation engine', 'reputation', 'tagging', 'personalization', 'Alag', 'build a social application', or when combining user behavior, content, and recommendations into a product. Pairs with: programming-collective-intelligence, enterprise-application-architecture, database-internals-engines, audience-psychology-analyst.
---
# Collective Intelligence in Action

Transfers Alag's product engineering for collective intelligence: turn user behavior and content into profiles, recommendations, and reputation at web scale.

## When to use
- Building a product feature driven by user behavior (recommendations, reputation, personalization).
- Architecting the data pipeline that collects, stores, and serves user signals.
- Designing tags, profiles, and trust models for a community application.

## Core practice
1. Collect the raw signals (behavior, ratings, content) and store them with context for reuse.
2. Build user and item profiles; enrich them with tags, taxonomies, and derived attributes.
3. Recommend with collaborative and content-based engines; rank by reputation and trust, not raw popularity.
4. Present personalized results with explanation so users trust the system.

## Engineering rules
- Design for scale: batch precompute what can be computed offline, cache hot results.
- Keep the data model flexible as new signals and features arrive.
- Make reputation transparent and robust to gaming.

## Verification discipline
- Validate recommendations and reputation on real traffic with measurable engagement.
- Monitor for feedback loops where the system amplifies its own biases.
- Reproduce any recommendation from logged data.

## Pairs with
programming-collective-intelligence, enterprise-application-architecture, database-internals-engines, audience-psychology-analyst.
