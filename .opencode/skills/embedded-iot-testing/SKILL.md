---
name: embedded-iot-testing
description: "Embedded and IoT testing distilled. Use when testing firmware, hardware-in-loop, sensor data, OTA updates, power and connectivity loss."
---

# Embedded IoT Testing

## Purpose

Test devices where software meets physics: hardware-in-loop rigs, sensor simulation, OTA safety, power-loss resilience, fleet telemetry.

## When to use

Use when the user says 'firmware test', 'IoT test', 'hardware in loop', 'OTA update', 'sensor simulation', 'power loss test'.

## Steps

1. Layer tests: host unit, simulator integration, hardware rig, field pilot.
2. Simulate sensors with recorded plus synthetic edge profiles.
3. Test OTA with interrupted downloads and rollback to known-good.
4. Kill power mid-write; assert state recovers cleanly.
5. Monitor fleets for crash, battery, and connectivity signals.

## Anti-patterns

- Simulator-only testing for timing-critical paths.
- OTA without rollback proven.
- Power-loss behavior assumed instead of tested.
- Fleet signals missing until customers report.

## Example

Rig check: recorded sensor profile replayed, device output diffed against golden trace.

## Verification

Layers all green, OTA rollback proven, power-loss recovery asserted, fleet monitored.

## Pairs-with

embedded-systems-architecture, resilience-circuit-testing, test-environment-management, observability-test-telemetry.
