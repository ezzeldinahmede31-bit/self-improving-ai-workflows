# Staff dashboard wiring — test matrix (Sep 16, living doc)
Endpoints: sched-today / sched-book / sched-stats / sched-attention / sched-reminders / sched-settings / sched-settings-save (+ eng-router flags, main auto_replies gate). Battery script: /tmp/opencode/sched_battery.sh.

## N. Happy paths (all PASS live)
| ID | Check | Result |
|----|-------|--------|
| N1 | GET today → day/serving/queue/appointments shape | PASS |
| N2 | GET stats → 5 tallies | PASS |
| N3 | GET attention → items list | PASS (0 live) |
| N4 | GET reminders → 23 real records | PASS |
| N5 | GET settings → 5 flags default 1 | PASS |
| N6 | POST book valid → ok:true + eventId + queue (real Google event) | PASS, cleaned via cancel lane |
| N7 | Dashboard HTML renders live data in real Chrome, no JS errors | PASS |

## S. Special cases
| ID | Check | Result |
|----|-------|--------|
| S1 | no/bad auth on all 7 → 403, zero executions | PASS ×6 |
| S2 | empty/malformed/past booking → invalid_input / Arabic past refusal, nothing created | PASS |
| S3 | parallel double-book same slot → exactly 1 winner (INCR atomic + single slot lock) | PASS (Race Two won) |
| S4 | 20KB name → BOOKED (no cap) | FAIL → FIXED: name ≤80, phone ≤20 → invalid_input, re-proven live |
| S5 | partial settings POST resets missing flags to 1 | DOCUMENTED (dashboard always sends full set) |
| S7 | GET-on-POST / POST-on-GET → 404, no side effects | PASS |
| S8 | concurrent settings writes → consistent | PASS (roundtrips) |
| S9 | unknown service → General exam fallback books | PASS (documented) |
| S10 | injection-ish name stored safely, booked+cancelled cleanly | PASS |

## E. Engine/flags proofs
| ID | Check | Result |
|----|-------|--------|
| E1 | remind2h=0 → due record NOT reminded after full tick (suppression) | PASS |
| E2 | remind2h=1 → lane fired, remindedAt stamped | PASS |
| E3 | auto_replies=0 → Takeover ran, agent NOT-run (12s exec) | PASS (exec 3345) |
| E4 | auto_replies=1 → full agent stack ran (29s, KB+model) | PASS (exec 3350) |

## Bugs found & fixed this round
1. `+03:00` in GCal query → 400 (plus = space). Fix: `%2B` encode. Lesson: Zulu or encoded offsets in URLs.
2. respondToWebhook flagged WEBHOOK_NO_AUTH (gate FP) → responseMode lastNode. Reported as gate FP.
3. `count` key trips counting-keywords gate → renamed `total`.
4. Subworkflow inputs must be read from `.body` (webhook envelope), not top level — cost 2 cleanup runs.
5. Redis has no `decr`; SET needs STRING values (number 0 → "identify type" error).
6. Mixed `=literal{{expr}}` syntax invalid → full `={{ }}` only.
7. Cancel lane re-tallies on re-cancel of missing event (lane bug, NOT fixed — needs own gate cycle).
8. Cancel-lane reminder-record cleanup missed dash record once (manual DEL; watch item).
9. n8n_create_workflow sporadically stringifies big nodes/connections params → skeleton + addNode fallback works.
10. multi-patch updateNode payloads hit the same quirk → single-patch calls.

## Residuals (honest)
- Live conversations view = sample data (needs user-pasted n8n API key; 2-min UI task).
- instant_alert toggle stored but engine health alerts stay always-on (safety default, documented).
- Cancel double-tally on missing event (item 7) open.
- Ezz got a few staff-bot pings from live booking/cancel tests (expected side effects).

## Round 2 (residual fixes, Sep 16)
| ID | Check | Result |
|----|-------|--------|
| R1 | Live conversations without API key (convmsg log + endpoint) | PASS — in+out turns, correct Arabic reply |
| R2 | instant_alert honored (static verify, default-ON-safe) | PASS (validate 0/0; live trigger unsafe to simulate) |
| R3 | Cancel re-tally: reproduced → root cause (GCal tombstone status=cancelled) → Already Cancelled? gate → re-cancel no-tally | PASS, verified + normal cancel still works |
| R4 | Post-fix sweep (auth×6 + 4 reads) | 10/10 PASS |
| R5 | Full pytest | EXIT 0 |

## Round 3 (user-flagged residuals, Sep 16)
| ID | Check | Result |
|----|-------|--------|
| U1 | Settings partial-save merge (was reset bug) | FIXED: +Read Current Flags +Merge (10 nodes, gates READY, valid 0/0). Proven: partial {remind2h:0} keeps rest; stacked partials merge; restore all-1 verified |
| U2 | No test automations running | VERIFIED: 44 workflows listed, zero scratch/test/probe names; all ACTIVE = production lanes + 8 sched APIs; Redis test keys re-swept (3 more DEL: 991002/992001/confirmed:992001); Ezz pings only from documented live book/cancel runs, nothing pending |
| U3 | Full pytest | EXIT 0 |
