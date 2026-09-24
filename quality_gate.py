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

# ---------------------------------------------------------------------------
# Strict-quality hardening (user rule: جودة صارمة). Small, capped deductions
# so idiomatic clean workflows (webhook → https, pinned, connected) still
# score ~85 PASSED, while sloppy graphs fail harder and for more reasons.
# ---------------------------------------------------------------------------
# Node types that START an execution (a graph with none can never run).
TRIGGER_HINTS = ("trigger", "webhook", "schedule", "chat", "form")

# Node-type keywords that perform an external network call (need retry/timeout
# — ASI08 cascading-failure discipline: a slow dependency must not hang the
# whole graph forever).
NETWORK_HINTS = (
    "httprequest", "httprequesttool", "sendemail", "telegram", "slack",
    "discord", "gmail", "twilio", "whatsapp", "openai", "anthropic",
    "stripe", "github", "hubspot", "salesforce", "postgres", "mysql",
    "mongodb", "redis", "notion", "airtable", "sheets",
)

# Side-effecting write signals (need idempotency/dedup — redeliveries must
# not duplicate effects).
WRITE_HINTS = (
    "create", "update", "upsert", "insert", "append", "delete", "write",
    "send", "post", "publish",
)
READ_ONLY_HINTS = ("get", "list", "read", "search", "fetch")

IDEMPOTENCY_HINTS = (
    "idempotency", "dedup", "dedupe", "webhook-id", "request-id",
    "event-id", "executionid", "execution_id",
)

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

    def _scan_identity(self, nodes: list[dict]) -> list[str]:
        """Strict identity: duplicate names break $node refs; a graph with no
        trigger can never execute. (-15 each — structural, not style.)"""
        findings = []
        seen: dict[str, int] = {}
        for n in nodes:
            name = str(n.get('name', '') or '')
            if name:
                seen[name] = seen.get(name, 0) + 1
        dupes = sorted(k for k, c in seen.items() if c > 1)
        if dupes:
            findings.append(
                f"Duplicate node names {dupes} — $node references resolve "
                f"ambiguously; rename so every node is unique")
        if nodes and not any(
                any(h in str(n.get('type', '')).lower() for h in TRIGGER_HINTS)
                or str(n.get('type', '')).lower().endswith('.form')
                for n in nodes):
            findings.append(
                "No trigger node (webhook/schedule/manual/chat/form) — "
                "the graph can never start executing")
        return findings

    def _is_write_op(self, node: dict) -> bool:
        t = str(node.get('type', '')).lower()
        params = node.get('parameters', {}) or {}
        op = str(params.get('operation', '')).lower()
        if op and any(k in op for k in WRITE_HINTS):
            return True
        if not any(k in t for k in WRITE_HINTS):
            return False
        return not any(k in op for k in READ_ONLY_HINTS)

    def _scan_resilience(self, nodes: list[dict]) -> list[str]:
        """Strict resilience (ASI08): network calls need retry/timeout;
        writes need idempotency. (-5 per affected node, capped — guidance
        with teeth, not a guillotine.)"""
        retry_hits: list[str] = []
        idem_hits: list[str] = []
        for n in nodes:
            t = str(n.get('type', '')).lower()
            params = n.get('parameters', {}) or {}
            body = json.dumps(params, default=str).lower()
            if any(k in t for k in NETWORK_HINTS):
                has_retry = bool(params.get('retryOnFail')) or 'retry' in body \
                    or 'timeout' in body
                if not has_retry:
                    retry_hits.append(str(n.get('name')))
            if self._is_write_op(n):
                if not any(k in body for k in IDEMPOTENCY_HINTS):
                    idem_hits.append(str(n.get('name')))
        findings = []
        if retry_hits:
            findings.append(
                f"Network node(s) {retry_hits[:3]} without retry/timeout — "
                f"one slow dependency hangs the graph (ASI08 cascading "
                f"failure); set retryOnFail + timeout")
        if idem_hits:
            findings.append(
                f"Write node(s) {idem_hits[:3]} without idempotency/dedup "
                f"signal — redeliveries duplicate effects; consume a "
                f"webhook-id/request-id/event-id key")
        return findings

    def _scan_hygiene(self, workflow: dict) -> list[str]:
        """Strict hygiene: debug residue, TODO markers, insecure http://.
        Small deductions that make sloppiness visible in review."""
        findings = []
        text = json.dumps(workflow, default=str)
        code_text = " ".join(
            str((n.get('parameters', {}) or {}).get(k, ""))
            for n in workflow.get('nodes', [])
            for k in ("jsCode", "pythonCode", "functionCode"))
        if re.search(r"console\.log\s*\(|print\s*\(", code_text):
            findings.append(
                "Debug residue (console.log/print) in Code node — strip "
                "before production; logs leak internals")
        if re.search(r"\bTODO\b|\bFIXME\b|\bHACK\b", text):
            findings.append(
                "TODO/FIXME/HACK marker ships in the artifact — finish or "
                "file it, never deploy a reminder as code")
        if re.search(r'"https?://[^"]*"', text) and re.search(
                r'"http://(?!localhost|127\.0\.0\.1)[^"]*"', text):
            findings.append(
                "Insecure http:// URL literal — credentials and PII travel "
                "in cleartext; use https://")
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
        missing_error = any('Error Trigger' in v or 'continueOnFail' in v
                            for v in reliability)
        missing_pin = any('pinnedData' in v for v in reliability)
        if reliability:
            isolated_count = sum(1 for v in reliability if 'Isolated' in v)
            # Isolated nodes are a hard structural failure: -20 each
            score -= 20 * isolated_count
            # Other reliability issues -10 each
            score -= 10 * (len(reliability) - isolated_count)
            violations += reliability
        # Strict combo: NEITHER error handling NOR test data — untestable
        # AND unrecoverable. Extra -10 on top of the two singles.
        if missing_error and missing_pin:
            score -= 10
            violations.append(
                "Strict: no error handling AND no pinnedData — the workflow "
                "is neither testable nor recoverable; add an Error Trigger "
                "and pin sample data")

        # 4b. Strict identity (-15 each)
        identity = self._scan_identity(nodes)
        if identity:
            score -= 15 * len(identity)
            violations += identity

        # 4c. Strict resilience (-5 per class, capped at -10)
        resilience = self._scan_resilience(nodes)
        if resilience:
            score -= 5 * len(resilience)
            violations += resilience

        # 4d. Strict hygiene (-5 debug/TODO, -10 insecure http)
        hygiene = self._scan_hygiene(workflow)
        for h in hygiene:
            score -= 10 if h.startswith("Insecure http") else 5
            violations.append(h)

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