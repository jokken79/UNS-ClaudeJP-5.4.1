@echo off
REM ============================================================================
REM STOP.bat - Detener todos los servicios de LolaAppJp
REM ============================================================================
setlocal EnableDelayedExpansion

cd /d "%~dp0.."

echo.
echo ========================================
echo   LolaAppJp - Stopping Services
echo ========================================
echo.

REM Verificar que Docker está corriendo
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Docker Desktop may already be stopped.
    echo.
    pause >nul
    exit /b 1
)

echo [1/2] Stopping all containers...
docker-compose down

echo [2/2] Removing orphan containers...
docker-compose down --remove-orphans

echo.
echo ========================================
echo   All services stopped successfully!
echo ========================================
echo.

REM Mostrar estado
echo Current status:
docker-compose ps

echo.
echo ========================================

REM NO CERRAR LA VENTANA AUTOMÁTICAMENTE
pause >nul
