"""Dependency drift: pinned baseline vs live environment.

A change in a package or image is a change in the product. pin()
freezes {name: version} (+ optional image digests); check(live)
diffs against the freeze and classifies added / removed / upgraded /
downgraded; verdict() demands rescan + retest when anything security-
relevant moved (major bump, removal, or unknown addition). Consumes
supply_chain.python_sbom() output directly.

Only stdlib is used. No network calls.
"""

from __future__ import annotations

import time


def _major(version: str) -> str:
    return str(version).split(".")[0]


class DependencyDrift:
    """Pinned baseline with classified diffs and retest verdicts."""

    def __init__(self):
        self._pinned: dict[str, str] = {}
        self._pinned_at: float = 0.0
        self._images: dict[str, str] = {}

    def pin(self, packages: dict, images: dict | None = None) -> dict:
        """Freeze a baseline ({name: version}, {image: digest})."""
        self._pinned = {str(k): str(v) for k, v in (packages or {}).items()}
        self._images = {str(k): str(v) for k, v in (images or {}).items()}
        self._pinned_at = time.time()
        return {"pinned": len(self._pinned), "images": len(self._images)}

    def check(self, live_packages: dict,
              live_images: dict | None = None) -> dict:
        """Diff live state vs baseline with classified changes."""
        live = {str(k): str(v) for k, v in (live_packages or {}).items()}
        added = sorted(set(live) - set(self._pinned))
        removed = sorted(set(self._pinned) - set(live))
        upgraded, downgraded, same = [], [], 0
        for name in set(live) & set(self._pinned):
            if live[name] == self._pinned[name]:
                same += 1
            elif _major(live[name]) != _major(self._pinned[name]):
                (upgraded if live[name] > self._pinned[name]
                 else downgraded).append(
                    {"name": name, "was": self._pinned[name],
                     "now": live[name], "major_change": True})
            else:
                upgraded.append({"name": name, "was": self._pinned[name],
                                 "now": live[name], "major_change": False})
        limg = {str(k): str(v) for k, v in (live_images or {}).items()}
        img_changed = sorted(n for n, d in limg.items()
                             if self._images.get(n) != d)
        return {"added": added, "removed": removed, "upgraded": upgraded,
                "downgraded": downgraded, "same": same,
                "images_changed": img_changed}

    def verdict(self, diff: dict) -> dict:
        """Retest demand: major moves, removals, additions, image swaps."""
        security_relevant = bool(
            diff.get("removed") or diff.get("added")
            or [u for u in diff.get("upgraded", [])
                if u.get("major_change")]
            or diff.get("downgraded") or diff.get("images_changed"))
        actions = (["rescan", "retest", "review"] if security_relevant
                   else ["log"])
        return {"drifted": bool(
                    diff.get("added") or diff.get("removed")
                    or diff.get("upgraded") or diff.get("downgraded")
                    or diff.get("images_changed")),
                "security_relevant": security_relevant, "actions": actions}
