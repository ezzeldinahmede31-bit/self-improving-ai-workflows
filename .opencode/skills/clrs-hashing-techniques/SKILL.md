---
name: clrs-hashing-techniques
description: "Applies the hashing chapter of CLRS (Introduction to Algorithms) to design correct, fast hash-based structures: hash functions and universal families, collision resolution via chaining vs open addressing (linear / quadratic probing, double hashing), load-factor behavior, deletion discipline, and defense against adversarial keys. Use when the user says 'design a hash table', 'universal hashing', 'collision resolution', 'chaining vs open addressing', 'double hashing', 'adversarial keys', 'hash DoS', 'hash function choice', 'load factor', 'rehashing', or when a hash map must be fast and hard to attack. Pairs with: clrs-data-structures-mastery, clrs-algorithm-mastery, database-internals-engines, web-security-browser-internals, off-by-one-boundary-guard."
---

# Hashing Techniques (CLRS)

A hash table trades ordering for speed: expected constant time per operation.
The whole discipline is making the hash function good and the collisions cheap.

## When to use

- Lookup-heavy structures where order does not matter.
- Defending against adversarial keys (attacker-chosen inputs).
- Choosing the collision strategy for a specific workload.

## Hash functions and universal families

- A good hash spreads keys evenly across the table; a bad one clusters them.
- Universal hashing picks the function at random from a family, so no fixed
  adversary can know which inputs collide — the expected worst-case behavior
  becomes provably good.
- For integer keys use multiplication or shift-based mixing; never use a naive
  modulo of user input without the universal layer.

## Chaining

- Each table slot holds a linked list of keys that hash to it.
- With load factor α = n/m and simple uniform hashing, expected lookup time is
  O(1 + α). Keep α bounded; rehash when it drifts high.
- Deletion is trivial — remove from the list.

## Open addressing

- All keys live in the table; probing finds an empty slot (linear, quadratic,
  or double hashing).
- Load factor must stay well below 1 or probes explode; deletion must use
  tombstones or a rehash, never plain removal (a removed slot would break the
  probe chain).
- Double hashing spreads probes best; linear probing is simplest but clusters.

## Adversarial keys

- With a fixed hash, an attacker can pick keys that all land in one slot, turning
  lookups into O(n) operations. Universal hashing and a randomized seed are the
  defenses.
- This is why web-facing hash maps must not use a deterministic bare hash.

Pairs with: clrs-data-structures-mastery, database-internals-engines (real hash
designs), web-security-browser-internals (hash-DoS surface), off-by-one-boundary-guard
(slot-index boundary care).
