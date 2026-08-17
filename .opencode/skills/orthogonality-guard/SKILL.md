---
name: orthogonality-guard
description: "Enforces the Pragmatic Programmer principle of Orthogonality: changes in one area of the system should not affect other areas. In n8n workflows, this means detecting hidden coupling between modules, ensuring node configurations are independent, and preventing parameter leaks between seemingly unrelated workflows. Triggers on workflow build/validation; reports coupling issues with severity and refactoring recommendations. Pairs with: gate-first-pass-builder, code-smell-detector, n8n-syntax-v2-enforcer."
---
# Orthogonality Guard

The Pragmatic Programmer's Orthogonality principle states: "A change in one module should not break unrelated modules." In n8n workflow design, this translates to ensuring that workflow components are truly independent - no hidden dependencies, no state leaks, and no implicit ordering requirements.

## Clean Code & Pragmatic Programmer Alignment

This skill enforces:
- **Orthogonality** (Pragmatic Programmer): "A change in one module should not affect other unrelated modules"
- **Single Responsibility** (Clean Code): each workflow module should have one purpose
- **Minimal Surprise** (Pragmatic Programmer): "don't make me think" - workflow behavior should be predictable
- **Explicit Over Implicit** (Pragmatic Programmer): explicit connections and data flows, no implicit sharing

## Coupling Detection Catalog (20+ Patterns)

### A. Parameter Leakage (1-10)

| # | Coupling Type | Description | Refactoring Recipe |
|---|--------------|-------------|-------------------|
| P1 | **Shared Parameter** | Two+ nodes reference the same parameter name without explicit connection | Parameterize via dedicated Set node; avoid implicit sharing |
| P2 | **Configuration Drift** | Similar-named configs in different nodes diverge over time | Version configs explicitly; use separate Set nodes per context |
| P3 | **Implicit Data Flow** | Data moves through workflow without explicit trigger/connections | Add explicit triggers and connection points; document data flow |
| P4 | **Context Leak** | Node accesses context it shouldn't (e.g., downstream node reading upstream data) | Restrict node scope; use dedicated Set nodes for data transformation |
| P5 | **Hidden Dependency** | Node behaves differently based on invisible state | Make all dependencies explicit in node parameters or connections |
| P6 | **Configuration Share** | Same config structure used in multiple places without abstraction | Abstract shared config into reusable Sub-Workflow via `n8n-subworkflow-modularizer` |

### B. State & Execution Coupling (11-20)

| # | Coupling Type | Description | Refactoring Recipe |
|---|--------------|-------------|-------------------|
| S1 | **Temporal Coupling** | Workflow assumes execution order that isn't guaranteed | Reorder nodes to be independent; use `n8n-subworkflow-modularizer` for sequential steps |
| S2 | **Stateful Assumption** | Workflow assumes state from previous execution persists | Add explicit state reset nodes or use persistent storage |
| S3 | **Order Dependency** | Node execution order affects output (not parallel-safe) | Design for parallel execution; use idempotent operations |
| S4 | **Transaction Assumption** | Workflow assumes all-or-nothing execution | Add compensation steps; use `n8n-error-boundary-architect` patterns |
| S5 | **Resource Leak** | Workflow acquires resources (connections, locks) without release | Add explicit cleanup nodes; use `onError` handlers |
| S6 | **Initialization Dependency** | Workflow requires specific initialization order | Extract initialization into separate sub-workflow; call via Execute Workflow node |

## Usage

### Detection Mode (default)
Run skill detection on a workflow JSON:
```bash
venv/bin/python scripts/detect_orthogonality.py .opencode/skills/orthogonality-guard   --workflow /path/to/workflow.json   --output /path/to/coupling_report.json
```

### Report Format
```json
{
  "workflow_id": "example",
  "total_couplings": 3,
  "couplings": [
    {
      "id": "P1",
      "name": "Shared Parameter",
      "severity": "high",
      "nodes": ["Set/param1", "Set/param2"],
      "description": "Both Set nodes reference 'user_data' parameter without explicit connection",
      "refactoring": "Create dedicated Set node with user_data; connect explicitly via Execute Workflow",
      "auto_fix_possible": false
    }
  ],
  "summary": {
    "high_severity": 1,
    "medium_severity": 2,
    "recommendation": "Address high severity coupling first to prevent subtle bugs"
  }
}
```

## Integration with Gate Pipeline

This skill integrates with `build-gates-pipeline.py`:
1. **Pre-flight check**: Run `orthogonality-guard` before `SchemaPreflightGate`
2. **High-severity flagging**: Any high-severity coupling auto-adds to the avoid-list
3. **Fix verification**: After fixing couplings, re-run to confirm exit 0
4. **Mandatory skills**: When `orthogonality-guard` reports >2 high-severity couplings, gate pipeline should block delivery until addressed

## Pairing Recommendations

- **With `code-smell-detector`**: Concurrent structural and orthogonal quality checks
- **With `gate-first-pass-builder`**: Ensures first-pass success considers module independence
- **With `incremental-generation`**: Fixes are applied module-by-module, maintaining gate compliance
- **With `n8n-syntax-v2-enforcer`**: Concurrent syntax and orthogonal quality checks
