#!/usr/bin/env bash
# install-deps.sh — Red/Blue Team Lab 의존성 자동 설치
# start.sh / capture-wireshark.sh에서 source 하여 사용하거나,
# 단독으로 실행 가능: bash install-deps.sh
#
# 설치 항목:
#   1. Docker Engine + Docker Compose Plugin (apt 기반)
#   2. Docker 데몬 시작 (WSL2/Linux)
#   3. tcpdump, tshark (패킷 캡처 도구)
#   4. 현재 사용자 docker 그룹 추가

# ─── sudo password ───
# 이미 SUDO_PW 변수가 설정되어 있으면 재입력 생략 (source 호출 시)
if [ -z "$SUDO_PW" ]; then
    echo "============================================"
    echo "  Red/Blue Team Lab - Dependency Installer"
    echo "============================================"
    echo ""
    read -s -p "[*] sudo password: " SUDO_PW
    echo ""
    export SUDO_PW
fi

# Verify sudo password
if ! echo "$SUDO_PW" | sudo -S true 2>/dev/null; then
    echo "[ERROR] Wrong sudo password"
    return 1 2>/dev/null || exit 1
fi

# ─── 1. Docker Engine ───
if ! command -v docker &>/dev/null; then
    echo "[!] Docker not found. Installing Docker Engine..."
    echo ""

    echo "$SUDO_PW" | sudo -S apt-get update -qq 2>/dev/null
    echo "$SUDO_PW" | sudo -S apt-get install -y -qq ca-certificates curl gnupg 2>/dev/null

    echo "$SUDO_PW" | sudo -S install -m 0755 -d /etc/apt/keyrings 2>/dev/null
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null
    echo "$SUDO_PW" | sudo -S chmod a+r /etc/apt/keyrings/docker.gpg 2>/dev/null

    ARCH=$(dpkg --print-architecture)
    CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
    echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 2>&1

    echo "$SUDO_PW" | sudo -S apt-get update -qq 2>/dev/null
    echo "$SUDO_PW" | sudo -S apt-get install -y docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin 2>/dev/null

    echo "[+] Docker installed!"
else
    echo "[+] Docker already installed"
fi

# ─── 2. Docker daemon ───
if ! echo "$SUDO_PW" | sudo -S docker info &>/dev/null; then
    echo "[*] Starting Docker daemon..."
    echo "$SUDO_PW" | sudo -S service docker start >/dev/null 2>&1
    for i in $(seq 1 10); do
        if echo "$SUDO_PW" | sudo -S docker info &>/dev/null; then
            break
        fi
        sleep 1
    done
fi

if ! echo "$SUDO_PW" | sudo -S docker info &>/dev/null; then
    echo "[ERROR] Docker daemon failed to start"
    return 1 2>/dev/null || exit 1
fi
echo "[+] Docker daemon running ($(echo "$SUDO_PW" | sudo -S docker --version 2>/dev/null))"

# ─── 3. Packet capture tools ───
NEED_CAPTURE=false
if ! command -v tcpdump &>/dev/null; then NEED_CAPTURE=true; fi
if ! command -v tshark &>/dev/null; then NEED_CAPTURE=true; fi

if $NEED_CAPTURE; then
    echo "[*] Installing packet capture tools (tcpdump, tshark)..."
    echo "$SUDO_PW" | sudo -S apt-get update -qq 2>/dev/null
    echo "$SUDO_PW" | sudo -S DEBIAN_FRONTEND=noninteractive apt-get install -y -qq tcpdump tshark 2>/dev/null
    echo "[+] Capture tools installed"
else
    echo "[+] Capture tools already installed (tcpdump, tshark)"
fi

# ─── 4. docker group ───
CURRENT_USER=$(whoami)
if ! groups "$CURRENT_USER" 2>/dev/null | grep -q docker; then
    echo "$SUDO_PW" | sudo -S usermod -aG docker "$CURRENT_USER" 2>/dev/null
    echo "[+] Added $CURRENT_USER to docker group (takes effect on next login)"
fi

# ─── 5. Docker Compose check ───
if echo "$SUDO_PW" | sudo -S docker compose version &>/dev/null; then
    echo "[+] Docker Compose available"
elif command -v docker-compose &>/dev/null; then
    echo "[+] docker-compose (standalone) available"
else
    echo "[WARN] Docker Compose not found — docker compose build/up will fail"
fi

echo ""
echo "[+] All dependencies are ready!"
echo ""
