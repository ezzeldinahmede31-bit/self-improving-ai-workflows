---
name: computational-geometry
description: "Solves geometry algorithmically: hulls, intersections, triangulations, diagrams. Use when the user says 'convex hull', 'segment intersection', 'sweep line', 'triangulation', 'Voronoi', 'Delaunay', 'point location', 'robust predicates', 'de Berg', or when shapes, maps, or layouts need exact algorithms."
---

# Computational Geometry

Distilled from de Berg et al.'s *Computational Geometry: Algorithms and
Applications*: geometry becomes tractable through orientation tests,
sweep-line order, and divide-and-conquer — plus paranoia about degeneracies.

## Purpose

Pick the right geometric algorithm with its bound, and implement it so
degenerate inputs (collinear, coincident, cocircular) do not silently corrupt
output.

## The toolkit (problem -> method -> bound)

1. **Orientation is everything.** The `orient(p,q,r)` predicate (sign of the
   cross product) decides left/right/collinear. Build ALL decisions on exact
   predicates (integers or adaptive arithmetic) — float comparisons at
   branch points are the classic corruption source.
2. **Convex hulls.** Graham scan (sort by angle, maintain left turns) or
   divide-and-conquer; both O(n log n), optimal. Andrew's monotone chain is
   the implementation sweet spot. Output in consistent winding order.
3. **Segment intersection via sweep line.** Sort endpoints, sweep left to
   right maintaining y-ordered status in a balanced tree; only NEIGHBORS can
   intersect next. O((n+k) log n). Event queue discipline (no duplicate
   events, handle shared endpoints explicitly).
4. **Triangulation.** Polygon triangulation O(n log n) (and linear with
   Chazelle-level effort — know it exists, ship the log factor). Delaunay
   maximizes the minimum angle (in-circle test); Voronoi is its dual —
   nearest-site queries fall out for free.
5. **Point location and range search.** Trapezoidal maps / kd-trees / range
   trees with fractional cascading; state preprocessing vs query bounds
   explicitly (logarithmic query usually costs superlinear build).
6. **Robustness rules.** Epsilon-free design: exact predicates, symbolic
   perturbation for degeneracies, snap-rounding documented where used. Test
   with: random clouds, grids, all-collinear, all-coincident, cocircular
   sets. If only random tests pass, the code is not done.

## Verification

Each routine ships with: asymptotic bound + which structure buys it,
degeneracy handling stated, and the five hostile test sets passing. A
geometry routine without a degeneracy story is rejected.

## Pairs with

- `clrs-graph-algorithm-design` (planar graphs, duality),
  `clrs-sorting-and-ordering` (sweep ordering),
  `foley-computer-graphics` (rendering uses of geometry),
  `algorithmic-math-reasoner` (proof discipline).
