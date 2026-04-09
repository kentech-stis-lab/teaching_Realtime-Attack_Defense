#!/usr/bin/env bash
set -e

echo "============================================"
echo "  Red/Blue Team Lab - Starting Environment"
echo "============================================"
echo ""

# ─── sudo password prompt ───
read -s -p "[*] sudo password: " SUDO_PW
echo ""
export SUDO_PW

# ─── Install all dependencies (Docker, tcpdump, tshark, etc.) ───
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/install-deps.sh"

# ─── Docker Compose detection ───
if echo "$SUDO_PW" | sudo -S docker compose version &>/dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
else
    echo "[ERROR] Docker Compose is not installed"
    exit 1
fi

# ─── Build & Start ───
echo "[*] Building custom images... (first run may take a few minutes)"
echo "$SUDO_PW" | sudo -S $COMPOSE build 2>&1

echo ""
echo "[*] Starting all services..."
echo "$SUDO_PW" | sudo -S $COMPOSE up -d 2>&1

echo ""
echo "[*] Waiting for services to be ready..."
sleep 5

# Health checks
echo ""
echo "--- Service Status ---"
for container in juice-shop ssh-server ftp-server suricata internal-db internal-api backend dashboard; do
    status=$(echo "$SUDO_PW" | sudo -S docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "not found")
    printf "  %-20s %s\n" "$container" "$status"
done

echo ""
echo "============================================"
echo "  Lab is ready!"
echo "============================================"
echo ""
echo "  Dashboard:    http://localhost:8080"
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Juice Shop:   http://localhost:3000"
echo "  SSH Server:   ssh admin@localhost -p 2222"
echo "  FTP Server:   ftp localhost 2121"
echo ""
echo "  Run ./stop.sh to shut everything down"
echo "  Run ./capture-wireshark.sh to capture packets"
echo ""
