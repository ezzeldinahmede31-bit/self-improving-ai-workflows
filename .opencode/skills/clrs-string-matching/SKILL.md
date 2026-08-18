---
name: clrs-string-matching
description: "Applies the string-matching chapter of CLRS (Introduction to Algorithms) to find patterns in text correctly and fast: the naive scan, Rabin-Karp hashing, the Knuth-Morris-Pratt prefix function, the Boyer-Moore heuristics, and finite-automaton matching — with the preprocessing-versus-comparison trade-offs that decide which one to use. Use when the user says 'search for a pattern in text', 'Rabin-Karp', 'KMP', 'Knuth-Morris-Pratt', 'Boyer-Moore', 'prefix function', 'string search', 'find all occurrences', 'pattern matching', 'text search performance', or when implementing a search or matching primitive. Pairs with: clrs-algorithm-mastery, algorithm-design-manual-war-stories, algorithmic-math-reasoner, code-execution-guided-swemaster."
---

# String Matching (CLRS)

Finding a pattern in text is a preprocessing-versus-time trade: pay once to
build a structure, then scan the text once, regardless of how frequently the pattern
appears.

## When to use

- Implementing text search, find-all, or plagiarism-style scanning.
- Choosing the matching algorithm for pattern and text sizes.
- Understanding why naive scanning is slow on repetitive text.

## The naive approach

- Slide the pattern across the text and compare at every offset. O(n·m) worst
  case.
- Correct but wasteful; the smarter algorithms skip comparisons.

## Rabin-Karp (hashing)

- Compare rolling hashes of the window against the pattern hash; verify only on
  a hash match.
- Excellent for searching for multiple patterns at once and for plagiarism
  detection. Worst case is still quadratic, but expected behavior is linear.

## Knuth-Morris-Pratt (prefix function)

- Preprocess the pattern once to build the prefix function, which tells how much
  to shift after a mismatch — the text pointer never moves backward.
- Linear in text length, works with a single pass, no random hashing.

## Boyer-Moore (heuristics)

- Skips from the right end of the pattern using the bad-character and
  good-suffix heuristics.
- Often the fastest in practice on large alphabets and long patterns.

## Finite-automaton matching

- Build a DFA from the pattern; scan the text once, always advancing. Useful
  when the same text must be scanned against many patterns; the cost is in
  automaton construction.

Pairs with: clrs-algorithm-mastery, algorithm-design-manual-war-stories,
algorithmic-math-reasoner (complexity proofs), code-execution-guided-swemaster.
