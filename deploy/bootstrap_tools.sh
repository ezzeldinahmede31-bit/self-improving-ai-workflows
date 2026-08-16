#!/usr/bin/env bash
# Bootstrap the open-source tool stack for the JIT architect (Linux Mint + Docker).
#
#   Phase 1: docker compose stack (LiteLLM proxy, Prism mock, Qdrant)
#   Phase 2: docker pulls for security scanners
#   Phase 3: optional git clones (PyRIT, garak, LightRAG) into ./vendor/
#
# Idempotent: safe to re-run. Skips anything already present.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENDOR="$ROOT/vendor"

echo "==[1/3] Docker compose stack =="
docker compose -f "$ROOT/deploy/docker-compose.yml" --profile default up -d

echo "==[2/3] Security scanner images =="
docker pull projectdiscovery/nuclei:latest
docker pull ghcr.io/semgrep/semgrep:latest

echo "==[3/3] Optional vendor sources (git clone) =="
mkdir -p "$VENDOR"

clone_or_skip() {
  local name="$1"; local url="$2"
  if [ -d "$VENDOR/$name/.git" ]; then
    echo "  skip  $name (already cloned)"
    return 0
  fi
  echo "  clone $name"
  git clone --depth 1 "$url" "$VENDOR/$name"
}

clone_or_skip PyRIT https://github.com/Azure/PyRIT
clone_or_skip garak  https://github.com/NVIDIA/garak
clone_or_skip LightRAG https://github.com/HKUDS/LightRAG

cat <<EOF

Done. Tool layer ready:
  LiteLLM  http://localhost:4000   (edit deploy/litellm_config.yaml + DEEPSEEK_API_KEY)
  Prism    http://localhost:4010   (serve your OpenAPI spec in deploy/api-spec.yaml)
  Qdrant   http://localhost:6333   (dashboard http://localhost:6333/dashboard)
  Nuclei   docker run projectdiscovery/nuclei:latest -u <target>
  Semgrep  docker run --rm -v "\$PWD:/src" ghcr.io/semgrep/semgrep:latest scan /src
EOF