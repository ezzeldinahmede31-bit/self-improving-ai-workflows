#!/usr/bin/env bash
# Google Calendar OAuth Auto-Reconnect — systemd service installer
# Run: sudo bash install_google_calendar_daemon.sh

set -euo pipefail

PROJ="/home/ezzeldin/Documents/Default Project"
SERVICE_NAME="google-calendar-oauth"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PYTHON="${PROJ}/venv/bin/python"
SCRIPT="${PROJ}/scripts/google_calendar_oauth.py"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Verify project exists
if [[ ! -f "${SCRIPT}" ]]; then
    echo "Project not found at ${PROJ}"
    exit 1
fi

# Create systemd service
cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Google Calendar OAuth Auto-Reconnect for n8n
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=ezzeldin
WorkingDirectory=${PROJ}
ExecStart=${PYTHON} ${SCRIPT} daemon 300
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

# Resource limits
MemoryMax=100M
CPUQuota=10%

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl start "${SERVICE_NAME}"

echo "✓ Service installed and started: ${SERVICE_NAME}"
echo "  Status: systemctl status ${SERVICE_NAME}"
echo "  Logs: journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "⚠️  REQUIRED: Add Google OAuth credentials to ${PROJ}/.env:"
echo "  GOOGLE_CLIENT_ID=your_client_id"
echo "  GOOGLE_CLIENT_SECRET=your_client_secret"
echo ""
echo "Then restart: systemctl restart ${SERVICE_NAME}"