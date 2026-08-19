---
name: taocp-vol2-seminumerical-algorithms
description: Applies Knuth's TAOCP Volume 2 to random-number generation and arithmetic: linear congruential generators, statistical tests of randomness, arbitrary-precision arithmetic, rational and polynomial arithmetic, and number-theoretic algorithms such as gcd and modular exponentiation. Use when the user says 'random number generation', 'PRNG', 'test randomness', 'arbitrary precision arithmetic', 'big integer math', 'polynomial arithmetic', 'gcd', 'modular exponentiation', 'Knuth random', or when a numeric algorithm must be correct and its randomness honest.
---

# TAOCP Vol 2: Seminumerical Algorithms

Volume 2 is the canonical treatment of the two most-used numeric building blocks: pseudo-random numbers and arithmetic on numbers too large for the machine word. This skill applies both correctly.

## Random number generation

- Linear congruential generators are simple but must use carefully chosen constants and enough modulus bits to avoid short cycles.
- Never use a generator's output directly for security-critical work; test any generator statistically before trusting it.
- Separate the generator from the distribution: map uniform output to the target distribution explicitly.

## Statistical testing

- Run the standard tests (frequency, serial, gap, run, poker) on a sample before declaring a generator usable.
- A generator that passes one test suite is not proven random; tests provide evidence, not guarantees.
- Record the test configuration so results are reproducible by anyone.

## Arbitrary precision arithmetic

- Implement arithmetic on digit arrays with carry propagation, and estimate the digit bound before each operation.
- Choose representation (base, sign handling) up front so add, multiply, and divide share one convention.
- For big-integer multiplication, switch to subquadratic methods when the operands are large enough to make them worthwhile.

## Number-theoretic algorithms

- gcd via Euclid's algorithm, and extended gcd for modular inverses, are the foundation of all modular arithmetic.
- Modular exponentiation by repeated squaring is the standard fast path for raising powers modulo n.
- When analysis needs an exact result, verify with an independent small implementation before trusting the math.

## Pairs with
taocp-vol1-fundamental-algorithms, algorithmic-math-reasoner, formal-math-logic-verification-engine, applied-cryptography-engineering, math-olympiad
