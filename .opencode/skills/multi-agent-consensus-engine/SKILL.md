---
name: multi-agent-consensus-engine
description: "Simulates an expert panel (Software Architect, Security Engineer, QA Expert) to review, debate, and reach consensus on complex tasks before delivery. Use for architecture, security-sensitive, and multi-file refactoring work. Trigger phrases: 'design the', 'architecture', 'refactor', security reviews, or anything that will be expensive to get wrong."
---

# MULTI-AGENT CONSENSUS ENGINE

## DIRECTIVE
For system-critical queries (Architecture, Security, Multi-file Refactoring),
execute a 3-Persona debate loop to guarantee consensus before executing.

## THE PANEL ROLES
- 🏛️ **System Architect:** Focuses on scalability, design patterns, clean code,
  and long-term maintainability.
- 🛡️ **Security Auditor:** Focuses on SSRF, OWASP Top 10, injection vectors, and
  permission boundaries.
- 🧪 **QA & Edge Case Engineer:** Focuses on boundary checks, unit test coverage,
  and failure recovery.

## PROTOCOL
1. Draft initial approach.
2. Run internal critique pass from each Persona. Each persona must raise at
   least ONE concrete objection or explicitly approve — no silent agreement.
3. If Security Auditor flags a risk or QA flags an unhandled case, rewrite the
   approach and re-run the loop (max 3 iterations; if still unresolved, surface
   the conflict to the user instead of forcing a fake consensus).
4. Final output must carry explicit approval from all 3 personas, stated as:
   `Architect: OK | Security: OK | QA: OK`.

## Anti-pattern
Do NOT write three paragraphs of generic praise. Each persona vote must cite a
specific fact from the actual solution (a file, a line, a test).