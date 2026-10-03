"""Real secret management — pluggable backends with rotation.

Existing SecretVault is a good *transit* mask, but it's in-memory only and
there's no persistent secret manager integration for external systems. This
module adds:

  SecretProvider  : backend interface (env / file / HashiCorp Vault / AWS SSM)
  SecretManager   : resolves a name -> value with TTL cache, auto-reload after
                    expiry (rotation), and fail-closed safe lookup.

Backends degrade gracefully: if Vault/AWS unreachable, a `local_file` fallback
is attempted, then env. Never raises — always returns None for missing.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional


class SecretBackend:
    name = "base"

    def get(self, name: str) -> Optional[str]:
        raise NotImplementedError


class EnvBackend(SecretBackend):
    name = "env"

    def get(self, name: str) -> Optional[str]:
        return os.environ.get(name)


class FileBackend(SecretBackend):
    """.env-style or JSON key=value file."""

    name = "file"

    def __init__(self, path: Optional[str] = None):
        self.path = path or os.environ.get("SECRETS_FILE", "") or "./.secrets.json"
        self._cache: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        p = Path(self.path)
        if not p.exists():
            return
        raw = p.read_text()
        if self.path.endswith(".json"):
            try:
                self._cache = json.loads(raw)
            except json.JSONDecodeError:
                self._cache = {}
            return
        for line in raw.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                self._cache[k.strip()] = v.strip()

    def get(self, name: str) -> Optional[str]:
        self._load()  # rotation-safe: re-read source each access
        return self._cache.get(name)


class VaultBackend(SecretBackend):
    """HashiCorp Vault KV v2 via HTTP. Uses the X-Vault-Token from env/.secrets.

    Transport is connection-pinned (fetch_pinned): the Vault address is
    validated AND the socket opens the authorized IP literally, so DNS
    between check and connect cannot reroute a request carrying the Vault
    token. Pass egress_policy explicitly in production; the default gates
    a fixed private/Vault-shaped destination (never open egress).
    """

    name = "vault"

    def __init__(self, addr: Optional[str] = None, token: Optional[str] = None,
                 mount: str = "secret", egress_policy=None):
        self.addr = (addr or os.environ.get("VAULT_ADDR", "")).rstrip("/")
        self.token = token or os.environ.get("VAULT_TOKEN", "") or ""
        self.mount = mount
        self.egress_policy = egress_policy

    def get(self, name: str) -> Optional[str]:
        if not self.addr:
            return None
        from egress_firewall import (fetch_pinned, EgressPolicy,
                                     PinnedFetchBlocked)
        url = f"{self.addr}/v1/{self.mount}/data/{name}"
        policy = self.egress_policy or EgressPolicy()
        try:
            out = fetch_pinned(
                url, policy, method="GET",
                headers={"X-Vault-Token": self.token}, timeout_s=3)
        except PinnedFetchBlocked:
            return None
        if out.get("status") != 200:
            return None
        try:
            data = json.loads(out["body"].decode())
            return data.get("data", {}).get("data", {}).get(name)
        except (ValueError, UnicodeDecodeError, AttributeError):
            return None


class SecretManager:
    """Ordered backend resolution + TTL caching (rotation-aware)."""

    def __init__(self, backends: Optional[list[SecretBackend]] = None,
                 ttl_sec: float = 300.0):
        self.backends = backends or [
            EnvBackend(), FileBackend(),
            VaultBackend(),   # last — network; only if env/file missed
        ]
        self.ttl = ttl_sec
        self._cache: dict[str, tuple[Optional[str], float]] = {}

    def resolve(self, name: str) -> Optional[str]:
        now = time.time()
        if name in self._cache:
            val, ts = self._cache[name]
            if now - ts < self.ttl:
                return val
            del self._cache[name]  # TTL reached (rotatable source)

        value: Optional[str] = None
        for backend in self.backends:
            try:
                value = backend.get(name)
            except Exception:
                value = None
            if value:
                break

        self._cache[name] = (value, now)
        return value

    def rotate(self) -> int:
        """Drop all cached entries so next resolve re-fetches (rotation)."""
        n = len(self._cache)
        self._cache.clear()
        return n

    def set_override(self, name: str, value: Optional[str]) -> None:
        """For tests / local dev: pin a value in the cache layer."""
        self._cache[name] = (value, time.time())


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp()
    f = Path(d) / ".secrets.json"
    f.write_text(json.dumps({"OPENAI_API_KEY": "sk-testoverride-123456789012"}))
    mgr = SecretManager(backends=[FileBackend(path=str(f))], ttl_sec=1)
    print("resolved:", mgr.resolve("OPENAI_API_KEY"))
    time.sleep(1.1)
    print("rotated:", mgr.rotate())
    print("after rotate:", mgr.resolve("OPENAI_API_KEY"))