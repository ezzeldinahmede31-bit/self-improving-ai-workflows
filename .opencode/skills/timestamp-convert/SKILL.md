---
name: timestamp-convert
description: "Converts between Unix timestamps (seconds/milliseconds/nanoseconds, auto-detected) and ISO-8601 datetimes, in UTC or Africa/Cairo. Use when the user asks 'convert this timestamp', 'what time is 1760100000', 'epoch to date', 'ISO to unix', 'كام الساعة بالـ epoch', 'حول الطابع الزمني', or pastes a bare 10/13/19-digit number asking for its date."
---

# Timestamp Convert

Deterministic timestamp conversion — never guess the unit, never mental-math
the date. One script, exact output.

## Steps

1. Detect the input shape:
   - 10 digits → seconds, 13 digits → milliseconds, 19 digits → nanoseconds.
   - Contains `T`/`-`/`:`/`Z` → ISO-8601 string → convert to epoch.
2. Run (never compute by hand):
   `venv/bin/python .opencode/skills/timestamp-convert/scripts/ts_convert.py <value> [--tz Africa/Cairo]`
   Default timezone is UTC; pass `--tz Africa/Cairo` when the user speaks of
   local/Egypt time.
3. Quote the script output verbatim. On script error, report the error text
   and stop (do not fall back to guessing).

## Verification

- `ts_convert.py 0` prints `1970-01-01T00:00:00+00:00` (epoch zero anchor).
- Round-trip: ISO output fed back in returns the original epoch.

## Pairs with

- `skill-forge` — built end-to-end by the forge pipeline (eval 1.00, delta +0.83).
- `off-by-one-boundary-guard` — ms/s/ns unit mistakes are boundary errors.
- `evidence-over-memory` — run the script instead of recalling dates.
