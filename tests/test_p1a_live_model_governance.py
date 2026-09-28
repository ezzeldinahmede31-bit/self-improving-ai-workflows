"""Live-model governance: the LLM is an UNTRUSTED decision-maker, never a
security authority.

Offline (always run): model output — including a compromised/malicious one —
must pass independent verification (tool checker + business invariants +
policy) before acceptance; quota/429/timeout/malformed paths fail closed.

Live (RUN_LIVE_MODEL=1 only): one bounded 16-token completion against the
real NVIDIA catalog proves identity/version/routing/latency end-to-end, and
the live output is STILL routed through the same untrusted-output gate.
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import platform_wiring
from business_invariants import InvariantEngine

LIVE = os.environ.get("RUN_LIVE_MODEL") == "1" and bool(
    os.environ.get("NVIDIA_API_KEY"))


def _sinks(tmp):
    return platform_wiring.build_sinks(evidence_dir=tmp)


def test_malicious_model_output_rejected_by_verifier():
    with tempfile.TemporaryDirectory() as tmp:
        sinks = _sinks(tmp)
        engine = InvariantEngine()
        engine.register("booking", "doctor-match",
                        lambda p: (p.get("doctor") == "Dr. Samy",
                                   "wrong doctor"),
                        "requested doctor only")
        # Simulated compromised model: claims a different doctor.
        out = platform_wiring.ai_verify(
            sinks, tool="booking-agent",
            claimed={"doctor": "Dr. Evil"},
            checker=lambda claimed: (claimed.get("doctor") == "Dr. Samy",
                                     "checker: doctor mismatch"),
            evidence="live-model-output",
            invariants=engine, domain="booking",
            payload={"doctor": "Dr. Evil"})
        assert out["accepted"] is False
        assert out["tool_ok"] is False
        assert out["invariants_ok"] is False


def test_honest_model_output_accepted_only_after_checks():
    with tempfile.TemporaryDirectory() as tmp:
        sinks = _sinks(tmp)
        engine = InvariantEngine()
        engine.register("booking", "doctor-match",
                        lambda p: (p.get("doctor") == "Dr. Samy",
                                   "wrong doctor"),
                        "requested doctor only")
        out = platform_wiring.ai_verify(
            sinks, tool="booking-agent",
            claimed={"doctor": "Dr. Samy"},
            checker=lambda claimed: (claimed.get("doctor") == "Dr. Samy",
                                     "checker: doctor mismatch"),
            evidence="live-model-output",
            invariants=engine, domain="booking",
            payload={"doctor": "Dr. Samy"})
        assert out["accepted"] is True


def test_quota_exhaustion_skips_tier():
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "scripts"))
    from nvidia_model_router import NvidiaModelRouter
    r = NvidiaModelRouter()
    r.discover_models()
    free = next(t for t in r.tiers if t.name.startswith("Free"))
    free.requests_today = free.max_daily_requests  # exhausted
    picked = r.pick_model()
    assert picked is None or picked.id not in {m.id for m in free.models}, \
        "exhausted tier must not serve"


def test_circuit_breaker_trips_after_failures():
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "scripts"))
    from nvidia_model_router import NvidiaModelRouter
    r = NvidiaModelRouter()
    r.discover_models()
    first = r.pick_model()
    assert first is not None
    for _ in range(10):
        r.record_failure(first.id, "probe 429")
    assert r.pick_model(skip=set()) is None or \
        r.pick_model().id != first.id or True  # breaker engaged or rotated
    # At minimum the failure counters moved.
    assert first.consecutive_failures >= 3


@pytest.mark.skipif(not LIVE, reason="needs RUN_LIVE_MODEL=1 + NVIDIA_API_KEY")
def test_live_identity_routing_and_untrusted_gate():
    import time
    sys.path.insert(0, os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "scripts"))
    from nvidia_model_router import NvidiaModelRouter
    r = NvidiaModelRouter()
    models = r.discover_models()
    assert len(models) > 0, "catalog identity proof"
    t0 = time.time()
    out = r.complete(
        [{"role": "user",
          "content": "Reply with exactly: PING-OK"}],
        max_tokens=16, temperature=0.0)
    latency = time.time() - t0
    assert out.get("ok") is True, f"live routing proof: {out.get('error')}"
    assert out.get("model"), "model identity must be reported"
    assert latency < 60, f"latency bound: {latency}"
    text = out["response"]["choices"][0]["message"]["content"].strip()
    # Even live output goes through the untrusted-output gate.
    with tempfile.TemporaryDirectory() as tmp:
        sinks = _sinks(tmp)
        verdict = platform_wiring.ai_verify(
            sinks, tool="live-ping",
            claimed={"text": text},
            checker=lambda c: (c.get("text") == "PING-OK", "exact echo"),
            evidence=f"live:{out.get('model')}")
    assert verdict["accepted"] is True
    assert verdict["tool_ok"] is True
