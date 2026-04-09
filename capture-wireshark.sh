#!/usr/bin/env bash
# Packet Capture - Red/Blue Team Lab
# Captures Docker internal container traffic (all attack PoC packets)
#
# IMPORTANT: 공격 payload(예: ' OR 1=1--)는 Docker 내부 backend-net (172.20.1.0/24)에서
# 발생합니다. Windows Wireshark로는 이 트래픽을 볼 수 없으며, 이 스크립트를 WSL2에서
# 실행해야 합니다. pcap 파일로 저장 후 Windows Wireshark에서 열 수 있습니다.

echo "============================================"
echo "  Packet Capture - Red/Blue Team Lab"
echo "============================================"
echo ""

# ─── sudo password prompt ───
read -s -p "[*] sudo password: " SUDO_PW
echo ""
export SUDO_PW

# ─── Install all dependencies (Docker, tcpdump, tshark, etc.) ───
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/install-deps.sh"

# ─── Check Docker is running ───
if ! echo "$SUDO_PW" | sudo -S docker info &>/dev/null; then
    echo "[ERROR] Docker is not running. Run ./start.sh first."
    exit 1
fi

# ─── Find Docker bridge interfaces ───
FRONTEND_IFACE=""
BACKEND_IFACE=""

for NET_NAME in $(echo "$SUDO_PW" | sudo -S docker network ls --format '{{.Name}}' 2>/dev/null); do
    NET_ID=$(echo "$SUDO_PW" | sudo -S docker network inspect "$NET_NAME" --format '{{.Id}}' 2>/dev/null | head -c 12)
    CANDIDATE="br-${NET_ID}"
    if ! ip link show "$CANDIDATE" &>/dev/null 2>&1; then
        continue
    fi
    if echo "$NET_NAME" | grep -q "frontend-net"; then
        FRONTEND_IFACE="$CANDIDATE"
        echo "[+] frontend-net bridge: $FRONTEND_IFACE"
    elif echo "$NET_NAME" | grep -q "backend-net"; then
        BACKEND_IFACE="$CANDIDATE"
        echo "[+] backend-net bridge:  $BACKEND_IFACE"
    fi
done

if [ -z "$BACKEND_IFACE" ] && [ -z "$FRONTEND_IFACE" ]; then
    echo "[ERROR] Could not find Docker bridge interfaces. Is the lab running?"
    echo "        Run ./start.sh first."
    exit 1
fi

echo ""
echo "Capture mode:"
echo "  1) tshark - terminal verbose output (recommended, shows payload)"
echo "  2) tshark → pcap file (save to .pcap, open in Wireshark)"
echo "  3) tcpdump - lightweight hex dump"
echo "  4) wireshark - GUI window (Linux only)"
echo ""
read -p "Choice [1]: " MODE
MODE=${MODE:-1}

echo ""
echo "============================================"
echo "  Capturing ALL Docker internal traffic"
echo ""
echo "  *** 공격 payload는 backend-net에서 발생합니다 ***"
echo ""
echo "  backend-net (172.20.1.0/24) - attack payload traffic:"
echo "    172.20.1.100 Backend → executes attacks"
echo "    172.20.1.10  Juice Shop (3000) ← SQLi/XSS/BruteWeb/Bot/DoS"
echo "    172.20.1.30  internal-api (5000) ← Infiltration"
echo "    172.20.1.20  MySQL (3306) ← Infiltration"
echo ""
echo "  frontend-net (172.20.0.0/24) - network attacks:"
echo "    172.20.0.11 SSH server (2222) ← SSH Brute Force"
echo "    172.20.0.12 FTP server (21) ← FTP Brute Force"
echo "============================================"
echo ""
echo "  Press Ctrl+C to stop capture"
echo ""

# HTTP decode flags for non-standard ports
# Without these, ports 3000/5000/8000 are treated as raw TCP
# and http display filters won't match attack payloads.
DECODE_HTTP="-d tcp.port==3000,http -d tcp.port==5000,http -d tcp.port==8000,http"

case $MODE in
    4)
        if ! command -v wireshark &>/dev/null; then
            echo "[*] Installing Wireshark..."
            echo "$SUDO_PW" | sudo -S DEBIAN_FRONTEND=noninteractive apt-get install -y -qq wireshark 2>/dev/null
            echo "$SUDO_PW" | sudo -S dpkg-reconfigure -f noninteractive wireshark-common 2>/dev/null
            echo "$SUDO_PW" | sudo -S usermod -aG wireshark "$(whoami)" 2>/dev/null
        fi
        echo "$SUDO_PW" | sudo -S wireshark \
            -i "$BACKEND_IFACE" -i "$FRONTEND_IFACE" -k \
            $DECODE_HTTP &
        echo "[+] Wireshark started (ports 3000/5000/8000 decoded as HTTP)."
        echo "    Run attacks from the dashboard!"
        wait
        ;;
    3)
        echo "$SUDO_PW" | sudo -S tcpdump -i any -nn -X -l \
            '(net 172.20.0.0/24 or net 172.20.1.0/24) and not arp'
        ;;
    2)
        PCAP_FILE="$SCRIPT_DIR/capture_$(date +%Y%m%d_%H%M%S).pcap"
        echo "[*] Saving to: $PCAP_FILE"
        echo "[*] Run attacks from the dashboard, then Ctrl+C to stop."
        echo "[*] Open the .pcap file in Wireshark to analyze."
        echo ""
        echo "[TIP] Wireshark에서 열 때:"
        echo "  1. Analyze → Decode As → TCP port 3000 = HTTP"
        echo "  2. Display filter: ip.dst == 172.20.1.10 && http"
        echo "  3. 패킷 우클릭 → Follow → HTTP Stream으로 payload 확인"
        echo ""
        echo "$SUDO_PW" | sudo -S tshark -i any \
            -f "net 172.20.0.0/24 or net 172.20.1.0/24" \
            -w "$PCAP_FILE" $DECODE_HTTP
        echo ""
        echo "[+] Capture saved to: $PCAP_FILE"
        echo "    Open in Wireshark: wireshark $PCAP_FILE"
        ;;
    *)
        echo "$SUDO_PW" | sudo -S tshark -i any \
            -f "net 172.20.0.0/24 or net 172.20.1.0/24" \
            $DECODE_HTTP -V
        ;;
esac
