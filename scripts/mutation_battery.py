"""Real file-mutation battery: neuter one control, run its tests, expect FAIL,
restore byte-identical. Exit 0 only if EVERY mutant is caught."""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = str(Path(__file__).resolve().parent.parent)
PY = ROOT + "/venv/bin/python"

MUTS = [
    {"id": "POLICY-DENY", "file": "platform_wiring.py",
     "old": 'return {"enforced": True, "allowed": decision.allowed,',
     "new": 'return {"enforced": True, "allowed": True,  # MUTANT',
     "tests": ["tests/test_p0a_policy.py", "tests/test_e2e_integration.py"]},
    {"id": "CAPABILITY", "file": "capability.py",
     "old": '        """Check a token against one proposed (action, resource) pair."""',
     "new": '        """Check a token against one proposed (action, resource) pair."""\n        return True, "ok"  # MUTANT',
     "tests": ["tests/test_p0a_capability.py",
               "tests/test_p0d_capability_matrix.py",
               "tests/test_p0d_enforced_egress.py"]},
    {"id": "EGRESS", "file": "egress_firewall.py",
     "old": "def _ip_blocked(ip: ipaddress._BaseAddress) -> str | None:",
     "new": "def _ip_blocked(ip: ipaddress._BaseAddress) -> str | None:\n    return None  # MUTANT",
     "tests": ["tests/test_p0a_egress.py", "tests/test_p0d_dns_ttl_pinned.py",
               "tests/test_p0d_remote_target_guard.py"]},
    {"id": "TENANCY", "file": "tenancy.py",
     "old": '        return f"t:{tid}:{key}"',
     "new": '        return str(key)  # MUTANT: no namespacing',
     "tests": ["tests/test_p1c_tenancy_privacy.py"]},
    {"id": "AUDIT", "file": "immutable_audit.py",
     "old": '        """Append one event. Returns {id, event_hash}."""',
     "new": '        """Append one event. Returns {id, event_hash}."""\n        return {"id": 1, "event_hash": "MUTANT"}  # MUTANT',
     "tests": ["tests/test_p0b_audit.py", "tests/test_p0d_audit_matrix.py"]},
    {"id": "HITL", "file": "hitl_gate.py",
     "old": '        if self._is_expired(req):',
     "new": '        return {"status": HITLState.APPROVED, "request_id": request_id}  # MUTANT\n        if self._is_expired(req):',
     "tests": ["tests/test_p0d_hitl_matrix.py", "tests/test_hitl_gate.py"]},
    {"id": "N8N", "file": "n8n_integration.py",
     "old": "        if not self.config.api_key and not os.environ.get(\"N8N_API_KEY\"):",
     "new": '        return {"ok": True, "status": "stable", "runs": [], "consecutive": 5, "attempts": 5, "details": "MUTANT"}  # MUTANT\n        if not self.config.api_key and not os.environ.get("N8N_API_KEY"):',
     "tests": ["tests/test_p0d_gap01_closures.py"]},
    {"id": "SANDBOX", "file": "agent_sandbox.py",
     "old": '    """Execute a Python snippet under the strongest available tier."""',
     "new": '    """Execute a Python snippet under the strongest available tier."""\n    return SandboxResult(True, "mutant", 0, "pwned", "")  # MUTANT',
     "tests": ["tests/test_p0a_sandbox.py"]},
]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run_tests(tests):
    r = subprocess.run([PY, "-m", "pytest", "-q", "--tb=no",
                        "-p", "no:cacheprovider"] + tests,
                       cwd=ROOT, capture_output=True, text=True, timeout=600)
    return r.returncode


def main():
    failures = []
    for m in MUTS:
        path = f"{ROOT}/{m['file']}"
        before = sha(path)
        src = open(path).read()
        if m["old"] not in src:
            print(f"[{m['id']}] ANCHOR MISSING — abort, file untouched")
            failures.append((m["id"], "anchor-missing"))
            continue
        open(path, "w").write(src.replace(m["old"], m["new"], 1))
        try:
            rc = run_tests(m["tests"])
            caught = rc != 0
            print(f"[{m['id']}] mutant -> tests exit={rc} "
                  f"{'CAUGHT' if caught else 'NOT CAUGHT — TEST GAP'}")
            if not caught:
                failures.append((m["id"], "test-gap"))
        finally:
            open(path, "w").write(src)  # restore
        after = sha(path)
        if after != before:
            print(f"[{m['id']}] RESTORE MISMATCH!")
            failures.append((m["id"], "restore-mismatch"))
        else:
            print(f"[{m['id']}] restored byte-identical")
    print()
    if failures:
        print("MUTATION FAILURES:", failures)
        return 1
    print("ALL 8 MUTANTS CAUGHT, all files restored byte-identical")
    return 0


sys.exit(main())
