@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0A
title UNS-ClaudeJP 5.2 - MONITOR DE LOGS EN VIVO

cls
echo.
echo                        ██╗      ██████╗  ██████╗ ███████╗
echo                        ██║     ██╔═══██╗██╔════╝ ██╔════╝
echo                        ██║     ██║   ██║██║  ███╗███████╗
echo                        ██║     ██║   ██║██║   ██║╚════██║
echo                        ███████╗╚██████╔╝╚██████╔╝███████║
echo                        ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝
echo.
echo                    UNS-ClaudeJP 5.2 - MONITOR EN VIVO
echo                      📊 VISUALIZACIÓN DE LOGS 📊
echo.
timeout /t 2 /nobreak >nul

cd /d "%~dp0\.."

echo Verificando Docker Desktop...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   ❌ Docker Desktop no está corriendo
    echo   💡 Inicia primero con: scripts\START_FUN.bat
    echo.
    pause
    exit /b 1
)

set "DOCKER_COMPOSE_CMD="
docker compose version >nul 2>&1
if %errorlevel% EQU 0 (
    set "DOCKER_COMPOSE_CMD=docker compose"
) else (
    docker-compose version >nul 2>&1
    if %errorlevel% EQU 0 (
        set "DOCKER_COMPOSE_CMD=docker-compose"
    ) else (
        echo   ❌ Docker Compose no encontrado
        pause
        exit /b 1
    )
)

:menu
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          📊 SELECCIONA EL SERVICIO A MONITOREAR 📊        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo   🗄️  1 - Database (PostgreSQL)
echo      └─ Ver logs de la base de datos
echo.
echo   ⚙️  2 - Backend (FastAPI)
echo      └─ Ver logs de la API REST
echo.
echo   🎨 3 - Frontend (Next.js)
echo      └─ Ver logs del sitio web
echo.
echo   📦 4 - Importer
echo      └─ Ver logs de importación de datos
echo.
echo   💾 5 - Adminer (Database UI)
echo      └─ Ver logs de la interfaz de BD
echo.
echo   🌐 6 - Todos los servicios
echo      └─ Ver logs en tiempo real de TODO
echo.
echo   🚪 0 - Salir
echo.
echo ════════════════════════════════════════════════════════════
echo.

choice /C 01234567 /M "📍 Opción: "

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Presiona Ctrl+C para salir del monitoreo                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

if errorlevel 7 goto :menu
if errorlevel 6 (
    echo 🌐 Mostrando logs de TODOS los servicios en tiempo real...
    echo ─────────────────────────────────────────────────────────
    echo.
    timeout /t 1 /nobreak >nul
    %DOCKER_COMPOSE_CMD% logs -f
    goto :menu
)
if errorlevel 5 (
    echo 💾 Mostrando logs de ADMINER...
    echo ─────────────────────────────────────────────────────────
    echo.
    timeout /t 1 /nobreak >nul
    docker logs -f uns-claudejp-adminer
    goto :menu
)
if errorlevel 4 (
    echo 📦 Mostrando logs de IMPORTER...
    echo ─────────────────────────────────────────────────────────
    echo.
    timeout /t 1 /nobreak >nul
    docker logs -f uns-claudejp-importer
    goto :menu
)
if errorlevel 3 (
    echo 🎨 Mostrando logs de FRONTEND (Next.js)...
    echo ─────────────────────────────────────────────────────────
    echo.
    timeout /t 1 /nobreak >nul
    docker logs -f uns-claudejp-frontend
    goto :menu
)
if errorlevel 2 (
    echo ⚙️  Mostrando logs de BACKEND (FastAPI)...
    echo ─────────────────────────────────────────────────────────
    echo.
    timeout /t 1 /nobreak >nul
    docker logs -f uns-claudejp-backend
    goto :menu
)
if errorlevel 1 (
    echo 🗄️  Mostrando logs de DATABASE (PostgreSQL)...
    echo ─────────────────────────────────────────────────────────
    echo.
    timeout /t 1 /nobreak >nul
    docker logs -f uns-claudejp-db
    goto :menu
)

:end
echo.
echo ✅ Monitor de logs cerrado
echo.
pause >nul
