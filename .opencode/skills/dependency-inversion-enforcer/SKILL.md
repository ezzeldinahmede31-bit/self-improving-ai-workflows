---
name: dependency-inversion-enforcer
description: "Enforces Clean Architecture's core principle: Dependency Rule - source code dependencies must point inward, never outward. Inner layers (business logic) must not depend on outer layers (frameworks, databases, UI, external APIs). In n8n workflows, this means business logic nodes must not directly depend on specific API nodes, database nodes, or UI nodes. Triggers on workflow build; reports dependency violations with severity. Pairs with: gate-first-pass-builder, orthogonality-guard, n8n-subworkflow-modularizer, n8n-credential-security-guard."
---
# Dependency Inversion Enforcer

Clean Architecture's fundamental rule: **Dependencies must point inward**. The inner layers (Entities, Use Cases) contain business rules and should not know about outer layers (Interface Adapters, Frameworks, Databases, External APIs). This skill enforces this rule in n8n workflow design.

## Clean Architecture Layers (Applied to n8n)

### Inner Layers (Business Rules - Must Not Depend on Outer)
1. **Entities** (Enterprise Business Rules): Core domain objects, validation rules
2. **Use Cases** (Application Business Rules): Orchestration of entities, workflow logic

### Outer Layers (Details - Can Depend on Inner)
3. **Interface Adapters**: Convert data between inner and outer formats
4. **Frameworks & Drivers**: HTTP clients, Database drivers, UI frameworks, External APIs

## Dependency Rule Enforcement

### Rule 1: Inner Must Not Know Outer
```python
# VIOLATION: Use Case node directly calls HTTP Request node
# Use Case (inner) → HTTP Request (outer) = BAD

# CORRECT: Use Case → Interface Adapter → HTTP Request
# Use Case (inner) → Interface Adapter (middle) → HTTP Request (outer)
```

### Rule 2: Dependencies Point Inward via Interfaces
```python
# Use Case defines interface: "I need to send notification"
# Interface Adapter implements: "SendGrid sends notification"
# HTTP Request is hidden behind interface
```

### Rule 3: No Framework Leakage into Business Logic
```python
# VIOLATION: Business logic node contains SendGrid-specific fields
# CORRECT: Business logic uses generic "Notification" abstraction
```

## Dependency Violation Detection

### Direct Framework Coupling (High Severity)
```python
# Business logic node directly uses:
- n8n-nodes-base.httpRequest (instead of abstraction)
- n8n-nodes-base.postgres (instead of repository interface)
- n8n-nodes-base.sendGrid (instead of notification service)
- n8n-nodes-base.googleSheets (instead of storage abstraction)
```

### Database in Business Logic (High Severity)
```python
# Use Case contains:
- Direct SQL queries
- Table/column names
- Connection strings
```

### External API in Business Logic (High Severity)
```python
# Business logic contains:
- API endpoint URLs
- Authentication logic for specific APIs
- Request/response format parsing for specific services
```

### UI/Trigger in Business Logic (Medium Severity)
```python
# Business logic contains:
- Webhook parsing logic
- Form validation specific to UI framework
- Response formatting for specific clients
```

## Enforcement Strategies

### Strategy 1: Repository Pattern Enforcement
```
Instead of: Business Logic → Postgres Node
Use: Business Logic → Repository Interface → Postgres Adapter → Postgres Node
```

### Strategy 2: Service Abstraction
```
Instead of: Business Logic → SendGrid Node
Use: Business Logic → Notification Service Interface → SendGrid Adapter → SendGrid Node
```

### Strategy 3: Interface Adapter Layer
```
Every external dependency gets an adapter:
- HTTP Adapter: wraps httpRequest with retry, timeout, error handling
- Database Adapter: wraps postgres with connection pooling, transactions
- API Adapter: wraps specific API with auth, rate limiting, parsing
```

## Usage

### Detection Mode
```bash
venv/bin/python scripts/check_dependency_inversion.py .opencode/skills/dependency-inversion-enforcer   --workflow /path/to/workflow.json   --output /path/to/dependency_report.json
```

### Report Format
```json
{
  "workflow_id": "example",
  "layers_detected": {
    "entities": ["User", "Order"],
    "use_cases": ["ProcessOrder"],
    "interface_adapters": ["OrderRepository", "NotificationService"],
    "frameworks": ["Postgres", "SendGrid", "HTTP"]
  },
  "violations": [
    {
      "type": "Direct Framework Coupling",
      "severity": "high",
      "inner_layer": "Use Cases",
      "outer_layer": "Frameworks",
      "node": "ProcessOrder",
      "depends_on": "n8n-nodes-base.httpRequest",
      "recommendation": "Extract HTTP calls to Interface Adapter layer"
    },
    {
      "type": "Database in Business Logic",
      "severity": "high",
      "node": "ValidateUser",
      "depends_on": "n8n-nodes-base.postgres",
      "recommendation": "Extract to Repository Interface + Adapter"
    }
  ],
  "summary": {
    "total_violations": 2,
    "high_severity": 2,
    "recommendation": "All business logic must depend on abstractions, not concrete implementations"
  }
}
```

## Integration with Gate Pipeline

1. **Pre-flight check**: Run `dependency-inversion-enforcer` before `SchemaPreflightGate`
2. **Threshold**: Zero high-severity inward dependency violations allowed
2. **Fix verification**: After extracting adapters, re-run to confirm exit 0
3. **Mandatory skills**: Any direct inner→outer dependency blocks delivery

## Pairing Recommendations

- **With `orthogonality-guard`**: Dependency inversion reduces coupling
- **With `n8n-subworkflow-modularizer`**: Clean layers implemented as sub-workflows
- **With `n8n-credential-security-guard`**: Credentials stay in outer layer (adapters)
- **With `gate-first-pass-builder`**: Architecture validation runs alongside technical gates
