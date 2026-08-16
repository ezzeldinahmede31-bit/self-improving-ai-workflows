#!/usr/bin/env bash
# memory-sync.sh — FREE, ACCOUNTLESS, CLOUD memory sync via rentry.co.
#   pull   -> fetch latest memory from cloud (run at session start)
#   push   -> write memory + skills index to cloud (run after significant work)
#   init   -> create the cloud page if it doesn't exist yet
#
# Backend: rentry.co (free, no account, no keys). The page is public-read;
# writing requires the edit_code, which is stored locally in memory/.state
# (gitignored) and never leaves this machine.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

SLUG="${MEMORY_SLUG:-opencode-default-project-memory}"
STATE_FILE="memory/.state"
LOCAL_MEMORY="memory/conversation-memory.md"
PAGE_URL="https://rentry.co/${SLUG}"
RAW_URL="${PAGE_URL}/raw"

get_edit_code() {
  if [ -f "$STATE_FILE" ]; then
    cat "$STATE_FILE"
  else
    echo ""
  fi
}

save_edit_code() {
  echo "$1" > "$STATE_FILE"
  chmod 600 "$STATE_FILE"
}

fetch_raw() {
  curl -s --max-time 20 "$RAW_URL" 2>/dev/null || true
}

cloud_exists() {
  local raw
  raw="$(fetch_raw)"
  # rentry returns the page text; a nonexistent slug returns an error page
  [ -n "$raw" ] && ! printf '%s' "$raw" | grep -q "not found"
}

do_pull() {
  echo "[memory] pulling from ${PAGE_URL} ..."
  local raw
  raw="$(fetch_raw)"
  if [ -n "$raw" ] && printf '%s' "$raw" | grep -qv "404\|not found"; then
    printf '%s\n' "$raw" > "$LOCAL_MEMORY"
    echo "[memory] local copy updated ($(wc -c < "$LOCAL_MEMORY") bytes)"
  else
    echo "[memory] no cloud copy yet — keeping local file."
  fi
}

do_push() {
  local code
  code="$(get_edit_code)"
  if [ -z "$code" ]; then
    echo "[memory] ERROR: no edit_code found. Run '$0 init' first or set MEMORY_EDIT_CODE."
    exit 1
  fi
  echo "[memory] pushing to ${PAGE_URL} ..."
  local resp
  resp="$(curl -s -X POST \
    -F "url=${SLUG}" \
    -F "edit_code=${code}" \
    --form-string "text=$(cat "$LOCAL_MEMORY")" \
    https://rentry.co/api/edit)"
  if printf '%s' "$resp" | grep -q '"content": "OK"'; then
    echo "[memory] pushed OK"
  else
    echo "[memory] push failed: $resp"
    exit 1
  fi
}

do_init() {
  local code
  code="$(get_edit_code)"
  if [ -z "$code" ]; then
    echo "[memory] creating cloud page ${SLUG} ..."
    local resp
    resp="$(curl -s -X POST \
      -F "url=${SLUG}" \
      -F "title=OpenCode Default Project - Conversation Memory" \
      --form-string "text=$(cat "$LOCAL_MEMORY")" \
      https://rentry.co/api/new)"
    code="$(printf '%s' "$resp" | sed -n 's/.*"edit_code": "\([^"]*\)".*/\1/p')"
    if [ -n "$code" ]; then
      save_edit_code "$code"
      echo "[memory] page created at ${PAGE_URL} (edit_code stored in ${STATE_FILE})"
    else
      echo "[memory] init failed: $resp"
      exit 1
    fi
  else
    echo "[memory] page already initialized (${PAGE_URL}) — running push instead."
    do_push
  fi
}

ACTION="${1:-pull}"
case "$ACTION" in
  pull) do_pull ;;
  push) do_push ;;
  init) do_init ;;
  *) echo "usage: $0 [pull|push|init]"; exit 1 ;;
esac