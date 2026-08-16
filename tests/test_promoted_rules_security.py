"""Promoted-rules storage security: HMAC-signed, permission-checked, audited.

The 6 mandatory hardening scenarios:
  1. wrong HMAC signature  -> rule rejected (all reads refused)
  2. missing signature     -> rule rejected
  3. folder/file perms != 0700/0600 -> reads rejected entirely
  4. rule silently deleted -> startup integrity fires security_incident
  5. removal via remove_promoted_rule() -> no alert (audited 'remove')
  6. attacker hand-writes rules.json without the key -> fully rejected
Each scenario must also record a tampering_detected audit event where expected.
"""

import hashlib
import json
import os
import re
import sqlite3

import pytest

from auto_self_evolver import (CANONICAL_PROBES, SkillRegistry,
                               RuleTamperingError)
from feedback_loop import FeedbackLoop
from security_gate import SecurityGate


@pytest.fixture
def feedback(tmp_path):
    msgs: list[str] = []
    fb = FeedbackLoop(db_path=tmp_path / "fb.db",
                      rotation_notify=msgs.append,
                      operator_secret="test-ops-secret")
    fb.messages = msgs
    return fb


@pytest.fixture
def key(tmp_path):
    return tmp_path / "rules.key"


@pytest.fixture
def registry(tmp_path, key, feedback):
    reg = SkillRegistry(tmp_path / "skills", key_path=key, audit=feedback)
    reg.promote("ssrf_internal_egress",
                CANONICAL_PROBES["ssrf_internal_egress"],
                evidence={"rejection_count": 3, "verified_by": "test"})
    return reg


def _gate(tmp_path, key):
    return SecurityGate(rules_dir=tmp_path / "skills", key_path=str(key))


def _bad_wf():
    return {"nodes": [{"type": "n8n-nodes-base.httpRequest",
                       "parameters": {"url": "http://192.168.1.5/x"}}]}


def _raw_key(key_path):
    """Extract the raw 32-byte key from the env-style key file."""
    for line in open(key_path, encoding="utf-8").read().splitlines():
        if line.startswith("RULES_HMAC_KEY="):
            return bytes.fromhex(line.split("=", 1)[1].strip())
    raise AssertionError(f"no RULES_HMAC_KEY line in {key_path}")


def _events(feedback, event=None):
    conn = sqlite3.connect(feedback.db_path)
    conn.row_factory = sqlite3.Row
    if event:
        rows = conn.execute(
            "SELECT rule, reason FROM rule_audit WHERE event = ? ORDER BY id",
            (event,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT event, rule, reason FROM rule_audit ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _rotate_key(registry, key) -> tuple[list, bytes]:
    """Attacker scenario: replace RULES_HMAC_KEY with a fresh key AND inject a
    malicious rule re-signed under the new key (mathematically valid)."""
    import hashlib, hmac as _hmac
    new_key = os.urandom(32)
    other_lines = [l for l in key.read_text(encoding="utf-8").splitlines()
                   if not l.startswith("RULES_HMAC_KEY=")]
    other_lines.append("RULES_HMAC_KEY=" + new_key.hex())
    key.write_text("\n".join(other_lines) + "\n", encoding="utf-8")
    malicious = [{
        "rule": "evil_rule",
        "probe": {"n8n": True},
        "evidence": {},
        "promoted_at": "2026-01-01T00:00:00",
        "source": "attacker",
    }]
    data = json.dumps(malicious, indent=2).encode("utf-8")
    registry.rules_path.write_bytes(data)
    os.chmod(registry.rules_path, 0o600)
    registry.sig_path.write_text(
        _hmac.new(new_key, data, hashlib.sha256).hexdigest())
    os.chmod(registry.sig_path, 0o600)
    return malicious, new_key


def _approval_token(feedback) -> str:
    """The one-time approval token the notify channel delivered (mocked here).
    Only its sha256 is ever persisted — the test sees the raw value because
    that is what the operator would receive. The message carries both a 64-hex
    fingerprint and a 64-hex token, so we parse the explicitly labeled one."""
    text = feedback.messages[-1]
    m = re.search(r"Approve with token: ([0-9a-f]{64})", text)
    assert m, f"no labeled approval token in alert: {text!r}"
    return m.group(1)


class TestWrongSignature:
    def test_wrong_signature_rejects_rule(self, tmp_path, key, registry, feedback):
        # Attacker with a DIFFERENT key rewrites the signature.
        attacker_key = tmp_path / "attacker.key"
        attacker_key.write_bytes(os.urandom(32))
        os.chmod(attacker_key, 0o600)
        import hashlib, hmac as _hmac
        data = registry.rules_path.read_bytes()
        forged = _hmac.new(attacker_key.read_bytes(), data,
                           hashlib.sha256).hexdigest()
        registry.sig_path.write_text(forged)
        os.chmod(registry.sig_path, 0o600)

        assert registry.load_rules() == []
        gate = _gate(tmp_path, key)
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "APPROVED"
        assert any(ev["event"] == "tampering_detected" for ev in _events(feedback))

    def test_missing_signature_rejects_rule(self, tmp_path, key, registry, feedback):
        registry.sig_path.unlink()

        assert registry.load_rules() == []
        gate = _gate(tmp_path, key)
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "APPROVED"
        assert any(ev["event"] == "tampering_detected" for ev in _events(feedback))


class TestPermissionCheck:
    def test_folder_perms_755_rejects_all_reads(self, tmp_path, key, registry,
                                                feedback):
        os.chmod(registry.auto_rules_dir, 0o755)

        assert registry.load_rules() == []
        gate = _gate(tmp_path, key)
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "APPROVED"
        assert any(ev["event"] == "tampering_detected" for ev in _events(feedback))

    def test_rules_file_perms_644_rejects_all_reads(self, tmp_path, key, registry,
                                                    feedback):
        os.chmod(registry.rules_path, 0o644)

        assert registry.load_rules() == []
        gate = _gate(tmp_path, key)
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "APPROVED"
        assert any(ev["event"] == "tampering_detected" for ev in _events(feedback))


class TestStartupIntegrity:
    def test_silent_deletion_fires_incident(self, tmp_path, key, registry, feedback):
        # A second rule so deletion isn't the whole store.
        registry.promote("secret_hardcoded", CANONICAL_PROBES["secret_hardcoded"])
        # Attacker silently deletes one rule WITHOUT a logged 'remove'.
        kept = [r for r in registry.load_rules()
                if r["rule"] != "secret_hardcoded"]
        data = json.dumps(kept, indent=2).encode("utf-8")
        registry.rules_path.write_bytes(data)
        os.chmod(registry.rules_path, 0o600)
        import hashlib, hmac as _hmac
        registry.sig_path.write_text(
            _hmac.new(_raw_key(key), data, hashlib.sha256).hexdigest())
        os.chmod(registry.sig_path, 0o600)

        report = registry.check_startup_integrity()
        assert report["status"] == "security_incident"
        assert "secret_hardcoded" in report["missing"]

    def test_remove_promoted_rule_no_alert(self, tmp_path, key, registry, feedback):
        registry.promote("secret_hardcoded", CANONICAL_PROBES["secret_hardcoded"])
        assert registry.remove_promoted_rule("secret_hardcoded",
                                             reason="superseded by stricter guard")

        report = registry.check_startup_integrity()
        assert report["status"] == "ok"
        assert report["missing"] == []
        assert any(ev["event"] == "remove" and ev["rule"] == "secret_hardcoded"
                   for ev in _events(feedback))


class TestKeyRotationVsTampering:
    def test_key_rotation_distinct_from_tampering(self, tmp_path, key, registry,
                                                  feedback):
        # Baseline: promote signed + audited with the current key fingerprint.
        registry.promote("secret_hardcoded", CANONICAL_PROBES["secret_hardcoded"])
        last = feedback.last_known_state()
        assert last and last["key_fp"]
        # Legit rotation: the .env key file is REPLACED with a new key
        # (other lines of .env preserved), rules NOT re-signed yet.
        other_lines = [l for l in key.read_text(encoding="utf-8").splitlines()
                       if not l.startswith("RULES_HMAC_KEY=")]
        other_lines.append("RULES_HMAC_KEY=" + os.urandom(32).hex())
        key.write_text("\n".join(other_lines) + "\n", encoding="utf-8")

        assert registry.load_rules() == []

        events = _events(feedback)
        assert any(ev["event"] == "key_rotation_detected" for ev in events)
        assert not any(ev["event"] == "tampering_detected" for ev in events)
        rotation = [ev for ev in events if ev["event"] == "key_rotation_detected"]
        assert "ROTATED" in rotation[0]["reason"]

    def test_content_edit_still_reports_tampering(self, tmp_path, key, registry,
                                                  feedback):
        # Same key, content edited: must STILL be tampering_detected, not
        # rotation (rotation detection must not mask genuine tampering).
        data = registry.rules_path.read_bytes()
        registry.rules_path.write_bytes(data + b"\n")  # edit content
        os.chmod(registry.rules_path, 0o600)

        assert registry.load_rules() == []

        events = _events(feedback)
        assert any(ev["event"] == "tampering_detected" for ev in events)
        assert not any(ev["event"] == "key_rotation_detected" for ev in events)

    def test_rotation_does_not_auto_trust_new_rules(self, tmp_path, key, registry,
                                                    feedback):
        """THE critical scenario: attacker replaces RULES_HMAC_KEY AND re-signs
        rules.json with the new key, so the signature is MATHEMATICALLY valid
        under the current key. The rules must STILL not be accepted — only an
        explicit confirm_key_rotation() lifts the block."""
        import hashlib, hmac as _hmac
        new_key = os.urandom(32)
        # 1. attacker replaces the key line in .env
        other_lines = [l for l in key.read_text(encoding="utf-8").splitlines()
                       if not l.startswith("RULES_HMAC_KEY=")]
        other_lines.append("RULES_HMAC_KEY=" + new_key.hex())
        key.write_text("\n".join(other_lines) + "\n", encoding="utf-8")

        # 2. attacker injects a MALICIOUS rule and re-signs with the new key
        malicious = [{
            "rule": "evil_rule",
            "probe": {"n8n": True},
            "evidence": {},
            "promoted_at": "2026-01-01T00:00:00",
            "source": "attacker",
        }]
        data = json.dumps(malicious, indent=2).encode("utf-8")
        registry.rules_path.write_bytes(data)
        os.chmod(registry.rules_path, 0o600)
        registry.sig_path.write_text(
            _hmac.new(new_key, data, hashlib.sha256).hexdigest())
        os.chmod(registry.sig_path, 0o600)

        # 3. signature IS valid under current key — but rules MUST be blocked
        assert registry.load_rules() == []          # NOT auto-trusted
        assert registry._key_rotation_pending()      # rotation detected
        events = _events(feedback)
        assert any(ev["event"] == "key_rotation_detected" for ev in events)
        assert not any(ev["event"] == "tampering_detected" for ev in events)
        # gate also refuses to build on the malicious store
        gate = _gate(tmp_path, key)
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "APPROVED"

        # 4. an UNCONFIRMED rotation must not silently advance the baseline:
        #    re-persisting (e.g. a stray promote) must FAIL while blocked
        with pytest.raises(RuleTamperingError):
            registry.promote("ssrf_internal_egress",
                             CANONICAL_PROBES["ssrf_internal_egress"])

        # 5. explicit operator confirmation lifts the block, and ONLY then do
        #    the (attacker-injected) rules load — this is the sanctioned path.
        #    The one-time approval token was delivered via the same notify
        #    channel HITL uses; the registry never accepts a raw `confirmed_by`.
        token = _approval_token(feedback)
        assert token and len(token) == 64
        fp = registry.confirm_key_rotation(approval_token=token,
                                           confirmed_by="operator",
                                           reason="deliberate key change")
        assert fp == hashlib.sha256(new_key).hexdigest()
        assert any(ev["event"] == "key_confirmed"
                   for ev in feedback.rule_events("key_confirmed"))
        assert registry._key_rotation_pending() is False
        assert registry.load_rules() == malicious      # trusted now
        assert registry.load_rules()[0]["source"] == "attacker"


class TestAttackerInjection:
    def test_handwritten_rules_json_without_key_rejected(self, tmp_path, key,
                                                         registry, feedback):
        # Attacker hand-writes a rules.json that even matches a REAL probe,
        # but cannot sign it (no key) and cannot fix the perms either.
        injected = [{
            "rule": "ssrf_internal_egress",
            "probe": CANONICAL_PROBES["ssrf_internal_egress"],
            "evidence": {},
            "promoted_at": "2026-01-01T00:00:00",
            "source": "attacker",
        }]
        registry.rules_path.write_text(json.dumps(injected), encoding="utf-8")
        os.chmod(registry.rules_path, 0o600)
        # stale signature from the legit promote is now WRONG for new content

        assert registry.load_rules() == []
        gate = _gate(tmp_path, key)
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "APPROVED"
        assert any(ev["event"] == "tampering_detected" for ev in _events(feedback))

    def test_promote_refuses_tampered_store(self, tmp_path, key, registry):
        registry.sig_path.unlink()
        with pytest.raises(RuleTamperingError):
            registry.promote("secret_hardcoded",
                             CANONICAL_PROBES["secret_hardcoded"])


class TestRotationApprovalToken:
    """B1: confirm_key_rotation is a REAL approval gate — a one-time token
    verified at HITL severity, never a free-form confirmed_by string."""

    def test_confirm_rotation_rejects_invalid_token(self, tmp_path, key,
                                                    registry, feedback):
        _rotate_key(registry, key)
        assert registry.load_rules() == []          # blocked + pending
        assert feedback.rotation_status()["state"] == "pending"

        # wrong token -> rejected AND audited as forged attempt
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="0" * 64,
                                          confirmed_by="operator", reason="x")
        forged = [e for e in feedback.rule_events("rotation_confirm_forged_attempt")]
        assert len(forged) == 1
        assert registry._key_rotation_pending()      # still blocked

        # correct one-time token is the ONLY thing that lifts the block
        fp = registry.confirm_key_rotation(approval_token=_approval_token(feedback),
                                           confirmed_by="operator", reason="ok")
        assert fp == hashlib.sha256(_raw_key(key)).hexdigest()
        assert registry._key_rotation_pending() is False

    def test_confirm_rotation_rejects_reused_token(self, tmp_path, key,
                                                   registry, feedback):
        _rotate_key(registry, key)
        assert registry.load_rules() == []
        token = _approval_token(feedback)

        registry.confirm_key_rotation(approval_token=token,
                                      confirmed_by="operator", reason="once")
        before = len(feedback.rule_events("key_confirmed"))

        # replaying the same token must NOT confirm twice / keep working
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token=token,
                                          confirmed_by="operator",
                                          reason="replay")
        assert len(feedback.rule_events("key_confirmed")) == before


class TestRotationRateLimitLockdown:
    """B2: >3 rotation attempts in the window -> hard lockdown that ONLY a
    manual operator override (a different credential) can lift."""

    def test_rotation_rate_limit_triggers_lockdown(self, tmp_path, key,
                                                   registry, feedback):
        _rotate_key(registry, key)
        assert registry.load_rules() == []           # creation = attempt 1
        # forged attempt #1
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="a" * 64,
                                          confirmed_by="operator")
        assert not feedback.locked_down()
        # forged attempt #2 -> 3 attempts in window -> LOCKED DOWN
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="b" * 64,
                                          confirmed_by="operator")
        assert feedback.locked_down()
        assert feedback.rotation_status()["state"] == "lockdown"
        # reads are NOT killed during lockdown: the pre-incident trusted rule
        # still loads (from the last known GOOD state), never the attacker's
        locked = registry.load_rules()
        assert {r["rule"] for r in locked} == {"ssrf_internal_egress"}
        assert all(r.get("source") != "attacker" for r in locked)

        # the automated confirm path cannot lift it (no pending to confirm)
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="c" * 64,
                                          confirmed_by="operator")

        # a different forged create is refused too (promote propagates the
        # RotationLockedError as a hard block); reads still serve the last
        # known good state
        _rotate_key(registry, key)
        locked = registry.load_rules()
        assert {r["rule"] for r in locked} == {"ssrf_internal_egress"}
        assert all(r.get("source") != "attacker" for r in locked)
        with pytest.raises(RuleTamperingError):
            registry.promote("ssrf_internal_egress",
                             CANONICAL_PROBES["ssrf_internal_egress"])

        # wrong override cannot release
        assert registry.release_key_lockdown("not-the-secret")["status"] == \
            "INVALID_OVERRIDE"
        # the operator secret (HITL credential) CAN release
        assert registry.release_key_lockdown("test-ops-secret")["status"] == \
            "RELEASED"
        assert not feedback.locked_down()


class TestPendingRotationTimeoutRollback:
    """B3: a pending rotation never confirmed within the window is default-
    denied and rolled back to the last known-good snapshot under a fresh key."""

    def test_pending_rotation_auto_denies_after_timeout(self, tmp_path, key,
                                                        registry, feedback):
        last = feedback.last_known_state()
        assert last and last["rules_json"]

        _rotate_key(registry, key)
        assert registry.load_rules() == []           # pending + blocked
        assert feedback.rotation_status()["state"] == "pending"

        # force the default-deny window to elapse
        conn = sqlite3.connect(feedback.db_path)
        conn.execute("UPDATE rotation_requests SET expires_at = ? WHERE id = ?",
                     ("2000-01-01T00:00:00+00:00",
                      feedback.rotation_status()["id"]))
        conn.commit()
        conn.close()

        # next read auto-denies + rolls back; the injected evil rule is gone
        rules = registry.load_rules()
        names = {r["rule"] for r in rules}
        assert "ssrf_internal_egress" in names
        assert "evil_rule" not in names
        assert feedback.rotation_status()["state"] == "denied"
        assert feedback.rotation_status()["decision_reason"] == "timeout_default_deny"
        assert not registry._key_rotation_pending()
        assert len(feedback.rule_events("rotation_rollback")) == 1

        # the rolled-back baseline is a FRESH key (never the attacker's), and
        # the trust record must be a linked system confirm (system_rollback)
        assert feedback.trusted_key_fingerprint() == \
            hashlib.sha256(_raw_key(key)).hexdigest()


class TestAuditStoreProtection:
    """B4: the audit DB that owns the key-trust chain is permission-checked on
    EVERY read and direct injection of a trust row is detected."""

    def test_audit_db_perms_checked_on_every_read(self, tmp_path, key,
                                                  registry, feedback):
        assert registry.load_rules()                 # healthy baseline reads fine
        os.chmod(feedback.db_path, 0o644)            # world-readable anomaly

        assert registry.load_rules() == []           # ALL reads refused now
        ev = [e for e in feedback.rule_events("audit_store_tampering_suspected")]
        assert len(ev) >= 1

    def test_direct_db_injection_of_trust_row_detected_or_prevented(
            self, tmp_path, key, registry, feedback):
        assert registry.load_rules()
        legit = feedback.trusted_key_fingerprint()

        # attacker writes a trust row straight into key_trust, bypassing the
        # confirm verbs (record_id keeps its default 0 -> no live audit link)
        conn = sqlite3.connect(feedback.db_path)
        conn.execute(
            "INSERT INTO key_trust (at, fingerprint, confirmed_by, reason, "
            "record_id) VALUES (datetime('now'), ?, ?, ?, 0)",
            (legit, "attacker", "forged confirmation"))
        conn.commit()
        conn.close()

        with pytest.raises(RuleTamperingError):
            registry._key_rotation_pending()
        assert registry.load_rules() == []           # never trusts the row
        ev = [e for e in feedback.rule_events("audit_store_tampering_suspected")]
        assert len(ev) >= 1


class TestRotationTelegramAlert:
    """B5: entering pending fires an alert through the SAME notify channel the
    HITL gate posts approvals to (mocked here — no live Telegram in tests)."""

    def test_pending_rotation_sends_telegram_alert(self, tmp_path, key,
                                                   registry, feedback):
        assert not feedback.messages
        _rotate_key(registry, key)
        assert registry.load_rules() == []

        assert feedback.messages, "rotation pending must notify the operator"
        text = feedback.messages[-1]
        assert "KEY-ROTATION" in text and "PENDING" in text
        assert re.search(r"Approve with token: [0-9a-f]{64}", text)
        assert feedback.rotation_status()["state"] == "pending"

        # only ONE alert for the same pending request (no notify spam on re-read)
        assert registry.load_rules() == []
        assert len(feedback.messages) == 1


class TestOldKeyDestruction:
    """B6: after a confirmed rotation the old/stale key hex is physically
    scrubbed from the key file; the only residue is the sha256 fingerprint."""

    def test_confirmed_rotation_destroys_old_key(self, tmp_path, key,
                                                 registry, feedback):
        old_fp = feedback.trusted_key_fingerprint()
        malicious, new_key = _rotate_key(registry, key)
        assert registry.load_rules() == []

        # plant a stale duplicate key line AFTER the rotation: residual that
        # destroy must physically erase on confirmation
        stale = os.urandom(32).hex()
        key.write_text(key.read_text(encoding="utf-8")
                       + f"\nRULES_HMAC_KEY={stale}\n", encoding="utf-8")

        registry.confirm_key_rotation(approval_token=_approval_token(feedback),
                                      confirmed_by="operator", reason="rotate")

        key_lines = [l for l in key.read_text(encoding="utf-8").splitlines()
                     if l.startswith("RULES_HMAC_KEY=")]
        assert len(key_lines) == 1                   # stale line destroyed
        assert key_lines[0] == f"RULES_HMAC_KEY={new_key.hex()}"
        assert stale not in key.read_text(encoding="utf-8")
        destroyed = [e for e in feedback.rule_events("rotation_old_key_destroyed")]
        assert len(destroyed) == 1
        assert old_fp[:12] in destroyed[0]["reason"]  # only the hash leaves a trace
        assert registry._key_rotation_pending() is False
        assert registry.load_rules() == malicious



class TestConcurrentPendingRotation:
    """B7: a NEW rotation while one is already pending is refused — no
    replace, no stacking; the original pending remains the only one."""

    def test_concurrent_pending_rotation_rejected(self, tmp_path, key,
                                                  registry, feedback):
        _, new_key1 = _rotate_key(registry, key)
        assert registry.load_rules() == []
        fp1 = hashlib.sha256(new_key1).hexdigest()
        assert feedback.rotation_status()["fingerprint"] == fp1

        # second rotation to a DIFFERENT fingerprint while pending
        _rotate_key(registry, key)
        assert registry.load_rules() == []           # rejected, stays blocked
        assert len(feedback.rule_events("rotation_rejected")) == 1

        status = feedback.rotation_status()
        assert status["fingerprint"] == fp1          # pending NOT replaced
        assert status["state"] == "pending"

        # confirming the stale pending under the NEW current key is refused
        # (fingerprint mismatch — the pending belongs to the old fingerprint)
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token=_approval_token(feedback),
                                          confirmed_by="operator", reason="x")


class TestOperatorSecretSeparation:
    """FINAL Q1: the lockdown-release credential is ENTIRELY separate from the
    HITL security token — its own env var / dedicated 0600 file in its own
    folder, and release_key_lockdown() never accepts the HITL secret."""

    def test_lockdown_release_rejects_hitl_secret(self, tmp_path, monkeypatch,
                                                  key, registry, feedback):
        monkeypatch.setenv("HITL_SECURITY_TOKEN", "hitl-secret-abc123")
        monkeypatch.setenv("ROTATION_OPERATOR_SECRET", "")  # neutralize any leak
        # A FeedbackLoop with NO operator secret must NOT inherit the HITL
        # token (the old `or os.environ.get("HITL_SECURITY_TOKEN")` fallback
        # is gone).
        bare = FeedbackLoop(db_path=tmp_path / "bare.db",
                            rotation_notify=feedback.messages.append)
        assert bare.operator_secret is None
        # The configured operator secret is genuinely separate from the HITL
        # token, so the two can be compared head-to-head.
        assert feedback.operator_secret == "test-ops-secret"
        assert feedback.operator_secret != "hitl-secret-abc123"

        # trigger a rate-limit lockdown
        _rotate_key(registry, key)
        assert registry.load_rules() == []          # pending
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="a" * 64,
                                          confirmed_by="operator")
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="b" * 64,
                                          confirmed_by="operator")
        assert feedback.locked_down()

        # the HITL security token CANNOT release the lockdown
        assert registry.release_key_lockdown("hitl-secret-abc123")["status"] == \
            "INVALID_OVERRIDE"
        assert feedback.locked_down()
        # the separate operator secret CAN
        assert registry.release_key_lockdown("test-ops-secret")["status"] == \
            "RELEASED"
        assert not feedback.locked_down()

    def test_operator_secret_stored_separately_0600(self, tmp_path, monkeypatch):
        target = tmp_path / ".operator" / "rotation_override.secret"
        monkeypatch.setattr("feedback_loop.OPERATOR_SECRET_PATH", target)
        assert not target.exists()

        fb = FeedbackLoop(db_path=tmp_path / "fb2.db")
        assert fb.operator_secret is None           # no source -> fail closed
        p = fb.set_operator_secret("ops-xyz-987")
        assert p == target
        assert p.parent.name == ".operator"
        assert p.parent != tmp_path / ".env"        # separate folder, not .env
        assert (p.parent.stat().st_mode & 0o777) == 0o700
        assert (p.stat().st_mode & 0o777) == 0o600
        assert "ops-xyz-987" in p.read_text(encoding="utf-8")

        # a fresh FeedbackLoop (no arg, no env) recovers it from the file ONLY
        fb2 = FeedbackLoop(db_path=tmp_path / "fb3.db")
        assert fb2.operator_secret == "ops-xyz-987"


class TestLockdownReadsKeepWorking:
    """FINAL Q2: during a rate-limit lockdown, previously-trusted (pre-incident)
    promoted rules STILL load and are enforced — only new rotation acceptance /
    confirmation is blocked. No full DoS."""

    def test_lockdown_does_not_block_reading_existing_trusted_rules(
            self, tmp_path, key, registry, feedback):
        # gate with the audit trail threaded: this is the enforcement reader
        gate = SecurityGate(rules_dir=tmp_path / "skills", key_path=str(key),
                            audit=feedback)
        # baseline: the trusted ssrf guard is enforced pre-incident
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "REJECTED_SECURITY_RISK"

        # attacker rotates key + re-signs malicious rules, then two failed
        # confirmations trip the rate-limit LOCKDOWN
        _rotate_key(registry, key)
        assert registry.load_rules() == []          # blocked (pending)
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="a" * 64,
                                          confirmed_by="operator")
        with pytest.raises(RuleTamperingError):
            registry.confirm_key_rotation(approval_token="b" * 64,
                                          confirmed_by="operator")
        assert feedback.locked_down()

        # DURING lockdown the pre-incident trusted rule still reads back
        locked = registry.load_rules()
        assert {r["rule"] for r in locked} == {"ssrf_internal_egress"}
        assert all(r.get("source") != "attacker" for r in locked)

        # and the gate STILL rejects the malicious workflow with it
        result = gate.evaluate_to_dict(_bad_wf())
        assert result["status"] == "REJECTED_SECURITY_RISK"
        assert any("Auto-rule" in v for v in result["violations"])

        # scope check: accepting/confirming a NEW rotation stays blocked, but
        # the trusted read keeps working (last known good state)
        _rotate_key(registry, key)
        assert feedback.locked_down()               # lockdown persists
        with pytest.raises(RuleTamperingError):
            registry.promote("ssrf_internal_egress",
                             CANONICAL_PROBES["ssrf_internal_egress"])
        assert {r["rule"] for r in registry.load_rules()} == {"ssrf_internal_egress"}
        assert gate.evaluate_to_dict(_bad_wf())["status"] == "REJECTED_SECURITY_RISK"

        # operator release restores normal operation
        assert registry.release_key_lockdown("test-ops-secret")["status"] == \
            "RELEASED"
        assert not feedback.locked_down()
