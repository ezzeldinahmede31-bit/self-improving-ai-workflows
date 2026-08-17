---
name: law-of-demeter-guard
description: "Enforces Clean Code's Law of Demeter principle: objects should only talk to their immediate friends (direct dependencies). Prevents chaining method calls like a.getB().getC().doSomething() which violate separation of concerns and increase coupling. Use when designing n8n workflows with AI agents, building class structures, or any code that risks transitive navigation of dependencies. Trigger phrases: 'law of demeter', 'demeter rule', 'train wreck', 'chaining method calls', 'avoid transitive navigation', 'limit object collaboration'."
---
# Law of Demeter Guard

The Law of Demeter (LoD) principle states that an object should have limited knowledge about the internal structure of what it touches. In practice: **don't write `a.getB().getC().doSomething()`** — instead, expose a single method on `a` that orchestrates the inner calls, or let `b` call `c` directly.

## Clean Code Alignment

Clean Code's "Data/Object Anti-Symmetry" chapter (Chapter 6) highlights the anti-symmetry between objects and data structures:
- **Objects** hide data and expose functions
- **Data structures** expose data and have no significant behavior

The Law of Demeter extends this by limiting how deeply objects navigate each other's internals.

## LoD Violations to Avoid

### Train Wrecks
- `nodeA.getB().getC().doSomething()` — chaining three or more method calls
- `workflow.getNode('X').getNode('Y').getNode('Z').execute()` — n8n transitive navigation
- `user.getAddress().getCity().getPostalCode()` — deep object graph traversal

### Safe Alternatives
- Expose a single method on the root object: `nodeA.executeTask()`
- Use helper functions that accept only what they need: `process(nodeA)`
- In n8n: prefer connecting nodes directly via `$node['X'].json` rather than chaining expressions

## LoD Enforcement Checklist (run before finalizing any object interaction)

### 1. Inspect method call chains
- Count the depth of `.method().method().method()` chains in the code
- If depth ≥ 3 → FAIL: rewrite to reduce depth to ≤ 2 or expose a root-level method

### 2. Check n8n expression chaining
- `{{ $node['A'].item.json.field1 }}` → OK (depth 1 from trigger)
- `{{ $node['A'].item.json.field1.nodeB.field2 }}` → FAIL: depth 3+; rewrite as separate expression or root method

### 3. Verify class dependency boundaries
- For each class, list its direct collaborators (friends per Law of Demeter)
- Ensure the class does not reference attributes of collaborators' collaborators

### 4. Refactor to reduce coupling
- Extract the chained logic into a new method on the root object
- Use the **Pure Data Pattern**: pass only data needed, not the whole object
- In n8n: use `$json` directly rather than navigating `.item.json.nodeX.field`

## LoD Enforcement in n8n Workflows

### Before (Violation)
```javascript
// Chaining 3+ nodes to get a value
$node['Webhook'].item.json.user.getAddress().getCity().population
```

### After (Compliant)
```javascript
// Single method exposure, or separate steps
// Option 1: Expose on root
$node['Webhook'].item.json.userProfile.population

// Option 2: Two-step extraction
const city = $node['Webhook'].item.json.user.getAddress().city;
$node['Set'].json.population = city.population;
```

## LoD and Separation of Concerns

Clean Code pairs LoD with **Single Responsibility Principle**: each object/class should have one reason to change. LoD enforces this by limiting what an object knows about others' internals — this naturally limits each object's responsibilities and changes.

## Rules of Engagement

1. **Gate before finalizing any object interaction**: Count the method call depth; if ≥ 3, rewrite
2. **Prefer root-level methods** over transitive navigation
3. **In n8n**: use `$json` and direct node connections over expression chaining
4. **Pair with `n8n-syntax-v2-enforcer`** to ensure expression syntax is also clean
5. **Pair with `single-responsibility-validator`** (if added) to verify each node does one thing