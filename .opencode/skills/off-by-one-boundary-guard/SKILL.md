---
name: off-by-one-boundary-guard
description: "Destroys the off-by-one class of errors in counting problems (open vs closed intervals, fence-post counts, period-crossing counts, inclusive/exclusive ranges, endpoint levels, integer ranges). The verified I-18 Grade-A case is encoded here: 'how many x in (0, 2π) solve sin(7π sin(5x)) = 0' → 139 roots + 10 tangencies = 149, NOT 150. Use whenever counting solutions, enumerating cases, computing sums over ranges, counting periods × crossings, or any answer that differs by ±1 from a plausible count. Clean Code alignment: this skill enforces 'precision over cleverness' (Clean Code principle: 'express the author's intent clearly — no hidden surprises'), 'meaningful names' (counting variables should explicitly state interval status, e.g., 'inclusive_lower' vs 'exclusive_lower'), and 'no duplication' (avoid reusing the same boundary formula without Gate 1 inventory). Trigger phrases: 'how many', 'count', 'between a and b', 'in the interval', 'for i in', 'inclusive', 'divisible', 'at most / at least', 'n+1 vs n', 'fence-post', AIME/USAMO/MATH-500 counting problems."
---

# Off-by-One Boundary Guard

The single most common integer-error in fast models is a ±1 at a boundary.
Root cause: treating an OPEN interval/level as CLOSED (or vice versa) while
sweeping a "periods × crossings" or "range × rate" formula. It is NOT a
reasoning failure — it is a boundary-bookkeeping failure, and it is
PREVENTABLE by making the boundary inventory an explicit checklist step.

## Five-gate protocol (run before finalizing ANY count)

### Gate 1 — Boundary inventory
Write down, literally:
- Every interval in the problem with its ENDPOINT STATUS: `(a,b)` open, `[a,b]`
  closed, `a<x<b`, `x≤N`, "between", "strictly between", "up to and including".
- Every special LEVEL of the function being counted (for trig/continuous):
  amplitude extremes `±1` (min/max), zero level `0` (period endpoints),
  inflection/critical levels.
- Every range boundary in discrete counts: `for i in range(lo, hi)` =
  `hi − lo` elements (Python); inclusive `lo..hi` = `hi − lo + 1`.
- Grid/path/combinatoric extremes: corners, first/last columns, diagonals.

Rule: if the inventory line is not written, the count is not final.

### Gate 2 — Fence-post formula
- N segments ⇒ N+1 points. `last − first` vs `last − first + 1` — decide by
  reading Gate 1's endpoint status, never by feel.
- Multiples of d in `(a,b)`: `floor(b/d) − ceil(a/d) + 1` for INCLUSIVE,
  and for EXCLUSIVE boundaries shift: `floor((b−1)/d)` style adjustments —
  write the adjusted formula explicitly.
- Periods × crossings: generic interior level ⇒ `k·2` crossings over k full
  periods. BUT the level AT the period boundary (0 at sin's multiples of π,
  ±1 at maxima) does NOT cross twice: count it ONCE per period, and check the
  OPEN/CLOSED ends of the total range — the shared endpoint may add or drop
  exactly ONE root.

### Gate 3 — Endpoint plug-in test
Substitute BOTH endpoints (a and b) into the defining equation/condition and
record whether each is a solution. Then:
- open end that solves ⇒ subtract 1 from the naive count;
- closed end that solves ⇒ keep it;
- endpoint NOT a solution ⇒ no adjustment.
For level counting: test the level against the period endpoints (mπ, π/2+mπ,
...). For `sin(5x)=0` on `(0, 2π)`: the roots are `x = mπ/5` with `m=1..9`
— `m=0` and `m=10` are EXCLUDED by the open interval; writing 5 periods × 2
crossings = 10 is WRONG: it is 9. This one subtraction is the entire lesson.

### Gate 4 — Encoding-independent enumeration
Never trust a single counting formula. Re-enumerate with a DIFFERENT
representation:
- Finite cases: brute-force loop over every candidate (grid of points,
  all k values, all ranges) in code (numpy/sympy/mini script), count directly,
  compare to the formula.
- Continuous cases: sample/numeric scan at fine resolution to confirm the
  count of sign changes / crossings (np.diff(np.sign(...))), plus derivative
  check for tangencies (f' = 0 at root).
- Discrete: count via an explicit generator (itertools / recursion for n=1,2,3
  small cases) and extrapolate only with a stated formula, then re-verify.
If enumeration says formula±1 → the boundary is the bug: rerun Gates 1–3.

### Gate 5 — Second-method + parity check
Derive the count by an INDEPENDENT method (algebraic level-count AND
derivative/geometry; inclusion-exclusion AND direct listing; complement
counting). Cross-checks that catch ±1:
- Total = Σ over disjoint buckets must match the naive total.
- Symmetry: even/odd parity of the count where the problem implies it.
- "Answer differs from mine by exactly 1" ⇒ assume off-by-one FIRST, audit
  boundaries before touching the core math.

## Known pitfall patterns (checklist)

| Pattern | Trap | Fix |
|---|---|---|
| sin/cos equation over (0, 2πk) | "2 roots per period" at level 0 or ±1 | level 0 at period ends: k periods ⇒ 2k−1 roots (shared endpoints); ±1: k roots |
| "Between a and b" | a and b excluded/included guessed | plug a, b into condition; adjust ±1 |
| Multiples in range | floor/ceil off-by-one | use explicit floor(b/d)−ceil(a/d)+1 per endpoint status |
| Loops `range(lo,hi)`, inclusive `lo..hi` | hi−lo vs hi−lo+1 | decide from problem wording (≤ vs <) |
| Divisions: "a divides b" | counting divisors of n up to √n | divisors come in pairs except perfect squares |
| Periods × crossings general | ignoring boundary levels | Gate 2 rule: deviation ONLY at boundary levels |
| Probability "≥ 5 vs > 5" | equality case | enumerate the equality event separately |
| Summations Σ over m | m or m−1 terms when reindexed | reindex with explicit first/last substitution |
| Grid paths / lattice points | corners double-counted | draw the 2×2 and 3×3 cases, generalize by induction |

## Worked case: AIME 2025 I-18 (the skill's namesake)

f(x) = sin(7π·sin(5x)), count roots n + tangencies t on 0 < x < 2π.
- Levels: sin(5x) = j/7 for j ∈ {−7..7} (15 levels).
- Gate 2: generic levels j = ±1..±6 (12 levels): 2 crossings/period × 5
  periods = 10 each ⇒ 120. Level j = 0: period-boundary level ⇒ 9 not 10.
  Levels ±1 (amplitude): 1/period ⇒ 5+5 = 10. n = 139.
- Gate 3: endpoints x→0, x→2π: sin(5x) → 0: excluded by open interval
  (j=0 gives 5x = 0 or 10π — both outside). The 10th "crossing" of level 0
  was the shared boundary — dropped once.
- Tangencies t: f' = 0 at a root ⟺ cos(5x) = 0 ⟺ sin(5x) = ±1 (j=±7 levels):
  t = 10. n + t = 149 (not 150).
- The naive answer 150 came from "5 periods × (2×13 + 1) + …" style sweeping —
  exactly one shared endpoint too many. 149 is the keyed answer.

## Rules of engagement
- Gate 1 inventory is MANDATORY for any count; skip it only when the count is
  from an exhaustive enumeration that itself is the answer.
- When two methods disagree by exactly 1, both must be audited for their OWN
  boundary handling (the formula AND the enumeration can each be off once).
- If the answer must be an integer in a range and your count sits at a
  boundary value (min/max), redo Gates 3–4 before writing it.
- Pair with `algorithmic-math-reasoner` (formal restatement + brute-force
  cross-validation) and `evidence-over-memory` (never state a count from
  memory — recompute).