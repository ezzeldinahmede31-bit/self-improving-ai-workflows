---
name: code-smell-detector
description: "Detects code smells in n8n workflows based on Martin Fowler's catalog of 70+ smells from 'Refactoring' (1999). Enforces clean code principles: minimal parameters, single responsibility, meaningful names, no duplication, proper error handling. Pragmatic Programmer alignment: DRY (Don't Repeat Yourself) - detects and eliminates duplicated parameter configurations, expression patterns, and node structures across workflows. WET (Write Everything Twice) - validates learning loops before production deployment; ensures characterization tests exist before major refactors. Orthogonality - detects hidden coupling between workflow modules; ensures changes in one area don't silently break others. Reversibility - documents undo/redo patterns; warns on stateful nodes without clear rollback strategies. Temporal Coupling - warns when node execution order matters and subtle bugs can occur from sequencing. Software Rot - monitors for decay in workflow quality over time, flagging smells that accumulate. reports smells with severity and refactoring recipe. Pairs with: gate-first-pass-builder, incremental-generation, n8n-syntax-v2-enforcer, verification-before-completion."
---
# Code Smell Detector

Detects code smells in n8n workflows based on Martin Fowler's catalog from
"Refactoring" (1999). This skill scans workflow JSON for 30+ common code smells
and reports them with severity, refactoring recipes, and automatic fix suggestions
where applicable.

## Clean Code & Code Complete Alignment

This skill enforces the following principles:
- **Meaningful Names** (Code Complete): node names and parameter names should be
  intention-revealing, not cryptic or single-letter (except loop counters)
- **Small Functions/Nodes** (Code Complete): each node should do one thing and
  keep parameters minimal (ideally ≤3, max 5)
- **Single Responsibility** (Clean Code + Code Complete): no node should have
  multiple unrelated responsibilities masquerading as one flow
- **No Duplication** (Code Complete): avoid repeating the same expression
  patterns, parameter structures, or node configurations
- **Comprehensive Error Handling** (Code Complete): every error path should be
  explicit, not silently ignored
- **Testability** (Code Complete): every workflow should be unit-testable
  instantly (pinned data, idempotent operations)

## Smell Catalog (30+ Smells Detected)

### A. Function/Node Smells (1-10)

| # | Smell | Description | Refactoring Recipe |
|---|-------|-------------|-------------------|
| F1 | **Large Node** | Node has too many parameters (>5) or complex config | Split node into multiple smaller nodes, each with single responsibility |
| F2 | **Long Expression** | Expression chain exceeds 3 nested `{{ $json.X }}` | Break expression into multiple steps with intermediate nodes |
| F3 | **Output Argument** | Node modifies its input parameters | Extract modified values into new node outputs, avoid side effects |
| F4 | **Flag Argument** | Boolean parameter controlling different behaviors | Replace with separate nodes for each behavior branch |
| F5 | **Dead Node** | Node is never executed (no incoming edges) | Remove node entirely, or connect if genuinely needed |
| F6 | **Commented-Out Code** | Node has expressions commented out // ... | Remove commented code; keep history in version control |
| F7 | **Mixing Levels** | Node mixes high-level and low-level operations | Separate into orchestrator node (high-level) + worker nodes (low-level) |

### B. Error Handling Smells (11-20)

| # | Smell | Description | Refactoring Recipe |
|---|-------|-------------|-------------------|
| E1 | **Return Code Blind** | Workflow uses return codes without checking them | Add Error Trigger nodes, explicit error branches, or `continueOnFail` |
| E2 | **Null Return** | Node can return null without handling | Add null checks, use Default Node, or wrap in conditional |
| E3 | **Silent Failure** | No error handling on nodes that can fail | Add Error Trigger, `onError: continueRegularOutput`, or `continueOnFail` |
| E4 | **Broad Exception** | Catching all exceptions without differentiation | Catch specific exception types, add meaningful error messages |
| E5 | **Missing Error Context** | Error messages don't include what failed | Add contextual information to error outputs (`{node: "X", operation: "Y", error: ...}`) |
| E6 | **Try-Catch Obfuscation** | Over-nested try/catch blocks making flow hard to follow | Flatten error handling, use separate error handler workflows |
| E6 | **Hardcoded Error Values** | Magic numbers/strings for error codes | Replace with named constants or referenced credential error messages |

### C. Structure Smells (21-30)

| # | Smell | Description | Refactoring Recipe |
|---|-------|-------------|-------------------|
| S1 | **Duplicate Node Structure** | Two+ nodes have identical parameter configurations | Extract common configuration into a template/sub-workflow, use `n8n-subworkflow-modularizer` |
| S2 | **Duplicate Expression** | Same `{{ $json.X }}` pattern in multiple places | Create a shared variable node or use dedicated schema-defined parameters |
| S3 | **Data Clumping** | Multiple parameters always used together | Create a configuration node or use a Set node to consolidate |
| S4 | **Primitive Obsession** | Using primitive types (string, number) where objects would be clearer | Create data structure nodes, use object-style parameters where feasible |
| S5 | **Secondary Abstraction** | Unexplained constants litter the workflow | Document constants with Set nodes having meaningful names |
| S5 | **Message Chain** | Workflow chains `.getA().getB().getC()` (depth ≥3) | Redesign: expose root-level method, or split into separate workflows |
| S6 | **Inappropriate Intimacy** | Nodes accessing internal details of other nodes | Use public APIs/expressions only; avoid direct `item.json` deep access |
| S7 | **Laziness** | Using simplest solution without considering maintainability | Step back, consider future maintainers (Code Complete principle); add documentation |

## Usage

### Detection Mode (default)
Run skill detection on a workflow JSON:
```bash
venv/bin/python scripts/detect_code_smells.py .opencode/skills/code-smell-detector \
  --workflow /path/to/workflow.json \
  --output /path/to/smells_report.json
```

### Report Format
```json
{
  "workflow_id": "example",
  "total_smells": 5,
  "smells": [
    {
      "id": "F1",
      "name": "Large Node",
      "severity": "high",
      "node": "Set",
      "description": "Node has 7 parameters, exceeds recommended max of 5",
      "refactoring": "Split into 2 nodes: one for data transformation, one for formatting",
      "auto_fix_possible": false
    },
    {
      "id": "S2",
      "name": "Duplicate Expression",
      "severity": "medium",
      "locations": ["Set/params/X", "IF/params/Y"],
      "description": "Same `{{ $json.source }}` pattern in 2 places",
      "refactoring": "Create shared Set node with source parameter, reference from both places",
      "auto_fix_possible": true
    }
  ],
  "summary": {
    "high_severity": 2,
    "medium_severity": 2,
    "low_severity": 1,
    "recommendation": "Address high severity first, then medium"
  }
}
```

### Severity Scale
- **High**: Severely impacts maintainability, testability, or correctness; must fix before delivery
- **Medium**: Affects readability or moderate maintainability; fix before significant expansions
- **Low**: cosmetic or future-proofing; address when time permits

## Rules of Engagement

1. **Run before gate-first-pass**: Execute detection as part of pre-build checklist
2. **High severity blocker**: Any high-severity smell should be addressed before `build-gates-pipeline` run
3. **Pair with incremental-generation**: When fixing smells, rebuild node-by-node using incremental approach
4. **Pair with n8n-syntax-v2-enforcer**: Ensure expression syntax is clean while fixing structural smells
5. **Do not auto-fix critical flows**: Some refactorings change workflow semantics; always verify after auto-fix

## Examples

### Before (smells detected: F1, F3, S2)
```json
{
  "nodes": [
    {
      "name": "Process All Data",
      "type": "n8n-nodes-base.set",
      "typeVersion": 2,
      "parameters": {
        "values": [
          { "name": "user", "value": "={{ $json.user.getFullName() }}", "type": "string" },
          { "name": "email", "value": "={{ $json.user.getEmail() }}", "type": "string" },
          { "name": "phone", "value": "={{ $json.user.getPhone() }}", "type": "string" },
          { "name": "address", "value": "={{ $json.user.getAddress().street + ' ' + $json.user.getAddress().city }}", "type": "string" },
          { "name": "extra1", "value": "unnecessary", "type": "string" },
          { "name": "extra2", "value": "also_unnecessary", "type": "string" }
        ]
      }
    },
    {
      "name": "Send Summary",
      "type": "n8n-nodes-base.telegram",
      "parameters": {
        "chat_id": "={{ $json.chat_id }}",
        "text": "={{ $json.user.getFullName() }} has been processed"
      }
    }
  ]
}
```

### After (smells resolved)
```json
{
  "nodes": [
    {
      "name": "Extract User Details",
      "type": "n8n-nodes-base.set",
      "typeVersion": 2,
      "parameters": {
        "values": [
          { "name": "full_name", "value": "={{ $json.user.getFullName() }}", "type": "string" },
          { "name": "email", "value": "={{ $json.user.email }}", "type": "string" },
          { "name": "phone", "value": "={{ $json.user.phone }}", "type": "string" }
        ]
      }
    },
    {
      "name": "Format Address",
      "type": "n8n-nodes-base.set",
      "typeVersion": 2,
      "parameters": {
        "values": [
          { "name": "address", "value": "={{ $json.user.street + ' ' + $json.user.city }}", "type": "string" }
        ]
      }
    },
    {
      "name": "Send Telegram",
      "type": "n8n-nodes-base.telegram",
      "parameters": {
        "chat_id": "={{ $json.chat_id }}",
        "text": "={{ $json.full_name }} has been processed at {{ $json.address }}"
      }
    }
  ]
}
```

## Refactoring Recipes (Selected)

### Large Node (F1)
**Problem**: Node has too many parameters/configurations  
**Solution**: 
1. Identify the distinct responsibilities within the node
2. Create separate nodes for each responsibility
3. Connect via data flow, ensuring each new node has ≤5 parameters
4. Update all downstream references to use new node outputs

### Long Expression (F2)
**Problem**: Expression chain exceeds 3 levels of nesting  
**Solution**:
1. Break the expression into intermediate steps
2. Use Set nodes to store intermediate results
3. Reference intermediate results in subsequent nodes
4. Improves readability and debuggability

### Return Code Blind (E1)
**Problem**: Workflow uses return codes without checking them  
**Solution**:
1. Add Error Trigger nodes at critical points
2. Explicitly check output data for error indicators
3. Use `continueOnFail` or `onError: continueRegularOutput` for non-fatal errors
4. Add clear error branches that surface to the user

### Duplicate Expression (S2)
**Problem**: Same `{{ $json.X }}` pattern in multiple places  
**Solution**:
1. Create a shared Set node with the common expression
2. Reference the Set node's output from all locations
3. Update any location-specific modifications as separate parameters
4. Single source of truth for the expression

---

## Integration with Gate Pipeline

This skill is designed to integrate with `build-gates-pipeline.py`:

1. **Pre-flight check**: Run `code-smell-detector` before `SchemaPreflightGate`
2. **High-severity flagging**: Any high-severity smell auto-adds to the avoid-list
3. **Fix verification**: After fixing smells, re-run to confirm exit 0
4. **Mandatory skills**: When `code-smell-detector` reports >3 high-severity smells, gate pipeline should block delivery until addressed

## Pairing Recommendations

- **With `gate-first-pass-builder`**: Ensures first-pass success considers code quality
- **With `incremental-generation`**: Fixes are applied node-by-node, maintaining gate compliance
- **With `n8n-syntax-v2-enforcer`**: Concurrent syntax and structural quality checks
- **With `verification-before-completion`**: Confirms refactored workflows pass execution tests

---