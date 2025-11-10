@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0A
title UNS-ClaudeJP 5.2 - MEMORY STATS

cls
echo.
echo                 ███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗
echo                 ████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝
echo                 ██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝
echo                 ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝
echo                 ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║
echo                 ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
echo.
echo            UNS-ClaudeJP 5.2 - ESTADÍSTICAS DE RECURSOS
echo                  📊 MEMORY Y CPU STATS 📊
echo.
timeout /t 2 /nobreak >nul

echo ╔════════════════════════════════════════════════════════════╗
echo ║      📊 CONSUMO DE RECURSOS - DOCKER CONTAINERS 📊       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo   ⏳ Recopilando estadísticas de Docker...
echo.

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker no está corriendo
    pause
    exit /b 1
)

echo   CONTENEDORES ACTIVOS Y SU CONSUMO:
echo   ─────────────────────────────────────────────────────────
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>nul | findstr "uns-claudejp"
echo   ─────────────────────────────────────────────────────────
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║           💾 INFORMACIÓN DETALLADA POR SERVICIO 💾        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1] 🗄️  DATABASE (PostgreSQL)
echo   ⏳ Obteniendo estadísticas...
docker stats uns-claudejp-db --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>nul | tail -1
echo.

echo [2] ⚙️  BACKEND (FastAPI)
echo   ⏳ Obteniendo estadísticas...
docker stats uns-claudejp-backend --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>nul | tail -1
echo.

echo [3] 🎨 FRONTEND (Next.js)
echo   ⏳ Obteniendo estadísticas...
docker stats uns-claudejp-frontend --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>nul | tail -1
echo.

echo [4] 📦 IMPORTER
echo   ⏳ Obteniendo estadísticas...
docker stats uns-claudejp-importer --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>nul | tail -1
echo.

echo [5] 💾 ADMINER (Database UI)
echo   ⏳ Obteniendo estadísticas...
docker stats uns-claudejp-adminer --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>nul | tail -1
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║           🖥️  ESTADÍSTICAS DEL SISTEMA 🖥️               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo   Docker Desktop Resources:
docker system df 2>nul | findstr /v "^$"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           🧹 OPTIMIZACIÓN 🧹                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set /p LIMPIAR="¿Limpiar imágenes no usadas? (S/N): "
if /i "!LIMPIAR!"=="S" (
    echo   ⏳ Limpiando...
    docker image prune -f >nul 2>&1
    echo   ✅ Limpieza completada
    echo.
    echo   Nuevo resumen:
    docker system df 2>nul | findstr /v "^$"
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  💡 SI EL USO ES MUY ALTO, EJECUTA: RESET_DOCKER_FUN.bat ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause >nul
