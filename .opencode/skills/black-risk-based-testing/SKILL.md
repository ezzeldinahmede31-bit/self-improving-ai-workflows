---
name: black-risk-based-testing
description: "Manages testing by risk: analysis, priorities, and process control. Use when the user says 'risk-based testing', 'test management', 'test planning', 'Rex Black', 'Pragmatic Software Testing', 'test estimation', 'defect tracking', or when testing must be managed, not just performed."
---

# Black Risk-Based Testing

Distilled from Rex Black *Managing the Testing Process* + *Pragmatic
Software Testing*: testing is risk management under schedule pressure —
identify what threatens the release, aim testing there, and report status
in risks, not test counts.

## Purpose

Run testing as a managed activity: planned by risk, estimated honestly,
tracked visibly, and reported in business impact.

## The management loop

1. **Quality risk analysis (first, with stakeholders).** Enumerate risks
   (feature × failure mode), score impact × likelihood, sort. The top risks
   BECOME the test plan — every test traces to a risk it retires. Re-score
   as knowledge grows; risks, not documents, steer daily work.
2. **Estimate and staff by risk.** Test effort from risk coverage (not from
   code size alone): high-risk areas get design + review + automation;
   low-risk get smoke checks. Staff skills to risks (security risks need
   security testers). Say what the budget does NOT cover — explicitly.
3. **Track leading indicators.** Planned vs executed vs passed (with the
   RISK label on each), defect arrival/fix rates, open defects by risk
   (not just severity — a cosmetic bug on the payment page outranks a crash
   in an unused dialog). Escape defects reviewed for process gaps, never
   for blame.
4. **Report risks, not counts.** Status answers: which top risks are retired,
   which remain, what would retire them, and the ship recommendation with
   residual risk stated. "95% tests pass" without risk context is noise —
   translate every metric into release risk.
5. **Defect process that works.** Lifecycle (new → triage → fix → verify →
   close) with SLAs per severity; duplicates merged with data preserved;
   rejected reports get reasons (reporter education, not dismissal);
   root-cause categories trended (requirements? design? code?) to fix the
   process leaking the defects.

## Verification

Release readiness: top-risk retirement table, residual risks accepted in
writing by owners, defect trends healthy (arrival falling, fix keeping
pace), process-improvement action from escapes. Shipping on test-counts
alone is rejected as a decision basis.

## Pairs with

- `kaner-lessons-testing` (context judgment),
  `mcconnell-software-estimation` (test estimation),
  `berkun-making-things-happen` (driving the plan),
  `tradeoff-and-postmortem-documenter` (escape analysis).
