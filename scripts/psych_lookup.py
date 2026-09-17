"""Query the 2000-book psychology index. Read-only lookup for the audience OS.

Usage:
  psych_lookup.py --school persuasion-influence --top 5
  psych_lookup.py --query "no-show"
  psych_lookup.py --query "price" --school decision-behavior --top 3
"""
import argparse
import json
import os
import sys

INDEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'memory', 'psychology-books-index.json')


def load():
    with open(INDEX, encoding='utf-8') as f:
        return json.load(f)


def show(r):
    au = ', '.join(r.get('authors', [])[:2])
    print(f"#{r['rank']} {r['title'][:75]}")
    print(f"   {au[:50]} ({r.get('year')}) [{r['school']}/{r.get('tier')}]")
    print(f"   thesis({r['thesis_provenance']}): {r['thesis'][:220]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--school', default='')
    ap.add_argument('--query', default='')
    ap.add_argument('--top', type=int, default=5)
    a = ap.parse_args()
    idx = load()
    rows = idx
    if a.school:
        rows = [r for r in rows if r['school'] == a.school]
    if a.query:
        q = a.query.lower()
        rows = [r for r in rows
                if q in r['title'].lower() or q in r['thesis'].lower()]
    if not rows:
        print('NO_MATCH')
        return 1
    for r in rows[:a.top]:
        show(r)
        print()
    print(f'matched={len(rows)} shown={min(a.top, len(rows))}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
