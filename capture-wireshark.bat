@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   Wireshark Capture - Red/Blue Team Lab
echo ============================================
echo.

:: Check admin privileges (needed for Npcap install)
net session >nul 2>&1
if errorlevel 1 (
    echo [*] Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ─── Step 1: Check/Install Wireshark ───
set "WS="
if exist "C:\Program Files\Wireshark\Wireshark.exe" (
    set "WS=C:\Program Files\Wireshark\Wireshark.exe"
) else if exist "C:\Program Files (x86)\Wireshark\Wireshark.exe" (
    set "WS=C:\Program Files (x86)\Wireshark\Wireshark.exe"
)

if "%WS%"=="" (
    echo [!] Wireshark not found. Installing...
    echo.

    :: Check if winget is available
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo [*] winget not available. Downloading installer directly...
        echo [*] Downloading Wireshark...
        powershell -Command "Invoke-WebRequest -Uri 'https://2.na.dl.wireshark.org/win64/Wireshark-4.4.6-x64.exe' -OutFile '%TEMP%\wireshark-installer.exe'"
        if errorlevel 1 (
            echo [ERROR] Download failed!
            echo         Please install manually: https://www.wireshark.org/download.html
            pause
            exit /b 1
        )
        echo [*] Installing Wireshark (includes Npcap)...
        "%TEMP%\wireshark-installer.exe" /S /desktopicon=yes
        timeout /t 30 /nobreak >nul
        del "%TEMP%\wireshark-installer.exe" 2>nul
    ) else (
        echo [*] Installing Wireshark via winget...
        winget install --id WiresharkFoundation.Wireshark --accept-package-agreements --accept-source-agreements
    )

    :: Re-check
    if exist "C:\Program Files\Wireshark\Wireshark.exe" (
        set "WS=C:\Program Files\Wireshark\Wireshark.exe"
    ) else (
        echo [ERROR] Wireshark installation failed!
        echo         Please install manually: https://www.wireshark.org/download.html
        echo         Make sure to install Npcap during setup.
        pause
        exit /b 1
    )

    echo [+] Wireshark installed successfully!
    echo.
) else (
    echo [+] Wireshark found: %WS%
)

:: ─── Step 2: Check Npcap ───
if not exist "C:\Program Files\Npcap\npcap.sys" (
    if not exist "C:\Windows\System32\Npcap\npcap.sys" (
        echo [!] Npcap not found. Installing...
        echo [*] Downloading Npcap...
        powershell -Command "Invoke-WebRequest -Uri 'https://npcap.com/dist/npcap-1.80.exe' -OutFile '%TEMP%\npcap-installer.exe'"
        if errorlevel 1 (
            echo [WARN] Npcap download failed. Wireshark may not capture loopback traffic.
            echo        Install manually: https://npcap.com/
        ) else (
            echo [*] Installing Npcap (loopback capture enabled)...
            "%TEMP%\npcap-installer.exe" /loopback_support=yes /S
            timeout /t 10 /nobreak >nul
            del "%TEMP%\npcap-installer.exe" 2>nul
            echo [+] Npcap installed!
        )
        echo.
    )
) else (
    echo [+] Npcap found
)

:: ─── Step 3: Start Wireshark ───
:: No port filter - capture ALL traffic to see every attack type
:: Using loopback adapter to capture localhost Docker traffic
echo.
echo ============================================
echo   Starting Wireshark - capturing ALL traffic
echo.
echo   Captures all 12 PoC attack types:
echo     SQLi, XSS, Brute Force (Web/SSH/FTP),
echo     Bot, DoS, Port Scan, Infiltration
echo ============================================
echo.

:: Try Npcap loopback first (captures all localhost Docker traffic)
:: -d flags decode non-standard ports as HTTP so attack payloads are visible
start "" "%WS%" -i "Adapter for loopback traffic capture" -k -d "tcp.port==3000,http" -d "tcp.port==5000,http" -d "tcp.port==8000,http"

echo [+] Wireshark started! (ports 3000/5000/8000 decoded as HTTP)
echo.
echo [*] If capture doesn't start automatically:
echo     1. Select interface: "Adapter for loopback traffic capture"
echo        or "Npcap Loopback Adapter"
echo     2. If using Docker with WSL: try "vEthernet (WSL)"
echo     3. Optional display filter: ip.addr == 172.20.0.0/24
echo.
echo [*] Wireshark Decode As (already applied):
echo     Analyze - Decode As - TCP port 3000 = HTTP
echo     Analyze - Decode As - TCP port 5000 = HTTP
echo     Analyze - Decode As - TCP port 8000 = HTTP
echo.
pause
