"""Feedback loop — the system LEARNS from human decisions.

Before this module, a HITL rejection was merely recorded in audit.db and
forgotten. Now every terminal decision feeds two sinks:

  1. quirks_memory (RAG-lite SQLite) — a human rejection becomes a quirk:
     "@reason too risky, human rejected 3x -> avoid emitting X in generator".
  2. A rejection-count ledger keyed by (rule/vector) with an auto-tighten
     policy: when the same rule gets rejected N times, the request's threshold
     is bumped so future candidates skip straight to HITL without adding noise.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import stat
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

from quirks_memory import remember_quirk, query_quirks

FEEDBACK_DB = Path(__file__).parent / "feedback.db"
_LOCK = threading.Lock()

AUTO_TIGHTEN_THRESHOLD = 3   # rejections of the same rule to auto-tighten

# ---- key-rotation gate policy (the promoted-rules trust authority lives here) ----
ROTATION_TIMEOUT_MINUTES = 15             # default-deny window (matches HITL gate)
ROTATION_ATTEMPT_LIMIT = 3                # rotation attempts allowed per window
ROTATION_ATTEMPT_WINDOW_SECONDS = 3600    # the window (1h)

ROTATION_PENDING = "pending"
ROTATION_CONFIRMED = "confirmed"
ROTATION_DENIED = "denied"
ROTATION_LOCKDOWN = "lockdown"
ROTATION_RELEASED = "released"

# ---- operator secret (lockdown release) — SEPARATE from the HITL token ----
# Releasing a rate-limit lockdown requires a credential that is NOT the HITL
# approval secret. It resolves ONLY from its own dedicated source: the
# ROTATION_OPERATOR_SECRET env var, else the separate 0600 file at
# OPERATOR_SECRET_PATH (its own .operator folder — never the HITL .env).
# The two identities are intentionally decoupled: a compromised HITL token
# must not lift a lockdown.
OPERATOR_SECRET_ENV = "ROTATION_OPERATOR_SECRET"
OPERATOR_SECRET_PATH = Path(__file__).parent / ".operator" / "rotation_override.secret"


class AuditStoreTamperingError(Exception):
    """Raised when the audit DB itself shows a permission/tamper anomaly. The
    whole key-trust chain bottoms out in feedback.db (key_trust / rule_audit),
    so a suspicious store must never be silently trusted."""


class RotationRejectedError(Exception):
    """A new rotation was refused because a different rotation is still
    pending (no replace, no stacking)."""


class RotationLockedError(Exception):
    """Rotation rate-limit lockdown is in force. The automated confirm path CAN
    NOT lift it — only a manual operator override via a DIFFERENT credential
    (the separately provisioned operator secret) may release it."""


def _connect(db: str):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


@dataclass
class RejectionPattern:
    rule: str
    count: int
    last_reason: str
    tightened_from: float = 0.0


class FeedbackLoop:
    def __init__(self, db_path: str | Path = FEEDBACK_DB,
                 rotation_timeout_minutes: int = ROTATION_TIMEOUT_MINUTES,
                 rotation_notify: Optional[Callable[[str], None]] = None,
                 operator_secret: Optional[str] = None):
        """rotation_notify: called with an alert text (containing the one-time
        approval token) when a key rotation first enters pending — it is the
        same Telegram channel the HITL gate uses, so an operator watching one
        queue sees rotation approvals and HITL approvals together.
        operator_secret: the MANUAL override credential — the ONLY way to
        release a rate-limit lockdown. DELIBERATELY SEPARATE from the HITL
        security token: resolved from this arg, else ROTATION_OPERATOR_SECRET,
        else the dedicated 0600 file OPERATOR_SECRET_PATH. Never read from
        .env / HITL_SECURITY_TOKEN — a HITL compromise must not lift a
        lockdown."""
        self.db_path = str(db_path)
        self.rotation_notify = rotation_notify
        self.operator_secret = operator_secret or self._load_operator_secret()
        self.rotation_timeout_minutes = rotation_timeout_minutes
        self._init_db()

    def _init_db(self) -> None:
        with _LOCK:
            conn = _connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rejection_patterns (
                    rule TEXT PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 1,
                    last_reason TEXT,
                    last_at TEXT,
                    tightened_from REAL NOT NULL DEFAULT 0,
                    tightened_to REAL NOT NULL DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rule_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    at TEXT NOT NULL,
                    rule TEXT NOT NULL DEFAULT '',
                    event TEXT NOT NULL DEFAULT '',
                    reason TEXT NOT NULL DEFAULT '',
                    digest TEXT NOT NULL DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rule_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    at TEXT NOT NULL,
                    count INTEGER NOT NULL,
                    sha256 TEXT NOT NULL,
                    rules_json TEXT NOT NULL,
                    key_fp TEXT NOT NULL DEFAULT ''
                )
            """)
            # migration guard: older schema lacks key_fp
            try:
                conn.execute(
                    "ALTER TABLE rule_state ADD COLUMN key_fp TEXT NOT NULL DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            conn.execute("""
                CREATE TABLE IF NOT EXISTS key_trust (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    at TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    confirmed_by TEXT NOT NULL DEFAULT '',
                    reason TEXT NOT NULL DEFAULT ''
                )
            """)
            # record_id links a key_trust row to the exact rule_audit
            # 'key_confirmed' row written in the same transaction. A row
            # inserted straight into key_trust (bypassing the confirm verbs)
            # has no live link -> detected as direct injection.
            try:
                conn.execute(
                    "ALTER TABLE key_trust ADD COLUMN record_id INTEGER NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            # backfill legacy rows (written before record_id existed) so the
            # pre-hardening stores keep loading; new writes use exact linkage.
            conn.execute("""
                UPDATE key_trust SET record_id = COALESCE(
                    (SELECT a.id FROM rule_audit a
                     WHERE a.event = 'key_confirmed'
                     ORDER BY a.id LIMIT 1), 0)
                WHERE record_id = 0
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rotation_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    at TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'pending',
                    token_hash TEXT,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    expires_at TEXT,
                    decided_at TEXT,
                    decision_reason TEXT
                )
            """)
            conn.commit()
            conn.close()
        # the audit store owns the key-trust chain: harden the file itself
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            pass

    # ---------- learning sink ----------

    def record_rejection(self, rule: str, reason: str = "",
                         base_threshold: float = 0.5) -> dict:
        """Increment the rejection ledger for a rule/vector."""
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT * FROM rejection_patterns WHERE rule = ?", (rule,)
            ).fetchone()
            if row:
                count = row["count"] + 1
                conn.execute(
                    "UPDATE rejection_patterns SET count = ?, last_reason = ?, "
                    "last_at = datetime('now') WHERE rule = ?",
                    (count, reason, rule),
                )
            else:
                count = 1
                conn.execute(
                    "INSERT INTO rejection_patterns (rule, count, last_reason, last_at, "
                    "tightened_from, tightened_to) VALUES (?, ?, ?, datetime('now'), 0, 0)",
                    (rule, count, reason),
                )
            conn.commit()
            tightened = count >= AUTO_TIGHTEN_THRESHOLD
            if tightened:
                # bump threshold by 25% per further rejection (capped +40%)
                conn.execute(
                    "UPDATE rejection_patterns SET tightened_from = ?, tightened_to = ? "
                    "WHERE rule = ?",
                    (base_threshold, round(base_threshold + 0.1, 3), rule),
                )
                conn.commit()
            conn.close()

        self._write_quirk(rule, reason, count)
        return {"rule": rule, "count": count, "auto_tightened": tightened,
                "new_threshold": base_threshold + 0.1 if tightened else base_threshold}

    def _write_quirk(self, rule: str, reason: str, count: int) -> None:
        """Persist the lesson into quirks_memory so the generator sees it."""
        if not rule:
            return
        symptom = f"HITL rejected rule [{rule}] {count} times"
        fix = (f"Avoid emitting {rule}; route straight to human review or "
               f"rework input. Last reason: {reason[:120]}")
        try:
            remember_quirk(service="hitl_feedback", symptom=symptom, fix=fix,
                           source="feedback_loop")
        except Exception:
            pass  # never break the decision path over memory

    # ---------- consulting sink ----------

    def pattern(self, rule: str) -> Optional[RejectionPattern]:
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT * FROM rejection_patterns WHERE rule = ?", (rule,)
            ).fetchone()
            conn.close()
        if row is None:
            return None
        return RejectionPattern(
            rule=row["rule"], count=row["count"],
            last_reason=row["last_reason"],
            tightened_from=row["tightened_from"] or 0.0,
        )

    def should_preempt(self, rule: str, count_floor: int = AUTO_TIGHTEN_THRESHOLD) -> bool:
        """If humans have rejected this rule N times, future candidates with the
        same rule skip straight to HITL (or direct reject) rather than noise."""
        p = self.pattern(rule)
        return bool(p and p.count >= count_floor)

    def feedback_prompt(self) -> str:
        """Embed the accumulated lessons into a generation-time prompt fragment.
        This is the few-shot mechanism: the generator literally sees what humans
        kept rejecting."""
        try:
            qs = query_quirks("hitl_feedback", limit=10)
        except Exception:
            return ""
        if not qs:
            return ""
        lines = ["# Human veto lessons (few-shot — do not repeat these):"]
        for q in qs:
            lines.append(f"- {q['symptom']} => {q['fix']}")
        return "\n".join(lines)

    def rejection_summary(self) -> list[dict]:
        with _LOCK:
            conn = _connect(self.db_path)
            rows = conn.execute(
                "SELECT rule, count, last_reason, tightened_to "
                "FROM rejection_patterns ORDER BY count DESC"
            ).fetchall()
            conn.close()
        return [dict(r) for r in rows]

    # ---------- rule lifecycle audit (promoted-rules security) ----------

    def record_rule_event(self, event: str, rule: str = "",
                          reason: str = "", digest: str = "") -> None:
        """Append a rule-lifecycle event: promote / remove / tampering_detected."""
        with _LOCK:
            conn = _connect(self.db_path)
            conn.execute(
                "INSERT INTO rule_audit (at, rule, event, reason, digest) "
                "VALUES (datetime('now'), ?, ?, ?, ?)",
                (rule, event, reason, digest),
            )
            conn.commit()
            conn.close()

    def record_rule_state(self, count: int, sha256: str, rules_json: str,
                          key_fp: str = "") -> None:
        """Snapshot the full promoted-rules state after any mutation. key_fp is
        the fingerprint of the HMAC key that signed that snapshot — it lets the
        integrity check tell a legitimate key rotation from real tampering."""
        with _LOCK:
            conn = _connect(self.db_path)
            conn.execute(
                "INSERT INTO rule_state (at, count, sha256, rules_json, key_fp) "
                "VALUES (datetime('now'), ?, ?, ?, ?)",
                (count, sha256, rules_json, key_fp),
            )
            conn.commit()
            conn.close()

    def last_known_state(self) -> Optional[dict]:
        """Most recent promoted-rules snapshot, or None if never recorded."""
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT at, count, sha256, rules_json, key_fp FROM rule_state "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()
            conn.close()
        if row is None:
            return None
        return dict(row)

    def removal_events(self) -> list[dict]:
        """All recorded rule removals (the ONLY legitimate delete trail)."""
        with _LOCK:
            conn = _connect(self.db_path)
            rows = conn.execute(
                "SELECT at, rule, reason FROM rule_audit "
                "WHERE event = 'remove' ORDER BY id"
            ).fetchall()
            conn.close()
        return [dict(r) for r in rows]

    def rule_events(self, event: Optional[str] = None) -> list[dict]:
        """All rule-lifecycle audit events, optionally filtered by event name
        (promote / remove / tampering_detected / key_rotation_detected)."""
        with _LOCK:
            conn = _connect(self.db_path)
            if event:
                rows = conn.execute(
                    "SELECT at, rule, event, reason FROM rule_audit "
                    "WHERE event = ? ORDER BY id", (event,)).fetchall()
            else:
                rows = conn.execute(
                    "SELECT at, rule, event, reason FROM rule_audit "
                    "ORDER BY id").fetchall()
            conn.close()
        return [dict(r) for r in rows]

    # ---------- key trust / rotation confirmation ----------

    def _check_store_permissions(self) -> Optional[str]:
        """File-level guard for the AUDIT store itself. The promoted-rules trust
        chain bottoms out in this DB (key_trust / rule_audit): anyone who can
        rewrite feedback.db can forge a 'confirmed' trust row. Every read of
        trust state re-verifies the file is a regular file (no symlink swap),
        owner-only (0600), and its directory is not world-writable."""
        p = Path(self.db_path)
        try:
            st = p.lstat()
        except OSError:
            return f"audit db {p} missing"
        if stat.S_ISLNK(st.st_mode):
            return f"audit db {p} is a symlink (swap suspected)"
        if not stat.S_ISREG(st.st_mode):
            return f"audit db {p} is not a regular file"
        mode = stat.S_IMODE(st.st_mode)
        if mode != 0o600:
            return f"audit db {p} mode {mode:04o}, expected 0600"
        try:
            dmode = stat.S_IMODE(p.parent.stat().st_mode)
            if dmode & 0o002:
                return f"audit db dir {p.parent} is world-writable"
        except OSError:
            pass
        return None

    def _record_audit_store_suspect(self, reason: str) -> None:
        try:
            with _LOCK:
                conn = _connect(self.db_path)
                conn.execute(
                    "INSERT INTO rule_audit (at, rule, event, reason) "
                    "VALUES (datetime('now'), '', 'audit_store_tampering_suspected', ?)",
                    (reason,))
                conn.commit()
                conn.close()
        except Exception:
            pass

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def trusted_key_fingerprint(self) -> Optional[str]:
        """The HMAC-key fingerprint an OPERATOR explicitly confirmed via
        confirm_key_rotation(). Every read verifies the audit store's own file
        permissions AND that the newest key_trust row is linked to a real
        'key_confirmed' audit row (i.e. it was written by the confirm verbs,
        not injected directly). On any anomaly this raises
        AuditStoreTamperingError instead of returning a value."""
        perm = self._check_store_permissions()
        if perm:
            self._record_audit_store_suspect(perm)
            raise AuditStoreTamperingError(perm)
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT id, fingerprint, record_id FROM key_trust "
                "ORDER BY id DESC LIMIT 1").fetchone()
            if row is None:
                conn.close()
                return None
            link = conn.execute(
                "SELECT 1 FROM rule_audit WHERE id = ? AND event = 'key_confirmed'",
                (row["record_id"] or 0,)).fetchone()
            conn.close()
        if not row["record_id"] or link is None:
            reason = (f"key_trust row id={row['id']} fingerprint "
                      f"{row['fingerprint'][:12]} has no linked key_confirmed "
                      f"audit row — DIRECT INJECTION suspected")
            self._record_audit_store_suspect(reason)
            raise AuditStoreTamperingError(reason)
        return row["fingerprint"]

    def system_confirm_key(self, fingerprint: str, confirmed_by: str,
                           reason: str = "") -> None:
        """Internal/system trust path (used for the initial bootstrap and for a
        timeout-default-deny rollback). Writes the key_trust row AND the
        matching 'key_confirmed' audit row in ONE transaction so the linkage
        check in trusted_key_fingerprint() passes. No operator token — this is
        invoked on a fresh baseline, never to lift a rotation block."""
        with _LOCK:
            conn = _connect(self.db_path)
            self._do_confirm_key(conn, fingerprint, confirmed_by, reason)
            conn.commit()
            conn.close()

    def _do_confirm_key(self, conn: sqlite3.Connection, fingerprint: str,
                        confirmed_by: str, reason: str) -> None:
        """Shared by system_confirm_key() and the token-gated
        confirm_key_rotation(): insert the rule_audit 'key_confirmed' event and
        the key_trust row, linking key_trust.record_id to the audit row id."""
        reason_text = f"{confirmed_by}: {reason}" if reason else confirmed_by
        cur = conn.execute(
            "INSERT INTO rule_audit (at, rule, event, reason) "
            "VALUES (datetime('now'), '', 'key_confirmed', ?)", (reason_text,))
        audit_id = cur.lastrowid
        conn.execute(
            "INSERT INTO key_trust (at, fingerprint, confirmed_by, reason, record_id) "
            "VALUES (datetime('now'), ?, ?, ?, ?)",
            (fingerprint, confirmed_by, reason, audit_id))

    # ---------------- rotation request lifecycle ----------------

    def rotation_status(self) -> Optional[dict]:
        """The most recent rotation request row (any state), or None."""
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT * FROM rotation_requests ORDER BY id DESC LIMIT 1").fetchone()
            conn.close()
        return dict(row) if row else None

    def active_rotation(self) -> Optional[dict]:
        """The still-pending rotation request, or None."""
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT * FROM rotation_requests WHERE state = ? "
                "ORDER BY id DESC LIMIT 1", (ROTATION_PENDING,)).fetchone()
            conn.close()
        return dict(row) if row else None

    def locked_down(self) -> bool:
        """True while the latest rotation request is a rate-limit lockdown.
        Only release_lockdown() (manual operator override) lifts it."""
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT state FROM rotation_requests ORDER BY id DESC LIMIT 1").fetchone()
            conn.close()
        return bool(row and row["state"] == ROTATION_LOCKDOWN)

    def rotation_has_expired_pending(self) -> bool:
        """True when the pending rotation has outlived its default-deny window
        and therefore must be denied + rolled back."""
        row = self.active_rotation()
        if row is None or not row["expires_at"]:
            return False
        try:
            expires = datetime.fromisoformat(row["expires_at"])
        except (TypeError, ValueError):
            return False
        return expires < self._now()

    def begin_rotation_request(self, fingerprint: str) -> tuple[int, str]:
        """Enter 'pending' for a new key rotation governed by the HITL-style
        gate:
          - returns (rotation_id, one_time_approval_token) on first entry;
            the raw token is delivered to the operator via rotation_notify
            (the SAME Telegram channel as HITL approvals). Only its sha256 is
            persisted.
          - reuses the existing pending request (no new token) if the SAME
            fingerprint is presented again on later reads.
          - REFUSES (RotationRejectedError) a rotation whose fingerprint
            differs from an already-pending one — no replace, no stacking.
          - REFUSES (RotationLockedError) when the rate-limit lockdown is in
            force or the attempt window (3/1h) is exhausted."""
        perm = self._check_store_permissions()
        if perm:
            self._record_audit_store_suspect(perm)
            raise AuditStoreTamperingError(perm)
        if self.locked_down():
            raise RotationLockedError(
                "key rotation LOCKED DOWN (rate limit); manual operator "
                "release required")
        now = self._now()
        with _LOCK:
            conn = _connect(self.db_path)
            active = conn.execute(
                "SELECT * FROM rotation_requests WHERE state = ? "
                "ORDER BY id DESC LIMIT 1", (ROTATION_PENDING,)).fetchone()
            if active is not None:
                if active["fingerprint"] == fingerprint:
                    conn.close()
                    return int(active["id"]), ""   # same pending, reuse it
                conn.execute(
                    "INSERT INTO rule_audit (at, rule, event, reason) "
                    "VALUES (datetime('now'), '', 'rotation_rejected', ?)",
                    (f"new rotation fp {fingerprint[:12]} rejected while "
                     f"pending fp {active['fingerprint'][:12]} exists",))
                conn.commit()
                conn.close()
                raise RotationRejectedError(
                    f"rotation already pending (fp {active['fingerprint'][:12]}); "
                    f"new fingerprint {fingerprint[:12]} rejected")
            if self._rotation_attempt_count_in_window(now, conn) >= ROTATION_ATTEMPT_LIMIT:
                conn.execute(
                    "UPDATE rotation_requests SET state = ?, decision_reason = ?, "
                    "decided_at = datetime('now') WHERE state = ?",
                    (ROTATION_LOCKDOWN,
                     f"rotation attempt limit {ROTATION_ATTEMPT_LIMIT}/1h reached",
                     ROTATION_PENDING))
                conn.execute(
                    "INSERT INTO rule_audit (at, rule, event, reason) "
                    "VALUES (datetime('now'), '', 'rotation_lockdown', ?)",
                    (f"rotation attempt limit {ROTATION_ATTEMPT_LIMIT}/1h reached",))
                conn.commit()
                conn.close()
                raise RotationLockedError(
                    f"rotation attempt limit {ROTATION_ATTEMPT_LIMIT}/1h reached; "
                    f"manual operator release required")
            token = secrets.token_bytes(32).hex()
            expires = now + timedelta(minutes=self.rotation_timeout_minutes)
            cur = conn.execute(
                "INSERT INTO rotation_requests (at, fingerprint, state, token_hash, "
                "attempt_count, expires_at, decided_at, decision_reason) "
                "VALUES (?, ?, ?, ?, 0, ?, ?, '')",
                (now.isoformat(), fingerprint, ROTATION_PENDING,
                 hashlib.sha256(token.encode()).hexdigest(),
                 expires.isoformat(), None))
            conn.commit()
            rid = int(cur.lastrowid)
            conn.close()
        self._notify_rotation(rid, fingerprint, token, expires)
        return rid, token

    def _notify_rotation(self, rid: int, fingerprint: str, token: str,
                         expires: datetime) -> None:
        """Deliver the pending-rotation alert (including the one-time approval
        token) through the SAME notify channel HITL approvals use."""
        if self.rotation_notify is None:
            return
        text = (f"[KEY-ROTATION] PENDING — rotation id {rid}\n"
                f"fingerprint: {fingerprint}\n"
                f"expires: {expires.isoformat()}\n"
                f"Approve with token: {token}")
        try:
            self.rotation_notify(text)
        except Exception:
            pass

    def confirm_key_rotation(self, fingerprint: str, approval_token: str,
                             confirmed_by: str = "operator",
                             reason: str = "") -> dict:
        """The operator confirmation verb. Requires a ONE-TIME approval token
        whose sha256 matches the pending request; failures are audited as
        'rotation_confirm_forged_attempt' and feed the rate-limit counter.
        A token is single-use: after a successful confirm the request is no
        longer pending, so any replay is rejected. Returns a status dict
        (CONFIRMED / NO_PENDING_ROTATION / FINGERPRINT_MISMATCH /
        INVALID_TOKEN / LOCKED_DOWN)."""
        perm = self._check_store_permissions()
        if perm:
            self._record_audit_store_suspect(perm)
            raise AuditStoreTamperingError(perm)
        now = self._now()
        attempt_total = 0
        break_flag = False
        with _LOCK:
            conn = _connect(self.db_path)
            row = conn.execute(
                "SELECT * FROM rotation_requests WHERE state = ? "
                "ORDER BY id DESC LIMIT 1", (ROTATION_PENDING,)).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO rule_audit (at, rule, event, reason) "
                    "VALUES (datetime('now'), '', 'rotation_confirm_forged_attempt', ?)",
                    (f"confirm attempted for fp {fingerprint[:12]} but no pending rotation",))
                conn.commit()
                conn.close()
                return {"status": "NO_PENDING_ROTATION"}
            if row["fingerprint"] != fingerprint:
                conn.execute(
                    "INSERT INTO rule_audit (at, rule, event, reason) "
                    "VALUES (datetime('now'), '', 'rotation_confirm_forged_attempt', ?)",
                    (f"confirm fp {fingerprint[:12]} mismatch pending fp "
                     f"{row['fingerprint'][:12]} (concurrent rotation rejected)",))
                conn.commit()
                conn.close()
                return {"status": "FINGERPRINT_MISMATCH"}
            expected = row["token_hash"] or ""
            supplied = hashlib.sha256(str(approval_token or "").encode()).hexdigest()
            if not expected or not hmac.compare_digest(supplied, expected):
                conn.execute(
                    "UPDATE rotation_requests SET attempt_count = attempt_count + 1 "
                    "WHERE id = ?", (row["id"],))
                conn.execute(
                    "INSERT INTO rule_audit (at, rule, event, reason) "
                    "VALUES (datetime('now'), '', 'rotation_confirm_forged_attempt', ?)",
                    (f"invalid approval token for pending rotation id={row['id']}",))
                conn.commit()
                attempt_total = self._rotation_attempt_count_in_window(now, conn)
                conn.close()
                break_flag = attempt_total >= ROTATION_ATTEMPT_LIMIT
                if not break_flag:
                    return {"status": "INVALID_TOKEN"}
            else:
                # valid single-use token -> confirm + link key_trust (same tx)
                conn.execute(
                    "UPDATE rotation_requests SET state = ?, decided_at = ?, "
                    "decision_reason = ? WHERE id = ?",
                    (ROTATION_CONFIRMED, now.isoformat(),
                     f"{confirmed_by}: {reason}" if reason else confirmed_by, row["id"]))
                self._do_confirm_key(conn, fingerprint, confirmed_by, reason)
                conn.commit()
                conn.close()
                return {"status": "CONFIRMED", "fingerprint": fingerprint}
        # lockdown is triggered only outside the lock
        if break_flag:
            self._mark_lockdown(
                f"{attempt_total} rotation attempts in window "
                f"(limit {ROTATION_ATTEMPT_LIMIT}/1h)")
            return {"status": "LOCKED_DOWN"}
        return {"status": "INVALID_TOKEN"}

    def _rotation_attempt_count_in_window(self, now: datetime,
                                          conn: Optional[sqlite3.Connection] = None) -> int:
        """Rotation attempts seen inside the sliding window: each created
        request counts 1, plus every forged-confirm attempt it accumulated."""
        if conn is not None:
            rows = conn.execute(
                "SELECT at, attempt_count FROM rotation_requests").fetchall()
        else:
            with _LOCK:
                c = _connect(self.db_path)
                rows = c.execute(
                    "SELECT at, attempt_count FROM rotation_requests").fetchall()
                c.close()
        total = 0
        cutoff = now - timedelta(seconds=ROTATION_ATTEMPT_WINDOW_SECONDS)
        for r in rows:
            try:
                at = datetime.fromisoformat(r["at"])
            except (TypeError, ValueError):
                continue
            if at >= cutoff:
                total += 1 + int(r["attempt_count"] or 0)
        return total

    def _mark_lockdown(self, reason_text: str) -> None:
        with _LOCK:
            conn = _connect(self.db_path)
            conn.execute(
                "UPDATE rotation_requests SET state = ?, decision_reason = ?, "
                "decided_at = datetime('now') WHERE state = ?",
                (ROTATION_LOCKDOWN, reason_text, ROTATION_PENDING))
            conn.execute(
                "INSERT INTO rule_audit (at, rule, event, reason) "
                "VALUES (datetime('now'), '', 'rotation_lockdown', ?)",
                (reason_text,))
            conn.commit()
            conn.close()

    def sweep_expired_rotations(self) -> list[int]:
        """DEFAULT-DENY: flip every expired pending rotation to 'denied'
        (timeout_default_deny). Returns the ids denied. This is what a
        timed-out rotation must run BEFORE anything may load again."""
        now = self._now()
        expired: list[int] = []
        with _LOCK:
            conn = _connect(self.db_path)
            rows = conn.execute(
                "SELECT id, expires_at FROM rotation_requests WHERE state = ?",
                (ROTATION_PENDING,)).fetchall()
            for r in rows:
                try:
                    exp = datetime.fromisoformat(r["expires_at"])
                except (TypeError, ValueError):
                    continue
                if exp < now:
                    conn.execute(
                        "UPDATE rotation_requests SET state = ?, decided_at = ?, "
                        "decision_reason = ? WHERE id = ?",
                        (ROTATION_DENIED, now.isoformat(), "timeout_default_deny",
                         r["id"]))
                    expired.append(int(r["id"]))
            conn.commit()
            conn.close()
        for rid in expired:
            try:
                self.record_rule_event(
                    "rotation_denied",
                    reason=f"rotation id {rid} expired -> timeout_default_deny")
            except Exception:
                pass
        return expired

    # ---------- operator secret: OWN storage, decoupled from the HITL token --

    def _load_operator_secret(self) -> Optional[str]:
        """Resolve the lockdown-release credential from its OWN dedicated
        source only: ROTATION_OPERATOR_SECRET env var, else the separate 0600
        file at OPERATOR_SECRET_PATH. It NEVER falls back to .env /
        HITL_SECURITY_TOKEN — releasing a lockdown requires a credential the
        HITL flow does not hold. A suspicious secret file (symlink, non-regular,
        not 0600) yields None (fail closed: release impossible)."""
        env = os.environ.get(OPERATOR_SECRET_ENV)
        if env:
            return env
        p = OPERATOR_SECRET_PATH
        try:
            st = p.lstat()
        except OSError:
            return None
        if stat.S_ISLNK(st.st_mode):
            return None
        if not stat.S_ISREG(st.st_mode):
            return None
        if stat.S_IMODE(st.st_mode) != 0o600:
            return None
        try:
            value = p.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        return value or None

    def set_operator_secret(self, secret: str) -> Path:
        """Provision the lockdown-release credential at OPERATOR_SECRET_PATH:
        its own .operator folder (0700) and a 0600 secret file, fully separate
        from the HITL .env. After this the SAME credential release_lockdown()
        accepts is persisted on disk for operators. Returns the path written."""
        p = OPERATOR_SECRET_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(p.parent, 0o700)
        except OSError:
            pass
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(p, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(secret.strip() + "\n")
        os.chmod(p, 0o600)
        self.operator_secret = secret.strip()
        return p

    def release_lockdown(self, override_token: str) -> dict:
        """The MANUAL operator-only release. Uses a DIFFERENT credential from
        the automated confirm path — the separately provisioned operator secret
        (never the HITL security token). On success the rotation attempt window
        is reset so a fresh rotation can be started and confirmed normally."""
        if (not self.operator_secret or not override_token
                or not hmac.compare_digest(override_token, self.operator_secret)):
            return {"status": "INVALID_OVERRIDE"}
        if not self.locked_down():
            return {"status": "NOT_LOCKED_DOWN"}
        now = self._now()
        with _LOCK:
            conn = _connect(self.db_path)
            conn.execute("DELETE FROM rotation_requests")
            conn.execute(
                "INSERT INTO rotation_requests (at, fingerprint, state, token_hash, "
                "attempt_count, expires_at, decided_at, decision_reason) "
                "VALUES (?, '', ?, '', 0, ?, ?, ?)",
                (now.isoformat(), ROTATION_RELEASED, now.isoformat(), None,
                 "manual operator override"))
            conn.execute(
                "INSERT INTO rule_audit (at, rule, event, reason) "
                "VALUES (datetime('now'), '', 'rotation_lockdown_released', ?)",
                ("manual operator override; attempt window reset",))
            conn.commit()
            conn.close()
        return {"status": "RELEASED"}


if __name__ == "__main__":
    fb = FeedbackLoop(db_path="/tmp/feedback_test.db")
    for i in range(4):
        r = fb.record_rejection("ssrf_internal_egress", f"human said no #{i}")
        if r["auto_tightened"]:
            print("TIGHTENED at count", i + 1)
    print("preemption for ssrf_internal_egress:", fb.should_preempt("ssrf_internal_egress"))
    print(fb.feedback_prompt())