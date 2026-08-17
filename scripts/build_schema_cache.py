"""Build memory/n8n_schema_cache.json from the same node-schema data the
n8n-mcp server ships (data/nodes.db) — the ground truth for what n8n 2.x
actually accepts. The gate's SchemaPreflightGate expects:
    { "<full node type>": { "required": [param names] } }

Usage:
  venv/bin/python scripts/build_schema_cache.py [--types a b c] [--out memory/n8n_schema_cache.json]

--types defaults to a small core set (webhook/code/telegram/if/set/schedule/
manual trigger/httpRequest/respondToWebhook). Use "--types all" to build the
full cache for every node type in the DB.
"""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

N8N_MCP_DB_CANDIDATES = [
    Path.home() / ".npm" / "_npx",
]


def find_nodes_db() -> Path:
    """Locate the n8n-mcp data/nodes.db inside the npx cache."""
    base = Path.home() / ".npm" / "_npx"
    if not base.exists():
        raise FileNotFoundError("no ~/.npm/_npx cache — run `npx -y n8n-mcp` once first")
    for entry in base.iterdir():
        db = entry / "node_modules" / "n8n-mcp" / "data" / "nodes.db"
        if db.exists():
            return db
    raise FileNotFoundError("n8n-mcp data/nodes.db not found in npx cache")


def full_type(package_name: str, node_type: str) -> str:
    """Reconstruct the live node type: package_name + '.' + suffix after the
    first dot. nodes-base.webhook -> n8n-nodes-base.webhook;
    nodes-langchain.agent -> @n8n/n8n-nodes-langchain.agent."""
    suffix = node_type.split(".", 1)[1] if "." in node_type else ""
    return f"{package_name}.{suffix}"


def required_params(properties_schema) -> list[str]:
    """Top-level property names flagged required: true and not hidden behind a
    displayOptions condition (those are conditional, not always-required)."""
    props = properties_schema
    if isinstance(props, str):
        try:
            props = json.loads(props)
        except (TypeError, ValueError):
            props = []
    if not isinstance(props, list):
        return []
    out = []
    for p in props:
        if not isinstance(p, dict):
            continue
        if p.get("required") and not p.get("displayOptions"):
            out.append(p["name"])
    return out


def build_cache(types: list[str] | None, out_path: Path) -> dict:
    db = find_nodes_db()
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    cache: dict[str, dict] = {}

    if types == ["all"]:
        rows = conn.execute(
            "SELECT package_name, node_type, version, properties_schema "
            "FROM nodes"
        ).fetchall()
    else:
        wanted = set(types)
        # The DB stores types WITHOUT the prefix (nodes-base.x / nodes-langchain.y)
        # and sometimes with @scoped/package prefix. Match on the suffix so the
        # CLI can pass live types like n8n-nodes-base.webhook or
        # @n8n/n8n-nodes-langchain.agent.
        suffix_wanted = {t.split(".", 1)[-1] for t in wanted}
        rows = conn.execute(
            "SELECT package_name, node_type, version, properties_schema FROM nodes"
        ).fetchall()

    count = 0
    for r in rows:
        ft = full_type(r["package_name"], r["node_type"])
        if types != ["all"] and ft not in wanted and r["node_type"] not in wanted \
                and r["node_type"].split(".", 1)[-1] not in suffix_wanted:
            continue
        req = required_params(r["properties_schema"])
        cache[ft] = {
            "required": req,
            "version": r["version"],
        }
        count += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[SCHEMA] cache written: {out_path} ({count} node types, source: {db.name})")
    for ft in sorted(cache):
        print(f"  {ft}  v{cache[ft]['version']}  required={cache[ft]['required']}")
    return cache


if __name__ == "__main__":
    args = sys.argv[1:]
    types = None
    out = ROOT / "memory" / "n8n_schema_cache.json"
    if "--types" in args:
        i = args.index("--types")
        types = args[i + 1].split()
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
    if types is None:
        types = [
            "n8n-nodes-base.webhook", "n8n-nodes-base.code",
            "n8n-nodes-base.telegram", "n8n-nodes-base.if",
            "n8n-nodes-base.set", "n8n-nodes-base.scheduleTrigger",
            "n8n-nodes-base.manualTrigger", "n8n-nodes-base.httpRequest",
            "n8n-nodes-base.respondToWebhook",
        ]
    build_cache(types, out)