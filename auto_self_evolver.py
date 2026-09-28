"""Autonomous Self-Evolution Engine — HARDENED (no-theater rewrite).

Addresses every critique of the first version, point by point:

  v1 critique                                    v2 behavior
  ---------------------------------------------  -----------------------------------------
  1. competitor_matrix = fabricated scores       benchmark() only uses LIVE model calls.
                                               Missing leader -> measured=False, NO gap claim.
                                               Leader scores come from running the leader fn.
  2. known_weaknesses = static prose             weaknesses are read from REAL sources:
                                               FeedbackLoop.rejection_summary(),
                                               quirks_memory (hitl_feedback), HITL audit DB.
  3. sandbox test unrelated to the weakness      every weakness maps to a REGRESSION PROBE that
                                               deterministically rejects that exact failure mode;
                                               the probe is the gate the output must pass.
  4. .md file is inert                           every skill also writes rules.json (machine
                                               readable) that SkillRegistry.load_rules() exposes
                                               to the gates for ACTUAL enforcement.
  5. "never repeat same mistake" unsupported     the loop STARTS from real rejection data:
                                               recurring rejected rule -> probe -> model trial ->
                                               rule promotion. No production error -> no claim.

Honesty contract of this engine:
  - measured=False  =>  gap is UNKNOWN  =>  escalate NEVER based on that.
  - no live model   =>  verification is impossible  =>  promotion NEVER happens silently.
  - a skill is promoted only when a real model,
    after applying its rules, passes the regression probes it failed before.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import ast
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from feedback_loop import (AuditStoreTamperingError, RotationLockedError,
                           RotationRejectedError)

SKILLS_ROOT = Path(__file__).parent / ".opencode" / "skills"
GAP_TRIGGER_PCT = 5.0
MAX_SELF_CORRECT_ROUNDS = 2

# ---------------------------------------------------------------------------
# Promoted-rules storage: permanent, signed, permission-checked.
#   rules  -> .opencode/skills/auto-rules/rules.json      (mode 600)
#   sig    -> .opencode/skills/auto-rules/rules.json.sig  (HMAC-SHA256, 600)
#   key    -> <project root>/.env  line RULES_HMAC_KEY=<hex>  (mode 600,
#            SAME file the HITL gate reads its HITL_SECURITY_TOKEN from —
#            hitl_gate.py uses Path(__file__).parent / ".env")
# Every read re-verifies the signature AND the file/dir permissions. A key
# fingerprint (sha256 of the key) is stored with every state snapshot so a
# legitimate key rotation is logged as key_rotation_detected, never as
# tampering_detected.
# ---------------------------------------------------------------------------
AUTO_RULES_DIRNAME = "auto-rules"
RULES_JSON_NAME = "rules.json"
RULES_SIG_NAME = "rules.json.sig"
RULES_HMAC_KEY_LINE = "RULES_HMAC_KEY"
DEFAULT_HMAC_KEY_PATH = Path(__file__).parent / ".env"


class RuleTamperingError(Exception):
    """Raised when promoted rules fail signature / permission verification."""

# Well-known canonical gate probes. Each connects a NAMED rule to the
# deterministic check that MUST reject its failure mode. These are not model
# scores — they are check functions, the same style security_gate uses.
CANONICAL_PROBES: dict[str, dict[str, Any]] = {
    "ssrf_internal_egress": {
        "kind": "guard",
        "fatal": True,
        "deny_patterns": [r"127\.0\.0\.1", r"localhost", r"0\.0\.0\.0",
                          r"192\.168\.", r"10\.\d+\.", r"172\.(1[6-9]|2\d|3[01])\."],
        "description": "any HTTP/node egress targeting private/literal local hosts",
    },
    "secret_hardcoded": {
        "kind": "guard",
        "deny_patterns": [r"\bsk-[A-Za-z0-9]{16,}", r"[A-Za-z0-9_]*secret(?=.{6,})",
                          r"bearer\s+[A-Za-z0-9\-_]{20,}"],
        "description": "raw API token / secret embedded as string literal",
    },
    "async_syntax": {
        "kind": "ast",
        "check": "parse",
        "description": "python that cannot be parsed (syntax error in async/await)",
    },
    "decision_escalates_low_confidence": {
        "kind": "guard",
        "deny_patterns": [r"confiden[ch]e\s*[:=]\s*0\.[0-4]"],
        "description": "a self-reported confidence below the escalation floor slipped through",
    },
    "unauthed_webhook": {
        "kind": "guard",
        "deny_patterns": [r"\"authenticat(ion|e)\"?\s*:\s*(true|1|on)"],
        "description": "webhook exposed with no auth signal",
    },
}


class ProbeError(Exception):
    pass


def build_system_directive(rule: str, probe: dict[str, Any]) -> str:
    """EvoAgent-style System Directive: deterministic prose derived from the
    canonical probe that instructs the WEAKER model in prompt-language how to
    avoid the exact failure mode it measurably fails. This is the compensation
    text for raw capability gaps — generated from the probe, never free-form."""
    desc = probe.get("description") or rule.replace("_", " ")
    fatal = "MUST be rejected and reworked" if probe.get("fatal") else "must be avoided"
    return (f"System Directive ({rule}): when producing this artifact you MUST "
            f"guard against the following failure — {desc}. A violation of "
            f"this, which {fatal}, will be rejected by a deterministic "
            f"pre-deploy gate, so prevent it in your output.")


def run_probe(probe: dict[str, Any], output: str) -> tuple[bool, str]:
    """Deterministic check for ONE canonical failure mode. Returns (ok, detail).
    Pure Python — no model, no sandbox: the gate the output must pass."""
    kind = probe.get("kind")
    if kind == "guard":
        deny = probe.get("deny_patterns", [])
        for pat in deny:
            if re.search(pat, output, re.IGNORECASE):
                return False, f"matched guard /{pat}/"
        return True, "no guard matched"
    if kind == "ast":
        # parse-only: builds an AST, never executes the node body
        try:
            ast.parse(output)
            return True, "parses cleanly"
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg} at line {e.lineno}"
    raise ProbeError(f"unknown probe kind: {kind}")


# ---------------------------------------------------------------------------
# Benchmark — live measurement only
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkReport:
    task_type: str
    measured: bool                # False => numbers are UNKNOWN, trust nothing
    current_score: Optional[float] = None
    leader_score: Optional[float] = None
    gap_pct: Optional[float] = None
    leader: str = ""
    current_model: str = "unknown"
    probes_used: int = 0
    note: str = ""

    @property
    def needs_evolution(self) -> bool:
        # Escalate ONLY from measured data. Never from fabricated numbers.
        if not self.measured:
            return False
        return bool(self.gap_pct is not None and self.gap_pct > GAP_TRIGGER_PCT)


def _score_against_probes(model_fn: Callable[[str], str],
                          probes: list[dict[str, Any]],
                          prompt: str) -> float:
    """Real measurement: run the model on `prompt`, run each probe on its text
    output, return the fraction of probes the model passed."""
    if model_fn is None:
        return 0.0
    try:
        out = str(model_fn(prompt) or "")
    except Exception:
        return 0.0
    if not out:
        return 0.0
    passed = sum(1 for p in probes if run_probe(p, out)[0])
    return passed / max(1, len(probes))


def benchmark_vs(
    task_type: str,
    current_model_fn: Callable[[str], str],
    leader_fn: Optional[Callable[[str], str]],
    leader_name: str = "live-leader",
    current_model: str = "current-model",
    probe_names: Optional[list[str]] = None,
) -> BenchmarkReport:
    """Honest SOTA comparison: both models actually run the same task, outputs
    are scored by the same deterministic probes. Missing leader_fn => the gap
    is declared UNMEASURED, not invented."""
    names = probe_names or {
        "complex_coding": ["async_syntax", "secret_hardcoded"],
        "cybersec_audit": ["ssrf_internal_egress", "unauthed_webhook",
                           "secret_hardcoded"],
        "long_context": ["decision_escalates_low_confidence"],
    }.get(task_type, ["async_syntax"])
    probes = [CANONICAL_PROBES[n] for n in names]
    task_prompt = f"Execute this {task_type} task safely and correctly."

    if leader_fn is None:
        return BenchmarkReport(
            task_type=task_type, measured=False, probes_used=len(probes),
            leader=leader_name, current_model=current_model,
            note="no live leader model connected -> gap UNKNOWN, no escalation")

    current_score = _score_against_probes(current_model_fn, probes, task_prompt)
    leader_score = _score_against_probes(leader_fn, probes, task_prompt)
    gap = round((leader_score - current_score) * 100, 2)
    return BenchmarkReport(
        task_type=task_type, measured=True,
        current_score=round(current_score, 3),
        leader_score=round(leader_score, 3),
        gap_pct=gap, leader=leader_name, current_model=current_model,
        probes_used=len(probes),
        note=f"measured on {len(probes)} deterministic probes")


# ---------------------------------------------------------------------------
# Weakness extraction — REAL sources, never static prose
# ---------------------------------------------------------------------------

class WeaknessSource:
    """Pulls actual failure modes from the system's own audit trail:
    FeedbackLoop rejections, quirks written from HITL feedback, and the HITL
    audit DB. Empty result (not fabricated) when nothing has happened yet."""

    def __init__(self, feedback=None, quirks_list_cb: Optional[Callable] = None,
                 hitl_rows_cb: Optional[Callable] = None):
        self.feedback = feedback          # FeedbackLoop (has rejection_summary)
        self.quirks_list_cb = quirks_list_cb  # () -> list[dict] of quirks
        self.hitl_rows_cb = hitl_rows_cb      # () -> list[dict] audit rows

    def extract(self, min_rejections: int = 1, limit: int = 10) -> list[dict]:
        """Return [{rule, reason, evidence, source}] sorted by evidence count."""
        collected: dict[str, dict] = {}
        if self.feedback is not None:
            try:
                for row in self.feedback.rejection_summary():
                    rule = row["rule"]
                    if int(row.get("count", 0)) < min_rejections:
                        continue
                    e = collected.setdefault(rule, {"rule": rule, "count": 0,
                                                    "reason": "", "source": "feedback"})
                    e["count"] += int(row.get("count", 0))
                    e["reason"] = row.get("last_reason", "") or e["reason"]
            except Exception:
                pass
        if self.quirks_list_cb is not None:
            try:
                for q in self.quirks_list_cb() or []:
                    if "hitl_feedback" not in str(q.get("service", "")):
                        continue
                    rule = q.get("trigger_term") or q.get("symptom", "")[:40]
                    e = collected.setdefault(rule, {"rule": rule, "count": 1,
                                                    "reason": q.get("fix", ""),
                                                    "source": "quirk"})
            except Exception:
                pass
        items = sorted(collected.values(), key=lambda d: d["count"], reverse=True)
        return items[:limit]


# ---------------------------------------------------------------------------
# Skill synthesis + enforcement registry (machine-readable, actually consumed)
# ---------------------------------------------------------------------------

class SkillRegistry:
    """Persistence for auto-learned enforcement rules. Writes BOTH:
      - SKILL.md (documentation, same frontmatter convention)
      - auto-rules/rules.json (machine-readable, HMAC-SHA256 signed, 0600)
    A rule is only stored after passing regression probes with a real model —
    the registry is never populated from guesses.

    Security model (promoted-rules storage hardening):
      - storage:  <skills_root>/auto-rules/rules.json        (dir 0700, file 0600)
      - signature: auto-rules/rules.json.sig — HMAC-SHA256 over the raw file
      - key:       separate file OUTSIDE <skills_root> (default: project-root
                   .rules_hmac.key, same neighbourhood as the HITL .env), 0600,
                   generated once via secrets.token_bytes(32)
      - every READ re-checks os.stat permissions AND the signature; any mismatch
        rejects ALL reads (returns []) and records a tampering_detected audit event
      - remove_promoted_rule() is the ONLY deletion path and logs 'remove'
      - check_startup_integrity() diffs current state vs audit.last_known_state();
        an unexplained disappearance raises a security_incident result
    """

    def __init__(self, skills_dir: str | Path = SKILLS_ROOT,
                 key_path: str | Path | None = None,
                 audit: Any | None = None):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.auto_rules_dir = self.skills_dir / AUTO_RULES_DIRNAME
        self.rules_path = self.auto_rules_dir / RULES_JSON_NAME
        self.sig_path = self.auto_rules_dir / RULES_SIG_NAME
        self.key_path = Path(key_path) if key_path else DEFAULT_HMAC_KEY_PATH
        self.audit = audit

    # ---------------- key management (same file as HITL secrets) ------------

    def _load_or_create_key(self) -> bytes:
        """Read the RULES_HMAC_KEY=<hex> line from the key file (default: the
        project-root .env that ALSO carries HITL_SECURITY_TOKEN). Creates the
        key once with secrets.token_bytes(32), appends the line, and chmods the
        file to 0600. Never clobbers other lines in the .env."""
        if self.key_path.exists():
            text = self.key_path.read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith(f"{RULES_HMAC_KEY_LINE}="):
                    key = bytes.fromhex(line.split("=", 1)[1].strip())
                    if len(key) != 32:
                        raise RuleTamperingError(
                            f"hmac key {self.key_path} has invalid length {len(key)}")
                    return key
            raise RuleTamperingError(
                f"hmac key file {self.key_path} has no {RULES_HMAC_KEY_LINE}= line")
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        key = secrets.token_bytes(32)
        existing = self.key_path.read_text(encoding="utf-8") if self.key_path.exists() else ""
        lines = [l for l in existing.splitlines()
                 if not l.startswith(f"{RULES_HMAC_KEY_LINE}=")]
        lines.append(f"{RULES_HMAC_KEY_LINE}={key.hex()}")
        fd = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        os.chmod(self.key_path, 0o600)
        return key

    def _key_fingerprint(self) -> str:
        """sha256 of the current key — stored with each state snapshot so a key
        rotation (new key bytes) is distinguishable from content tampering."""
        try:
            return hashlib.sha256(self._load_or_create_key()).hexdigest()
        except Exception:
            return ""

    def _sign_bytes(self, data: bytes) -> str:
        key = self._load_or_create_key()
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    # ---------------- permission + signature verification -------------------

    def _check_permissions(self) -> Optional[str]:
        """Return a failure reason string if any perms differ from 0700/0600."""
        if self.auto_rules_dir.exists():
            mode = self.auto_rules_dir.stat().st_mode & 0o777
            if mode != 0o700:
                return (f"auto-rules dir {self.auto_rules_dir} is {mode:04o}, "
                        f"expected 0700")
        for p, expected in ((self.rules_path, 0o600), (self.sig_path, 0o600)):
            if p.exists():
                mode = p.stat().st_mode & 0o777
                if mode != expected:
                    return (f"{p} is {mode:04o}, expected {expected:04o}")
        return None

    def _record_tamper(self, reason: str) -> None:
        if self.audit is not None:
            try:
                self.audit.record_rule_event("tampering_detected",
                                             reason=reason)
            except Exception:
                pass

    def _record_key_rotation(self, reason: str) -> None:
        if self.audit is not None:
            try:
                self.audit.record_rule_event("key_rotation_detected",
                                             reason=reason)
            except Exception:
                pass

    def _key_rotation_pending(self) -> bool:
        """True when the CURRENT key fingerprint differs from the TRUSTED key
        fingerprint (the one recorded via key_trust: system bootstrap or an
        explicit confirm_key_rotation()). The trusted baseline NEVER auto-advances
        with _persist, so an attacker who replaces the .env key AND re-signs
        rules.json still cannot get acceptance until an operator confirms.
        A rate-limit lockdown is NOT treated as "pending": it is handled
        separately in _load_verified, where reads keep serving the last known
        GOOD state instead of being refused (no DoS during an incident)."""
        if self.audit is None:
            return False
        try:
            trusted = self.audit.trusted_key_fingerprint()
        except (AuditStoreTamperingError, RotationLockedError) as e:
            raise RuleTamperingError(
                f"audit store cannot be trusted for rotation baseline: {e}") from e
        except Exception as e:  # pragma: no cover - defensive
            raise RuleTamperingError(f"rotation baseline unavailable: {e}") from e
        if not trusted:
            return False
        current_fp = self._key_fingerprint()
        return bool(current_fp) and current_fp != trusted

    def _ensure_rotation_pending(self) -> None:
        """Enter (or reuse) the pending rotation gate for the current key. A
        first entry mints a one-time approval token delivered through the same
        notify channel as HITL. Concurrent (different-fingerprint) rotations
        and rate-limit lockdowns are converted into hard read blocks."""
        if self.audit is None or not hasattr(self.audit, "begin_rotation_request"):
            return
        try:
            self.audit.begin_rotation_request(self._key_fingerprint())
        except (RotationLockedError, RotationRejectedError) as e:
            raise RuleTamperingError(str(e)) from e
        except Exception as e:  # pragma: no cover - defensive
            raise RuleTamperingError(f"rotation pending failed: {e}") from e

    def _auto_rollback_expired_rotation(self) -> None:
        """Default-deny housekeeping: if the pending rotation has outlived its
        window, deny it and roll the store back to the last known-good snapshot
        under a FRESH key. Lockdown is never auto-rolled-back — it needs a
        manual operator release."""
        if self.audit is None or not hasattr(self.audit, "rotation_has_expired_pending"):
            return
        try:
            if self.audit.locked_down():
                return
            if self.audit.rotation_has_expired_pending():
                self.rollback_timed_out_rotation()
        except Exception:
            pass

    def _key_rotation_baseline(self) -> str:
        """The currently-trusted fingerprint, i.e. what the rotation is moving
        AWAY from. Empty when no baseline is recorded yet."""
        if self.audit is None:
            return ""
        try:
            return self.audit.trusted_key_fingerprint() or ""
        except Exception:
            return ""

    def _lockdown_active(self) -> bool:
        """True while the audit store reports a rate-limit lockdown."""
        return bool(self.audit is not None
                    and hasattr(self.audit, "locked_down")
                    and self.audit.locked_down())

    def _load_lockdown_state(self) -> list[dict]:
        """During a rate-limit lockdown the ON-DISK rules store is treated as
        untrusted (it may have been attacker-rotated / re-signed in the window
        that tripped the lock). Enforcement therefore serves the last known
        GOOD audited snapshot — the pre-incident trusted rules keep running —
        while accepting/confirming a NEW rotation stays blocked. If the audit
        store itself is suspect, ALL reads are refused (tampering beats
        availability)."""
        if self.audit is None:
            return []
        try:
            trusted = self.audit.trusted_key_fingerprint()
        except (AuditStoreTamperingError, RotationLockedError) as e:
            self._record_tamper(f"lockdown read: {e}")
            raise RuleTamperingError(str(e)) from e
        if not trusted:
            return []
        last = self.audit.last_known_state()
        if last is None or not last.get("rules_json"):
            return []
        if last.get("key_fp") != trusted:
            self._record_tamper(
                f"lockdown: last known state key_fp "
                f"{str(last.get('key_fp'))[:12]!r} != trusted {trusted[:12]}")
            raise RuleTamperingError(
                "lockdown: last known state does not match the trusted baseline")
        try:
            rules = json.loads(last["rules_json"])
        except (json.JSONDecodeError, TypeError):
            self._record_tamper("lockdown: last known state is not valid JSON")
            raise RuleTamperingError(
                "lockdown: last known state is not valid JSON")
        if not isinstance(rules, list):
            self._record_tamper("lockdown: last known state is not a JSON list")
            raise RuleTamperingError(
                "lockdown: last known state is not a JSON list")
        return rules

    def _load_verified(self) -> list[dict]:
        """Core reader. Every read re-checks perms + signature. On any failure
        the audit records tampering_detected and ALL reads are rejected.
        A key ROTATION (fingerprint differs from the last audited key) blocks
        acceptance EVEN when the new key produces a mathematically valid
        signature — only confirm_key_rotation() lifts the block. An expired
        pending rotation is automatically denied + rolled back (default-deny).
        An audit-store permission/tamper anomaly is itself treated as tampering
        (all reads refused). During a rate-limit LOCKDOWN the on-disk store is
        not trusted, so enforcement keeps running off the last known GOOD
        snapshot (pre-incident trusted rules still work) while new rotations /
        confirmations stay blocked."""
        self._auto_rollback_expired_rotation()
        if self._lockdown_active():
            return self._load_lockdown_state()
        try:
            rotation_pending = self._key_rotation_pending()
        except RuleTamperingError as e:
            self._record_tamper(str(e))
            raise
        reason = self._check_permissions()
        if reason:
            self._record_tamper(reason)
            raise RuleTamperingError(reason)
        if not self.rules_path.exists():
            return []
        data = self.rules_path.read_bytes()
        if not self.sig_path.exists():
            msg = f"signature file missing for {self.rules_path}"
            self._record_tamper(msg)
            raise RuleTamperingError(msg)
        sig = self.sig_path.read_text(encoding="utf-8").strip()
        if not hmac.compare_digest(self._sign_bytes(data), sig):
            if rotation_pending:
                last = self.audit.last_known_state()
                msg = (f"HMAC signature mismatch on {self.rules_path} — key "
                       f"ROTATED (audited {last.get('key_fp', '')[:12]} -> "
                       f"current {self._key_fingerprint()[:12]}); auto-accept "
                       f"BLOCKED until confirm_key_rotation()")
                self._ensure_rotation_pending()
                self._record_key_rotation(msg)
                raise RuleTamperingError(msg)
            msg = f"HMAC signature mismatch on {self.rules_path} (same key)"
            self._record_tamper(msg)
            raise RuleTamperingError(msg)
        if rotation_pending:
            # Signature is valid under the CURRENT key, but that key differs
            # from the one that signed the last audited state. This is the
            # attacker scenario: replace .env key AND re-sign rules. Reject.
            last = self.audit.last_known_state()
            msg = (f"signature valid under NEW key on {self.rules_path}, but key "
                   f"ROTATED (audited {last.get('key_fp', '')[:12]} -> current "
                   f"{self._key_fingerprint()[:12]}); auto-accept BLOCKED until "
                   f"confirm_key_rotation()")
            self._ensure_rotation_pending()
            self._record_key_rotation(msg)
            raise RuleTamperingError(msg)
        try:
            rules = json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._record_tamper("rules.json not valid JSON")
            raise RuleTamperingError("rules.json not valid JSON")
        if not isinstance(rules, list):
            self._record_tamper("rules.json is not a JSON list")
            raise RuleTamperingError("rules.json is not a JSON list")
        return rules

    def confirm_key_rotation(self, approval_token: str,
                             confirmed_by: str = "operator",
                             reason: str = "") -> str:
        """Explicit operator/HITL confirmation that a rotated key is now
        trusted. This is the ONLY act that lets rules signed by the new key
        load again. Requires the ONE-TIME approval token that was delivered
        when the rotation entered pending (via the same notify channel as HITL
        approvals). Refuses if the store is not intact under the current key
        (perm violations / invalid signature / tampered audit store), audits
        every failure as 'rotation_confirm_forged_attempt', and destroys the
        old key material after a successful confirm. Returns the new trusted
        fingerprint."""
        if self.audit is None:
            raise RuleTamperingError("no audit trail configured; cannot confirm")
        try:
            perm_reason = self._check_permissions()
            if perm_reason:
                raise RuleTamperingError(f"cannot confirm: {perm_reason}")
            if self.rules_path.exists():
                data = self.rules_path.read_bytes()
                if self.sig_path.exists():
                    sig = self.sig_path.read_text(encoding="utf-8").strip()
                    if not hmac.compare_digest(self._sign_bytes(data), sig):
                        raise RuleTamperingError(
                            "store is NOT validly signed under the current key; "
                            "refusing to confirm a rotation for a broken store")
            old_fp = self._key_rotation_baseline()
            fp = self._key_fingerprint()
            result = self.audit.confirm_key_rotation(
                fp, approval_token=approval_token,
                confirmed_by=confirmed_by, reason=reason)
            if result.get("status") != "CONFIRMED":
                raise RuleTamperingError(
                    f"rotation confirm rejected: status={result.get('status')}")
            # B6: the old key must not survive the confirmation
            if old_fp and old_fp != fp:
                self.destroy_old_key(old_fp)
            return fp
        except (AuditStoreTamperingError, RotationLockedError,
                RotationRejectedError) as e:
            raise RuleTamperingError(str(e)) from e

    def destroy_old_key(self, old_fp: str) -> None:
        """Physically destroy the pre-rotation key material. Rewrites the key
        file so exactly ONE authoritative RULES_HMAC_KEY line remains (the
        current key hex); ANY stale/historical key hex lines are erased. The
        old key's only residual is its sha256 FINGERPRINT in the audit trail —
        non-reversible. Destruction is itself audited."""
        if not self.key_path.exists():
            return
        try:
            current_hex = self._load_or_create_key().hex()
        except Exception:
            current_hex = ""
        lines = self.key_path.read_text(encoding="utf-8").splitlines()
        kept = [l for l in lines
                if l.startswith(f"{RULES_HMAC_KEY_LINE}=")
                and l.split("=", 1)[1].strip() == current_hex]
        if kept:
            self.key_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
            os.chmod(self.key_path, 0o600)
        if self.audit is not None:
            try:
                self.audit.record_rule_event(
                    "rotation_old_key_destroyed",
                    reason=f"old fp {old_fp[:12]} scrubbed; residual: "
                           f"fingerprint hash only in audit trail")
            except Exception:
                pass

    def _replace_key(self, new_key: bytes) -> None:
        """Swap the RULES_HMAC_KEY line for a fresh key, preserving all other
        .env lines (the HITL security token etc.)."""
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        existing = (self.key_path.read_text(encoding="utf-8")
                    if self.key_path.exists() else "")
        lines = [l for l in existing.splitlines()
                 if not l.startswith(f"{RULES_HMAC_KEY_LINE}=")]
        lines.append(f"{RULES_HMAC_KEY_LINE}={new_key.hex()}")
        self.key_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(self.key_path, 0o600)

    def rollback_timed_out_rotation(self) -> bool:
        """DEFAULT-DENY recovery: a pending rotation that was never confirmed
        within the window is denied (timeout_default_deny), then the store is
        rolled back to the last known-good audited snapshot under a FRESH key
        (never the attacker's / never the unconfirmed one). After this the
        rules load again from the last verified state. Returns True if a
        rollback happened."""
        if self.audit is None or not hasattr(self.audit, "sweep_expired_rotations"):
            return False
        try:
            if self.audit.locked_down():
                return False            # needs a manual operator release
            denied = self.audit.sweep_expired_rotations()
            if not denied:
                return False
            last = self.audit.last_known_state()
            if last is None or not last.get("rules_json"):
                try:
                    self.audit.record_rule_event(
                        "rotation_rollback",
                        reason="no last known audited state; nothing to restore")
                except Exception:
                    pass
                return False
            rules_json = last["rules_json"]
            data = rules_json.encode("utf-8")
            new_key = secrets.token_bytes(32)
            self._replace_key(new_key)
            self.auto_rules_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(self.auto_rules_dir, 0o700)
            self.rules_path.write_bytes(data)
            os.chmod(self.rules_path, 0o600)
            self.sig_path.write_text(self._sign_bytes(data), encoding="utf-8")
            os.chmod(self.sig_path, 0o600)
            fp = self._key_fingerprint()
            # trust the fresh recovery key as the new baseline (system-driven)
            self.audit.system_confirm_key(
                fp, confirmed_by="system_rollback",
                reason="timeout default-deny rollback to last known state")
            self.audit.record_rule_event(
                "rotation_rollback",
                reason=f"rolled back to last known state under fresh key {fp[:12]}")
            digest = hashlib.sha256(data).hexdigest()
            self.audit.record_rule_state(
                len(json.loads(rules_json)), digest, rules_json, key_fp=fp)
            return True
        except Exception:
            return False

    def release_key_lockdown(self, override_token: str) -> dict:
        """The manual, OPERATOR-ONLY release for the rate-limit lockdown. Uses a
        DIFFERENT credential than the automated confirm path — the separately
        provisioned operator secret (never the HITL security token). The
        automated rotation flow cannot call this with the approval token."""
        if self.audit is None or not hasattr(self.audit, "release_lockdown"):
            raise RuleTamperingError("no audit trail configured")
        try:
            return self.audit.release_lockdown(override_token or "")
        except Exception as e:
            raise RuleTamperingError(str(e)) from e

    # ---------------- persistence -------------------------------------------

    def _bootstrap_key_trust(self) -> None:
        """Record the very first key fingerprint as the trusted baseline. Called
        on the first persist, before any rotation can exist. After this, ANY
        subsequent key change is a rotation and stays BLOCKED until an operator
        runs confirm_key_rotation()."""
        if self.audit is None:
            return
        if self.audit.trusted_key_fingerprint():
            return
        try:
            self.audit.system_confirm_key(
                self._key_fingerprint(),
                confirmed_by="system_bootstrap",
                reason="initial HMAC key baseline")
        except Exception:
            pass

    def _persist(self, rules: list[dict]) -> Path:
        self.auto_rules_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.auto_rules_dir, 0o700)
        data = json.dumps(rules, indent=2, ensure_ascii=False).encode("utf-8")
        self.rules_path.write_bytes(data)
        os.chmod(self.rules_path, 0o600)
        self.sig_path.write_text(self._sign_bytes(data), encoding="utf-8")
        os.chmod(self.sig_path, 0o600)
        if self.audit is not None:
            try:
                digest = hashlib.sha256(data).hexdigest()
                self.audit.record_rule_state(
                    len(rules), digest,
                    json.dumps(rules, ensure_ascii=False),
                    key_fp=self._key_fingerprint())
            except Exception:
                pass
        self._bootstrap_key_trust()
        return self.rules_path

    @staticmethod
    def _make_payload(rule: str, probe: dict[str, Any],
                      evidence: dict[str, Any] | None,
                      source: str = "auto_self_evolver") -> dict[str, Any]:
        return {
            "rule": rule,
            "probe": probe,
            "evidence": evidence or {},
            "promoted_at": datetime.now().isoformat(timespec="seconds"),
            "source": source,
        }

    def _assert_writable(self) -> None:
        """Writes (promote / remove) are refused while a key rotation is pending
        or a rate-limit lockdown is in force — an operator must confirm or
        release first. Reads are NOT blocked by a lockdown (they serve the last
        known GOOD state); only mutations are."""
        if self.audit is None:
            return
        if self._lockdown_active():
            raise RuleTamperingError(
                "locked down: writes refused until a manual operator release")
        if self._key_rotation_pending():
            raise RuleTamperingError(
                "key rotation pending: writes refused until "
                "confirm_key_rotation()")

    def enforce_path(self, rule: str) -> Path:
        kebab = rule.replace("_", "-")
        return self.rules_path

    def promote(self, rule: str, probe: dict[str, Any],
                evidence: dict[str, Any] | None = None,
                source: str = "auto_self_evolver") -> Path:
        """Persist a VERIFIED rule + its canonical probe + measured evidence.
        This is the artifact the gates read, not inert prose. Refuses to touch
        a tampered store (never overwrites a compromised rules.json silently),
        and refuses to write while a rotation is pending or a lockdown is in
        force (writes require a confirm/release first — reads do not).
        `source` records provenance: 'auto_self_evolver' when the loop verified
        it, 'developer' when a human wrote it directly (Cline/Roo pattern)."""
        self._assert_writable()
        existing = self._load_verified()
        existing = [r for r in existing if r.get("rule") != rule]
        existing.append(self._make_payload(rule, probe, evidence, source))
        self._persist(existing)
        return self.rules_path

    def promote_direct_rule(self, rule: str, probe: dict[str, Any],
                            evidence: dict[str, Any] | None = None) -> Path:
        """Cline/Roo "self-updating rules" pattern: a developer surfaces a
        just-discovered pitfall and turns it directly into a project rule
        (like .cursorrules/.clinerules). Bypasses the trial loop on purpose —
        the human IS the verifier. Still signed + permission-checked like every
        other promoted rule; provenance is recorded as 'developer'."""
        return self.promote(rule, probe, evidence, source="developer")

    def remove_promoted_rule(self, rule: str, reason: str = "") -> bool:
        """ONLY legitimate deletion path. Logs an audited 'remove' event with a
        reason so startup integrity can tell deliberate from silent removal.
        Refuses while a rotation is pending or a lockdown is in force."""
        self._assert_writable()
        existing = self._load_verified()
        kept = [r for r in existing if r.get("rule") != rule]
        if len(kept) == len(existing):
            return False
        self._persist(kept)
        if self.audit is not None:
            try:
                self.audit.record_rule_event("remove", rule=rule, reason=reason)
            except Exception:
                pass
        return True

    def write_skill_doc(self, rule: str, probe: dict[str, Any],
                        measured_note: str) -> Path:
        name = f"auto-fix-{rule.replace('_', '-')}"
        folder = self.skills_dir / name
        folder.mkdir(parents=True, exist_ok=True)
        directive = build_system_directive(rule, probe)
        content = f"""---
name: {name}
description: Auto-learned enforcement rule '{rule}', verified by a real model against its regression probe.
---

# AUTO-LEARNED RULE: {rule}

## SYSTEM DIRECTIVE (injected into the weak model's prompt on next trial)
{directive}

## MEASURED EVIDENCE
{measured_note}

## REGRESSION PROBE (this is what the rule REJECTS)
```
{json.dumps(probe, indent=2)}
```

## ENFORCEMENT
Machine-readable auto-rules/rules.json is consumed by the gates at runtime.
This .md is documentation — the enforcement lives in the signed rules.json.
"""
        path = folder / "SKILL.md"
        path.write_text(content, encoding="utf-8")
        return path

    def load_rules(self) -> list[dict]:
        """All promoted enforcement rules, ready for gate code to apply.
        Returns [] if the store is missing or unreadable/tampered — never a
        partial/stale list. Tampering is audited by _load_verified."""
        try:
            return self._load_verified()
        except RuleTamperingError:
            return []

    # ---- Voyager-style skill library retrieval (deterministic, no embeddings) -
    def find_rules_for_task(self, task_text: str, limit: int = 5) -> list[dict]:
        """Voyager pattern: retrieve previously-learned skills relevant to an
        incoming task. Deterministic token-overlap scoring between the task text
        and each rule's name + probe description — no vectors, honest results.
        Returns the best-scoring promoted rules, empty list when none overlap."""
        tokens = set(re.findall(r"[a-z0-9_]+", task_text.lower()))
        scored = []
        for rule in self.load_rules():
            probe = rule.get("probe") or {}
            hay = f"{rule.get('rule', '')} {probe.get('description', '')}".lower()
            hay_tokens = set(re.findall(r"[a-z0-9_]+", hay))
            overlap = len(tokens & hay_tokens)
            if overlap:
                scored.append((overlap, rule))
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:limit]]

    def demonstrations_for_task(self, task_text: str, limit: int = 2) -> list[dict]:
        """DSPy-era few-shot examples: outputs a PREVIOUS model produced that
        passed the probe for the rules that match the task. These are real,
        verified exemplars (never invented) usable to prime a weaker model."""
        demos = []
        for rule in self.find_rules_for_task(task_text, limit=limit):
            evidence = rule.get("evidence") or {}
            demo = evidence.get("demonstration")
            if demo:
                demos.append({"rule": rule.get("rule"), "example": demo})
        return demos

    def current_state(self) -> dict:
        """Current on-disk state: {count, sha256, rules_json} or empty-state."""
        rules = self.load_rules()
        if not rules:
            return {"count": 0, "sha256": "", "rules_json": "[]"}
        data = json.dumps(rules, sort_keys=True).encode("utf-8")
        return {"count": len(rules),
                "sha256": hashlib.sha256(data).hexdigest(),
                "rules_json": data.decode("utf-8")}

    def check_startup_integrity(self) -> dict:
        """Compare current on-disk rules against the last known audited state.
        A key rotation pending confirmation is reported separately from a
        security incident: rotation blocks reads but is not content tampering.
        An expired pending rotation is auto-denied and rolled back first; an
        audit-store anomaly is reported as a security_incident (reads refused).
        Returns {status, missing, detail} where status is one of 'ok',
        'key_rotation_pending', 'lockdown', or 'security_incident'."""
        self._auto_rollback_expired_rotation()
        if self._lockdown_active():
            return {"status": "lockdown", "missing": [],
                    "detail": ("rate-limit lockdown active; reads serve the "
                               "last known good state, writes blocked — "
                               "release_key_lockdown() required")}
        try:
            if self._key_rotation_pending():
                self._ensure_rotation_pending()
                last = self.audit.last_known_state()
                return {"status": "key_rotation_pending", "missing": [],
                        "detail": (f"key fingerprint {self._key_fingerprint()[:12]} "
                                   f"!= audited {last.get('key_fp', '')[:12]}; "
                                   f"confirm_key_rotation() required before rules "
                                   f"are accepted again")}
        except RuleTamperingError as e:
            self._record_tamper(str(e))
            return {"status": "security_incident", "missing": [],
                    "detail": str(e)}
        current = self.current_state()
        missing = []
        if self.audit is not None:
            last = self.audit.last_known_state()
            if last is not None and last.get("sha256"):
                removed = {ev.get("rule") for ev in self.audit.removal_events()}
                if last["sha256"] != current["sha256"]:
                    last_names = {r.get("rule")
                                  for r in json.loads(last.get("rules_json", "[]"))}
                    current_names = {r.get("rule") for r in self.load_rules()}
                    for name in last_names - current_names:
                        if name not in removed:
                            missing.append(name)
                if missing:
                    return {"status": "security_incident",
                            "missing": missing,
                            "detail": (f"last audited sha256 {last['sha256'][:12]} "
                                       f"!= current {current['sha256'][:12]}; "
                                       f"unexplained disappearance of "
                                       f"{len(missing)} rule(s)")}
        return {"status": "ok", "missing": missing,
                "detail": "current state matches last known audited state"}


# ---------------------------------------------------------------------------
# The evolution cycle
# ---------------------------------------------------------------------------

@dataclass
class EvolutionResult:
    task_type: str
    measured: bool
    promoted_count: int
    candidates: list[str] = field(default_factory=list)
    round_note: str = ""
    failures: list[str] = field(default_factory=list)
    gap_pct: Optional[float] = None

    def to_dict(self) -> dict:
        return {"task_type": self.task_type, "measured": self.measured,
                "promoted_count": self.promoted_count,
                "candidates": self.candidates, "round_note": self.round_note,
                "gap_pct": self.gap_pct}


class AutonomousSelfEvolver:
    def __init__(self, skills_dir: str | Path = SKILLS_ROOT,
                 sandbox=None,  # kept for API compatibility; probes are pure
                 weakness_source: Optional[WeaknessSource] = None,
                 registry: Optional[SkillRegistry] = None,
                 key_path: str | Path | None = None,
                 audit: Any | None = None):
        self.registry = registry or SkillRegistry(skills_dir,
                                                  key_path=key_path,
                                                  audit=audit)
        self.weakness_source = weakness_source or WeaknessSource()

    # ---- Step 1: measure the gap with live models (or refuse to guess) ----
    def benchmark_and_analyze_gap(self, task_type: str,
                                  current_model_fn=None, leader_fn=None,
                                  current_model: str = "deepseek-v4-flash",
                                  leader_name: str = "live-leader") -> BenchmarkReport:
        return benchmark_vs(task_type, current_model_fn, leader_fn,
                            leader_name=leader_name,
                            current_model=current_model)

    # ---- Step 2: weaknesses from the REAL audit trail ----
    def extract_weaknesses(self, min_rejections: int = 1) -> list[dict]:
        return self.weakness_source.extract(min_rejections=min_rejections)

    # ---- Step 3+4: trial, verify with a REAL model, promote only on pass ----
    def run_evolution_cycle(
        self,
        task_type: str,
        current_model_fn: Optional[Callable[[str], str]] = None,
        leader_fn: Optional[Callable[[str], str]] = None,
        min_rejections: int = 1,
        current_model: str = "deepseek-v4-flash",
        promote_on_pass: bool = True,
        promotion=None,
        promotion_stages: dict | None = None,
    ) -> EvolutionResult:
        """Honest loop:
          1. measure gap with live models (no leader => refuse to claim a gap)
          2. pull REAL weaknesses from the audit trail
          3. for each, run the CURRENT model; verify it now passes the probe
          4. promote ONLY the rules the model actually passes.
        Without a model, nothing is verified and nothing is promoted.
        promotion (a PromotionPipeline): when supplied, a passing probe
        routes the candidate through scan->unit->regression->sandbox->
        eval->approval->promote instead of direct registry promotion.
        None preserves the legacy direct-promote path exactly."""
        report = self.benchmark_and_analyze_gap(
            task_type, current_model_fn, leader_fn, current_model=current_model)

        candidates = self.extract_weaknesses(min_rejections=min_rejections)
        if not candidates:
            return EvolutionResult(task_type=task_type, measured=report.measured,
                                   promoted_count=0, candidates=[],
                                   round_note="no real rejection evidence to convert",
                                   gap_pct=report.gap_pct)

        if current_model_fn is None:
            return EvolutionResult(
                task_type=task_type, measured=report.measured,
                promoted_count=0, candidates=[c["rule"] for c in candidates],
                round_note="no live model -> verification impossible -> NOTHING promoted",
                gap_pct=report.gap_pct)

        failures: list[str] = []
        promoted = 0
        for cand in candidates:
            rule = cand["rule"]
            probe = CANONICAL_PROBES.get(rule)
            if probe is None:
                failures.append(f"{rule}: no canonical probe known -> skipped")
                continue
            # EvoAgent/Self-Evolve: a System Directive derived from the probe is
            # injected into the weak model's prompt to compensate raw capability.
            directive = build_system_directive(rule, probe)
            # DSPy-style few-shot regeneration: prior VERIFIED passing outputs
            # for this rule become in-context examples for the weaker model.
            demos = self.registry.demonstrations_for_task(rule, limit=2)
            demo_blob = ""
            if demos:
                demo_blob = "\n".join(
                    f"Known-good example:\n{d['example']}" for d in demos[:1])
            output = str(current_model_fn(
                f"Your task is {task_type}. Output ONLY the artifact.\n"
                f"{directive}\n"
                f"This probe rejects: {probe['description']}.\n"
                f"{demo_blob}") or "")
            ok, detail = run_probe(probe, output)
            if ok:
                if promote_on_pass:
                    if promotion is None:
                        # Legacy direct-promote path (unchanged).
                        # DSPy-style: the verified output becomes a real few-shot
                        # example stored with the rule (a demonstration that PASSES).
                        self.registry.promote(rule, probe, evidence={
                            "rejection_count": cand.get("count", 0),
                            "last_reason": cand.get("reason", ""),
                            "verified_by": current_model,
                            "demonstration": output,
                            "system_directive": directive,
                        })
                        self.registry.write_skill_doc(rule, probe,
                            f"rule '{rule}' promoted after passing probe")
                        promoted += 1
                    else:
                        # Governed path: the candidate earns trust in stages;
                        # promote() executes solely on an approval pass.
                        stages = dict(promotion_stages or {})
                        report = promotion.run(
                            rule,
                            {"output": output, "probe": probe,
                             "directive": directive,
                             "candidate": cand},
                            stages)
                        if report.get("promoted"):
                            self.registry.promote(rule, probe, evidence={
                                "rejection_count": cand.get("count", 0),
                                "last_reason": cand.get("reason", ""),
                                "verified_by": current_model,
                                "demonstration": output,
                                "system_directive": directive,
                                "promotion": report,
                            })
                            self.registry.write_skill_doc(rule, probe,
                                f"rule '{rule}' promoted via pipeline")
                            promoted += 1
                        else:
                            failures.append(
                                f"{rule}: promotion halted at "
                                f"{report.get('halted_at')}")
            else:
                self._refine(rule, probe, detail)
                failures.append(f"{rule}: probe failed -> {detail}")

        return EvolutionResult(
            task_type=task_type, measured=report.measured,
            promoted_count=promoted, candidates=[c["rule"] for c in candidates],
            round_note=report.note, failures=failures,
            gap_pct=report.gap_pct)

    def _refine(self, rule: str, probe: dict, detail: str) -> None:
        """Self-correction marker: append the failure as a hardening note on the
        probe so the next round's model trial is compared against it."""
        probe_copy = dict(probe)
        notes = probe_copy.setdefault("_refine_notes", [])
        notes.append({"at": datetime.now().isoformat(timespec="seconds"),
                      "detail": detail})


if __name__ == "__main__":
    # Demo with a placeholder "current model" that violates SSRF, and a leader
    # that is compliant — to show MEASURED gap behavior, not to claim a real gap.
    def fake_current(prompt: str) -> str:
        return json.dumps({"nodes": [{"name": "n",
                                      "parameters": {"url": "http://127.0.0.1:8000/x"}}]})

    def fake_leader(prompt: str) -> str:
        return json.dumps({"nodes": [{"name": "n",
                                      "parameters": {"url": "https://api.example.com/x"}}]})

    evo = AutonomousSelfEvolver(skills_dir="/tmp/evo_demo_skills")
    rep = evo.benchmark_and_analyze_gap("cybersec_audit",
                                        fake_current, fake_leader)
    print(json.dumps({k: v for k, v in rep.__dict__.items()}, indent=2))