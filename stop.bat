@echo off
chcp 65001 >nul 2>&1
echo ============================================
echo   Red/Blue Team Lab - Stopping Environment
echo ============================================
echo.

echo [*] Stopping and removing all containers...
docker compose down

echo.
echo [+] All services stopped.
echo [*] To also remove volumes: docker compose down -v
echo.

pause
