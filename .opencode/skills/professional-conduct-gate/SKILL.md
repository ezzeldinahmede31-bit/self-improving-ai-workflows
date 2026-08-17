---
name: professional-conduct-gate
description: "Enforces The Clean Coder's professionalism principles: honest estimation, saying no to impossible deadlines, continuous learning, test-driven development as discipline, and taking responsibility for code quality. Adds professional conduct checks to workflow builds: validates estimation realism, ensures testing discipline, checks for deadline pressure indicators. Triggers on workflow build; reports professionalism violations with severity. Pairs with: gate-first-pass-builder, verification-before-completion, tdd-sandbox-proof-engine, rate-limit-and-cost-guard."
---
# Professional Conduct Gate

The Clean Coder teaches that professionalism is a responsibility, not just a job title. This skill encodes Uncle Bob's professional conduct principles into automated checks for n8n workflow development.

## The Clean Coder Principles Enforced

### 1. Honest Estimation (Say "No" to Impossible)
- **Principle**: "The only way to go fast is to go well." Never commit to deadlines you can't meet.
- **Check**: Workflow builds with `rate-limit-and-cost-guard` must have realistic time estimates. Flag workflows that promise impossible throughput without resource scaling.

### 2. TDD as Discipline (Not Optional)
- **Principle**: "Test-driven development is not a technique. It's a discipline."
- **Check**: Every workflow must have pinned data (instant testability) AND pass `verification-before-completion` before delivery. No exceptions.

### 3. Continuous Learning (20 Hours/Week)
- **Principle**: "Professionals invest in themselves." 20 hours/week learning new tech.
- **Check**: Workflow skills referenced must be up-to-date (skill version check via `router_register.py`). Flag deprecated node types.

### 4. Responsibility for Quality
- **Principle**: "You are responsible for the quality of your code."
- **Check**: Every workflow must pass `build-gates-pipeline.py` with `READY_FOR_DEPLOYMENT`. No "ship and fix later."

### 5. No "Hero" Programming
- **Principle**: "Working late to meet a deadline you agreed to is not heroic."
- **Check**: Flag workflows with `continueOnFail` on critical paths without explicit human approval. Detect "band-aid" fixes.

## Professional Conduct Checks

### Estimation Realism Validator
```python
# Detects unrealistic promises in workflow configs
- HTTP node timeout < 1000ms → "Optimistic timeout"
- Rate limit > 1000 req/min without scaling → "Unrealistic throughput"
- Sub-workflow chain > 10 levels → "Unmaintainable depth"
```

### Testing Discipline Enforcer
```python
# Enforces TDD discipline
- No pinned data on primary nodes → "TDD violation: no instant testability"
- No Error Trigger node → "No error handling = not professional"
- Expected result missing in dry-run → "No verification = not professional"
```

### Continuous Learning Tracker
```python
# Tracks skill currency
- Node type version > 2 versions behind → "Deprecated skill"
- Skill not updated in 90 days → "Stale skill"
- Uses deprecated `moment.js` instead of `luxon` → "Outdated practice"
```

### Quality Responsibility Gate
```python
# Enforces personal responsibility
- Hardcoded secrets → "Unprofessional security practice"
- No schema cache preflight → "Skipped quality gate"
- `DRY_RUN_EVIDENCE_MISSING` → "Shipped without verification"
```

## Usage

### Detection Mode
```bash
venv/bin/python scripts/check_professionalism.py .opencode/skills/professional-conduct-gate   --workflow /path/to/workflow.json   --output /path/to/professionalism_report.json
```

### Report Format
```json
{
  "workflow_id": "example",
  "professionalism_score": 72,
  "violations": [
    {
      "principle": "Honest Estimation",
      "severity": "high",
      "issue": "HTTP timeout set to 500ms for external API",
      "recommendation": "Set realistic timeout based on SLA measurements"
    },
    {
      "principle": "TDD Discipline",
      "severity": "high",
      "issue": "No pinned data on primary HTTP node",
      "recommendation": "Add pinned data for instant testability"
    }
  ],
  "summary": {
    "score": 72,
    "grade": "C",
    "recommendation": "Address high-severity professionalism violations before delivery"
  }
}
```

## Grading Scale
- **A (90-100)**: Professional standard - ready for production
- **B (80-89)**: Good - minor improvements needed
- **C (70-79)**: Acceptable - significant professionalism gaps
- **D (60-69)**: Below standard - major violations
- **F (<60)**: Unprofessional - must not ship

## Integration with Gate Pipeline

1. **Pre-flight check**: Run `professional-conduct-gate` before `SchemaPreflightGate`
2. **Score threshold**: Minimum score 80 (grade B) required for delivery
3. **Fix verification**: After addressing violations, re-run to confirm score ≥ 80
4. **Mandatory skills**: Any `F` grade auto-blocks delivery

## Pairing Recommendations

- **With `gate-first-pass-builder`**: Professionalism checks run alongside technical gates
- **With `verification-before-completion`**: TDD discipline enforced at delivery
- **With `rate-limit-and-cost-guard`**: Estimation realism validated against cost/reliability
- **With `tdd-sandbox-proof-engine`**: TDD not optional - enforced as discipline
