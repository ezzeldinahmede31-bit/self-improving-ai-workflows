#!/usr/bin/env python3
"""NVIDIA Model Router — auto-discovery, health checks, and tiered failover.

Implements the litellm-tier-router skill for NVIDIA NIM models:
- Auto-discovers available models from NVIDIA catalog
- Health checks each model before use
- 3-tier fallback: Free/Routine → Standard → Frontier
- Circuit breaker on failures
- Quota tracking per tier
- Zero-downtime model rotation when models go 410 GONE
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_CATALOG_URL = "https://integrate.api.nvidia.com/v1/models"
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


@dataclass
class NvidiaModel:
    """NVIDIA NIM model with metadata."""
    id: str
    name: str
    owned_by: str
    context_window: int = 4096
    max_output: int = 1024
    tier: str = "standard"  # free, standard, frontier
    cost_per_1k: float = 0.0
    healthy: bool = True
    last_check: float = 0
    consecutive_failures: int = 0
    last_latency_ms: float = 0.0


@dataclass
class ModelTier:
    """A tier of models with fallback semantics."""
    name: str
    models: list[NvidiaModel]
    max_daily_requests: int = 1000
    requests_today: int = 0
    circuit_open_until: float = 0
    breaker_threshold: int = 3
    breaker_timeout: float = 60.0


class NvidiaModelRouter:
    """
    Auto-discovers NVIDIA models, organizes into tiers, and routes requests
    with automatic failover and health monitoring.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        self.api_key = api_key or NVIDIA_API_KEY
        self.cache_dir = Path(cache_dir or "/home/ezzeldin/Documents/Default Project/memory/.nvidia_models")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_cache_file = self.cache_dir / "models.json"
        self.tiers: list[ModelTier] = []
        self.current_tier_idx = 0
        self.request_log = self.cache_dir / "requests.jsonl"
        self._load_cached_models()
    
    def _load_cached_models(self) -> None:
        """Load cached model list from disk."""
        if self.model_cache_file.exists():
            try:
                data = json.loads(self.model_cache_file.read_text())
                if time.time() - data.get("timestamp", 0) < 3600:  # 1h cache
                    self._rebuild_tiers(data["models"])
                    return
            except Exception:
                pass
        # No valid cache - will discover on first request
        self.tiers = []
    
    def _save_model_cache(self, models: list[dict]) -> None:
        """Save model list to cache."""
        self.model_cache_file.write_text(json.dumps({
            "timestamp": time.time(),
            "models": models
        }))
    
    def discover_models(self, force: bool = False) -> list[NvidiaModel]:
        """Discover available models from NVIDIA catalog."""
        if not force and self.tiers:
            # Flatten tiers
            all_models = []
            for tier in self.tiers:
                all_models.extend(tier.models)
            if all_models:
                return all_models
        
        if not self.api_key:
            return self._get_fallback_models()
        
        try:
            req = urllib.request.Request(
                NVIDIA_CATALOG_URL,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
            
            models = []
            for m in data.get("data", []):
                model_id = m.get("id", "")
                # Classify by model name patterns
                tier = self._classify_tier(model_id)
                cost = self._estimate_cost(model_id, tier)
                
                models.append(NvidiaModel(
                    id=model_id,
                    name=m.get("id", ""),
                    owned_by=m.get("owned_by", "nvidia"),
                    context_window=m.get("context_length", 4096),
                    max_output=m.get("max_tokens", 1024),
                    tier=tier,
                    cost_per_1k=cost
                ))
            
            # Cache the raw data
            self._save_model_cache([{
                "id": m.id, "name": m.name, "owned_by": m.owned_by,
                "context_window": m.context_window, "max_output": m.max_output,
                "tier": m.tier, "cost_per_1k": m.cost_per_1k
            } for m in models])
            
            self._rebuild_tiers(models)
            return models
            
        except Exception as e:
            print(f"Model discovery failed: {e}, using fallbacks")
            return self._get_fallback_models()
    
    def _classify_tier(self, model_id: str) -> str:
        """Classify model into tier based on name patterns."""
        model_lower = model_id.lower()
        # Free tier indicators
        if any(x in model_lower for x in ["free", "nemotron-3-ultra", "llama-3.1", "llama-3.2"]):
            return "free"
        # Frontier tier indicators
        if any(x in model_lower for x in ["nemotron-3-ultra", "nemotron-4", "llama-3.3-70b", "llama-3.3-nemotron"]):
            return "frontier"
        return "standard"
    
    def _estimate_cost(self, model_id: str, tier: str) -> float:
        """Estimate cost per 1k tokens based on tier."""
        costs = {"free": 0.0, "standard": 0.001, "frontier": 0.01}
        return costs.get(tier, 0.001)
    
    def _get_fallback_models(self) -> list[NvidiaModel]:
        """Hardcoded fallback models when API unavailable."""
        fallbacks = [
            NvidiaModel("nvidia/nemotron-3-ultra-free", "Nemotron 3 Ultra Free", "nvidia", 
                       tier="free", cost_per_1k=0.0),
            NvidiaModel("nvidia/llama-3.3-nemotron-super-49b-v1", "Nemotron Super 49B", "nvidia",
                       tier="frontier", cost_per_1k=0.008),
            NvidiaModel("nvidia/nemotron-3.5-lightning-30b-a3b", "Nemotron Lightning 30B", "nvidia",
                       tier="standard", cost_per_1k=0.001),
            NvidiaModel("nvidia/llama-3.1-nemotron-70b-instruct", "Nemotron 70B Instruct", "nvidia",
                       tier="standard", cost_per_1k=0.001),
        ]
        self._rebuild_tiers(fallbacks)
        return fallbacks
    
    def _rebuild_tiers(self, models: list[NvidiaModel]) -> None:
        """Organize models into tiers."""
        tier_map = {"free": [], "standard": [], "frontier": []}
        for m in models:
            tier_map[m.tier].append(m)
        
        self.tiers = [
            ModelTier("Free/Routine", tier_map["free"], max_daily_requests=500),
            ModelTier("Standard", tier_map["standard"], max_daily_requests=200),
            ModelTier("Frontier", tier_map["frontier"], max_daily_requests=50),
        ]
        # Filter empty tiers
        self.tiers = [t for t in self.tiers if t.models]
        self.current_tier_idx = 0
    
    def pick_model(self, prefer_tier: Optional[str] = None, 
                   skip: Optional[set[str]] = None) -> Optional[NvidiaModel]:
        """Pick the best available model with failover logic."""
        skip = skip or set()
        
        # Determine starting tier
        start_idx = 0
        if prefer_tier:
            for i, t in enumerate(self.tiers):
                if t.name.lower().startswith(prefer_tier.lower()):
                    start_idx = i
                    break
        
        # Try each tier in order
        for tier_idx in range(start_idx, len(self.tiers)):
            tier = self.tiers[tier_idx]
            
            # Check circuit breaker
            if time.time() < tier.circuit_open_until:
                continue
            
            # Check quota
            if tier.requests_today >= tier.max_daily_requests:
                continue
            
            # Find healthy model in tier
            for model in tier.models:
                if model.id in skip:
                    continue
                if not model.healthy:
                    continue
                if time.time() < tier.circuit_open_until:
                    continue
                return model
        
        return None
    
    def record_success(self, model_id: str, latency_ms: float) -> None:
        """Record successful request."""
        for tier in self.tiers:
            for model in tier.models:
                if model.id == model_id:
                    model.consecutive_failures = 0
                    model.last_latency_ms = latency_ms
                    model.healthy = True
                    model.last_check = time.time()
                    tier.requests_today += 1
                    self._log_request(model_id, True, latency_ms)
                    return
    
    def record_failure(self, model_id: str, error: str = "") -> None:
        """Record failed request and potentially trip circuit breaker."""
        for tier in self.tiers:
            for model in tier.models:
                if model.id == model_id:
                    model.consecutive_failures += 1
                    model.last_check = time.time()
                    if model.consecutive_failures >= tier.breaker_threshold:
                        model.healthy = False
                        tier.circuit_open_until = time.time() + tier.breaker_timeout
                    self._log_request(model_id, False, 0, error)
                    return
    
    def _log_request(self, model_id: str, success: bool, latency_ms: float, error: str = "") -> None:
        """Log request for observability."""
        entry = {
            "ts": time.time(),
            "model": model_id,
            "success": success,
            "latency_ms": latency_ms,
            "error": error,
            "tier_idx": self.current_tier_idx
        }
        with self.request_log.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def complete(self, messages: list[dict], prefer_tier: Optional[str] = None,
                 max_tokens: int = 1024, temperature: float = 0.7) -> dict[str, Any]:
        """
        Execute chat completion with automatic failover.
        Returns: {"ok": bool, "model": str, "response": dict, "error": str, "fallback": bool}
        """
        if not self.api_key:
            return {"ok": False, "error": "No NVIDIA_API_KEY configured"}
        
        tried = set()
        max_attempts = sum(len(t.models) for t in self.tiers)
        
        for _ in range(max_attempts):
            model = self.pick_model(prefer_tier, skip=tried)
            if model is None:
                break
            
            tried.add(model.id)
            start = time.time()
            
            try:
                payload = {
                    "model": model.id,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False
                }
                req = urllib.request.Request(
                    NVIDIA_CHAT_URL,
                    data=json.dumps(payload).encode(),
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as r:
                    response = json.loads(r.read().decode())
                
                latency = (time.time() - start) * 1000
                self.record_success(model.id, latency)
                
                return {
                    "ok": True,
                    "model": model.id,
                    "response": response,
                    "fallback": len(tried) > 1
                }
                
            except urllib.error.HTTPError as e:
                latency = (time.time() - start) * 1000
                error_body = e.read().decode() if e.fp else str(e)
                self.record_failure(model.id, f"HTTP {e.code}: {error_body[:200]}")
                
                # 410 GONE = model retired, mark permanently unhealthy
                if e.code == 410:
                    for tier in self.tiers:
                        for m in tier.models:
                            if m.id == model.id:
                                m.healthy = False
                                m.consecutive_failures = 999
                
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                latency = (time.time() - start) * 1000
                self.record_failure(model.id, f"{e.__class__.__name__}: {e}")
        
        return {"ok": False, "error": "all models exhausted", "tried": list(tried)}
    
    def get_status(self) -> dict:
        """Get current router status."""
        return {
            "tiers": [{
                "name": t.name,
                "models": [{
                    "id": m.id,
                    "tier": m.tier,
                    "healthy": m.healthy,
                    "failures": m.consecutive_failures,
                    "latency_ms": m.last_latency_ms,
                    "cost_per_1k": m.cost_per_1k
                } for m in t.models],
                "requests_today": t.requests_today,
                "max_daily": t.max_daily_requests,
                "circuit_open": time.time() < t.circuit_open_until
            } for t in self.tiers],
            "current_tier": self.tiers[self.current_tier_idx].name if self.tiers else None
        }
    
    def health_check_all(self) -> dict[str, bool]:
        """Probe all models for health."""
        results = {}
        for tier in self.tiers:
            for model in tier.models:
                try:
                    # Quick probe with minimal request
                    payload = {"model": model.id, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1}
                    req = urllib.request.Request(
                        NVIDIA_CHAT_URL,
                        data=json.dumps(payload).encode(),
                        headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=5) as r:
                        model.healthy = r.status < 500
                        results[model.id] = model.healthy
                except Exception:
                    model.healthy = False
                    results[model.id] = False
        return results


# Integration with existing model_failover
def create_nvidia_ladder() -> "ModelLadder":
    """Create a ModelLadder compatible with model_failover.ModelLadder."""
    router = NvidiaModelRouter()
    router.discover_models()
    
    # Convert to model_failover format
    from model_failover import ModelLeg, ModelLadder
    
    legs = []
    for tier in router.tiers:
        for model in tier.models:
            legs.append(ModelLeg(
                name=model.id,
                kind="remote",
                probe_url=NVIDIA_CHAT_URL,
                cost_per_1k=model.cost_per_1k
            ))
    
    return ModelLadder(legs=legs)


# CLI
if __name__ == "__main__":
    import sys
    router = NvidiaModelRouter()
    models = router.discover_models()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print(json.dumps(router.get_status(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "health":
        print(json.dumps(router.health_check_all(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "complete":
        messages = [{"role": "user", "content": sys.argv[2] if len(sys.argv) > 2 else "Hello"}]
        result = router.complete(messages)
        print(json.dumps(result, indent=2))
    else:
        print(f"Discovered {len(models)} models:")
        for m in models:
            print(f"  {m.id} [{m.tier}] {'✓' if m.healthy else '✗'} ${m.cost_per_1k}/1k")