---
name: test-environment-management
description: "Test environment management distilled. Use when provisioning envs, parity with prod, data refresh, booking, ephemeral previews, chaos-safe staging."
---

# Test Environment Management

## Purpose

Give testing reliable ground: prod-like parity, fresh safe data, clear booking, ephemeral previews per change, staging fit for failure drills.

## When to use

Use when the user says 'test environment', 'staging', 'preview env', 'env parity', 'data refresh', 'env booking', 'ephemeral environment'.

## Steps

1. Define parity tiers: which env mirrors prod closely and where gaps are known.
2. Refresh data on schedule with scrubbed production-shaped sets.
3. Book shared envs explicitly; show queue and ownership.
4. Spin ephemeral previews per change with seeded data plus smoke.
5. Reserve staging capacity for failure drills and performance runs.

## Anti-patterns

- One shared env everyone fights over with stale data.
- Production data copied raw into test.
- Parity gaps undocumented, surprises blamed on env.
- Preview envs without smoke proof.

## Example

Env card: tier, parity notes, data age, booking owner, smoke status link.

## Verification

Tiers defined, data fresh and safe, booking visible, previews smoked, drills scheduled.

## Pairs-with

test-data-management, environment-promotion-config, chaos-testing-patterns, performance-testing-k6-jmeter.
