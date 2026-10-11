#!/usr/bin/env python3
"""ts_convert.py — deterministic Unix epoch <-> ISO-8601 conversion.

Usage:
  ts_convert.py <value> [--tz Africa/Cairo]

<value>: 10-digit seconds | 13-digit ms | 19-digit ns | ISO-8601 string.
Default output zone is UTC. Exit 1 with reason on unparseable input.
"""
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

EPOCH_ANCHOR = "1970-01-01T00:00:00+00:00"


def to_iso(epoch_s: float, tz: str) -> str:
    return datetime.fromtimestamp(epoch_s, ZoneInfo(tz)).isoformat()


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--tz")]
    tz = "UTC"
    for a in sys.argv[1:]:
        if a.startswith("--tz"):
            tz = a.split("=", 1)[1] if "=" in a else sys.argv[
                sys.argv.index(a) + 1]
    if not args:
        print("usage: ts_convert.py <value> [--tz Zone]")
        return 1
    v = args[0].strip().strip("'\"")
    try:
        ZoneInfo(tz)
    except Exception:
        print(f"ERROR: unknown timezone '{tz}'")
        return 1
    try:
        if v.isdigit():
            n = len(v)
            if n <= 10:
                print(to_iso(int(v), tz))
            elif n == 13:
                print(to_iso(int(v) / 1e3, tz))
            elif n == 19:
                print(to_iso(int(v) / 1e9, tz))
            else:
                print(f"ERROR: {n}-digit number is not s/ms/ns epoch")
                return 1
        else:
            s = v.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo(tz))
            print(int(dt.timestamp()))
    except (ValueError, OverflowError, OSError) as e:
        print(f"ERROR: cannot parse '{v}': {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
