---
name: fluent-python
description: Applies Luciano Ramalho's Fluent Python to write Python that uses the language the way it was designed: the data model and special methods, sequence and mapping protocols, functions as first-class objects, descriptors, decorators, operator overloading, and async pipelines. Encodes the principle that understanding the data model makes code behave predictably and read naturally. Use when the user says 'use Python idiomatically', 'special methods', 'make my class behave like a sequence', 'decorator or descriptor', 'dunder methods', or 'build a small DSL in Python'.
---

# fluent-python

Fluent Python is about the data model: every special method, protocol, and language feature exists for a reason, and code that honors those contracts behaves predictably. This skill transfers that fluency so a class, function, or pipeline reads like idiomatic Python rather than translated C.

## Core principles

- The data model defines how objects behave, so follow the dunder contracts exactly.
- Protocols beat inheritance: implement the behavior, not the ancestor.
- Functions are objects: pass them, return them, decorate them.
- Choose the right collection type for the access pattern.
- Keep classes small and their special methods few and correct.
- Understand the machinery before using the magic.

## Key patterns

- Implement `__getitem__` and `__len__` to make a class behave like a sequence.
- Rely on collections.abc to express intent and get behavior for free.
- Use functools tools (partial, cached_property, wraps) for callable composition.
- Build decorators that preserve names and signatures.
- Model domain objects as dataclasses with clear equality semantics.
- Compose async/await pipelines for concurrent I/O-heavy work.

## Applying this to scripting/automation/code

- Write Code nodes whose objects behave predictably under n8n's transformations.
- Model workflow records as classes with explicit equality and representation.
- Build small domain languages and parsers as fluent Python objects.
- Use protocols so different data sources share one interface.

## Hard rules

- Honor mutable and immutable semantics exactly as documented.
- Keep `__eq__` and `__hash__` consistent within a class.
- Never name a method like a dunder unless you implement the dunder.
- Avoid cleverness that costs a reader their understanding.
- Profile before optimizing; fluency is not the same as speed.
- Test the behavior that special methods provide.

## Pairs with

code-linter-python-js, code-execution-guided-swemaster, evidence-over-memory, pragmatic-programmer, clean-craftsmanship
