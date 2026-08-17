#!/usr/bin/env python3
"""Reusable RAG query: embed a question with NVIDIA (input_type 'query'),
search the Qdrant collection, and print the top hits with their metadata and
score — the retrieval step the n8n RAG workflow performs in its Query Vector
Store node.

Usage:
  venv/bin/python scripts/rag_query.py --query "<question>" --collection <name>
      [--limit 3] [--json]

Secrets from project .env (NVIDIA_API_KEY, QDRANT_URL, QDRANT_API_KEY).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.rag_common import embed_query, search_points  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", required=True, help="the question to answer")
    ap.add_argument("--collection", required=True, help="Qdrant collection name")
    ap.add_argument("--limit", type=int, default=3, help="top-k hits (default 3)")
    ap.add_argument("--json", action="store_true", help="print raw JSON")
    args = ap.parse_args(argv)

    print("embedding query (input_type=query)...")
    vec = embed_query(args.query)
    hits = search_points(args.collection, vec, limit=args.limit)

    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return 0

    print(f"top {len(hits)} hits in '{args.collection}':")
    for i, h in enumerate(hits, 1):
        payload = h.get("payload") or {}
        content = payload.get("content", "")
        meta = payload.get("metadata", {})
        print(f"\n  [{i}] score={h.get('score')} id={h.get('id')} "
              f"metadata={meta}")
        print(f"      {content[:220]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
