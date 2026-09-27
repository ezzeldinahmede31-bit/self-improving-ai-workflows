#!/usr/bin/env python3
"""Emergent Reasoning Cache — token-efficient caching layer for emergent-reasoning-edge.

Adds:
1. Search result caching (TTL-based, keyed by query hash)
2. Frame generation caching (keyed by problem hash)
3. Candidate generation caching
4. Cross-domain analogy caching
5. Falsification round result caching
6. Early exit conditions (stop when confidence > threshold)
7. Token budget tracking per session

Usage: import and use EmergentCache in emergent-reasoning-edge workflows
"""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional


class EmergentCache:
    """Persistent cache for emergent reasoning pipeline stages."""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir or "/home/ezzeldin/Documents/Default Project/memory/.emergent_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.token_budget = 50000  # per session
        self.tokens_used = 0
        self.session_log = self.cache_dir / f"session_{int(time.time())}.jsonl"
    
    def _hash(self, *parts: str) -> str:
        """Generate deterministic cache key from parts."""
        content = "|".join(parts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _cache_path(self, stage: str, key: str) -> Path:
        return self.cache_dir / f"{stage}_{key}.json"
    
    def _is_valid(self, path: Path) -> bool:
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text())
            return (time.time() - data.get("timestamp", 0)) < self.ttl
        except Exception:
            return False
    
    def get(self, stage: str, key: str) -> Optional[Any]:
        """Get cached value for stage/key if valid."""
        path = self._cache_path(stage, key)
        if self._is_valid(path):
            try:
                data = json.loads(path.read_text())
                self._log_access(stage, key, "hit")
                return data.get("value")
            except Exception:
                pass
        self._log_access(stage, key, "miss")
        return None
    
    def set(self, stage: str, key: str, value: Any, tokens: int = 0) -> None:
        """Cache value for stage/key with token cost tracking."""
        path = self._cache_path(stage, key)
        data = {
            "stage": stage,
            "key": key,
            "value": value,
            "tokens": tokens,
            "timestamp": time.time()
        }
        path.write_text(json.dumps(data))
        self.tokens_used += tokens
        self._log_access(stage, key, "set", tokens)
    
    def _log_access(self, stage: str, key: str, event: str, tokens: int = 0):
        """Log cache access for analysis."""
        log_entry = {
            "ts": time.time(),
            "stage": stage,
            "key": key[:32],
            "event": event,
            "tokens": tokens,
            "budget_used": self.tokens_used,
            "budget_remaining": self.token_budget - self.tokens_used
        }
        with self.session_log.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def check_budget(self, estimated_tokens: int) -> bool:
        """Check if we have budget for estimated tokens."""
        return (self.tokens_used + estimated_tokens) <= self.token_budget
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        hits = 0
        misses = 0
        sets = 0
        if self.session_log.exists():
            for line in self.session_log.read_text().splitlines():
                try:
                    entry = json.loads(line)
                    if entry["event"] == "hit":
                        hits += 1
                    elif entry["event"] == "miss":
                        misses += 1
                    elif entry["event"] == "set":
                        sets += 1
                except Exception:
                    pass
        return {
            "hits": hits,
            "misses": misses,
            "sets": sets,
            "hit_rate": hits / (hits + misses) if (hits + misses) > 0 else 0,
            "tokens_used": self.tokens_used,
            "budget_remaining": self.token_budget - self.tokens_used
        }
    
    # Stage-specific cache methods
    
    def get_search(self, query: str) -> Optional[dict]:
        """Get cached search results."""
        key = self._hash("search", query)
        return self.get("search", key)
    
    def set_search(self, query: str, results: dict, tokens: int) -> None:
        """Cache search results."""
        key = self._hash("search", query)
        self.set("search", key, results, tokens)
    
    def get_frames(self, problem: str) -> Optional[list[str]]:
        """Get cached problem frames."""
        key = self._hash("frames", problem)
        return self.get("frames", key)
    
    def set_frames(self, problem: str, frames: list[str], tokens: int) -> None:
        """Cache problem frames."""
        key = self._hash("frames", problem)
        self.set("frames", key, frames, tokens)
    
    def get_candidates(self, problem: str, frames: list[str]) -> Optional[list[dict]]:
        """Get cached candidate solutions."""
        key = self._hash("candidates", problem, "|".join(frames))
        return self.get("candidates", key)
    
    def set_candidates(self, problem: str, frames: list[str], candidates: list[dict], tokens: int) -> None:
        """Cache candidate solutions."""
        key = self._hash("candidates", problem, "|".join(frames))
        self.set("candidates", key, candidates, tokens)
    
    def get_analogy(self, candidate: str, domain: str) -> Optional[dict]:
        """Get cached cross-domain analogy."""
        key = self._hash("analogy", candidate, domain)
        return self.get("analogy", key)
    
    def set_analogy(self, candidate: str, domain: str, analogy: dict, tokens: int) -> None:
        """Cache cross-domain analogy."""
        key = self._hash("analogy", candidate, domain)
        self.set("analogy", key, analogy, tokens)
    
    def get_falsification(self, candidate: str, round_name: str) -> Optional[dict]:
        """Get cached falsification round result."""
        key = self._hash("falsify", candidate, round_name)
        return self.get("falsify", key)
    
    def set_falsification(self, candidate: str, round_name: str, result: dict, tokens: int) -> None:
        """Cache falsification round result."""
        key = self._hash("falsify", candidate, round_name)
        self.set("falsify", key, result, tokens)
    
    def should_early_exit(self, confidence: float, threshold: float = 0.85) -> bool:
        """Check if we should early exit based on confidence."""
        return confidence >= threshold


def create_optimized_emergent_pipeline(cache: EmergentCache) -> dict:
    """
    Returns the optimized pipeline config for emergent-reasoning-edge.
    This replaces the full 6-gate pipeline with cached/early-exit versions.
    """
    return {
        "gate_1_frames": {
            "cache": True,
            "estimate_tokens": 500,
            "early_exit_if_cached": True
        },
        "gate_2_candidates": {
            "cache": True,
            "estimate_tokens": 1500,
            "max_candidates": 4,  # reduced from 6
            "early_exit_if_cached": True
        },
        "gate_3_evidence": {
            "cache": True,
            "estimate_tokens": 2000,
            "max_sources_per_candidate": 2,  # reduced from unlimited
            "early_exit_if_cached": True
        },
        "gate_4_falsification": {
            "cache": True,
            "estimate_tokens": 2000,
            "rounds": ["red_team", "worst_idea", "pre_mortem"],  # council vote optional
            "council_vote": False,  # disabled by default for cost
            "early_exit_if_cached": True
        },
        "gate_5_synthesis": {
            "cache": False,  # synthesis is cheap
            "estimate_tokens": 500
        },
        "gate_6_log": {
            "cache": False,
            "estimate_tokens": 100
        },
        "global": {
            "token_budget": 50000,
            "early_exit_threshold": 0.85,
            "max_total_tokens": 8000,  # hard cap per invocation
            "skip_council_vote": True,  # major cost saver
            "max_candidates": 4,
            "max_sources_per_candidate": 2
        }
    }


# CLI for testing
if __name__ == "__main__":
    import sys
    cache = EmergentCache()
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        print(json.dumps(cache.get_stats(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "config":
        print(json.dumps(create_optimized_emergent_pipeline(cache), indent=2))
    else:
        print("Emergent Cache Ready")
        print(f"Cache dir: {cache.cache_dir}")
        print(f"Token budget: {cache.token_budget}")
        print("Usage: python emergent_cache.py [stats|config]")