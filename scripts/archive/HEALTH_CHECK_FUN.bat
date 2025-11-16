@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0A
title UNS-ClaudeJP 5.4 - HEALTH CHECK

cls
echo.
echo                   ██╗  ██╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗
echo                   ██║  ██║██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║
echo                   ███████║█████╗  ███████║██║     ██║   ███████║
echo                   ██╔══██║██╔══╝  ██╔══██║██║     ██║   ██╔══██║
echo                   ██║  ██║███████╗██║  ██║███████╗██║   ██║  ██║
echo                   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝
echo.
echo            UNS-ClaudeJP 5.4 - VERIFICACIÓN DE SALUD
echo                  💚 HEALTH CHECK COMPLETO 💚
echo.
timeout /t 2 /nobreak >nul

cd /d "%~dp0\.."

echo ╔════════════════════════════════════════════════════════════╗
echo ║         🏥 INICIANDO DIAGNÓSTICO DE SALUD COMPLETO 🏥    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar Docker
echo [1/6] 🐳 DOCKER DESKTOP
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker no está corriendo
    for /L %%i in (1,1,10) do (
        <nul set /p ="░">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [OFFLINE]
) else (
    echo   ✅ Docker activo
    for /L %%i in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [100%%]
)
echo.

REM Verificar Docker Compose
echo [2/6] 🔧 DOCKER COMPOSE
docker compose version >nul 2>&1
if %errorlevel% EQU 0 (
    echo   ✅ Docker Compose V2 detectado
    set "DC=docker compose"
) else (
    docker-compose version >nul 2>&1
    if %errorlevel% EQU 0 (
        echo   ✅ Docker Compose V1 detectado
        set "DC=docker-compose"
    ) else (
        echo   ❌ Docker Compose no encontrado
    )
)
for /L %%i in (1,1,10) do (
    <nul set /p ="█">nul
    timeout /t 0.1 /nobreak >nul
)
echo. [100%%]
echo.

REM Verificar servicios
echo [3/6] 📦 ESTADO DE CONTENEDORES
for /L %%i in (1,1,10) do (
    <nul set /p ="█">nul
    timeout /t 0.1 /nobreak >nul
)
echo. [ESCANEANDO]
echo.

%DC% ps --format "table {{.Names}}\t{{.Status}}"

echo.

REM Health check de Database
echo [4/6] 🗄️  DATABASE (PostgreSQL)
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-db 2>nul | findstr "healthy" >nul
if %errorlevel% EQU 0 (
    echo   ✅ PostgreSQL - SALUDABLE
    for /L %%i in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [100%%]
) else (
    echo   ❌ PostgreSQL - NO RESPONDE
    for /L %%i in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [0%%]
)
echo.

REM Health check de Backend
echo [5/6] ⚙️  BACKEND (FastAPI)
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-backend 2>nul | findstr "healthy" >nul
if %errorlevel% EQU 0 (
    echo   ✅ FastAPI - SALUDABLE
    for /L %%i in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [100%%]
) else (
    echo   ⚠️  FastAPI - INICIALIZANDO
    for /L %%i in (1,1,8) do (
        <nul set /p ="▓">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [80%%]
)
echo.

REM Health check de Frontend
echo [6/6] 🎨 FRONTEND (Next.js)
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-frontend 2>nul | findstr "healthy" >nul
if %errorlevel% EQU 0 (
    echo   ✅ Next.js - SALUDABLE
    for /L %%i in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [100%%]
) else (
    echo   ⚠️  Next.js - COMPILANDO
    for /L %%i in (1,1,7) do (
        <nul set /p ="▓">nul
        timeout /t 0.1 /nobreak >nul
    )
    echo. [70%%]
)
echo.

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  🏥 REPORTE DE SALUD 🏥                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

%DC% ps

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  📊 DETALLES TÉCNICOS 📊                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo   🐳 DOCKER:
docker version --format "   • Client: {{.Client.Version}}"
docker version --format "   • Server: {{.Server.Version}}"
echo.

echo   🗄️  DATABASE:
docker logs uns-claudejp-db 2>nul | findstr "ready" | tail -1
echo.

echo   🌐 ACCESO:
echo   • Frontend:   http://localhost:3000
echo   • Backend:    http://localhost:8000/api/docs
echo   • Adminer:    http://localhost:8080
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║  Si algún servicio está ROJO, ejecuta: START_FUN.bat      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause >nul
