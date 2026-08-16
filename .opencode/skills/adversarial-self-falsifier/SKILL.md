---
name: adversarial-self-falsifier
description: "Actively attacks and attempts to break generated code, math, or logic before finalizing the response. Use for any non-trivial code, algorithm, architecture, or security-relevant deliverable. Trigger phrases: 'make sure it's correct', 'is this safe', 'any bugs', 'harden this', or any solution you just generated."
---

# ADVERSARIAL SELF-FALSIFIER SKILL

## DIRECTIVE
Never approve a complex solution upon first generation. Before presenting any
code or architecture, act as an aggressive Red-Teamer and attempt to break your
own work using extreme edge cases, invalid inputs, and concurrency race
conditions.

## FALSIFICATION PROTOCOL
1. **Generate Draft Solution (Candidate A).**
2. **Switch Role to Adversary:**
   - Ask: "How can I trigger an uncaught exception in this code?"
   - Ask: "What happens under high load, network dropouts, or corrupted JSON inputs?"
   - Ask: "Are there any hardcoded assumptions or implicit state bugs?"
   - Ask: "What if the input is empty, gigantic, duplicated, or hostile?"
3. **Sandbox Stress Test:** Execute boundary-condition inputs inside a clean
   sandbox (this project: `venv/bin/python` + `pytest` — run the cases for real,
   do not simulate them in your head).
4. **Patch & Prove:** Patch all discovered failure points. Present ONLY
   Candidate B (the hardened solution) together with the evidence that Candidate
   A failed and Candidate B passes.

## Local adaptation
"Sandbox" here means the project venv, not Docker: write a throwaway script in
`/tmp` or a `pytest` test, run it, and paste the actual failure/success output.