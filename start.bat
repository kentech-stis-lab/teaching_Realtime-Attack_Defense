@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   Red/Blue Team Lab - Starting Environment
echo ============================================
echo.

:: Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo         Install Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop is not running!
    echo         Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [+] Docker is available

:: Check Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not available
    pause
    exit /b 1
)

echo [+] Docker Compose is available
echo.

:: Build images
echo [*] Building custom images... (this may take a few minutes on first run)
docker compose build
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [*] Starting all services...
docker compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services!
    pause
    exit /b 1
)

echo.
echo [*] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

:: Health checks
echo.
echo --- Service Status ---
for %%c in (juice-shop ssh-server ftp-server suricata internal-db internal-api backend dashboard) do (
    for /f "tokens=*" %%s in ('docker inspect -f "{{.State.Status}}" %%c 2^>nul') do (
        echo   %%c: %%s
    )
)

echo.
echo ============================================
echo   Lab is ready!
echo ============================================
echo.
echo   Dashboard:    http://localhost:8080
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Juice Shop:   http://localhost:3000
echo   SSH Server:   ssh admin@localhost -p 2222
echo   FTP Server:   ftp localhost 2121
echo.
echo   Run stop.bat to shut everything down
echo.

:: Open dashboard in default browser
start http://localhost:8080

pause
