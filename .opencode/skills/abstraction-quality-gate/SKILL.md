---
name: abstraction-quality-gate
description: "Enforces A Philosophy of Software Design's core principle: complexity management through deep modules and shallow interfaces. Validates that workflow modules hide complexity (deep) and expose simple interfaces (shallow). Detects shallow modules (too much exposed), information leakage, and interface bloat. Triggers on workflow build; reports abstraction violations with severity. Pairs with: gate-first-pass-builder, code-smell-detector, orthogonality-guard, n8n-schema-guardrail."
---
# Abstraction Quality Gate

John Ousterhout's "A Philosophy of Software Design" teaches: **complexity is the enemy**. The solution is **deep modules** - modules that hide significant complexity behind simple interfaces. This skill enforces deep module design in n8n workflows.

## Core Principles Enforced

### 1. Deep Modules (High Functionality / Simple Interface)
- **Principle**: "The best modules are deep: they allow the caller to do a lot with a small interface."
- **Check**: Workflow sub-workflows should expose minimal parameters while doing significant work. Shallow modules (many params, little logic) are flagged.

### 2. Information Hiding
- **Principle**: "The most important property of a module is what it hides, not what it exposes."
- **Check**: Configuration details, implementation specifics, and error handling should be hidden inside sub-workflows, not exposed to callers.

### 3. Shallow Interfaces = Warning
- **Principle**: "A shallow module is one whose interface is more complex than the functionality it provides."
- **Check**: Nodes/sub-workflows with many parameters but little logic are flagged as shallow.

### 4. General-Purpose vs Special-Purpose
- **Principle**: "Modules should be somewhat general-purpose. Special-purpose modules are shallow."
- **Check**: Overly specific nodes that only work in one exact context are flagged.

## Abstraction Quality Checks

### Module Depth Analysis
```python
# Deep = High logic complexity / Low interface complexity
# Shallow = Low logic complexity / High interface complexity

def module_depth(subworkflow):
    interface_complexity = len(params) + len(return_types)
    logic_complexity = count_nodes + count_branches + count_operations
    return logic_complexity / max(interface_complexity, 1)

# Deep: ratio > 5
# Shallow: ratio < 2
```

### Information Leakage Detection
```python
# Information that should be hidden but is exposed:
- Implementation-specific error codes in outputs
- Internal configuration structure in parameters
- Debug-only fields in normal outputs
- Implementation-dependent parameter names
```

### Interface Bloat Detection
```python
# Interface complexity indicators:
- > 10 parameters on a sub-workflow
- > 5 output types from a single node
- Parameters that duplicate each other (data clumping)
- Parameters that are never used (dead params)
```

## Deep vs Shallow Examples

### Shallow Module (Flagged)
```
Sub-workflow: "Format Phone Number"
Interface: 8 params (country, format, separator, prefix, suffix, 
                     validation, error_handling, fallback)
Logic: 1 Set node
Ratio: 1/8 = 0.125 → SHALLOW
Fix: Reduce to 2 params (number, format_type); hide rest internally
```

### Deep Module (Good)
```
Sub-workflow: "Process Customer Onboarding"
Interface: 3 params (customer_id, notification_channel, dry_run)
Logic: 15 nodes (validation, DB write, email, Slack, webhook, 
                  error handling, retry, logging, compensation)
Ratio: 15/3 = 5 → DEEP
```

## Usage

### Detection Mode
```bash
venv/bin/python scripts/check_abstraction_quality.py .opencode/skills/abstraction-quality-gate   --workflow /path/to/workflow.json   --output /path/to/abstraction_report.json
```

### Report Format
```json
{
  "workflow_id": "example",
  "modules_analyzed": 5,
  "violations": [
    {
      "module": "Format Phone Number",
      "type": "Shallow Module",
      "severity": "medium",
      "depth_ratio": 0.125,
      "interface_params": 8,
      "logic_nodes": 1,
      "recommendation": "Reduce interface to 2 params; move formatting logic inside"
    },
    {
      "module": "Validate Email",
      "type": "Information Leak",
      "severity": "low",
      "leaked": "regex_pattern",
      "recommendation": "Hide regex inside; expose only validation_mode param"
    }
  ],
  "summary": {
    "deep_modules": 3,
    "shallow_modules": 1,
    "info_leaks": 1,
    "recommendation": "Refactor shallow modules; hide implementation details"
  }
}
```

## Integration with Gate Pipeline

1. **Pre-flight check**: Run `abstraction-quality-gate` before `SchemaPreflightGate`
2. **Threshold**: No shallow modules with depth_ratio < 1.5 in critical paths
3. **Fix verification**: After refactoring, re-run to confirm all modules pass depth threshold
4. **Mandatory skills**: Critical path modules must have depth_ratio ≥ 2

## Pairing Recommendations

- **With `code-smell-detector`**: Shallow modules often correlate with code smells
- **With `orthogonality-guard`**: Information hiding reduces coupling
- **With `n8n-subworkflow-modularizer`**: Deep modules are well-designed sub-workflows
- **With `n8n-schema-guardrail`**: Interface complexity validated against schema
