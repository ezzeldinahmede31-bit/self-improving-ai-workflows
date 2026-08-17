#!/usr/bin/env python3
"""Reusable RAG ingestion: split a text file into chunks, embed them with
NVIDIA (nvidia/nv-embedqa-e5-v5, input_type 'passage'), and upsert into a
Qdrant collection with payload {content, metadata} — the same payload shape
@langchain/qdrant uses so the n8n vector-store node can read it.

Usage:
  venv/bin/python scripts/rag_ingest.py --text <file.txt> --collection <name>
      [--chunk-size 1000] [--chunk-overlap 0] [--batch 2]
      [--metadata key=value ...] [--recreate] [--dry-run]

--recreate  : ensure the collection exists (drop+recreate so ids stay 1..N)
--dry-run   : split + embed only, print the plan, do NOT touch Qdrant

Secrets from project .env (NVIDIA_API_KEY, QDRANT_URL, QDRANT_API_KEY).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.rag_common import (  # noqa: E402
    split_text, embed, ensure_collection, delete_all_points, upsert_points,
    DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, DEFAULT_BATCH,
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", required=True, help="path to the source text file")
    ap.add_argument("--collection", required=True, help="Qdrant collection name")
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    ap.add_argument("--metadata", action="append", default=[],
                    help="key=value metadata label, repeatable (default: source=<file>)")
    ap.add_argument("--recreate", action="store_true",
                    help="drop existing points so ids are contiguous 1..N")
    ap.add_argument("--dry-run", action="store_true",
                    help="split + embed only; do not touch Qdrant")
    args = ap.parse_args(argv)

    text_path = Path(args.text)
    if not text_path.exists():
        print(f"error: {args.text} not found")
        return 1
    text = text_path.read_text(encoding="utf-8", errors="replace")

    chunks = split_text(text, chunk_size=args.chunk_size,
                        chunk_overlap=args.chunk_overlap)
    print(f"chunks: {len(chunks)} "
          f"({sum(len(c) for c in chunks)}/{len(text)} chars kept)")
    for i, c in enumerate(chunks[:3]):
        print(f"  [{i}] {len(c)} chars :: {c[:80]!r}")

    metadata = {}
    for kv in args.metadata:
        if "=" in kv:
            k, v = kv.split("=", 1)
            metadata[k.strip()] = v.strip()
    if not metadata:
        metadata = {"source": text_path.name}

    print("embedding chunks (input_type=passage)...")
    vecs = embed(chunks, "passage", batch_size=args.batch)
    print(f"vectors: {len(vecs)} x {len(vecs[0])}")

    points = [
        {"id": i + 1, "vector": vecs[i],
         "payload": {"content": chunks[i], "metadata": metadata}}
        for i in range(len(chunks))
    ]

    if args.dry_run:
        print(f"DRY-RUN: would upsert {len(points)} points into "
              f"'{args.collection}' (metadata={metadata})")
        return 0

    if args.recreate:
        ensure_collection(args.collection, size=len(vecs[0]))
        delete_all_points(args.collection)
        print(f"recreated (emptied) collection '{args.collection}'")
    else:
        ensure_collection(args.collection, size=len(vecs[0]))

    inserted = upsert_points(args.collection, points)
    print(f"INSERT COMPLETE: {inserted} points in '{args.collection}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
