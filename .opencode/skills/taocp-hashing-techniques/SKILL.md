---
name: taocp-hashing-techniques
description: Applies the hashing section of Knuth's TAOCP Volume 3 to design correct, fast hash tables: the choice of hash functions and their statistical behavior, open addressing with probing sequences, separate chaining with collision lists, load factors, and the analysis of expected search effort so a hash design ships with a defensible complexity argument rather than a guess. Use when the user says 'design a hash table', 'choose a hash function', 'open addressing', 'linear probing', 'double hashing', 'separate chaining', 'load factor', 'hash collision strategy', 'why is my hash map slow', 'Knuth hashing', or when a hash-based structure must be sized and analyzed.
---

# The Art of Computer Programming: Hashing

Knuth's hashing treatment (TAOCP Volume 3) gives a hash table the same rigor as a sorting algorithm: every design choice — function, probe sequence, load factor — has a measured effect on the expected number of probes. This skill encodes the decision procedure so a hash table is designed with analysis, not guessing.

## Choosing a Hash Function
- Prefer a function that spreads inputs uniformly across the table; the goal is to scatter keys as if by random chance regardless of patterns in the data.
- Use the multiplicative method (multiply by a constant and take the high-order bits) as a robust default that resists key clustering.
- Beware of division-style functions on power-of-two table sizes, which throw away low-order bits that real keys often share.
- Test the chosen function on the actual key distribution when patterns are suspected; a statistically good function on adversarial keys beats a clever-looking one.

## Open Addressing
- Open addressing stores everything in the table itself and resolves collisions with a probe sequence; no extra memory per entry.
- Linear probing is simplest and cache-friendly but clusters long runs of occupied slots as the table fills.
- Double hashing uses a second function to compute the probe step, eliminating primary clustering.
- Stop-and-halt rule: when the load factor grows, probe cost climbs sharply — open addressing needs headroom or rehashing.
- Deletion under open addressing requires tombstones so probe chains are not broken.

## Separate Chaining
- Separate chaining keeps a linked list per bucket, so deletion is trivial and the table tolerates high load factors with graceful degradation.
- Chain length is governed by the load factor; expected search cost follows from the average list length.
- Trade-off: chaining spends a pointer or an entry per element, so it suits in-memory maps where node overhead is acceptable.

## Load Factor and Search Effort
- Expected probe cost rises with the load factor; know the curve for the chosen method before sizing the table.
- Pick a target load factor and size the table so the working set stays under it, then rehash when the threshold is crossed.
- Compare the expected probes of the candidate scheme against the actual access pattern — hot keys revisited often make even average cost matter.
- Document the chosen load factor and rehash rule as part of the design, not as an afterthought.

## Practical Design Rules
- Prefer the simplest scheme that meets the expected cost; linear probing with headroom beats double hashing when the table is not near capacity.
- If keys can be attacker-controlled, avoid plain division hashing on power-of-two tables and favor a randomized or multiplicative function.
- Size the table to a prime or use multiplicative hashing so patterns in keys do not align with the table size.
- Always provide a rehash path so the table can grow without rebuild surprises.
- Measure with the real workload after deployment; the analysis predicts, the profiler confirms.

## Pairs with
taocp-vol3-sorting-searching, taocp-vol1-fundamental-algorithms, clrs-hashing-techniques, database-internals-engines, systems-performance-profiling
