"""Programmatic implementation of the enterprise-quality-audit-loop skill.

Deterministic quality scoring of n8n workflow JSON against Schema V2 syntax,
graph integrity, and reliability requirements. Score below 80 = FAIL.

n8n-native parity (baked in — same grade as code): bare unwrapped
expressions ($json... without ={{...}}), missing `=` prefixes, deprecated
Function nodes, and empty node names are scored; node-name *style*
(verb-prefix) is a non-blocking note, never a deduction — idiomatic n8n
names like "Webhook" must not lose points.
"""

import re
import json
from dataclasses import dataclass, field
from typing import Any, Optional

QUALITY_THRESHOLD = 80
MAX_ATTEMPTS = 3
MAX_CYCLOMATIC = 10
MAX_NODES_SINGLE_WORKFLOW = 10

# Bare n8n variable references used as plain string values WITHOUT the
# ={{...}} expression wrapper — n8n evaluates them as literal text, so the
# node silently receives the wrong value. The most common AI-generation
# mistake (n8n-mcp #677). Anchored (^) to avoid flagging prose/SQL/comments.
# NOTE: Code-node sources (jsCode/functionCode/pythonCode) are JS, not
# expression strings — excluded from this scan (syntax gate owns them).
BARE_EXPRESSION_RES = [
    r"^\$json[.\[]", r"^\$node\[", r"^\$input\.", r"^\$execution\.",
    r"^\$workflow\.", r"^\$prevNode\.", r"^\$env\.",
    r"^\$(now|today|itemIndex|runIndex|executionId)$",
]

# Code-bearing parameter keys: JavaScript/Python source, never expressions.
CODE_PARAM_KEYS = {"jsCode", "functionCode", "pythonCode"}


# Deprecated syntax (banned)
DEPRECATED_SYNTAX = [
    r'\$[Nn]ode\[[\'"]',            # $node["X"] / $node['X']
    r'\$json\b(?!\.)',              # bare $json (not $json.field)
    r'\bmoment\s*\(',               # moment.js
]

# Mandated V2 expressions
V2_EXPRESSIONS = [
    r'\$input\.first\(\)\.json',
    r'\$input\.item\.json',
    r'\$input\.all\(\)',
    r'\$input\.first\(\),?',
]


@dataclass
class QualityResult:
    quality_score: int = 100
    violations: list[str] = field(default_factory=list)
    status: str = "PASSED"          # PASSED | REJECTED


class QualityGate:
    """Deterministic Schema-V2 / graph / reliability auditor."""

    def _scan_syntax(self, text: str) -> list[str]:
        findings = []
        for pat in DEPRECATED_SYNTAX:
            if re.search(pat, text):
                findings.append(f"Deprecated syntax `{pat}` used")
        # Check that Code nodes use V2 input accessors
        code_blocks = re.findall(r'(?:jsCode|pythonCode)[\'"]\s*:\s*[\'"]([^\'"]+)', text)
        for block in code_blocks:
            if re.search(r'\$json\b(?!\.)', block) and '$input' not in block:
                findings.append("Code-node uses bare $json without $input accessor")
        return findings

    def _scan_graph(self, nodes: list[dict]) -> tuple[list[str], list[str]]:
        """Returns (deductions, style_notes).

        Only EMPTY/missing names deduct score. Verb-prefix style is a
        non-blocking note — n8n-native names ('Webhook', 'HTTP Request',
        'Set1') are idiomatic and must not lose points the way a code
        lint would penalize them."""
        deductions = []
        style_notes = []
        for n in nodes:
            name = n.get('name', '')
            if not name or not str(name).strip():
                deductions.append("Node with empty/missing name — nodes must be named")
            elif not re.match(r'^[A-Z][a-zA-Z]+\s[A-Z][a-zA-Z]+', str(name)):
                style_notes.append(
                    f"Style (non-blocking): node name `{name}` is not "
                    f"verb-prefixed/discoverable (e.g. 'Send Email')")
        return deductions, style_notes

    def _scan_expressions(self, workflow: dict) -> list[str]:
        """Bare / malformed n8n expressions in plain string parameters."""
        findings = []
        for n in workflow.get('nodes', []):
            params = n.get('parameters', {}) or {}
            bad_hits: list[str] = []

            def _walk(obj, key=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        _walk(v, k)
                elif isinstance(obj, list):
                    for v in obj:
                        _walk(v, key)
                elif isinstance(obj, str):
                    if key in CODE_PARAM_KEYS or not obj.strip():
                        return
                    s = obj.strip()
                    if s.startswith("=") or "{{" in s and s.startswith("{{"):
                        # {{...}} without the `=` prefix — n8n treats it as
                        # literal text, not an expression.
                        if s.startswith("{{"):
                            bad_hits.append(f"{key}={s[:48]!r} (missing `=` prefix)")
                        return
                    for pat in BARE_EXPRESSION_RES:
                        if re.search(pat, s):
                            bad_hits.append(f"{key}={s[:48]!r} (bare, unwrapped)")
                            break

            _walk(params)
            if bad_hits:
                findings.append(
                    f"Node `{n.get('name')}` has {len(bad_hits)} bare/malformed "
                    f"expression(s) — wrap as ={{{{...}}}}: {bad_hits[0]}")
        return findings

    def _scan_deprecated_nodes(self, nodes: list[dict]) -> list[str]:
        findings = []
        for n in nodes:
            if str(n.get('type', '')) == "n8n-nodes-base.function":
                findings.append(
                    f"Node `{n.get('name')}` uses deprecated Function node — "
                    f"use the Code node (n8n-nodes-base.code) instead")
        return findings

    def _scan_complexity(self, js: str) -> int:
        """Rough cyclomatic complexity: count branch keywords."""
        if not js:
            return 1
        branches = len(re.findall(r'\b(if|for|while|catch|switch|case|&&|\|\|)\b', js))
        return branches + 1

    def _scan_reliability(self, workflow: dict) -> list[str]:
        findings = []
        node_keys = [n.get('name') for n in workflow.get('nodes', [])]
        connections = workflow.get('connections', {})

        # Isolated nodes: defined but not referenced in connections
        def _edge_nodes(edges) -> list:
            """Extract target node names from an edge value, handling BOTH the
            legacy shape {out: [edge, edge]} and the 2.x nested-list shape
            {out: [[edge, ...], [edge, ...]]} where index i = branch i."""
            found = []
            if isinstance(edges, dict):
                if 'node' in edges:
                    found.append(edges['node'])
            elif isinstance(edges, list):
                for e in edges:
                    found.extend(_edge_nodes(e))
            return found

        all_referenced = set()
        for src, outs in connections.items():
            all_referenced.add(src)
            for out_type, edges in outs.items():
                for tgt in _edge_nodes(edges):
                    all_referenced.add(tgt)
        isolated = [k for k in node_keys if k and k not in all_referenced]
        if isolated:
            findings.append(f"Isolated/unreachable nodes: {isolated}")

        # Error handling
        has_error_trigger = any('errorTrigger' in str(n.get('type', '')) for n in workflow.get('nodes', []))
        # onError / continueOnFail presence
        continue_on_fail_count = sum(
            1 for n in workflow.get('nodes', [])
            if n.get('continueOnFail') or n.get('onError') == 'continueRegularOutput'
        )
        if not has_error_trigger and continue_on_fail_count == 0:
            findings.append("No Error Trigger node and no continueOnFail on any node")

        # pinnedData
        has_pinned = any('pinnedData' in str(n.get('parameters', {})) or n.get('pinnedData')
                         for n in workflow.get('nodes', []))
        if not has_pinned:
            findings.append("No pinnedData on primary nodes — cannot unit-test instantly")

        return findings

    def evaluate(self, workflow: Any) -> QualityResult:
        if isinstance(workflow, str):
            try:
                workflow = json.loads(workflow)
            except json.JSONDecodeError:
                return QualityResult(
                    quality_score=0,
                    violations=["Invalid JSON — cannot audit"],
                    status="REJECTED",
                )
        if not isinstance(workflow, dict) or 'nodes' not in workflow:
            workflow = {'nodes': workflow.get('nodes', []), 'connections': workflow.get('connections', {})}

        nodes = workflow.get('nodes', [])
        connections = workflow.get('connections', {})
        full_text = json.dumps(workflow)

        score = 100
        violations = []

        # 1. Syntax enforcement (-15 each)
        syntax = self._scan_syntax(full_text)
        if syntax:
            score -= 15 * len(syntax)
            violations += syntax

        # 2. Graph integrity (-10 for empty names; style is non-blocking)
        graph_deductions, graph_style = self._scan_graph(nodes)
        if graph_deductions:
            score -= 10
            violations += graph_deductions[:1]
        violations += graph_style[:3]  # style notes: visible, never scored

        # 2b. n8n expression format (-5 per affected node, max -15)
        expr = self._scan_expressions(workflow)
        if expr:
            score -= 5 * min(len(expr), 3)
            violations += expr

        # 2c. Deprecated node types (-5 each)
        dep_nodes = self._scan_deprecated_nodes(nodes)
        if dep_nodes:
            score -= 5 * len(dep_nodes)
            violations += dep_nodes

        # 3. Size / maintainability (-10 if oversized)
        if len(nodes) > MAX_NODES_SINGLE_WORKFLOW:
            score -= 10
            violations.append(f"Workflow has {len(nodes)} nodes — recommend sub-workflow split")

        # 4. Reliability
        reliability = self._scan_reliability(workflow)
        if reliability:
            isolated_count = sum(1 for v in reliability if 'Isolated' in v)
            # Isolated nodes are a hard structural failure: -20 each
            score -= 20 * isolated_count
            # Other reliability issues -10 each
            score -= 10 * (len(reliability) - isolated_count)
            violations += reliability

        # 5. Code-node complexity (-5 each breach)
        for n in nodes:
            js = (n.get('parameters', {}).get('jsCode', ''))
            if js and self._scan_complexity(js) > MAX_CYCLOMATIC:
                score -= 5
                violations.append(f"Code node `{n.get('name')}` exceeds cyclomatic threshold")

        score = max(0, min(score, 100))
        status = "PASSED" if score >= QUALITY_THRESHOLD else "REJECTED"
        return QualityResult(
            quality_score=score,
            violations=violations,
            status=status,
        )

    def evaluate_to_dict(self, workflow: Any) -> dict:
        res = self.evaluate(workflow)
        return {
            "status": res.status,
            "quality_score": res.quality_score,
            "violations": res.violations,
            "threshold": QUALITY_THRESHOLD,
        }


# ============================================================
# Example / self-test
# ============================================================
if __name__ == "__main__":
    gate = QualityGate()

    clean = {
        "nodes": [
            {"name": "Receive Webhook", "type": "n8n-nodes-base.webhook",
             "parameters": {"path": "x", "pinnedData": {}}},
            {"name": "Send HTTP Response", "type": "n8n-nodes-base.httpRequest",
             "parameters": {"url": "https://api.example.com"}},
        ],
        "connections": {
            "Receive Webhook": {"main": [{"node": "Send HTTP Response"}]},
        }
    }
    print("CLEAN:", gate.evaluate_to_dict(clean))

    bad = {
        "nodes": [
            {"name": "a", "type": "n8n-nodes-base.code",
             "parameters": {"jsCode": "const x = $node[\"a\"].json; if(a&&b){if(c){}else{for(;;){catch(x){}}}}"}},
            {"name": "orphan", "type": "n8n-nodes-base.stickyNote", "parameters": {}},
        ],
        "connections": {}
    }
    print("BAD:", gate.evaluate_to_dict(bad))