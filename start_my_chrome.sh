#!/bin/bash
# Start YOUR Chrome with YOUR profile + remote debugging
# Run this once per session, then the agent connects automatically

echo "🛑 Closing existing Chrome..."
pkill -f "chrome" 2>/dev/null
sleep 2

echo "🚀 Starting YOUR Chrome with YOUR profile (Ezzeldin Ali)..."
nohup google-chrome \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir="/home/ezzeldin/.config/google-chrome-debug" \
  --no-first-run \
  --no-default-browser-check \
  > /tmp/chrome-debug.log 2>&1 &

sleep 3

echo "✅ Verifying CDP connection..."
curl -s http://127.0.0.1:9222/json/version | head -5

echo ""
echo "🎯 Ready! Your Chrome is running with:"
echo "   - Google account: Ezzeldin Ali (logged in)"
echo "   - n8n: https://ezzeldin8n.ezzeldin8n.cfd (logged in)"
echo "   - CDP port: 9222"
echo ""
echo "Agent will connect automatically via Playwright MCP"
