---
name: seacord-secure-coding
description: "Writes C/C++ and systems code that resists exploitation: input validation, memory safety, and integer correctness. Use when the user says 'secure coding', 'buffer overflow', 'format string', 'integer overflow', 'use after free', 'tainted input', 'Seacord', 'CERT C', or when any C/C++ code handles untrusted data."
---

# Seacord Secure Coding

Distilled from Robert Seacord's *Secure Coding in C and C++* (CERT rules):
most exploitable bugs come from a small set of unsafe habits. Replace each
habit with its safe counterpart, mechanically.

## Purpose

Eliminate the classic vulnerability classes at the source line — not with
mitigations piled on top of unsafe code.

## The rules (apply in code review order)

1. **Validate all inputs.** Treat every external byte as hostile until proven
   otherwise: range, size, encoding, and null-termination checked BEFORE use.
   Canonicalize paths; reject rather than sanitize when the input shape is
   wrong.
2. **Strings are bounded.** Prefer explicit-length APIs (`strncpy`-family done
   right, `snprintf`, C++ `std::string`/`string_view`). Every copy names its
   destination size; truncation is handled, never silent.
3. **Integers are checked.** Signed overflow is undefined behavior; unsigned
   wraps silently. Check BEFORE the operation (precondition tests,
   wider-type staging, or checked-arithmetic helpers). Sizes for allocation
   are validated against overflow (multiplication checked first).
4. **Memory has a single owner.** Free exactly once; null the pointer after;
   no use-after-free, no double-free. Prefer RAII/scoped ownership so the
   lifetime is structural, not remembered. Dynamic arrays carry their
   capacity alongside the pointer.
5. **Errors fail closed.** Every fallible call's return is checked; error
   paths deny by default and release resources. `errno`-style channels are
   read before any other call clobbers them. Assertions guard invariants in
   debug; production uses handled errors, never bare `assert` on untrusted
   input.
6. **Concurrency is disciplined.** Shared state under explicit locking with a
   documented lock order (no ad-hoc nesting); time-of-check to time-of-use
   races closed by holding the guard across check AND use; threads joined,
   never detached-and-forgotten.
7. **Heed the toolchain.** Zero warnings at high warning levels; static
   analysis clean; sanitizers (address/UB) green in tests; FORTIFY and
   protections on in builds. A new warning is a defect until proven otherwise.

## Verification

Secure review per function: inputs enumerated + validated, every copy
bounded, every arithmetic checked, ownership stated, error paths closed,
locks ordered. One unchecked item = one finding.

## Pairs with

- `security-review` (audit process), `expert-c-programming`/`modern-c`
  (language depth), `zeller-why-programs-fail` (finding the flaw),
  `aumasson-serious-crypto` (crypto misuse).
