# Clinic system — master test matrix (world-class QA, living doc)
Every production bug gets a row here. Status: PASS / FAIL / UNPROVEN.

## A. Intent coverage (normal)
| ID | Scenario | Expect | Status |
|----|----------|--------|--------|
| A1 | greeting (هاي) | short Arabic greeting | PASS (1467 live) |
| A2 | price exact | 800 verbatim | PASS (1610: التنظيف والتلميع 800 جنيه مصري; hedges were KB-outage artifact) |
| A3 | hours/doctors/address | KB answer | PASS (prior battery) |
| A4 | book full slot | confirm+address+queue | PASS (1416) |
| A5 | cancel natural | find+cancel, event deleted | PASS (1297/98) |
| A6 | reschedule natural | atomic move + Cairo reply | PASS (1479) |
| A7 | complaint/human-request | deterministic ESC + summary, agent suppressed | PASS (1617/18: human-request intent) |
| A8 | graceful close | deterministic warm-close lane incl. combos (regex fix) | PASS (1709) |
| A9 | multi-intent | knowledge-multis deterministic (arabized, no agent); book+cancel = order rule + reschedule tool | PASS-deterministic for knowledge (1718: التنظيف والتلميع 800 جنيه); book+cancel via reschedule tool proven |
| A10 | language switch mid-conv | mirror new language | NEW |

## B. Special cases (edge)
| ID | Scenario | Expect | Status |
|----|----------|--------|--------|
| B1 | nonexistent service (زراعة الشعر) | no invention, escalate/offer | NEW |
| B2 | nonexistent doctor | no invention | NEW |
| B3 | correction (لا قصدي الحشو) | corrected entity + exact price | PASS (800→1200 both exact) |
| B4 | conflicting (احجز والغي) | clarify, no destructive act | NEW |
| B5 | past date booking | past-date refusal | PASS (tool path) |
| B6 | taken slot + verified alternatives | check-tool discipline (booking never used to check) + VALIDATOR live substitution | PASS (2389: validator replaced deliberation with deterministic offer, validated:true) |
| B7 | cutoff <24h cancel | staffOnly Arabic | PASS (1333) |
| B8 | resched: new-taken / past-new / unknown / old<24h | graceful each | PASS (direct 1485/87/90) |
| B9 | severe emergency keywords | deterministic ESC, agent suppressed | PASS (1491) |
| B10 | medical advice | NO prescription (safe) + deterministic severe net exists | PASS-safe (apology; severe-keyword path deterministic) |
| B11 | gibberish/empty/emoji/typo | polite + usable | PASS (prior battery) |
| B12 | voice unclear | fallback bypass | PASS (prior) |
| B13 | flood (3-5 rapid) | 1 processed, rest discarded | PASS (T1/storm) |
| B14 | duplicate delivery | discarded | PASS |
| B15 | callback taps (confirm/rate) | mapped + answered | PASS (1227/rating) |
| B16 | edited message / contact / sticker / location | handled | PASS (prior) |
| B17 | dice/poll/unsupported | graceful unsupported | PASS (prior) |

## C. Subsystems (deterministic)
| ID | Scenario | Expect | Status |
|----|----------|--------|--------|
| C1 | info touch 24h + confirm 2h w/ button | both fire | PASS (1314/15) |
| C2 | confirm via button/text | marked, no escalation | PASS |
| C3 | unconfirmed silence 2min | nurse ping with risk tally | PASS (prior R-lifecycle) |
| C4 | no-show follow-up | sent + record cleaned, one-shot | PASS (synthetic lifecycle) |
| C5 | post-visit thanks + form link + stars | sent | PASS (1314/15) |
| C6 | review form render+submit | digest exact | PASS (1250) |
| C7 | recall from DURABLE visits log (180d + invite-once) | table-driven, Redis-free | PASS (720 invited w/ correct chatId; 721 ignored; invite-once verified; limit250 cap found) |
| C8 | waitlist join (LPUSH) | LLEN=1 | PASS (1310) |
| C9 | waitlist offer on cancel | merged+sent+consumed (propertyName unwrap fix) | PASS (1640) |
| C10 | /stats real numbers | correct tallies | PASS (1318) |
| C11 | queue position tool | correct relay | PASS (prior) |
| C12 | ACK placeholder + edit-in-place | same message edited | PASS (1467 real chat) |
| C13 | edit-fail fallback chain | Placeholder→Edit→Fallback→Alert path executes | PASS (1680 wiring) |

## D. Security & platform
| ID | Scenario | Expect | Status |
|----|----------|--------|--------|
| D1 | webhook no/bad auth | 403, no execution | PASS (many) |
| D2 | stranger /stats | refused | PASS (prior) |
| D3 | secrets in outputs | none | PASS (design) |
| D4 | retention: records die post-appt | deleted | PASS (cleanup lane) |
| D5 | all 10 workflows active + health | active, healthz ok | PASS (audit) |
| D6 | latency: ACK <2s | placeholder instant | PASS (1464/67) |
| D7 | latency: final p50/p90 | measured(opts) | MEASURED 74s/214s (provider-bound) |
| D8 | hang cap | executionTimeout 300 FIRED live (1686 canceled at cap) | PASS |
