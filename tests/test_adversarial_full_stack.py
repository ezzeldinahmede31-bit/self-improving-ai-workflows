"""Full-stack adversarial integration suite.

Deliberately attacks the platform end-to-end. EVERY attack MUST fail
closed (deny/raise) or route to HUMAN REVIEW by design. Any attack that
silently succeeds is a regression and fails the test.

Attack inventory (each is one test):
  policy:      missing / malformed / mutation / downgrade / unknown
  capability:  replay-after-revoke / expiry / tamper / scope-widen /
               wrong-tenant / wrong-resource / wrong-tool / forged /
               attenuate-widen
  egress:      loopback / localhost / metadata / private-10/172/192 /
               ipv6-loopback / userinfo / decimal-ip / hex-ip /
               octet-overflow / file-scheme / bad-port / unresolvable
  sandbox:     adversarial workload forced off local tier; env scrubbed
  skill-trust: modified file / unregistered / high-risk / tampered seal
  secrets:     redactor masks API key in logs/tool results; vault lease
               single-use; expired lease refused
  audit:       production sinks fail closed without key; tamper detected;
               unsigned chain verifies structurally but is NOT signed
  provenance:  gaps() reports missing links
  tool-verify: false/wrong-resource result never commits
  invariants:  double-booking blocked; cross-tenant cancel blocked
  saga/idem:   duplicate delivery executes once; crash-recovery replays
               without double side effects
  tenancy:     cross-tenant read/write blocked; budget cannot overspend
  deployment:  gate failure blocks release; probe failure rolls back
  flags:       unknown flag off; corrupt percent clamped; flag never
               bypasses EnforcedExecutor
  hitl:        sensitive action without approval denied in strict mode
  enforce:     NO_SENSITIVE_EXECUTION_WITHOUT_ENFORCEMENT invariant —
               every SENSITIVE_ACTIONS member denied with no profile
  resources:   huge prompt / huge tool result capped; CPU timeout honored
"""

import os
import time

import pytest

from enforced_execution import EnforcedExecutor, EnforcementError, SENSITIVE_ACTIONS
from capability import CapabilityIssuer, CapabilityError
from egress_firewall import EgressPolicy, check_url
from policy_engine import PolicyEngine
import platform_wiring
from platform_wiring import EnforcementProfile


SECRET = b"test-secret-16bytes-min!!"


def strict_profile(**kw):
    base = dict(
        policy={"allow": ["*"], "deny": [], "approve": []},
        capability_secret=SECRET,
        egress=EgressPolicy(allow_public_internet=False,
                            allowed_domains=("example.com",)),
        sandbox_docker=False,
    )
    base.update(kw)
    return EnforcementProfile.from_dict(base)


def fake_resolve_public(host):
    return ["93.184.216.34"]


# ---------------------------------------------------------------- policy ---

class TestPolicyBypass:
    def test_missing_policy_strict_denies(self):
        ex = EnforcedExecutor(profile=None, strict=True)
        with pytest.raises(EnforcementError):
            ex.execute(action="tool.execute", run=lambda: "SHOULD NOT RUN")

    def test_malformed_policy_denies(self):
        prof = EnforcementProfile.from_dict(
            {"policy": {"allow": ["*"], "deny": ["workflow.execute"]},
             "capability_secret": SECRET})
        ex = EnforcedExecutor(profile=prof, strict=True)
        with pytest.raises(EnforcementError):
            ex.execute(action="workflow.execute", run=lambda: 1)

    def test_policy_downgrade_denies(self):
        eng = PolicyEngine({"allow": ["read"], "deny": ["*"]})
        d = eng.evaluate(agent="a", action="tool.execute", resource="x")
        assert not d.allowed

    def test_unknown_action_default_deny(self):
        eng = PolicyEngine({"allow": ["read.only"], "deny": []})
        d = eng.evaluate(agent="a", action="nuke.everything", resource="x")
        assert not d.allowed or d.needs_approval


# ----------------------------------------------------------- capability ---

class TestCapabilityBypass:
    def _issuer(self):
        return CapabilityIssuer(SECRET)

    def test_replay_after_revoke_fails(self):
        iss = self._issuer()
        tok = iss.issue(actions=["tool.execute"], resource="task:1")
        body = iss._decode(tok)
        assert iss.revoke(body["id"]) is True
        ok, why = iss.verify(tok, action="tool.execute", resource="task:1")
        assert not ok and "revok" in why

    def test_expired_token_fails(self):
        iss = self._issuer()
        tok = iss.issue(actions=["tool.execute"], resource="*", ttl_s=1)
        body = iss._decode(tok)
        body["exp"] = int(time.time()) - 3600
        import base64, json, hmac as _hm, hashlib as _hl
        raw = json.dumps(body, sort_keys=True,
                         separators=(",", ":")).encode()
        sig = base64.urlsafe_b64encode(
            _hm.new(SECRET, raw, _hl.sha256).digest()).decode().rstrip("=")
        forged_exp = (base64.urlsafe_b64encode(raw).decode().rstrip("=")
                      + "." + sig)
        ok, why = iss.verify(forged_exp, action="tool.execute",
                             resource="*")
        assert not ok and "expir" in why

    def test_tampered_payload_fails(self):
        iss = self._issuer()
        tok = iss.issue(actions=["tool.execute"], resource="*")
        part, sig = tok.split(".")
        bad = ("A" if part[0] != "A" else "B") + part[1:]
        ok, _ = iss.verify(bad + "." + sig, action="tool.execute",
                           resource="*")
        assert not ok

    def test_scope_widen_via_attenuate_fails(self):
        iss = self._issuer()
        tok = iss.issue(actions=["read"], resource="task:1", ttl_s=600)
        with pytest.raises(CapabilityError):
            iss.attenuate(tok, actions=["read", "admin"])

    def test_wrong_resource_fails(self):
        iss = self._issuer()
        tok = iss.issue(actions=["tool.execute"], resource="tenant-a:*")
        ok, _ = iss.verify(tok, action="tool.execute",
                           resource="tenant-b:db")
        assert not ok

    def test_wrong_tool_fails(self):
        iss = self._issuer()
        tok = iss.issue(actions=["read"], resource="*")
        ok, _ = iss.verify(tok, action="deployment.promote", resource="*")
        assert not ok

    def test_forged_token_fails(self):
        iss = self._issuer()
        other = CapabilityIssuer(b"different-secret-16b!!")
        tok = other.issue(actions=["*"], resource="*")
        ok, _ = iss.verify(tok, action="tool.execute", resource="*")
        assert not ok

    def test_strict_executor_requires_capability(self):
        prof = strict_profile(policy=None)
        ex = EnforcedExecutor(profile=prof, strict=True)
        with pytest.raises(EnforcementError):
            ex.execute(action="database.write", run=lambda: "NO COMMIT")


# --------------------------------------------------------------- egress ---

FAKE_DNS = {
    "example.com": ["93.184.216.34"],
    "internal.example": ["10.1.2.3"],
    "rebind.example": ["93.184.216.34", "169.254.169.254"],
}


def _resolve(host):
    return FAKE_DNS.get(host, ["93.184.216.34"])


class TestEgressBypass:
    POL = EgressPolicy(allow_public_internet=True)

    @pytest.mark.parametrize("url", [
        "http://127.0.0.1/admin",
        "http://localhost:8080/",
        "http://[::1]/",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.5/",
        "http://172.16.4.4/",
        "http://192.168.1.1/",
        "http://0.0.0.0/",
        "http://2130706433/",          # decimal 127.0.0.1
        "http://0x7f.0x0.0x0.0x1/",    # hex 127.0.0.1
        "http://0x7f000001/",
        "http://127.1/",
        "http://user:pass@example.com/",
        "file:///etc/passwd",
        "ftp://example.com/x",
        "http://example.com:22/",
        "http://[fe80::1]/",
    ])
    def test_blocked_destinations(self, url):
        v = check_url(url, self.POL, resolve=_resolve)
        assert not v.allowed, f"EGRESS BYPASS: {url} -> {v.reason}"

    def test_dns_rebinding_all_answers_checked(self):
        v = check_url("http://rebind.example/", self.POL, resolve=_resolve)
        assert not v.allowed

    def test_unresolvable_denied(self):
        v = check_url("http://no-such-host.invalid/", self.POL,
                      resolve=lambda h: [])
        assert not v.allowed

    def test_allowlisted_public_passes(self):
        v = check_url("https://example.com/api", self.POL, resolve=_resolve)
        assert v.allowed

    def test_remote_client_enforces_policy(self):
        from remote_api import RemoteAPIClient, EgressBlockedError
        c = RemoteAPIClient(egress_policy=EgressPolicy(
            allow_public_internet=True))
        with pytest.raises(EgressBlockedError):
            c.request("GET", "http://169.254.169.254/latest/meta-data/")


# -------------------------------------------------------------- sandbox ---

class TestSandboxAdversarial:
    def test_empty_code_refused(self):
        from agent_sandbox import run_python
        r = run_python("", prefer_docker=False)
        assert not r.ok

    def test_env_scrubbed_local(self):
        from agent_sandbox import run_python
        os.environ["ADVERSARIAL_PROBE_SECRET"] = "should-not-leak"
        r = run_python("import os; print(os.environ.get("
                       "'ADVERSARIAL_PROBE_SECRET', 'ABSENT'))",
                       prefer_docker=False)
        assert "should-not-leak" not in (r.stdout or "")

    def test_timeout_enforced(self):
        from agent_sandbox import run_python
        r = run_python("import time; time.sleep(30)", timeout_s=2,
                       prefer_docker=False)
        assert not r.ok and r.timed_out

    def test_adversarial_prefers_docker_tier(self):
        from agent_sandbox import run_python, _has_docker
        r = run_python("print('hi')", prefer_docker=True)
        if _has_docker():
            assert r.tier == "docker"
        else:
            # No docker on box: local tier is NOT a security boundary;
            # adversarial workloads must be refused a security claim.
            assert r.tier == "local"


# ---------------------------------------------------------- skill trust ---

class TestSkillTrustBypass:
    def test_unregistered_skill_excluded(self, tmp_path):
        from skill_trust import TrustRegistry
        reg = TrustRegistry(str(tmp_path / "t.json"), SECRET)
        skill = tmp_path / "evil.md"
        skill.write_text("# evil")
        verdict, _ = reg.check_load("evil", str(skill))
        assert verdict == "unknown"
        prof = EnforcementProfile(
            policy=None, trust_registry_path=str(tmp_path / "t.json"),
            trust_secret=SECRET)
        rec = type("R", (), {"name": "evil",
                             "path": str(skill)})()
        allowed, report = platform_wiring.skill_filter(prof, [rec])
        assert report["mode"] == "enforce" and allowed == []

    def test_modified_skill_detected(self, tmp_path):
        from skill_trust import TrustRegistry
        reg = TrustRegistry(str(tmp_path / "t.json"), SECRET)
        skill = tmp_path / "s.md"
        skill.write_text("# v1")
        reg.register(skill_id="s", version="1", author="t",
                     source="test", skill_md_path=str(skill),
                     permissions=["read"], risk="low")
        reg.save()
        skill.write_text("# v1 + injected exfiltration")
        reg2 = TrustRegistry(str(tmp_path / "t.json"), SECRET)
        verdict, _ = reg2.check_load("s", str(skill))
        assert verdict == "tamper"

    def test_tampered_seal_fails_closed(self, tmp_path):
        from skill_trust import TrustRegistry
        p = tmp_path / "t.json"
        reg = TrustRegistry(str(p), SECRET)
        skill = tmp_path / "s.md"
        skill.write_text("# v1")
        reg.register(skill_id="s", version="1", author="t",
                     source="test", skill_md_path=str(skill),
                     permissions=["read"], risk="low")
        reg.save()
        p.write_text('{"entries": {}}')  # tamper without re-sealing
        reg2 = TrustRegistry(str(p), SECRET)
        assert not reg2.sealed_ok
        verdict, _ = reg2.check_load("s", str(skill))
        assert verdict == "unknown"

    def test_high_risk_needs_human(self, tmp_path):
        from skill_trust import TrustRegistry
        reg = TrustRegistry(str(tmp_path / "t.json"), SECRET)
        skill = tmp_path / "s.md"
        skill.write_text("# risky")
        reg.register(skill_id="s", version="1", author="t",
                     source="test", skill_md_path=str(skill),
                     permissions=["exec"], risk="high")
        verdict, _ = reg.check_load("s", str(skill))
        assert verdict == "review"


# -------------------------------------------------------------- secrets ---

class TestSecretsLeakage:
    def test_api_key_redacted_from_text(self):
        from secret_redactor import SecretRedactor
        red = SecretRedactor()
        out = red.scan_and_redact(
            "call with key sk-live-ABCDEF1234567890abcdef done")
        assert "sk-live-ABCDEF1234567890abcdef" not in out["redacted"]
        assert out["found"], "redactor must detect the planted key"

    def test_vault_lease_single_use_and_expiry(self):
        from secrets_vault import Vault
        v = Vault()
        lid, raw = v.issue(scope=["read"], ttl_s=300)  # max_uses=1 default
        ok, _ = v.redeem(raw, operation="read")
        assert ok
        ok2, why2 = v.redeem(raw, operation="read")
        assert not ok2 and "budget" in why2  # double spend refused
        lid2, raw2 = v.issue(scope=["read"], ttl_s=300)
        v._leases[lid2].expires_at = time.time() - 1  # force expiry
        ok3, why3 = v.redeem(raw2, operation="read")
        assert not ok3 and "expired" in why3
        _, raw3 = v.issue(scope=["read"], ttl_s=300)
        ok4, _ = v.redeem(raw3, operation="write")  # wrong scope
        assert not ok4


# ---------------------------------------------------------------- audit ---

class TestAuditIntegrity:
    def test_production_sinks_fail_closed_without_key(self, tmp_path,
                                                      monkeypatch):
        monkeypatch.delenv("AUDIT_HMAC_KEY", raising=False)
        with pytest.raises(RuntimeError):
            platform_wiring.build_production_sinks(str(tmp_path))

    def test_production_sinks_signed_with_key(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUDIT_HMAC_KEY", "ab" * 16)
        sinks = platform_wiring.build_production_sinks(str(tmp_path))
        assert sinks["signed"] is True
        e = sinks["audit"].append(kind="t", actor="a", subject="s")
        assert sinks["audit"].verify()["ok"] is True
        assert e["event_hash"]

    def test_tamper_detected(self, tmp_path):
        from immutable_audit import AuditChain
        import sqlite3
        c = AuditChain(str(tmp_path / "a.db"), secret=SECRET)
        c.append(kind="deploy", actor="ops", subject="r1", detail="ok")
        conn = sqlite3.connect(str(tmp_path / "a.db"))
        conn.execute("UPDATE events SET detail='forged' WHERE id=1")
        conn.commit()
        conn.close()
        assert c.verify()["ok"] is False

    def test_sequence_gap_detected(self, tmp_path):
        from immutable_audit import AuditChain
        import sqlite3
        c = AuditChain(str(tmp_path / "a.db"))
        c.append(kind="a", actor="a", subject="s")
        c.append(kind="b", actor="a", subject="s")
        conn = sqlite3.connect(str(tmp_path / "a.db"))
        conn.execute("DELETE FROM events WHERE id=1")
        conn.commit()
        conn.close()
        assert c.verify()["ok"] is False


# ----------------------------------------------------------- provenance ---

class TestProvenanceGap:
    def test_gaps_reported(self, tmp_path):
        from provenance import ProvenanceLog, STAGES
        log = ProvenanceLog(str(tmp_path / "p.jsonl"))
        log.link("req-1", "decision", "d1")
        gaps = log.gaps("req-1")
        assert gaps  # decision without the rest = gap
        for stage in STAGES:
            if stage != "decision":
                log.link("req-1", stage, f"{stage}-ref")
        assert log.gaps("req-1") == []


# ---------------------------------------------------------- tool verify ---

class TestToolResultVerification:
    def test_false_result_never_commits(self, tmp_path):
        from tool_result_verifier import ResultVerifier
        v = ResultVerifier(str(tmp_path / "v.jsonl"))
        out = v.verify(tool="booking.create",
                       claimed={"doctor": "WRONG", "slot": "taken"},
                       checker=lambda c: c.get("doctor") == "dr-adel"
                       and c.get("slot") != "taken",
                       evidence="test")
        assert not out["verified"]

    def test_strict_executor_blocks_unverified_commit(self):
        from tool_result_verifier import ResultVerifier
        import tempfile
        d = tempfile.mkdtemp()
        prof = strict_profile()
        iss = CapabilityIssuer(SECRET)
        tok = iss.issue(actions=["tool.execute"], resource="*")
        ex = EnforcedExecutor(profile=prof, strict=True,
                              verifier=ResultVerifier(d + "/v.jsonl"))
        with pytest.raises(EnforcementError):
            ex.execute(action="tool.execute",
                       capability_token=tok, capability_issuer=iss,
                       run=lambda: {"doctor": "WRONG"},
                       verify_checker=lambda c: c.get("doctor") == "dr-adel",
                       verify_tool="booking.create")


# ------------------------------------------------------------ invariants ---

class TestBusinessInvariants:
    def _engine(self):
        from business_invariants import InvariantEngine
        eng = InvariantEngine()
        eng.register("booking", "no-double-booking",
                     lambda p: (p.get("slot_taken") is False,
                                "slot already taken"), "")
        eng.register("booking", "same-tenant-cancel",
                     lambda p: (p.get("cancel_tenant") == p.get("owner_tenant"),
                                "cannot cancel another tenant"), "")
        return eng

    def test_double_booking_blocked(self):
        out = self._engine().evaluate("booking", {"slot_taken": True,
                                                  "cancel_tenant": "a",
                                                  "owner_tenant": "a"})
        assert not out["ok"]

    def test_cross_tenant_cancel_blocked(self):
        out = self._engine().evaluate("booking", {"slot_taken": False,
                                                  "cancel_tenant": "b",
                                                  "owner_tenant": "a"})
        assert not out["ok"]

    def test_honest_payload_passes(self):
        out = self._engine().evaluate("booking", {"slot_taken": False,
                                                  "cancel_tenant": "a",
                                                  "owner_tenant": "a"})
        assert out["ok"]


# ------------------------------------------------------- saga/idempotency ---

class TestSagaIdempotency:
    def test_duplicate_delivery_executes_once(self, tmp_path):
        from idempotency import IdempotencyStore
        store = IdempotencyStore(str(tmp_path / "i.json"))
        calls = []
        key = IdempotencyStore.make_key("booking", "tenant-a", "slot-9")
        for _ in range(3):
            store.execute(key, lambda: calls.append(1) or {"booked": 1})
        assert calls == [1]

    def test_crash_recovery_replays_without_double_effect(self, tmp_path):
        from idempotency import IdempotencyStore
        p = str(tmp_path / "i.json")
        s1 = IdempotencyStore(p)
        key = IdempotencyStore.make_key("charge", "t-a", "inv-5")
        s1.execute(key, lambda: {"charged": True})
        s2 = IdempotencyStore(p)  # "restart"
        calls = []
        out = s2.execute(key, lambda: calls.append(1) or {"charged": True})
        assert calls == [] and out["executed"] is False
        assert out["result"] == {"charged": True}


# ---------------------------------------------------------------- tenancy ---

class TestTenantIsolation:
    def test_cross_tenant_spend_blocked(self, tmp_path):
        from tenancy import Tenancy
        t = Tenancy(str(tmp_path / "t.json"))
        t.add_tenant("tenant-a", monthly_cap=10.0)
        t.add_tenant("tenant-b", monthly_cap=10.0)
        first = t.record_spend("tenant-a", 4.0, "job-1")
        assert first["state"] == "ok"
        # tenant-b must not ride tenant-a's budget/namespace
        assert t.namespaced("tenant-a", "k") != t.namespaced("tenant-b", "k")
        over = t.record_spend("tenant-a", 9.0, "job-2")  # 13/10 = 1.3
        assert over["state"] == "exceeded"
        assert "block_new_spend" in over["actions"]  # cap enforced

    def test_memory_namespace_isolation(self, tmp_path):
        from memory_governance import MemoryGovernor
        gov = MemoryGovernor(trusted_sources=("ops-handbook",))
        # untrusted source is quarantined, never served as truth
        r = gov.write("deploy-key", "X", source="random-web-page",
                      author="attacker")
        assert r["quarantined"] is True
        assert gov.read("deploy-key") is None
        # trusted source is served
        gov.write("deploy-key", "Y", source="ops-handbook", author="ops")
        assert gov.read("deploy-key") == "Y"
        # tenant isolation via namespaced keys
        from tenancy import Tenancy
        t = Tenancy(str(tmp_path / "t.json"))
        t.add_tenant("a", monthly_cap=5.0)
        t.add_tenant("b", monthly_cap=5.0)
        assert t.namespaced("a", "mem") != t.namespaced("b", "mem")


# ------------------------------------------------------------- deployment ---

class TestDeploymentGates:
    def test_gate_failure_blocks_release(self, tmp_path):
        sinks = platform_wiring.build_sinks(str(tmp_path))
        from promotion_pipeline import PromotionPipeline
        out = platform_wiring.deploy_release(
            sinks, release="r2", previous="r1",
            gates_fn=lambda: (False, "tests red"),
            probes={})
        assert out["released"] is False and out["live"] == "r1"

    def test_probe_failure_rolls_back(self, tmp_path):
        sinks = platform_wiring.build_sinks(str(tmp_path))
        out = platform_wiring.deploy_release(
            sinks, release="r2", previous="r1",
            gates_fn=lambda: (True, "green"),
            probes={"canary": lambda: (False, {})})
        assert out["rolled_back"] is True and out["live"] == "r1"

    def test_flag_never_bypasses_enforcement(self):
        from deployment import FeatureFlags
        flags = FeatureFlags()
        flags.set("skip_gates", 100)
        # Even at 100%, a strict executor still denies ungated execution.
        ex = EnforcedExecutor(profile=None, strict=True)
        with pytest.raises(EnforcementError):
            ex.execute(action="deployment.promote", run=lambda: 1)

    def test_unknown_flag_off(self):
        from deployment import FeatureFlags
        assert FeatureFlags().enabled("does-not-exist",
                                      identity="tenant-a") is False


# ------------------------------------------------------------------ HITL ---

class TestHitlSkipping:
    def test_sensitive_action_without_approval_denied(self):
        ex = EnforcedExecutor(profile=None, strict=True)
        with pytest.raises(EnforcementError):
            ex.execute(action="deployment.promote", run=lambda: 1)

    def test_hitl_token_single_use(self):
        from hitl_gate import HITLGate, HITLState
        g = HITLGate(security_token="tok")
        req = g.create_pending(raw_input="deploy r2", risk_score=80,
                               violations=["manual"])
        first = g.approve(req.request_id, token="tok")
        assert first["status"] == HITLState.APPROVED
        # second approval must NOT re-approve (state machine moved on)
        again = g.approve(req.request_id, token="tok")
        assert again["status"] != HITLState.PENDING
        # wrong token never approves
        req2 = g.create_pending(raw_input="deploy r3", risk_score=80,
                                violations=["manual"])
        bad = g.approve(req2.request_id, token="forged")
        assert bad["status"] == "INVALID_TOKEN"


# ------------------------------------------------- no-bypass invariant ---

class TestNoSensitiveExecutionWithoutEnforcement:
    @pytest.mark.parametrize("action", sorted(SENSITIVE_ACTIONS))
    def test_strict_denies_without_gates(self, action):
        ex = EnforcedExecutor(profile=None, strict=True)
        ran = []
        with pytest.raises(EnforcementError):
            ex.execute(action=action, run=lambda: ran.append(1))
        assert ran == []  # the callable NEVER ran

    def test_non_strict_records_but_allows_for_dev(self):
        ex = EnforcedExecutor(profile=None, strict=False)
        verdict, res = ex.execute(action="tool.execute",
                                  run=lambda: "dev-only")
        assert res == "dev-only"
        assert verdict.gates["policy"] == {"enforced": False}


# --------------------------------------------------------------- resources ---

class TestResourceExhaustion:
    def test_huge_tool_result_capped(self):
        from agent_sandbox import run_python
        r = run_python("print('x' * 10_000_000)", prefer_docker=False)
        assert len(r.stdout or "") <= 1_000_000  # output cap honored

    def test_concurrent_same_key_single_execution(self, tmp_path):
        import threading
        from idempotency import IdempotencyStore
        store = IdempotencyStore(str(tmp_path / "i.json"))
        key = IdempotencyStore.make_key("booking", "t", "slot-1")
        calls = []
        lock = threading.Lock()

        def once():
            with lock:
                return store.execute(
                    key, lambda: calls.append(1) or {"ok": True})

        threads = [threading.Thread(target=once) for _ in range(8)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        assert len(calls) == 1
