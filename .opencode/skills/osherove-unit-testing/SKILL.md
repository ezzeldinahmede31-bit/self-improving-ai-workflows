---
name: osherove-unit-testing
description: "Roy Osherove Art of Unit Testing distilled. Use when writing or reviewing unit tests, test doubles, mocks vs stubs vs fakes, trustable tests, maintainability."
---

# Osherove Unit Testing

## Purpose

Write unit tests that are trustable, maintainable, and readable per Roy Osherove (Art of Unit Testing 3rd ed): AAA pattern, test doubles taxonomy, isolation.

## When to use

Use when the user says 'unit test', 'mock', 'stub', 'fake', 'AAA', 'trustable test', 'test maintainability', 'Osherove', or reviews a unit suite.

## Steps

1. Structure every test as Arrange-Act-Assert with one logical assert.
2. Classify each double: stub (feed data in), mock (verify interaction out), fake (working shortcut, e.g. in-memory repo).
3. Isolate the unit under test: seam out filesystem, clock, network, randomness.
4. Name tests as UnitOfWork_StateUnderTest_ExpectedBehavior.
5. Check the 3 pillars: trustable (no logic, no flakes), maintainable (readable, DRY helpers), readable (intent clear).

## Anti-patterns

- Mocks for everything (overspecification); prefer stubs + state verification.
- Multiple Act steps or assertions covering different behaviors in one test.
- Logic inside tests (if/loops) that needs its own tests.
- Testing private methods directly instead of via observable behavior.

## Example

Python (pytest, stub + AAA):

```python
def test_calculate_total_empty_cart_returns_zero():
    # Arrange
    cart = []  # stub data
    # Act
    result = calculate_total(cart)
    # Assert
    assert result == 0
```

JS (vitest, mock verification):

```js
test('checkout_calls_payment_gateway_once', () => {
  const gateway = { charge: vi.fn() }; // mock
  checkout([], gateway);               // Act
  expect(gateway.charge).toHaveBeenCalledTimes(1);
});
```

## Verification

Each new test: AAA visible, double type named, name follows convention, passes plus one mutation (break prod code, test must fail).

## Pairs-with

xunit-test-patterns, test-smells-catalog, khorikov-unit-testing, okken-pytest-craft, python-testing-patterns.
