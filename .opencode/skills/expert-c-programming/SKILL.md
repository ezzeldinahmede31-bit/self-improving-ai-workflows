---
name: expert-c-programming
description: Applies Peter van der Linden's Expert C Programming to the deep semantics of C: the difference arrays versus pointers, storage classes and the extern/static split, declaration parsing with the spiral rule, struct layout and alignment, const and volatile, operator precedence, linking and the common C pitfalls, and why C is fast when its model is respected. Use when the user says 'expert C', 'array versus pointer', 'spiral rule', 'declaration parsing', 'extern static', 'struct padding', 'const volatile', 'operator precedence C', 'memory layout C', 'linking C', 'van der Linden', or when a subtle C behavior is causing a bug.
---

# Expert C Programming: Deep C Secrets (Peter van der Linden)

Van der Linden explains the C semantics that trip even experienced programmers. This skill applies those deep semantics to write correct, portable C.

## Arrays versus pointers

- An array name decays to a pointer in most expressions; know where it does not (sizeof, the address-of operator, initializers).
- Pointer arithmetic is scaled by the pointed-to type; compute the byte offset explicitly when you need it.
- Subscripting is commutative in C but reads best one way; write the clearest form.

## Declarations and the spiral rule

- Parse declarations with the spiral rule: start at the identifier and spiral outward through the specifiers.
- A typedef is a storage-class-like alias, not a type; use it to simplify complex function pointer types.
- const and volatile describe the object, not the pointer, unless placed after the asterisk.

## Storage, layout, and linking

- extern declares, definitions allocate; the linker resolves names only for defined objects.
- Struct layout inserts padding for alignment; serialize with explicit byte packing when the wire format matters.
- Static gives internal linkage or file-scope lifetime depending on position; use it to hide module internals.

## Pitfalls and the fast model

- Operator precedence: assignment and comparison, the comma operator, and pointer-increment bindings cause the classic bugs.
- A short-circuit condition that increments or assigns has side effects; isolate them.
- Benchmark before assuming; C is fast when the data layout matches the access pattern.

## Pairs with
c-programming-language, computer-systems-programmers-perspective, code-debugging, systems-performance-profiling
