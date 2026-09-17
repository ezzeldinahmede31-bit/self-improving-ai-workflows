"""Query the book indexes (psychology 3000 + marketing 3000). Read-only lookup.

Usage:
  psych_lookup.py --school persuasion-influence --top 5 [--lib psych|marketing|all]
  psych_lookup.py --query "price" [--lib all]
"""
import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBS = {'psych': 'memory/psychology-books-index.json',
        'marketing': 'memory/marketing-books-index.json'}


def load(lib):
    with open(os.path.join(BASE, LIBS[lib]), encoding='utf-8') as f:
        return json.load(f)


def show(r):
    au = ', '.join(r.get('authors', [])[:2])
    print(f"#{r['rank']} {r['title'][:75]}")
    print(f"   {au[:50]} ({r.get('year')}) [{r.get('_lib', '?')}/{r['school']}/{r.get('tier')}]")
    print(f"   thesis({r['thesis_provenance']}): {r['thesis'][:220]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--school', default='')
    ap.add_argument('--query', default='')
    ap.add_argument('--top', type=int, default=5)
    ap.add_argument('--lib', default='all', choices=['psych', 'marketing', 'all'])
    a = ap.parse_args()
    libs = ['psych', 'marketing'] if a.lib == 'all' else [a.lib]
    idx = []
    for lib in libs:
        for r in load(lib):
            r = dict(r)
            r['_lib'] = lib
            idx.append(r)
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
