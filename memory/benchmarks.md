# AIME 2025 FULL run — 30 problems (I-1..I-30), benchmark table

- Protocol: answers written BEFORE key unlock (`aime30_key.txt` chmod 0400 -> 0644),
  grading mechanical 1:1 (no fuzzy matching).
- Source: `yentinglin/aime_2025` (AoPS blocked). Key file: 30 lines `I-n: <answer>`.
- **SCORE: 29/30.**

| problem | my | key | result |
|---------|----|----|--------|
| I-1  | 70  | 70  | OK |
| I-2  | 468 | 468 | OK |
| I-3  | 588 | 588 | OK |
| I-4  | 49  | 49  | OK |
| I-5  | 16  | 16  | OK |
| I-6  | 82  | 82  | OK |
| I-7  | 117 | 117 | OK |
| I-8  | 106 | 106 | OK |
| I-9  | 279 | 279 | OK |
| I-10 | 336 | 336 | OK |
| I-11 | 504 | 504 | OK |
| I-12 | 293 | 293 | OK |
| I-13 | 821 | 821 | OK |
| I-14 | 237 | 237 | OK |
| I-15 | 77  | 77  | OK |
| I-16 | 610 | 610 | OK |
| I-17 | 62  | 62  | OK |
| I-18 | 150 | **149** | **X** |
| I-19 | 81  | 81  | OK |
| I-20 | 907 | 907 | OK |
| I-21 | 259 | 259 | OK |
| I-22 | 113 | 113 | OK |
| I-23 | 510 | 510 | OK |
| I-24 | 19  | 19  | OK |
| I-25 | 204 | 204 | OK |
| I-26 | 248 | 248 | OK |
| I-27 | 60  | 60  | OK |
| I-28 | 104 | 104 | OK |
| I-29 | 735 | 735 | OK |
| I-30 | 240 | 240 | OK |

## Root cause of the single miss (I-18)
- Problem: `sin(7π·sin(5x)) = 0` on `0<x<2π`; n = #roots, t = #tangent
  roots; find n+t (key: 149).
- My wrong count: n = 140 (5 periods × 28) + t = 10 -> 150.
- Correct: roots at `sin(5x) = j/7`, j ∈ {-7..7}:
  - j = ±1..±6 (12 inner levels): 10 roots each = 120 (2 per sin-period × 5)
  - j = 0: **9** (not 10 — level 0 rides the period endpoints: 5x = mπ, m=1..9 in (0,10π))
  - j = ±7 (sin=±1): 5+5 = 10
  - n = 139; t = 10 (f'=0 at roots ⟺ cos(5x)=0 ⟺ sin(5x)=±1); n+t = **149**.
- Lesson: when counting range-crossings by "periods × 2", levels that hit the
  boundary of the amplitude (0, ±1) lose/gain a crossing — check open-interval
  endpoint behavior explicitly.

## Methods that earned the other 29
- I-25 (expected regions, 204): MC-crossing model validated (unrestricted
  chords → 1/3 sanity); p' = P(two quadrant-chords cross) = 17/36 exact,
  E[regions] = 4 + 25·(1+4/3) + 300·(17/36) = 204.
- I-26 (248): raw fraction iteration EXPLODES (digits double per step ~2^k).
  Found reduced-pair recurrence (m', n') = (m²-mn+n², 3mn)/c with
  c = 3 ⟺ m ≡ -n (mod 3); verified vs exact x2..x6 mod 1000; iterated
  2024 steps mod 3^2027·1000 (~970-digit ints). m+n ≡ 248.
- I-27 (60): pentagon coords in Q(√3); min at interior Fermat-Weber point;
  v = 38 + 19√3 (minpoly v² - 76v + 361 = 0, 220-digit confirmation) -> 60.
- I-28 (104): sympy nsolve gave b=16√3, h=26, lx=3√3, ky=2; area BKLC =
  104√3.
- I-30 (240): self-intersection of critical-locus curve (k(x), h(x)): ties
  at x = 11.677..., 23.235..., 30.901... → k = 8, 32, 200 (EXACT integers);
  each verified to have exactly 2 global minima; sum = 240.
- I-23 (510): earlier ´2281.5√3´ was wrong; correct finite region is the
  triangle (-1,-1),(25,25),(-1,38) → projected 507 → 507√3 → 510.
- I-16 (610): hand derivation — greedy fails iff N ≡ 5..9 or 15..19 (mod 25)
  with N ≥ 25 → 195+195 failures → 610 successes (confirmed by old DP).
- I-22 (113): perfect matchings of 24-gon by chord-step d: Σ 2^{gcd(24,d)}
  (component length ≥4) with L=2 components counting 1: 113.

## Final tally
- 29/30 exact (the earlier 6/6 sample continues to hold).
- Model: opencode deepseek-v4-flash-free + full skill-stack (algorithmic-math-reasoner,
  evidence-over-memory, test-time-compute-scaling, sympy/mpmath/numpy).