"""Git worktree isolation: one branch + checkout per task, controlled merge.

Main branch stays clean: workers commit inside their worktree, the
integrator merges branch-by-branch and reports conflicts instead of
blind-overwriting.
"""
from __future__ import annotations
import os
import subprocess


def _git(args: list[str], cwd: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                       text=True, timeout=60)
    return p.returncode, (p.stdout + p.stderr).strip()


def is_repo(path: str) -> bool:
    rc, _ = _git(["rev-parse", "--git-dir"], path)
    return rc == 0


def init_repo(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    _git(["init", "-b", "main"], path)
    _git(["config", "user.email", "orch@test.local"], path)
    _git(["config", "user.name", "orch-test"], path)
    _git(["commit", "--allow-empty", "-m", "init"], path)


def create_worktree(repo: str, task_id: str, work_root: str) -> dict:
    branch = f"wt/{task_id}"
    wt_path = os.path.join(work_root, f"wt-{task_id}")
    _git(["branch", "-D", branch], repo)
    rc, out = _git(["worktree", "add", "-b", branch, wt_path], repo)
    if rc != 0:
        # branch may exist already; fall back to existing branch checkout
        _git(["branch", "--list", branch], repo)
        rc2, out2 = _git(["worktree", "add", wt_path, branch], repo)
        if rc2 != 0:
            raise RuntimeError(f"worktree add failed: {out} / {out2}")
    return {"path": wt_path, "branch": branch}


def commit_all(wt_path: str, message: str) -> str:
    _git(["add", "-A"], wt_path)
    rc, out = _git(["commit", "-m", message], wt_path)
    if rc != 0 and "nothing to commit" not in out:
        raise RuntimeError(f"commit failed: {out}")
    _, sha = _git(["rev-parse", "HEAD"], wt_path)
    return sha


def changed_files(wt_path: str) -> list[str]:
    _, base = _git(["merge-base", "HEAD", "main"], wt_path)
    if not base:
        base = "main"
    _, out = _git(["diff", "--name-only", base.strip(), "HEAD"], wt_path)
    return sorted(f for f in out.splitlines() if f.strip())


def merge_branch(repo: str, branch: str, target: str = "main") -> dict:
    _git(["checkout", target], repo)
    rc, out = _git(["merge", "--no-ff", "--no-edit", branch], repo)
    if rc != 0:
        _git(["merge", "--abort"], repo)
        return {"ok": False, "reason": "CONFLICT", "detail": out[-2000:]}
    return {"ok": True}


def remove_worktree(repo: str, wt_path: str, branch: str) -> None:
    _git(["worktree", "remove", "--force", wt_path], repo)
    _git(["branch", "-D", branch], repo)


def list_worktrees(repo: str) -> list[dict]:
    rc, out = _git(["worktree", "list", "--porcelain"], repo)
    if rc != 0:
        return []
    items, cur = [], {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                items.append(cur)
            cur = {"path": line[len("worktree "):]}
        elif line.startswith("branch "):
            cur["branch"] = line[len("branch "):].split("/")[-1]
    if cur:
        items.append(cur)
    return items


def reap_stale(repo: str, work_root: str, active_paths: set[str],
               branch_prefix: str = "wt/") -> dict:
    """Remove leaked worktrees/branches from crashed runs.

    Only touches: worktree dirs under work_root not in active_paths, and
    branches starting with branch_prefix not backing a live worktree.
    Never touches user branches or main. Returns a report.
    """
    report: dict[str, list[str]] = {"removed_worktrees": [],
                                    "deleted_branches": [], "kept": []}
    live_branches = {w.get("branch", "") for w in list_worktrees(repo)}
    for w in list_worktrees(repo):
        p = w.get("path", "")
        if work_root in p and p not in active_paths:
            _git(["worktree", "remove", "--force", p], repo)
            report["removed_worktrees"].append(p)
    rc, out = _git(["branch", "--list", f"{branch_prefix}*"], repo)
    if rc == 0:
        for b in [x.strip().lstrip("* ") for x in out.splitlines() if x.strip()]:
            if b not in live_branches:
                _git(["branch", "-D", b], repo)
                report["deleted_branches"].append(b)
    return report
