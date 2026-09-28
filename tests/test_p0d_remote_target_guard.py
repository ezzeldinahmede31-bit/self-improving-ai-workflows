"""Regression: legacy RemoteAPIClient refuses direct non-global targets."""

import pytest

from remote_api import EgressBlockedError, MockRouter, RemoteAPIClient


def test_direct_private_targets_blocked_without_policy():
    c = RemoteAPIClient(router=MockRouter())
    for url in ("http://127.0.0.1:9000/x", "http://10.0.0.5/x",
                "http://0x7f000001/x", "http://2130706433/x",
                "http://169.254.169.254/latest/meta-data/"):
        with pytest.raises(EgressBlockedError):
            c.request("GET", url)


def test_mock_routed_target_still_resolves():
    r = MockRouter(mappings={"api.example.com": "http://127.0.0.1:9000"})
    assert r.resolve("https://api.example.com/v1") == \
        "http://127.0.0.1:9000/v1"
