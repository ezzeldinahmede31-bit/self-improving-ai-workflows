---
name: digital-forensics
description: "Investigates digital evidence: volatility order, imaging, timelines, and memory. Use when the user says 'forensics', 'disk image', 'chain of custody', 'timeline analysis', 'memory forensics', 'log analysis', 'file carving', 'incident investigation', or when reconstructing what happened from digital traces."
---

# Digital Forensics

Distilled from the forensics canon (Carrier *File System Forensic Analysis*,
legally-grounded practice): evidence must be collected in volatility order,
hashed at capture, and analyzed without altering the original.

## Purpose

Reconstruct events defensibly: every claim traceable to an artifact, every
artifact traceable to a hashed image, every step documented.

## The method (order matters — volatility first)

1. **Order of volatility.** Registers/cache -> memory -> network state ->
   running processes -> disk -> logs -> archives. Capture from most to least
   ephemeral; photograph the screen and note the live state before touching
   anything.
2. **Image and hash.** Bit-for-bit copies (write-blocked); SHA-256 at capture
   and before every analysis session. Chain of custody: who, when, what, why —
   gaps in the chain are gaps in admissibility.
3. **Timeline first.** Super-timelines (filesystem + logs + registry +
   browser + mail unified, sorted): the skeleton every hypothesis hangs on.
   Anchor with known-good events (boot, login, scheduled tasks), then read
   anomalies against the anchor.
4. **Filesystem analysis.** Allocation vs unallocated vs slack; deleted-file
   recovery (carving by headers/footers); metadata (MAC times — know which
   operations update which stamp on your FS); journal/log replay for recent
   history.
5. **Memory forensics.** Process lists, network connections, injected code,
   credentials in memory; rootkit indicators (hidden processes, hooked
   tables). Memory often holds what disk never wrote.
6. **Logs and correlation.** One source lies by omission; three sources
   triangulate: endpoint + network + identity logs joined on time (NTP-synced
   clocks or the timeline is fiction).

## Anti-patterns that kill cases

- Analyzing the original instead of the image. Booting the suspect drive.
- "Enhancing" timestamps or editing logs to look cleaner.
- Conclusions without alternative hypotheses tested (confirmation bias is
  the examiner's enemy).

## Verification

Case file contains: hashes, custody log, unified timeline, artifact-to-claim
mapping, and a tested alternative hypothesis alongside the primary. Missing linkage =
unfinished analysis.

## Pairs with

- `security-monitoring` (detection sources), `linux-system-programming`
  (OS internals), `incident-response-ai-failures-hallucinations`
  (response playbooks), `audit-trail-compliance` (custody records).
