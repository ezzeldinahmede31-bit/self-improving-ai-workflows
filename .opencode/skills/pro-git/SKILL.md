---
name: pro-git
description: "Operates Git at the object-model level: blobs, trees, commits, branching, rebasing, and recovery. Use when the user says 'git workflow', 'rebase or merge', 'rewrite history', 'lost a commit', 'reflog', 'bisect', 'submodule', 'worktree', 'signed commits', 'pre-commit hook', 'detached HEAD', 'Pro Git', or when any Git operation must be safe and reversible."
---

# Pro Git

Distilled from Chacon & Straub's *Pro Git*: Git is a content-addressed object
store with labels (refs) on top. Every safe operation follows from that model.

## Purpose

Choose the right Git operation for the situation and never lose work: the
object model tells you what is recoverable and what is destructive.

## The model (5 facts that explain everything)

1. **Objects are immutable:** blob (content), tree (directory snapshot),
   commit (tree + parents + message), tag. Names are SHA hashes of content.
2. **Refs are movable labels:** branches and HEAD are pointers to commits.
   `HEAD` = "where I am"; detached HEAD just means HEAD points at a commit,
   not a branch.
3. **Three areas:** working tree -> staging (index) -> repository. `status`
   diffs working-vs-index and index-vs-HEAD; read it before every commit.
4. **History is a DAG:** merge adds a commit with two parents (preserves true
   history); rebase replays commits onto a new base (linear story, rewrites
   hashes). Rule: never rebase commits someone else has pulled.
5. **Almost nothing is lost:** dangling commits survive until gc; `reflog`
   records where every ref pointed for ~90 days — the universal undo log.

## Operation selection

- Private cleanup before sharing: interactive rebase (squash/fixup/reword).
- Integrating shared branches: merge (preserves provenance) or
  rebase-then-merge for a linear main.
- Undo staged: `restore --staged`; undo working: `restore`; undo a public
  commit: `revert` (new commit, no rewrite); undo private commits: `reset`.
- Find the breaking commit: `bisect` (binary search over history, ~log n).
- Big/binary/vendor code: submodules (pinned repos) or subtrees; parallel
  checkouts: `worktree`.
- Policy enforcement: hooks (pre-commit lint/tests), signed commits/tags,
  branch protection + required reviews on the forge.

## Verification

Before any history-rewriting command: `status` clean, target commits
unpushed-or-agreed, and a recovery path named (reflog/branch backup). After:
graph (`log --graph --oneline`) matches intent.

## Pairs with

- `autonomous-git-coworker` (day-to-day git driving),
  `using-git-worktrees` (isolated workspaces),
  `finishing-a-development-branch` (integration decisions).
