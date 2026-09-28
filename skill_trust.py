"""Skill trust registry: identity, version, hash, permissions, risk.

Every skill the platform loads must resolve to a registry entry carrying
id, version, author/source, sha256 of SKILL.md, permission allow-list,
risk tier, HMAC signature, and last-verified stamp. The registry file
itself is HMAC-sealed (separate .hmac sidecar); a failed seal fails
closed to an empty registry — unknown skills never load as trusted.

Risk tiers: low / medium / high. Loading policy: low loads freely,
medium loads with a logged note, high requires explicit human approval
(the caller enforces the approval; this module reports the tier).

Only stdlib is used. Storage is a JSON file pair chosen by the caller
(defaults keep platform state out of git-ignored scratch).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

RISKS = ("low", "medium", "high")


@dataclass
class TrustEntry:
    skill_id: str
    version: str
    author: str
    source: str
    sha256: str
    permissions: list[str]
    risk: str
    last_verified: float
    signature: str = ""


class TrustRegistry:
    """HMAC-sealed per-skill trust store."""

    def __init__(self, path: str, secret: bytes):
        if not isinstance(secret, bytes) or len(secret) < 16:
            raise ValueError("secret must be bytes of 16+ bytes")
        self._path = Path(path)
        self._secret = secret
        self._entries: dict[str, TrustEntry] = {}
        self._sealed_ok = False
        self._load()

    def _seal(self, raw: bytes) -> str:
        return hmac.new(self._secret, raw, hashlib.sha256).hexdigest()

    def _hmac_path(self) -> Path:
        return self._path.with_suffix(self._path.suffix + ".hmac")

    def _load(self) -> None:
        if not self._path.is_file():
            self._sealed_ok = True  # empty registry is a valid start
            return
        try:
            raw = self._path.read_bytes()
            want = self._hmac_path().read_text(encoding="utf-8").strip()
        except OSError:
            return  # fail closed: entries stay empty
        if not hmac.compare_digest(self._seal(raw), want):
            return  # tamper: fail closed
        try:
            data = json.loads(raw.decode("utf-8"))
        except ValueError:
            return
        for sid, item in (data.get("entries", {}) or {}).items():
            try:
                self._entries[str(sid)] = TrustEntry(**item)
            except TypeError:
                continue
        self._sealed_ok = True

    def save(self) -> None:
        """Persist entries + refresh the seal (creates parent dirs)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps({"entries": {k: asdict(v) for k, v in
                                      self._entries.items()}},
                         sort_keys=True, indent=1).encode("utf-8")
        self._path.write_bytes(raw)
        self._hmac_path().write_text(self._seal(raw), encoding="utf-8")
        self._sealed_ok = True

    @property
    def sealed_ok(self) -> bool:
        """False means the store failed verification (treat all unknown)."""
        return self._sealed_ok

    @staticmethod
    def hash_skill(skill_md_path: str) -> str:
        """sha256 over raw SKILL.md bytes."""
        h = hashlib.sha256()
        with open(skill_md_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def register(self, *, skill_id: str, version: str, author: str,
                 source: str, skill_md_path: str, permissions: list[str],
                 risk: str) -> TrustEntry:
        """Add or refresh an entry (re-hashes the file, re-stamps time)."""
        if risk not in RISKS:
            raise ValueError(f"risk must be one of {RISKS}")
        entry = TrustEntry(
            skill_id=str(skill_id), version=str(version),
            author=str(author), source=str(source),
            sha256=self.hash_skill(skill_md_path),
            permissions=[str(p) for p in permissions], risk=risk,
            last_verified=time.time())
        entry.signature = hmac.new(
            self._secret,
            f"{entry.skill_id}|{entry.version}|{entry.sha256}".encode(),
            hashlib.sha256).hexdigest()
        self._entries[entry.skill_id] = entry
        return entry

    def check_load(self, skill_id: str, skill_md_path: str) -> tuple[str, str]:
        """Verdict for loading a skill: ok / review / unknown / tamper."""
        entry = self._entries.get(str(skill_id))
        if entry is None or not self._sealed_ok:
            return "unknown", "no trust entry"
        try:
            current = self.hash_skill(skill_md_path)
        except OSError:
            return "unknown", "skill file unreadable"
        if not hmac.compare_digest(current, entry.sha256):
            return "tamper", "file hash differs from registry"
        if entry.risk == "high":
            return "review", "high-risk skill needs human approval"
        if entry.risk == "medium":
            return "ok", "medium risk noted in audit"
        return "ok", "low risk"
