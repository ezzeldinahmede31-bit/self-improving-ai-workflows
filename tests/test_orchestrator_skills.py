"""Orchestrator <-> skills library <-> gates wiring.

Every parallel worker must see the same skill surface (project + global +
library index) in its prompt, and the gates SKILLS stage must enforce the
manifest at merge time. Deterministic, hermetic (tmp dirs, monkeypatched
subprocess), no network.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from orchestrator import skills as skills_mod
from orchestrator import gates_qa as gates_qa_mod
from orchestrator import opencode_worker as ocw_mod
from orchestrator.schema import validate, with_defaults


def _skill_dir(root: str, name: str, desc: str):
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(f"---\nname: {name}\ndescription: {desc}\n---\n\nBody.\n")
    return d


def _project_repo(tmp_path):
    repo = str(tmp_path / "repo")
    proj = os.path.join(repo, ".opencode", "skills")
    _skill_dir(proj, "n8n-workflow-builder",
               "Build n8n workflows with webhook triggers and code nodes")
    _skill_dir(proj, "test-driven-development",
               "Write failing tests first, then implement until green")
    lib = os.path.join(repo, "memory")
    os.makedirs(lib, exist_ok=True)
    with open(os.path.join(lib, "skills-library.md"), "w",
              encoding="utf-8") as fh:
        fh.write("# Skill Library\n\n## Automation (2)\n\n"
                 "- **n8n-workflow-builder** — Build n8n workflows fast.\n"
                 "- **copywriting** — Write marketing copy for landing pages.\n")
    return repo


def _contract(**kw):
    c = {"task_id": "t1", "kind": "opencode", "role": "Builder",
         "goal": "build an n8n workflow with a webhook trigger",
         "outputs": [], "allowed_files": ["flow.json"],
         "dependencies": [],
         "acceptance": [{"id": "a", "kind": "file_exists",
                         "path": "flow.json"}]}
    c.update(kw)
    return with_defaults(c)


# ---------------------------------------------------------------------------
# index: three surfaces, project wins
# ---------------------------------------------------------------------------

def test_index_merges_three_surfaces(tmp_path, monkeypatch):
    repo = _project_repo(tmp_path)
    ghome = str(tmp_path / "home")
    gskills = os.path.join(ghome, ".claude", "skills")
    _skill_dir(gskills, "copywriting",
               "GLOBAL copywriting skill with email sequences")
    _skill_dir(gskills, "n8n-workflow-builder",
               "GLOBAL stale copy that must lose to project")
    monkeypatch.setattr(skills_mod, "GLOBAL_SKILLS_DIR", gskills)
    idx = skills_mod.build_index(repo)
    assert idx["n8n-workflow-builder"].surface == "project"
    assert idx["test-driven-development"].surface == "project"
    assert idx["copywriting"].surface == "global"
    assert "webhook" in idx["n8n-workflow-builder"].description
    assert idx["n8n-workflow-builder"].path.endswith("SKILL.md")


def test_library_only_row_resolves_without_path(tmp_path, monkeypatch):
    repo = _project_repo(tmp_path)
    monkeypatch.setattr(skills_mod, "GLOBAL_SKILLS_DIR",
                        str(tmp_path / "noglobal"))
    idx = skills_mod.build_index(repo)
    # copywriting exists only in the library index here
    assert "copywriting" in idx
    assert idx["copywriting"].surface == "library"


# ---------------------------------------------------------------------------
# resolve: explicit wins, auto threshold-adaptive, budget-capped, diverse
# ---------------------------------------------------------------------------

def test_explicit_skills_honored_unknown_flagged(tmp_path, monkeypatch):
    repo = _project_repo(tmp_path)
    monkeypatch.setattr(skills_mod, "GLOBAL_SKILLS_DIR",
                        str(tmp_path / "noglobal"))
    c = _contract(skills=["test-driven-development", "no-such-skill"])
    sel, rep = skills_mod.resolve_for_contract(c, repo)
    names = [s.name for s in sel]
    assert "test-driven-development" in names
    assert "no-such-skill" in names
    assert any("unverified" in n for n in rep["notes"])


def test_auto_resolve_matches_task_and_caps_budget(tmp_path, monkeypatch):
    repo = _project_repo(tmp_path)
    monkeypatch.setattr(skills_mod, "GLOBAL_SKILLS_DIR",
                        str(tmp_path / "noglobal"))
    c = _contract(skills_auto=True, skill_budget=1)
    sel, _ = skills_mod.resolve_for_contract(c, repo)
    assert len(sel) <= 1
    assert sel and sel[0].name == "n8n-workflow-builder"


def test_auto_resolve_empty_for_unrelated_task(tmp_path, monkeypatch):
    repo = _project_repo(tmp_path)
    monkeypatch.setattr(skills_mod, "GLOBAL_SKILLS_DIR",
                        str(tmp_path / "noglobal"))
    c = _contract(role="Poet", goal="write a haiku about rain",
                  allowed_files=["haiku.txt"])
    sel, _ = skills_mod.resolve_for_contract(c, repo)
    assert sel == []


# ---------------------------------------------------------------------------
# render + manifest
# ---------------------------------------------------------------------------

def test_render_empty_is_prompt_neutral():
    assert skills_mod.render_for_prompt([]) == ""


def test_render_contains_name_path_surface(tmp_path, monkeypatch):
    repo = _project_repo(tmp_path)
    monkeypatch.setattr(skills_mod, "GLOBAL_SKILLS_DIR",
                        str(tmp_path / "noglobal"))
    c = _contract(skill_budget=2)
    sel, _ = skills_mod.resolve_for_contract(c, repo)
    block = skills_mod.render_for_prompt(sel)
    assert "n8n-workflow-builder" in block
    assert "SKILL.md" in block


def test_manifest_written_and_valid(tmp_path):
    recs = [skills_mod.SkillRecord(name="a"), skills_mod.SkillRecord(name="b")]
    path = skills_mod.write_manifest(str(tmp_path), recs)
    assert os.path.isfile(path)
    assert json.load(open(path)) == {"skills_loaded": ["a", "b"]}


def test_manifest_per_task_filename_no_merge_collision(tmp_path):
    # Parallel tasks must never share one manifest path: same fixed name in
    # two worktrees = add/add merge conflict (regression).
    recs = [skills_mod.SkillRecord(name="a")]
    p1 = skills_mod.write_manifest(str(tmp_path), recs,
                                   filename="skills_manifest_t1.json")
    p2 = skills_mod.write_manifest(str(tmp_path), recs,
                                   filename="skills_manifest_t2.json")
    assert p1 != p2
    assert os.path.isfile(p1) and os.path.isfile(p2)


# ---------------------------------------------------------------------------
# schema: new fields validated
# ---------------------------------------------------------------------------

def test_schema_accepts_and_defaults_skill_fields():
    c = with_defaults(_contract())
    assert c["skills"] == [] and c["skills_auto"] is True
    assert c["skill_budget"] == 6
    assert validate(_contract(skills=["a"], skills_auto=False,
                              skill_budget=3)) == []


def test_schema_rejects_bad_skill_fields():
    assert validate(_contract(skills="notalist"))
    assert validate(_contract(skills=[""]))
    assert validate(_contract(skills_auto="yes"))
    assert validate(_contract(skill_budget=-1))
    assert validate(_contract(skill_budget=21))


# ---------------------------------------------------------------------------
# prompt threading (backward compatible: no block -> prompt unchanged shape)
# ---------------------------------------------------------------------------

def test_prompt_without_skills_has_no_skills_section(tmp_path):
    c = _contract()
    prompt = ocw_mod.build_task_prompt(c, {"inputs": {}}, str(tmp_path))
    assert "SKILLS" not in prompt


def test_prompt_with_skills_block(tmp_path):
    c = _contract()
    prompt = ocw_mod.build_task_prompt(c, {"inputs": {}}, str(tmp_path),
                                       skills_block="SKILLS\n- foo")
    assert "SKILLS" in prompt and "- foo" in prompt


# ---------------------------------------------------------------------------
# gates_qa: manifest + schema-cache flags passed, missing paths skipped
# ---------------------------------------------------------------------------

def test_gates_qa_passes_evidence_flags(tmp_path, monkeypatch):
    seen = {}

    class _Proc:
        stdout = '{"verdict": "READY_FOR_DEPLOYMENT", "reason_code": ""}'
        stderr = ""
        returncode = 0

    def fake_run(argv, **kw):
        seen["argv"] = argv
        return _Proc()

    monkeypatch.setattr(gates_qa_mod.subprocess, "run", fake_run)
    manifest = str(tmp_path / "skills_manifest.json")
    json.dump({"skills_loaded": ["a"]}, open(manifest, "w"))
    cache = str(tmp_path / "schema.json")
    json.dump({}, open(cache, "w"))
    out = gates_qa_mod.gate_changed_files(
        str(tmp_path), ["f.py"], str(tmp_path),
        skills_manifest=manifest, schema_cache=cache)
    assert out["passed"] is True
    argv = seen["argv"]
    assert "--skills-loaded" in argv and manifest in argv
    assert "--schema-cache" in argv and cache in argv


def test_gates_qa_skips_missing_evidence_paths(tmp_path, monkeypatch):
    seen = {}

    class _Proc:
        stdout = '{"verdict": "READY_FOR_DEPLOYMENT", "reason_code": ""}'
        stderr = ""
        returncode = 0

    def fake_run(argv, **kw):
        seen["argv"] = argv
        return _Proc()

    monkeypatch.setattr(gates_qa_mod.subprocess, "run", fake_run)
    out = gates_qa_mod.gate_changed_files(
        str(tmp_path), ["f.py"], str(tmp_path),
        skills_manifest=str(tmp_path / "nope.json"),
        schema_cache=str(tmp_path / "nocache.json"))
    assert out["passed"] is True
    assert "--skills-loaded" not in seen["argv"]
    assert "--schema-cache" not in seen["argv"]
