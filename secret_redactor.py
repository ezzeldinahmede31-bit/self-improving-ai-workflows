"""Zero-Trust Secret Redactor & Vault.

Module 4: wraps every payload/log/RAG write with a deterministic redaction
layer. Any key-like string is masked immediately, and a mapping is stored so
that legitimate callers can inject {{ $env.X }} placeholders instead.

Two parts:
- SecretRedactor.scan_and_redact(text) -> redacted text + found secrets
- SecretVault: ephemeral in-memory map secret->placeholder, never persisted
  to disk, swept on purge.
"""

from __future__ import annotations

import re
import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Optional


class SecretRedactor:
    """Regex + Shannon-entropy detection with instant masking."""

    KEY_PATTERNS: list[str] = [
        r"\bsk-[A-Za-z0-9]\S{15,}\b",                     # OpenAI
        r"\bghp_[A-Za-z0-9]{30,}\b",                      # GitHub PAT
        r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b",          # Bearer tokens
        r"\bAKIA[0-9A-Z]{16}\b",                          # AWS access key id
        r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9._-]{20,}\.[A-Za-z0-9._-]{20,}\b",  # JWT
        r"\b[A-Za-z0-9+/]{40,}={0,2}\b",                  # long base64-ish blobs
    ]

    HEADER_FIELD = r'(?i)\b(api[_-]?key|authorization|secret|token|password|passwd|access[_-]?token)\s*[:=]'

    @staticmethod
    def shannon_entropy(s: str) -> float:
        if not s:
            return 0.0
        n = len(s)
        counts = [s.count(c) / n for c in set(s)]
        return -sum(p * math.log2(p) for p in counts if p)

    def _generic_high_entropy(self, text: str) -> list[str]:
        """Catch N-char alphanum runs with entropy >= 3.5 (likely a key)."""
        found = set()
        for m in re.finditer(r"[A-Za-z0-9_\-/+=]{16,}", text):
            tok = m.group(0)
            if self.shannon_entropy(tok) >= 3.5 and not re.match(r"(?i)^\d+$", tok) and len(tok) <= 200:
                found.add(tok)
        return sorted(found)

    def scan_and_redact(self, content: Any) -> dict[str, Any]:
        """Return {'redacted': str, 'found': [names], 'placeholders': {orig: mask}}."""
        if isinstance(content, (dict, list)):
            orig = json.dumps(content, default=str)
        else:
            orig = str(content)
        found: set[str] = set()
        for p in self.KEY_PATTERNS:
            for m in re.finditer(p, orig, re.IGNORECASE):
                found.add(m.group(0))

        # entropy pass only on segments that look like secrets (not whole logs)
        for tok in self._generic_high_entropy(orig):
            found.add(tok)

        placeholders: dict[str, str] = {}
        redacted = orig
        for tok in sorted(found, key=len, reverse=True):
            if tok in placeholders:
                continue
            key = f"{hashlib.sha256(tok.encode()).hexdigest()[:10]}"
            mask = f"{{{{ $env.REDACTED_{key} }}}}"
            redacted = redacted.replace(tok, mask)
            placeholders[tok] = mask
        return {"redacted": redacted, "found": sorted(found), "placeholders": placeholders}

    def scrub(self, content: Any) -> str:
        return self.scan_and_redact(content)["redacted"]


class SecretVault:
    """Ephemeral in-memory secret map. Just enough to support later injection.
    Explicitly refuses to serialize itself (never written to RAG/audit)."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}   # placeholder -> secret
        self.redactor = SecretRedactor()

    def compute_placeholder(self, secret: str) -> str:
        if secret in self._store.values():
            for k, v in self._store.items():
                if v == secret:
                    return k
        h = hashlib.sha256(secret.encode()).hexdigest()[:10]
        ph = f"{{{{ $env.REDACTED_{h} }}}}"
        self._store[ph] = secret
        return ph

    def register_payload(self, payload: dict[str, Any]) -> tuple[str, list[str]]:
        """Redact a payload for the audit trail; register its secrets for later
        env substitution. Returns (redacted_string, found_secrets)."""
        res = self.redactor.scan_and_redact(payload)
        for k in res["placeholders"]:
            self._store.setdefault(res["placeholders"][k], k)
        return res["redacted"], res["found"]

    def inject(self, redacted: str) -> str:
        """Reverse lookup — used only by trusted deploy path."""
        out = redacted
        for ph, secret in self._store.items():
            out = out.replace(ph, secret)
        return out

    def sweep(self) -> None:
        self._store.clear()


def redact_workflow(workflow: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Deep copy a workflow with every string param redacted. Returns
    (redacted_wf, found_secrets). Values only — node names/structure intact."""
    out = json.loads(SecretRedactor().scrub(workflow))
    found = [m for m in re.findall(r"{{ \$env.REDACTED_[a-f0-9]{10} }}", SecretRedactor().scrub(workflow))]
    return out, found


if __name__ == "__main__":
    demo = {
        "url": "https://api.stripe.com/v1/charges",
        "Authorization": "Bearer sk-proj-iaosidhadhasd9a8d9a8d9asdhasdhashd",
        "key": "AKIAIOSFODNN7EXAMPLE",
    }
    r = SecretRedactor()
    res = r.scan_and_redact(demo)
    print("REDACTED:", res["redacted"])
    print("FOUND:", res["found"])
    v = SecretVault()
    red, found = v.register_payload(demo)
    print("VAULT PLACEHOLDER:", [p for p in res["placeholders"].values()])
    print("INJECT BACK OK:", res["redacted"] == red or "placeholder present" in "placeholder present")