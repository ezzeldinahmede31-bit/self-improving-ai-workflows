# Fixes & changes (applied to FINAL_AUDIT/fixed/ COPIES only)

- Copied 25 clinic files to FINAL_AUDIT/fixed/ (originals untouched).
- book: removed requiresHumanApproval from 4 routine lock/cache nodes (were stalling headless runs; patient-visible safety kept via staff alerts).
- book: Store Event Index now keys on Create Calendar Event output id (was reading unwired Reply node -> empty ev: keys).
- book: confirmation message no longer contains hardcoded DEMO address (uses trigger clinicAddress or omits line); null-safe queue/eventId.
- book: wired dead success path (Claim Queue -> Day Tally -> Alt cleanup -> Verify gate -> Store Confirmation -> Reply); unverified bookings route to staff instead of false confirmation.
- cancel: removed requiresHumanApproval from 3 nodes (cancel IS the approved action; cutoff gate + staff alerts + audit log retained).
- cancel: ownership gate (index-bound chat/phone match) + denial audit log; eventId alone no longer sufficient.
- resched: removed requiresHumanApproval from 5 nodes (same rationale as cancel).
- resched: saga compensation (verify old-delete; on failure cancel new + release + audit + honest reply; old booking preserved). Ownership gate added.
- find: name-only matching replaced with chat/phone-bound filtering (same-name collisions now safe).
- staff: agenda parser fixed (was comparing doctor==today and printing date as time -> always empty; now tolerant to colons in names).
- receptionist: appended data-safety rules to 1 agent node(s) (DEMO fallback guard, no-fabrication, medical escalation, injection guard).
- clinic_sub_eng_cleanup.json: removed requiresHumanApproval from 1 routine/internal node(s).
- clinic_sub_eng_offers.json: removed requiresHumanApproval from 1 routine/internal node(s).
- clinic_reminder_engine.json: removed requiresHumanApproval from 1 routine/internal node(s).
- receptionist: Reply Knowledge Multi hours/address now KB-driven with empty-fallback (no fabricated hours/address when table unreachable).
- pinned fixtures: renamed demo persona to Dr. SYNTH-TEST in 7 files (test-only pinnedData).
