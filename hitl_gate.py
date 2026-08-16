"""Human-in-the-Loop (HITL) Gate — Zero-Trust authorization layer.

Workflow: a Verifier Engine outcome with Risk Score >= 40 (or any security-
critical decision) is frozen as PENDING_APPROVAL, persisted in the audit DB,
then escalated to a human via Telegram Bot / local CLI. Default policy is
DENY: if no human decision within the timeout window the state flips to
EXPIRED_REJECTED and the operation is aborted.
"""

import hashlib
import hmac
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

DEFAULT_TIMEOUT_MINUTES = 15
DEFAULT_DB_PATH = Path(__file__).parent / "audit.db"


class HITLState:
    PENDING = "PENDING_APPROVAL"
    APPROVED = "OVERRIDE_APPROVED"
    REJECTED = "HARD_REJECT"
    EXPIRED = "EXPIRED_REJECTED"


@dataclass
class HITLRequest:
    request_id: str
    raw_input: str
    risk_score: int
    violations: list[str] = field(default_factory=list)
    payload: Any = None
    state: str = HITLState.PENDING
    created_at: str = ""
    expires_at: str = ""
    decided_at: Optional[str] = None
    decision_reason: str = ""
    token_hash: Optional[str] = None


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_request_id() -> str:
    import uuid
    return uuid.uuid4().hex[:16]


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ============================================================
# Custom exception type so the verifier can distinguish a
# hostile/cancelled approval from a normal one.
# ============================================================
class ApprovalWithheldError(Exception):
    """Raised when human rejects or fails to approve in time."""


class HITLGate:
    """State manager + default-deny timeout + notification dispatch."""

    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB_PATH,
        timeout_minutes: int = DEFAULT_TIMEOUT_MINUTES,
        security_token: Optional[str] = None,
        notify_handler: Optional[Callable[[HITLRequest], None]] = None,
        env_token: Optional[str] = None,
    ):
        self.db_path = str(db_path)
        self.timeout_minutes = timeout_minutes
        # Security token comes from: explicit arg > env var > .env file
        self.security_token = (
            security_token
            or env_token
            or os.environ.get("HITL_SECURITY_TOKEN")
            or self._load_env_token()
        )
        self.notify_handler = notify_handler
        self._init_db()

    # ---------- persistence helpers ----------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_approvals (
                    request_id TEXT PRIMARY KEY,
                    raw_input TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    violations TEXT,
                    payload TEXT,
                    state TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    decided_at TEXT,
                    decision_reason TEXT,
                    token_hash TEXT
                )
            """)
            conn.commit()

    def _load_env_token(self) -> Optional[str]:
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("HITL_SECURITY_TOKEN="):
                    return line.split("=", 1)[1].strip()
        return None

    # ---------- state transitions ----------

    def create_pending(
        self,
        raw_input: str,
        risk_score: int,
        violations: list[str],
        payload: Any = None,
    ) -> HITLRequest:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self.timeout_minutes)
        req = HITLRequest(
            request_id=_new_request_id(),
            raw_input=raw_input,
            risk_score=risk_score,
            violations=violations,
            payload=payload,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
        )
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO pending_approvals (
                    request_id, raw_input, risk_score, violations, payload, state,
                    created_at, expires_at, decided_at, decision_reason, token_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req.request_id, req.raw_input, req.risk_score,
                json.dumps(violations), json.dumps(payload, default=str),
                req.state, req.created_at, req.expires_at,
                None, "", None,
            ))
            conn.commit()
        self._notify(req)
        return req

    def get(self, request_id: str) -> Optional[HITLRequest]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM pending_approvals WHERE request_id = ?", (request_id,)
            ).fetchone()
        if row is None:
            return None
        return HITLRequest(
            request_id=row["request_id"],
            raw_input=row["raw_input"],
            risk_score=row["risk_score"],
            violations=json.loads(row["violations"] or "[]"),
            payload=json.loads(row["payload"]) if row["payload"] else None,
            state=row["state"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            decided_at=row["decided_at"],
            decision_reason=row["decision_reason"],
            token_hash=row["token_hash"],
        )

    def _transition(self, request_id: str, new_state: str, reason: str) -> None:
        with self._connect() as conn:
            conn.execute("""
                UPDATE pending_approvals
                SET state = ?, decided_at = ?, decision_reason = ?
                WHERE request_id = ?
            """, (new_state, _utcnow(), reason, request_id))
            conn.commit()

    # ---------- human decision verbs ----------

    def approve(self, request_id: str, token: str) -> dict:
        """Approve a pending request ONLY with a valid security token."""
        req = self.get(request_id)
        if req is None:
            return {"status": "NOT_FOUND", "request_id": request_id}

        if req.state != HITLState.PENDING:
            return {"status": req.state, "request_id": request_id,
                    "reason": req.decision_reason}

        if self.security_token is None or not hmac.compare_digest(
            token, self.security_token or ""
        ):
            return {"status": "INVALID_TOKEN", "request_id": request_id}

        # Record token hash so it's provable later (never store raw token)
        with self._connect() as conn:
            conn.execute(
                "UPDATE pending_approvals SET token_hash = ? WHERE request_id = ?",
                (_hash_token(token), request_id),
            )
            conn.commit()
        self._transition(request_id, HITLState.APPROVED, "human_approval")
        return {"status": HITLState.APPROVED, "request_id": request_id}

    def reject(self, request_id: str, reason: str = "") -> dict:
        req = self.get(request_id)
        if req is None:
            return {"status": "NOT_FOUND", "request_id": request_id}
        if req.state != HITLState.PENDING:
            return {"status": req.state, "request_id": request_id,
                    "reason": req.decision_reason}
        self._transition(request_id, HITLState.REJECTED, reason or "human_rejection")
        return {"status": HITLState.REJECTED, "request_id": request_id}

    def sweep_expired(self) -> list[str]:
        """Default-DENY: flip all expired PENDING requests to EXPIRED_REJECTED."""
        now = datetime.now(timezone.utc)
        expired = []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT request_id, expires_at FROM pending_approvals WHERE state = ?",
                (HITLState.PENDING,),
            ).fetchall()
            for row in rows:
                expires = datetime.fromisoformat(row["expires_at"])
                if expires < now:
                    conn.execute(
                        "UPDATE pending_approvals SET state = ?, decided_at = ?, "
                        "decision_reason = ? WHERE request_id = ?",
                        (HITLState.EXPIRED, _utcnow(), "timeout_default_deny",
                         row["request_id"]),
                    )
                    expired.append(row["request_id"])
            conn.commit()
        return expired

    # ---------- notification dispatch ----------

    def _notify(self, req: HITLRequest) -> None:
        if self.notify_handler is not None:
            try:
                self.notify_handler(req)
                return
            except Exception:
                pass
        self._notify_cli(req)

    def _notify_cli(self, req: HITLRequest) -> None:
        print(f"\n[HITL] PENDING APPROVAL — request {req.request_id}")
        print(f"  Risk score: {req.risk_score}/100")
        print(f"  Violations: {', '.join(req.violations) if req.violations else 'n/a'}")
        print(f"  Expires:    {req.expires_at}")
        print(f"  >>> telebot_approve {req.request_id} <TOKEN>   OR   "
              f"telebot_reject {req.request_id} <reason>")

    def notify_telegram(self, bot_token: str, chat_id: str) -> Callable[[HITLRequest], None]:
        """Build a notification handler that posts to Telegram."""
        def handler(req: HITLRequest) -> None:
            text = (
                f"⚠️ HITL Approval Required\n"
                f"Request: {req.request_id}\n"
                f"Risk: {req.risk_score}/100\n"
                f"Violations: {', '.join(req.violations)}\n"
                f"Expires: {req.expires_at}\n"
                f"Approve: /approve_{req.request_id}\n"
                f"Reject: /reject_{req.request_id}"
            )
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
            try:
                with urllib.request.urlopen(url + "?" + data.decode(), timeout=10) as resp:
                    resp.read()
            except Exception as e:
                print(f"[HITL][Telegram] notify failed: {e}", file=sys.stderr)
        return handler

    # ---------- inspection / reporting ----------

    def list_pending(self) -> list[HITLRequest]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM pending_approvals WHERE state = ? ORDER BY created_at",
                (HITLState.PENDING,),
            ).fetchall()
        return [self._row_to_req(r) for r in rows]

    def _row_to_req(self, row: sqlite3.Row) -> HITLRequest:
        return HITLRequest(
            request_id=row["request_id"], raw_input=row["raw_input"],
            risk_score=row["risk_score"],
            violations=json.loads(row["violations"] or "[]"),
            payload=json.loads(row["payload"]) if row["payload"] else None,
            state=row["state"], created_at=row["created_at"],
            expires_at=row["expires_at"], decided_at=row["decided_at"],
            decision_reason=row["decision_reason"], token_hash=row["token_hash"],
        )


# ============================================================
# CLI frontends — entry points for local human approval
# ============================================================
def cli_approve(gate: HITLGate, request_id: str, token: str) -> None:
    result = gate.approve(request_id, token)
    print(f"[HITL] {result.get('status')} {result.get('request_id', '')} "
          f"{result.get('reason', '')}")
    return_code = 0 if result.get("status") == HITLState.APPROVED else 1
    sys.exit(return_code)


def cli_reject(gate: HITLGate, request_id: str, reason: str = "") -> None:
    result = gate.reject(request_id, reason)
    print(f"[HITL] {result.get('status')} {result.get('request_id', '')} "
          f"{result.get('reason', '')}")
    sys.exit(0)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HITL approval CLI")
    parser.add_argument("action", choices=["approve", "reject", "list", "sweep"])
    parser.add_argument("request_id", nargs="?", default=None)
    parser.add_argument("token_or_reason", nargs="?", default=None)
    args = parser.parse_args()

    gate = HITLGate()

    if args.action == "list":
        for req in gate.list_pending():
            print(f"{req.request_id} | {req.risk_score} | {req.expires_at}")
    elif args.action == "sweep":
        expired = gate.sweep_expired()
        print(f"[HITL] expired -> {expired}")
    elif args.action == "approve" and args.request_id and args.token_or_reason:
        cli_approve(gate, args.request_id, args.token_or_reason)
    elif args.action == "reject" and args.request_id:
        cli_reject(gate, args.request_id, args.token_or_reason or "")
    else:
        parser.print_help()