#!/usr/bin/env bash
# Re-activate clinic workflows after host reboot (n8n does not always
# reactivate on startup). Safe to run anytime (activation is idempotent).
# Installed as: @reboot /home/ezzeldin/Documents/Default\ Project/scripts/n8n_reactivate.sh
set -u
PROJ="/home/ezzeldin/Documents/Default Project"
IDS="NVERkpgeFbzVrN1S Jy8EYH1uLoap9nU3 Jiyz8PIjggRnvTzB 4sfcxJL7rF14JXWt"
# wait for n8n (max ~5 min)
for _ in $(seq 1 60); do
  if curl -s -m 5 -o /dev/null http://localhost:5677/healthz; then break; fi
  sleep 5
done
API_KEY=$(grep '^N8N_API_KEY=' "$PROJ/.env" | cut -d= -f2)
for id in $IDS; do
  curl -s -m 20 -o /dev/null -w "$id:%{http_code}\n" -X POST \
    "http://localhost:5677/api/v1/workflows/$id/activate" \
    -H "X-N8N-API-KEY: $API_KEY" -H 'Content-Type: application/json' -d '{}'
done
