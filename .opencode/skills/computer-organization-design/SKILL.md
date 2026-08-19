---
name: computer-organization-design
description: Applies Patterson & Hennessy's Computer Organization and Design (the classic 'Patterson-Hennessy') to reason about what a program costs on real hardware: the MIPS/RISC-V instruction set and the correspondence of C to assembly, arithmetic and data representation, the processor datapath and control, memory hierarchies (cache, DRAM, virtual memory) and performance measurement with Amdahl's law. Use when the user says 'computer organization', 'instruction set', 'MIPS', 'RISC-V', 'assembly to C', 'datapath', 'pipeline', 'cache design', 'Amdahl law', 'clock cycle', 'CPI', 'Patterson Hennessy', or when a program's real hardware cost must be understood.
---

# Computer Organization and Design (Patterson & Hennessy)

Patterson & Hennessy teaches how instructions execute on real hardware, so a programmer can predict cost instead of guessing. This skill applies that ground-truth view to code and architecture choices.

## The instruction set as the contract

- Every C construct maps to a small set of instructions; knowing that mapping explains why code behaves as it does.
- Choose instructions by their cost on the target: register operations are cheapest, memory access costs latency, and branches cost pipeline flushes.
- Use the processor's canonical instruction set as the baseline; RISC-V and MIPS share the load-store discipline.

## Performance measurement

- Performance is measured in execution time, not clock frequency or instruction volume alone.
- CPI (cycles per instruction) times the instruction volume times the clock period equals time; change one factor and re-measure.
- Amdahl's law bounds the speedup of improving one part: the improvement is capped by the rest of the program.

## The memory hierarchy

- Cache behavior dominates real performance; structure the data and loop order so access exhibits locality.
- A cache miss costs far more than a cache hit; the miss path is where most performance is lost.
- Virtual memory and paging add another layer; keep working sets within the physical memory budget.

## Datapath and pipelining

- Pipelining overlaps instruction stages; hazards (data, control, structural) cost stalls or forwarding logic.
- Understand which instructions conflict and order the code to reduce pipeline stalls.
- Read a disassembly when performance questions arise; the compiler's schedule reveals the real cost.

## Pairs with
computer-systems-programmers-perspective, computer-architecture-quantitative, systems-performance-profiling, operating-systems-three-easy-pieces, nand-to-tetris-elements-computing
