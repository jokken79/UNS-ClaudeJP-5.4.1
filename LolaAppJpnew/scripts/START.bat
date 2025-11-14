@echo off
REM ============================================================================
REM START.bat - Iniciar todos los servicios de LolaAppJp
REM ============================================================================
setlocal EnableDelayedExpansion

cd /d "%~dp0.."

echo.
echo ========================================
echo   LolaAppJp - Starting Services
echo ========================================
echo.

REM Verificar que existe .env
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Creating .env from .env.example...
    copy ".env.example" ".env"
    echo.
    echo [IMPORTANT] Please edit .env file with your settings before continuing!
    echo Press any key to open .env file...
    pause >nul
    notepad .env
    echo.
    echo Press any key to continue after editing .env...
    pause >nul
)

REM Verificar que Docker está corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause >nul
    exit /b 1
)

echo [1/4] Stopping any existing containers...
docker-compose down >nul 2>&1

echo [2/4] Building images...
docker-compose build

echo [3/4] Starting services...
docker-compose up -d

echo [4/4] Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Services Status
echo ========================================
docker-compose ps

echo.
echo ========================================
echo   Access URLs
echo ========================================
echo.
echo   Frontend:     http://localhost:3000
echo   Backend API:  http://localhost/api
echo   API Docs:     http://localhost:8000/api/docs
echo   Adminer:      http://localhost:8080
echo   Grafana:      http://localhost:3001
echo   Prometheus:   http://localhost:9090
echo.
echo   Default Login: admin / admin123
echo.
echo ========================================
echo   Useful Commands
echo ========================================
echo.
echo   View logs:    scripts\LOGS.bat
echo   Stop all:     scripts\STOP.bat
echo.
echo ========================================

REM NO CERRAR LA VENTANA AUTOMÁTICAMENTE
pause >nul
