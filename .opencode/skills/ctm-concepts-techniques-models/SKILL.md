---
name: ctm-concepts-techniques-models
description: Applies Van Roy & Haridi's CTM to program in the right computation model for the job: the kernel-language approach where declarative, concurrent, message-passing, and distributed models share one core, with dataflow variables, streams and laziness, agents and ports, and transactions for stateful concurrency. Use when the user says 'kernel language', 'declarative programming', 'dataflow variables', 'streams', 'lazy evaluation', 'message passing', 'concurrent programming model', 'transaction model', 'Van Roy Haridi', 'which programming model fits', or when choosing the right model (functional, concurrent, distributed) for a feature.
---

# Concepts, Techniques, and Models of Computer Programming (Van Roy & Haridi)

CTM teaches that programming concepts form a small kernel: add features to the kernel and you get a new, well-understood model. This skill uses that to pick and apply the right model.

## One kernel, many models

- All mainstream paradigms are layers on a small kernel of computations; choosing a model means choosing which features you need.
- Declarative models are the safest default: deterministic, easy to reason about, easy to test.
- Add concurrency or state only when the problem demands it; each addition removes guarantees.

## Concurrency and dataflow

- Dataflow variables bind once and synchronize automatically: producers and consumers coordinate without locks.
- Streams connect producers to consumers lazily, giving incremental computation and bounded memory use.
- Model agents with ports and messages when true asynchrony is required, and keep the protocol explicit.

## Distribution and transactions

- Distributed models need names and protocols for crossing machine boundaries; keep the interface small and explicit.
- Transactions give atomicity for stateful operations across concurrent access; define the isolation the model provides.
- Model failure explicitly: what the system guarantees and what the caller must handle.

## Choosing the model

- Match the model to the requirement: pure computation to declarative, incremental streams to lazy dataflow, concurrent agents to message passing, multi-node to distributed.
- Document the model choice and its guarantees in the design, not just in code.

## Pairs with
sicp-abstraction-and-interpretation, multiprocessor-concurrency, designing-event-driven-systems, functional-programming-scala, sicp-streams-lazy-evaluation
