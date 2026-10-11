#!/bin/bash
# run_all.sh — ONE command to run the full permanent QA suite from a clean env.
# Usage: bash FINAL_AUDIT/qa/run_all.sh [--no-ai]
# Requires: project venv, node, docker (for temp redis), NO paid APIs.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY="venv/bin/python"
echo "=== [1/8] static audit ==="
$PY scripts/clinic_audit.py || exit 1
echo "=== [2/8] functional ==="
$PY FINAL_AUDIT/qa/test_functional.py || exit 1
echo "=== [3/8] temp redis up ==="
docker rm -f redis-test-tmp >/dev/null 2>&1
docker run -d --name redis-test-tmp -p 16379:6379 redis:7-alpine >/dev/null
sleep 5
echo "=== [4/8] concurrency ==="
$PY FINAL_AUDIT/qa/test_concurrency.py || { docker rm -f redis-test-tmp >/dev/null 2>&1; exit 1; }
echo "=== [5/8] compensation+authz ==="
$PY FINAL_AUDIT/qa/test_comp_authz.py || { docker rm -f redis-test-tmp >/dev/null 2>&1; exit 1; }
echo "=== [6/8] security ==="
$PY FINAL_AUDIT/qa/test_security.py || { docker rm -f redis-test-tmp >/dev/null 2>&1; exit 1; }
echo "=== [7/8] ops+faults ==="
$PY FINAL_AUDIT/qa/test_ops.py || { docker rm -f redis-test-tmp >/dev/null 2>&1; exit 1; }
echo "=== [8/8] perf+files+mutation ==="
$PY FINAL_AUDIT/qa/test_perf_files.py || { docker rm -f redis-test-tmp >/dev/null 2>&1; exit 1; }
$PY FINAL_AUDIT/qa/test_mutation.py || { docker rm -f redis-test-tmp >/dev/null 2>&1; exit 1; }
docker rm -f redis-test-tmp >/dev/null 2>&1
echo "ALL SUITES GREEN"
if [ "${1:-}" != "--no-ai" ]; then
  echo "NOTE: AI eval (300 cases) runs separately (free-tier dependent):"
  echo "  venv/bin/python FINAL_AUDIT/qa/test_ai_eval.py --chunk N/6"
fi
