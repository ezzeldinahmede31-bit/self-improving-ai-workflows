---
name: cybersecurity-fundamentals
description: "Covers security ground truth: CIA triad, threats, auth, and vuln classes. Use when the user says 'CIA triad', 'threat model', 'attack surface', 'authentication', 'access control', 'OWASP', 'vulnerability classes', 'defense in depth', 'incident response', or when any system needs its security baseline stated."
---

# Cybersecurity Fundamentals

Distilled from the RIT Cybersecurity Fundamentals tradition: security is
risk management over assets, threats, and vulnerabilities — everything else
is technique.

## Purpose

State any system's security posture completely: what matters, who threatens
it, where it breaks, and what happens when it does.

## The baseline (say all of it, every time)

1. **CIA + AAA.** Confidentiality (only the authorized read), Integrity
   (only the authorized write, detectably), Availability (works when needed).
   Authentication (who), Authorization (what allowed), Accounting (what
   happened). A design missing any letter has an unnamed exposure.
2. **Threat model.** Assets ranked by value; adversaries ranked by capability
   and motive (script kiddie -> organized crime -> insider -> nation-state);
   attack surface enumerated (network, physical, supply chain, human).
   STRIDE per component: Spoofing, Tampering, Repudiation, Info disclosure,
   DoS, Elevation.
3. **Vulnerability classes (know the shapes).** Injection (SQL/OS/LDAP),
   broken auth/session, XSS/CSRF/SSRF, deserialization, path traversal,
   insecure crypto use, misconfiguration, vulnerable components, logging gaps.
   Map each to its OWASP category when web-facing.
4. **Defense in depth.** No single control: prevent (least privilege, safe
   defaults, allowlists), detect (logging, monitoring, alerting), respond
   (playbooks, backups, drills), recover. Every critical asset needs all four
   layers named.
5. **Incidents happen.** Response order: detect -> contain -> eradicate ->
   recover -> lessons-learned. Preserve evidence (order of volatility:
   memory -> disk -> logs). Practice with table-tops before the real one.

## Non-negotiables (fail the review if missing)

- Default-deny posture; secrets out of code/logs; patches tracked with SLAs.
- Backups tested by RESTORE, not by existence. MFA on every privileged path.
- Third-party components inventoried (SBOM mindset) with update owner named.

## Verification

Security review deliverable: asset ranking, STRIDE table, control matrix
(prevent/detect/respond/recover per asset), and the incident playbook link.
Any blank cell is an accepted risk — written down, owner named, or it is not
accepted.

## Pairs with

- `security-engineering-threat-modeling` (adversarial design),
  `security-review` (code audit), `aumasson-serious-crypto` (crypto
  primitives), `incident-response-ai-failures-hallucinations` (playbooks).
