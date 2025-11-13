@echo off
REM ============================================================================
REM LOGS.bat - Ver logs de los servicios de LolaAppJp
REM ============================================================================
setlocal EnableDelayedExpansion

cd /d "%~dp0.."

:MENU
cls
echo.
echo ========================================
echo   LolaAppJp - Service Logs
echo ========================================
echo.
echo   Select a service to view logs:
echo.
echo   [1] All services
echo   [2] Backend (FastAPI)
echo   [3] Frontend (Next.js)
echo   [4] Database (PostgreSQL)
echo   [5] Redis
echo   [6] Nginx
echo   [7] Grafana
echo   [8] Prometheus
echo   [9] Exit
echo.
echo ========================================
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto ALL
if "%choice%"=="2" goto BACKEND
if "%choice%"=="3" goto FRONTEND
if "%choice%"=="4" goto DATABASE
if "%choice%"=="5" goto REDIS
if "%choice%"=="6" goto NGINX
if "%choice%"=="7" goto GRAFANA
if "%choice%"=="8" goto PROMETHEUS
if "%choice%"=="9" goto EXIT
goto MENU

:ALL
echo.
echo Showing logs for ALL services (Ctrl+C to stop)...
echo.
docker-compose logs -f
goto MENU

:BACKEND
echo.
echo Showing logs for Backend (Ctrl+C to stop)...
echo.
docker-compose logs -f backend
goto MENU

:FRONTEND
echo.
echo Showing logs for Frontend (Ctrl+C to stop)...
echo.
docker-compose logs -f frontend
goto MENU

:DATABASE
echo.
echo Showing logs for Database (Ctrl+C to stop)...
echo.
docker-compose logs -f db
goto MENU

:REDIS
echo.
echo Showing logs for Redis (Ctrl+C to stop)...
echo.
docker-compose logs -f redis
goto MENU

:NGINX
echo.
echo Showing logs for Nginx (Ctrl+C to stop)...
echo.
docker-compose logs -f nginx
goto MENU

:GRAFANA
echo.
echo Showing logs for Grafana (Ctrl+C to stop)...
echo.
docker-compose logs -f grafana
goto MENU

:PROMETHEUS
echo.
echo Showing logs for Prometheus (Ctrl+C to stop)...
echo.
docker-compose logs -f prometheus
goto MENU

:EXIT
echo.
echo Exiting...
exit /b 0
