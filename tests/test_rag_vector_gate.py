"""Tests for the RagVectorGate (Stage 3.45 RAG) — the vector-store / RAG
pipeline structural gate: an embeddings node wired into every vector store, a
real collection name, no dangling ai_vectorStore/ai_retriever refs, Qdrant
PUT-not-POST upserts, NVIDIA input_type, and loader-without-splitter.
Deterministic, no network, no audit.db writes (--no-hitl paths only).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.build_gates_pipeline import RagVectorGate, run_pipeline


class _SilentReporter:
    def stage(self, name, status, violations, score=None, warnings=None):
        pass


def _run(artifact, hitl=False):
    full_text = json.dumps(artifact, default=str)
    return run_pipeline(artifact, full_text, hitl=hitl, reporter=_SilentReporter())


def _wf(nodes, connections=None, extra=None):
    wf = {"name": "RAG", "nodes": nodes, "connections": connections or {}}
    if extra:
        wf.update(extra)
    return wf


def _node(name, ntype="n8n-nodes-base.httpRequest", **params):
    return {"id": name, "name": name, "type": ntype, "typeVersion": 2,
            "position": [0, 0], "parameters": params or {}}


def _store(name, collection="docs"):
    return _node(name, "@n8n/n8n-nodes-langchain.vectorStoreQdrant",
                 qdrantCollection=collection)


def _emb(name="NVIDIA Embeddings"):
    return _node(name, "@n8n/n8n-nodes-langchain.embeddingsNvidia")


def _agent(name="AI Agent"):
    return _node(name, "@n8n/n8n-nodes-langchain.agent")


def _wired(store="Qdrant Store", emb="NVIDIA Embeddings"):
    """A minimal correctly-wired RAG subgraph: embeddings -> store."""
    return {
        "NVIDIA Embeddings": {"ai_embedding": [[{"node": store,
                                                 "type": "ai_embedding", "index": 0}]]},
    }


# ---------------------------------------------------------------------------
# SKIP
# ---------------------------------------------------------------------------

def test_skip_empty_workflow():
    r = RagVectorGate().run(_wf([]))
    assert r["status"] == "SKIP"
    assert r["violations"] == []
    assert r["warnings"] == []


def test_skip_no_rag_nodes():
    r = RagVectorGate().run(_wf([_node("Code", "n8n-nodes-base.code", jsCode="return []")]))
    assert r["status"] == "SKIP"


# ---------------------------------------------------------------------------
# R1 — store without embeddings FAILs
# ---------------------------------------------------------------------------

def test_r1_store_without_embeddings_fails():
    r = RagVectorGate().run(_wf([_store("Qdrant")]))
    assert r["status"] == "FAIL"
    assert any("R1" in v for v in r["violations"])


def test_r1_store_with_embeddings_passes():
    wf = _wf(
        [_store("Qdrant Store"), _emb()],
        _wired(),
    )
    r = RagVectorGate().run(wf)
    assert r["status"] == "PASS"
    assert r["violations"] == []


def test_r1_two_stores_one_wired_one_not():
    nodes = [_store("S1", "a"), _store("S2", "b"), _emb()]
    conns = {"NVIDIA Embeddings": {"ai_embedding": [[{"node": "S1", "type": "ai_embedding", "index": 0}]]}}
    r = RagVectorGate().run(_wf(nodes, conns))
    assert r["status"] == "FAIL"
    assert any("S2" in v and "R1" in v for v in r["violations"])


def test_r1_tool_vector_store_not_required_to_embed():
    # toolVectorStore is a wrapper — its store arrives via ai_vectorStore,
    # embeddings wire into the underlying vectorStoreQdrant instead.
    nodes = [
        _store("Qdrant Store"),
        _emb(),
        _node("Query Vector Store", "@n8n/n8n-nodes-langchain.toolVectorStore"),
        _agent(),
    ]
    conns = {
        "NVIDIA Embeddings": {"ai_embedding": [[{"node": "Qdrant Store",
                                                 "type": "ai_embedding", "index": 0}]]},
        "Qdrant Store": {"ai_vectorStore": [[{"node": "Query Vector Store",
                                              "type": "ai_vectorStore", "index": 0}]]},
        "Query Vector Store": {"ai_tool": [[{"node": "AI Agent",
                                             "type": "ai_tool", "index": 0}]]},
    }
    r = RagVectorGate().run(_wf(nodes, conns))
    assert r["status"] == "PASS"
    assert not any("R1" in v for v in r["violations"])


# ---------------------------------------------------------------------------
# R2 — placeholder/empty collection WARNs (non-blocking)
# ---------------------------------------------------------------------------

def test_r2_empty_collection_warns():
    wf = _wf([_store("Qdrant Store", collection=""), _emb()], _wired())
    r = RagVectorGate().run(wf)
    assert r["status"] == "PASS"
    assert any("R2" in w for w in r["warnings"])


def test_r2_placeholder_collection_warns():
    wf = _wf([_store("Qdrant Store", collection="REPLACE_WITH_YOUR_COLLECTION"), _emb()], _wired())
    r = RagVectorGate().run(wf)
    assert any("R2" in w for w in r["warnings"])


def test_r2_real_collection_no_warning():
    wf = _wf([_store("Qdrant Store", collection="Q1.pdf"), _emb()], _wired())
    r = RagVectorGate().run(wf)
    assert not any("R2" in w for w in r["warnings"])


# ---------------------------------------------------------------------------
# R3 — dangling ai_vectorStore / ai_retriever FAILs
# ---------------------------------------------------------------------------

def test_r3_dangling_vector_store_fails():
    nodes = [_store("Qdrant Store"), _emb(), _agent()]
    conns = {
        "NVIDIA Embeddings": {"ai_embedding": [[{"node": "Qdrant Store",
                                                 "type": "ai_embedding", "index": 0}]]},
        "AI Agent": {"ai_vectorStore": [[{"node": "Ghost Store",
                                          "type": "ai_vectorStore", "index": 0}]]},
    }
    r = RagVectorGate().run(_wf(nodes, conns))
    assert r["status"] == "FAIL"
    assert any("R3" in v and "Ghost Store" in v for v in r["violations"])


def test_r3_dangling_retriever_fails():
    nodes = [_store("Qdrant Store"), _emb(), _agent()]
    conns = {
        "NVIDIA Embeddings": {"ai_embedding": [[{"node": "Qdrant Store",
                                                 "type": "ai_embedding", "index": 0}]]},
        "AI Agent": {"ai_retriever": [[{"node": "No Such Retriever",
                                        "type": "ai_retriever", "index": 0}]]},
    }
    r = RagVectorGate().run(_wf(nodes, conns))
    assert r["status"] == "FAIL"
    assert any("R3" in v for v in r["violations"])


def test_r3_valid_wiring_no_violation():
    nodes = [_store("Qdrant Store"), _emb(), _agent()]
    conns = {
        "NVIDIA Embeddings": {"ai_embedding": [[{"node": "Qdrant Store",
                                                 "type": "ai_embedding", "index": 0}]]},
        "AI Agent": {"ai_vectorStore": [[{"node": "Qdrant Store",
                                          "type": "ai_vectorStore", "index": 0}]]},
    }
    r = RagVectorGate().run(_wf(nodes, conns))
    assert not any("R3" in v for v in r["violations"])


# ---------------------------------------------------------------------------
# R4 — Qdrant upsert must be PUT, not POST (WARNING)
# ---------------------------------------------------------------------------

def test_r4_qdrant_post_upsert_warns():
    n = _node("Q HTTP", "n8n-nodes-base.httpRequest", method="POST",
              url="https://x.qdrant.io/collections/docs/points")
    r = RagVectorGate().run(_wf([n]))
    assert any("R4" in w for w in r["warnings"])


def test_r4_qdrant_put_upsert_no_warning():
    n = _node("Q HTTP", "n8n-nodes-base.httpRequest", method="PUT",
              url="https://x.qdrant.io/collections/docs/points")
    r = RagVectorGate().run(_wf([n]))
    assert not any("R4" in w for w in r["warnings"])


def test_r4_qdrant_search_post_no_warning():
    # POST on /points/search is the RETRIEVE path — allowed.
    n = _node("Q HTTP", "n8n-nodes-base.httpRequest", method="POST",
              url="https://x.qdrant.io/collections/docs/points/search")
    r = RagVectorGate().run(_wf([n]))
    assert not any("R4" in w for w in r["warnings"])


# ---------------------------------------------------------------------------
# R5 — NVIDIA embeddings need input_type (WARNING)
# ---------------------------------------------------------------------------

def test_r5_nvidia_embeddings_missing_input_type_warns():
    n = _node("N HTTP", "n8n-nodes-base.httpRequest", method="POST",
              url="https://integrate.api.nvidia.com/v1/embeddings",
              jsonBody={"input": ["hi"], "model": "nvidia/nv-embedqa-e5-v5"})
    r = RagVectorGate().run(_wf([n]))
    assert any("R5" in w for w in r["warnings"])


def test_r5_nvidia_embeddings_with_input_type_no_warning():
    n = _node("N HTTP", "n8n-nodes-base.httpRequest", method="POST",
              url="https://integrate.api.nvidia.com/v1/embeddings",
              jsonBody={"input": ["hi"], "model": "nvidia/nv-embedqa-e5-v5",
                        "input_type": "passage"})
    r = RagVectorGate().run(_wf([n]))
    assert not any("R5" in w for w in r["warnings"])


# ---------------------------------------------------------------------------
# R6 — loader without splitter WARNs (non-blocking)
# ---------------------------------------------------------------------------

def test_r6_loader_without_splitter_warns():
    nodes = [
        _node("Read Files", "n8n-nodes-base.readBinaryFiles"),
        _emb(),
        _store("Qdrant Store"),
    ]
    conns = {"NVIDIA Embeddings": {"ai_embedding": [[{"node": "Qdrant Store",
                                                     "type": "ai_embedding", "index": 0}]]}}
    r = RagVectorGate().run(_wf(nodes, conns))
    assert any("R6" in w for w in r["warnings"])


def test_r6_loader_with_splitter_no_warning():
    nodes = [
        _node("Read Files", "n8n-nodes-base.readBinaryFiles"),
        _node("Split Text", "@n8n/n8n-nodes-langchain.textSplitterRecursiveCharacterTextSplitter"),
        _emb(),
        _store("Qdrant Store"),
    ]
    conns = {"NVIDIA Embeddings": {"ai_embedding": [[{"node": "Qdrant Store",
                                                     "type": "ai_embedding", "index": 0}]]}}
    r = RagVectorGate().run(_wf(nodes, conns))
    assert not any("R6" in w for w in r["warnings"])


# ---------------------------------------------------------------------------
# pipeline integration — RAG stage blocks deployment, verdict wired
# ---------------------------------------------------------------------------

def test_pipeline_rag_violation_blocks():
    # Trigger + credentials so PRECISION passes; the store-without-embeddings
    # must be the single blocking stage (RAG_STRUCTURAL_VIOLATION).
    trigger = _node("Receive Webhook", "n8n-nodes-base.webhook",
                    path="h", authentication="headerAuth")
    store = _store("Qdrant")
    store["credentials"] = {"qdrantApi": {"id": "c1", "name": "Qdrant account"}}
    wf = _wf([trigger, store], {})
    res = _run(wf)
    assert res["verdict"] == "RAG_STRUCTURAL_VIOLATION"
    assert res["reason_code"] == "RAG_VECTOR_STORE_INCONSISTENCY"
    assert "rag" in res["stages"]
    assert res["stages"]["rag"]["status"] == "FAIL"


def test_pipeline_rag_stage_reported_and_passed():
    wf = _wf(
        [_store("Qdrant Store"), _emb()],
        _wired(),
    )
    res = _run(wf)
    assert res["stages"]["rag"]["status"] == "PASS"
    assert "rag" in res["stages"]
