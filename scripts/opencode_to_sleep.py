#!/usr/bin/env python3
"""Bridge: export opencode sessions -> SkillOpt-Sleep Claude transcript format.

Reads this machine's opencode SQLite store (~/.local/share/opencode/opencode.db),
selects sessions whose directory is (a subdir of) the project, and regenerates
the Claude-Code-style transcript files that skillopt-sleep's harvest() reads:

    <claude_home>/projects/<slug>/<sessionId>.jsonl

Each line is one record in the exact schema harvest.py expects:

    {"type": "user",
     "message": {"role": "user", "content": "<text>"},
     "cwd": "<project>", "gitBranch": "<branch>",
     "timestamp": "2026-08-16T17:47:36", "sessionId": "...", "version": "v2"}

    {"type": "assistant",
     "message": {"role": "assistant",
                 "content": [{"type": "text", "text": "..."},
                             {"type": "tool_use", "name": "<tool>"}]},
     "cwd": "<project>", "gitBranch": "<branch>",
     "timestamp": "...", "sessionId": "...", "version": "v2"}

Timestamps are local, formatted "%Y-%m-%dT%H:%M:%S" so the string comparison in
harvest()'s since_iso filter works lexicographically. Regeneration is
idempotent: each run overwrites the per-session file with the full transcript.

NOTE: harvest() reads ONLY <claude_home>/projects/**/*.jsonl — it does NOT read
history.jsonl, so this bridge does not write it.

Usage:
    venv/bin/python scripts/opencode_to_sleep.py \
        --claude-home memory/.skillopt-sleep/home \
        --project "/home/ezzeldin/Documents/Default Project" \
        --hours 72
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")

TS_FMT = "%Y-%m-%dT%H:%M:%S"


def _ts_iso(epoch_ms: Optional[int]) -> str:
    """Epoch millis -> local ISO '%Y-%m-%dT%H:%M:%S' (matches state._now_iso)."""
    if not epoch_ms:
        return ""
    return datetime.fromtimestamp(epoch_ms / 1000.0).strftime(TS_FMT)


def _text_from_parts(parts: List[Dict[str, Any]]) -> str:
    """Join text parts of a message into a single string."""
    texts: List[str] = []
    for p in parts:
        if p.get("type") == "text" and p.get("text"):
            texts.append(str(p["text"]))
    return "\n".join(texts)


def _tool_names_from_parts(parts: List[Dict[str, Any]]) -> List[str]:
    """Tool part data -> tool_use names (mirrors harvest's _tool_names_from_content)."""
    names: List[str] = []
    for p in parts:
        if p.get("type") == "tool" and p.get("tool"):
            names.append(str(p["tool"]))
    return names


def load_session_messages(cursor, session_id: str) -> List[Tuple[int, str, List[Dict[str, Any]]]]:
    """Return [(time_created_ms, role, [part_dict,...])] for a session, ordered."""
    out: List[Tuple[int, str, List[Dict[str, Any]]]] = []
    rows = cursor.execute(
        "SELECT id, data, time_created FROM message WHERE session_id = ? ORDER BY time_created",
        (session_id,),
    ).fetchall()
    for mid, msg_data_raw, msg_created in rows:
        try:
            msg = json.loads(msg_data_raw)
        except Exception:
            continue
        role = msg.get("role")
        if role not in ("user", "assistant"):
            continue
        parts: List[Dict[str, Any]] = []
        if mid:
            for pr in cursor.execute(
                "SELECT data FROM part WHERE message_id = ? ORDER BY time_created", (mid,)
            ).fetchall():
                try:
                    parts.append(json.loads(pr[0]))
                except Exception:
                    continue
        out.append((msg_created or 0, role, parts))
    return out


def export_session(
    cursor,
    session_row,
    claude_home: str,
    project: str,
    git_branch: str,
) -> Optional[str]:
    """Write one session's transcript; return the output path or None."""
    session_row = dict(session_row)
    session_id = session_row["id"]
    slug = session_row.get("slug") or "opencode"
    records: List[Dict[str, Any]] = []

    for created_ms, role, parts in load_session_messages(cursor, session_id):
        ts = _ts_iso(created_ms)
        base: Dict[str, Any] = {
            "cwd": project,
            "gitBranch": git_branch,
            "timestamp": ts,
            "sessionId": session_id,
            "version": "v2",
        }
        if role == "user":
            text = _text_from_parts(parts)
            if not text.strip():
                continue
            base["type"] = "user"
            base["message"] = {"role": "user", "content": text}
        else:
            text = _text_from_parts(parts)
            tools = _tool_names_from_parts(parts)
            content: List[Dict[str, Any]] = []
            if text.strip():
                content.append({"type": "text", "text": text.strip()})
            for t in tools:
                content.append({"type": "tool_use", "name": t})
            if not content:
                continue
            base["type"] = "assistant"
            base["message"] = {"role": "assistant", "content": content}
        records.append(base)

    if not records:
        return None

    out_dir = os.path.join(claude_home, "projects", slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{session_id}.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return out_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export opencode sessions to SkillOpt-Sleep Claude transcript format."
    )
    parser.add_argument("--db", default=DEFAULT_DB, help="path to opencode.db")
    parser.add_argument(
        "--claude-home",
        default="memory/.skillopt-sleep/home",
        help="dir that will contain projects/ (the --claude-home of skillopt-sleep)",
    )
    parser.add_argument(
        "--project",
        default=os.getcwd(),
        help="project dir to filter sessions by (default: cwd)",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=72.0,
        help="only sessions updated within this many hours (default 72)",
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="max sessions to export (0 = no cap)"
    )
    parser.add_argument(
        "--git-branch", default="", help="override gitBranch stamped on records"
    )
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.db):
        print(f"[bridge] ERROR: db not found: {args.db}", file=sys.stderr)
        return 2

    project = os.path.abspath(args.project)
    claude_home = os.path.abspath(args.claude_home)
    since_ms = (datetime.now().timestamp() - args.hours * 3600) * 1000

    db = sqlite3.connect(args.db)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # session.path is stored WITHOUT the leading slash ('home/ezzeldin/...'),
    # while directory is absolute. Match on directory.
    rows = cur.execute(
        """
        SELECT id, slug, directory, title, time_updated
        FROM session
        WHERE directory IS NOT NULL AND directory != ''
        ORDER BY time_updated DESC
        """
    ).fetchall()

    selected: List[sqlite3.Row] = []
    for r in rows:
        if r["time_updated"] and r["time_updated"] < since_ms:
            continue
        d = os.path.abspath(r["directory"])
        if d != project and not d.startswith(project + os.sep):
            continue
        selected.append(dict(r))
        if args.limit and len(selected) >= args.limit:
            break

    if args.dry_run:
        print(f"[bridge] dry-run: {len(selected)} session(s) would be exported to {claude_home}")
        for r in selected:
            print(f"  - {r['id']}  {r['title'] or ''}")
        return 0

    written = 0
    for r in selected:
        path = export_session(cur, r, claude_home, project, args.git_branch)
        if path:
            written += 1
            print(f"[bridge] wrote {path}")
        else:
            print(f"[bridge] skipped {r['id']} (no user/assistant content)")

    db.close()
    print(f"[bridge] done: {written}/{len(selected)} session(s) exported to {claude_home}/projects/")
    return 0


if __name__ == "__main__":
    sys.exit(main())