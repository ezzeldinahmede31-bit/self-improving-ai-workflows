---
name: async-testing-patterns
description: "Async code testing patterns distilled. Use when testing promises, async await, event loops, timeouts, cancellation, concurrent tasks."
---

# Async Testing Patterns

## Purpose

Test asynchronous code reliably: await real completion, control clocks, cover cancellation and rejection paths, forbid floating promises.

## When to use

Use when the user says 'async test', 'promise test', 'await', 'event loop', 'cancellation', 'timeout test', 'asyncio'.

## Steps

1. Await completion explicitly; never assert on pending state.
2. Use fake timers for delays, debounces, and retries.
3. Cover rejection, cancellation, and timeout paths, not only success.
4. Fail on unhandled rejections and floating promises in CI.
5. Test ordering guarantees where the contract promises them.

## Anti-patterns

- Fixed sleeps standing in for synchronization.
- Real timers making suites slow and flaky.
- Unhandled rejections ignored outside strict mode.
- Fire-and-forget tasks with no observable completion.

## Example

JS (vitest fake timers):

```js
vi.useFakeTimers();
const p = refreshSoon();
await vi.runAllTimersAsync();
await expect(p).resolves.toBe('done');
```

Python: `anyio`/`asyncio` test with `await` plus `pytest.raises(TimeoutError)` paths.

## Verification

No real-timer sleeps, rejection paths covered, unhandled rejections fail CI, ordering contracts asserted.

## Pairs-with

concurrency-testing-patterns, retry-backoff-jitter, timeout-graceful-degradation, flaky-test-elimination.
