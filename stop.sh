#!/usr/bin/env bash
set -e

echo "============================================"
echo "  Red/Blue Team Lab - Stopping Environment"
echo "============================================"
echo ""

# ─── sudo password prompt ───
read -s -p "[*] sudo password: " SUDO_PW
echo ""

if ! echo "$SUDO_PW" | sudo -S true 2>/dev/null; then
    echo "[ERROR] Wrong sudo password"
    exit 1
fi

if echo "$SUDO_PW" | sudo -S docker compose version &>/dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
else
    echo "[ERROR] Docker Compose is not installed"
    exit 1
fi

echo "[*] Stopping and removing all containers..."
echo "$SUDO_PW" | sudo -S $COMPOSE down 2>&1

echo ""
echo "[+] All services stopped."
echo "[*] To also remove volumes: sudo $COMPOSE down -v"
echo ""
