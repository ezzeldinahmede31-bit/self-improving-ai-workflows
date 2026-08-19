---
name: concrete-mathematics
description: Applies Graham, Knuth & Patashnik's Concrete Mathematics to solve sums, recurrences, and discrete problems exactly: summation and summation-by-parts, recurrences and the repertoire method, integer functions and floor/ceiling, number theory, binomial coefficients and their identities, generating functions, discrete probability, and asymptotic methods. Use when the user says 'solve this sum', 'concrete mathematics', 'repertoire method', 'generating functions', 'recurrence', 'floor ceiling', 'binomial identity', 'asymptotic expansion', 'discrete probability', 'GKP', or when a discrete math expression needs an exact closed form.
---

# Concrete Mathematics (Graham, Knuth, Patashnik)

Concrete mathematics is the bridge from calculus-style reasoning to the discrete world programmers live in. This skill applies its exact methods and honesty about closed forms.

## Summation

- Change the order of summation and factor terms to transform hard sums into known ones.
- The repertoire method solves recurrences by guessing a general linear form and fitting it to boundary conditions.
- Asymptotic estimates are the fallback when no closed form exists; say so rather than claiming one.

## Integer functions

- Floor and ceiling laws convert discrete and continuous reasoning without off-by-one traps.
- State whether a range endpoint is open or closed on each side; the answer changes at the boundary.
- Use explicit bounds when a formula depends on the parity or sign of its arguments.

## Number theory and binomials

- Work modulo small primes to test identities, then prove them with the algebraic laws of binomial coefficients.
- Generating functions turn recurrences into equations in a formal power series; solve there, then extract the coefficients.
- Discrete probability on finite sample spaces is exact arithmetic; keep it exact instead of approximating early.

## Asymptotics discipline

- Give the order of growth with the constant where it matters for the decision at hand.
- Confirm every closed form with a small-case numeric check before using it.

## Pairs with
algorithmic-math-reasoner, formal-math-logic-verification-engine, taocp-vol1-fundamental-algorithms, mathematics-for-computer-science, math-olympiad
