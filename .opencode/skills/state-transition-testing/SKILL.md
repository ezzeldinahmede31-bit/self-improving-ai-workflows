---
name: state-transition-testing
description: "State transition testing distilled. Use when testing state machines, workflows, order status, transitions, guards, invalid events."
---

# State Transition Testing

## Purpose

Test behavior as states and guarded transitions: valid moves, invalid events, entry/exit actions, per the ISTQB state-transition technique.

## When to use

Use when the user says 'state machine', 'state transition', 'order status', 'workflow states', 'invalid transition', 'guard condition'.

## Steps

1. Draw the diagram: states as nodes, events with guards as edges.
2. Cover all valid transitions plus invalid events per state.
3. Test entry/exit actions and side effects on each move.
4. Check persistence: reload mid-flow, state must survive.
5. Fuzz event order: double-submit, cancel-after-ship, refund-twice.

## Anti-patterns

- Testing only the happy path through states.
- Guards checked in UI but not on the server transition.
- No test for illegal jumps (client forges the next state).
- State stored only in memory so reloads reset the flow.

## Example

Python:

```python
def test_cancel_after_ship_rejected():
    order = ship(Order())
    with pytest.raises(InvalidTransition):
        cancel(order)
```

JS:

```js
expect(() => cancel(shippedOrder())).toThrow(InvalidTransition);
```

## Verification

Transition table fully covered, invalid events rejected server-side, reload-safe, abuse orderings tested.

## Pairs-with

beizer-domain-testing, api-testing-contract-patterns, state-machine-persistence, decision-table-testing.
