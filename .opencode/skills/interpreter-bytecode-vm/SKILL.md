---
name: interpreter-bytecode-vm
description: Applies the clox half of Robert Nystrom's Crafting Interpreters to build a bytecode virtual machine: chunks and opcodes, a value stack, the compiler that emits bytecode from a recursive-descent parser, the dispatch loop, and the mark-and-sweep garbage collector that keeps long-running interpreters stable. Use when the user says 'build a bytecode interpreter', 'virtual machine', 'clox', 'bytecode compiler', 'opcodes', 'value stack', 'dispatch loop', 'garbage collection', 'mark and sweep', 'compile a language to bytecode', 'make the interpreter faster', or when a tree-walking interpreter is too slow and needs a compiled-to-bytecode core. Pairs with: crafting-interpreters, dragon-book-compilers, sicp-interpreter-evaluator, systems-performance-profiling.
---

# Interpreter Bytecode VM

Transfers the clox design from Crafting Interpreters to any language runtime that must go faster than tree-walking: compile source to a compact bytecode, execute it in a tight dispatch loop, and keep memory safe with a real collector.

## When to use
- A tree-walking interpreter is correct but too slow.
- Building a runtime that must be portable across platforms.
- Teaching or implementing a minimal VM as the core of a larger system.

## Chunks and opcodes
- A chunk is a flat array of opcodes plus a constant table and line information for stack traces.
- Keep opcodes small and explicit; each opcode names the exact operation on the stack.
- Store constants out-of-line in the chunk's constant table, referenced by index.

## The value stack
- All evaluation happens on a shared value stack; every opcode either pushes, pops, or transforms the top.
- Track the stack pointer rigorously; every branch and return must leave the stack balanced.
- Represent values with a tagged union so arithmetic and calls know the type at runtime.

## Compiling to bytecode
- Compile from a recursive-descent parser directly to bytecode, emitting a chunk as productions are recognized.
- Resolve variables to stack slots or upvalue captures at compile time; the VM then does no symbol lookup.
- Emit jump opcodes with placeholder operands and patch them once the target is known.

## The dispatch loop
- The core loop fetches an opcode, switches on it, and updates the instruction pointer; keep it tight and branch-predictable.
- Handle function calls by pushing a call frame; each frame owns its stack base and return address.
- Add a disassembler early — readable traces make VM bugs trivial to find.

## Garbage collection
- Use mark-and-sweep: reachable objects are marked from roots (the stack, call frames, and the global table), then unmarked objects are freed.
- Run a collection when allocation pressure grows; the pause must be bounded for interactive runtimes.

## Verification discipline
- Assert chunk balance: every compiled program runs to a clean halt with the expected stack depth.
- Stress-test the collector with cycles and deep recursion; assert no leaks and no use-after-free.

## Pairs with
crafting-interpreters, dragon-book-compilers, sicp-interpreter-evaluator, systems-performance-profiling.