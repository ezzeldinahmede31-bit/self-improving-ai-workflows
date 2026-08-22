#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("books", help="JSON file with [{title, author}, ...] or '-' for stdin")
    ap.add_argument("--size", type=int, default=8)
    ap.add_argument("--out", default="/tmp/opencode/book_batches")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.books == "-" else Path(args.books).read_text()
    books = json.loads(raw)
    if not isinstance(books, list) or not all(
        isinstance(b, dict) and b.get("title") for b in books
    ):
        raise SystemExit("input must be a JSON list of {title, author} objects")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    state_path = out / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {"batches": {}}

    start = len(state["batches"]) + 1
    n = 0
    for i in range(0, len(books), args.size):
        chunk = books[i : i + args.size]
        k = start + i // args.size
        lines = ["# Book batch %d - convert each book into a skill" % k, ""]
        for b in chunk:
            slug_hint = b["title"].lower().replace(" ", "-")
            lines.append("- %s - %s (slug hint: %s)" % (b["title"], b.get("author", ""), slug_hint))
        (out / ("batch_%d.md" % k)).write_text("\n".join(lines) + "\n")
        state["batches"][str(k)] = {"items": [b["title"] for b in chunk], "status": "pending"}
        n += 1
    state_path.write_text(json.dumps(state, indent=2))
    print("wrote %d batch(es) to %s" % (n, out))


if __name__ == "__main__":
    main()
