@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0B
title UNS-ClaudeJP 5.2 - BUILD BACKEND

cls
echo.
echo ========================================================================
echo          UNS-ClaudeJP 5.4 - COMPILAR BACKEND
echo                  FASTAPI + PYTHON
echo ========================================================================
echo.
timeout /t 2 /nobreak >nul

cd /d "%~dp0\.."

echo ========================================================================
echo           VERIFICANDO DEPENDENCIAS
echo ========================================================================
echo.

REM Verificar Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker no está instalado
    pause
    exit /b 1
)
echo   ✅ Docker detectado
echo.

REM Verificar docker-compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    docker-compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo   ❌ Docker Compose no encontrado
        pause
        exit /b 1
    )
    set "DC=docker-compose"
) else (
    set "DC=docker compose"
)
echo   ✅ Docker Compose detectado
echo.

REM Verificar backend existe
if not exist "backend" (
    echo   ❌ Carpeta backend no encontrada
    pause
    exit /b 1
)
echo   ✅ Carpeta backend existe
echo.

echo ========================================================================
echo           COMPILANDO BACKEND (FASTAPI)
echo ========================================================================
echo.
echo   💾 Este proceso compilará:
echo      • FastAPI 0.115.6 - Framework REST asincrónico
echo      • SQLAlchemy 2.0.36 - ORM para base de datos
echo      • Pydantic v2 - Validación de datos
echo      • PostgreSQL driver (psycopg2)
echo      • Python 3.11+
echo.
echo   ⏳ Puede tardar 3-8 minutos en la primera ejecución
echo.

set /p CONTINUAR="¿Continuar con la compilación? (S/N): "
if /i NOT "!CONTINUAR!"=="S" (
    echo.
    echo   ❌ Compilación cancelada
    pause
    exit /b 0
)

echo.
echo   🔄 Construyendo imagen Docker del backend...
echo.

%DC% build --no-cache backend

if %errorlevel% neq 0 (
    echo.
    echo ========================================================================
    echo        ERROR DURANTE LA COMPILACION
    echo ========================================================================
    echo.
    echo   💡 Soluciones comunes:
    echo      1. Revisa los logs arriba (error de dependencias)
    echo      2. Intenta: LIMPIAR_CACHE_FUN.bat
    echo      3. Verifica Dockerfile en backend/
    echo      4. Luego reintenta BUILD_BACKEND_FUN.bat
    echo.
    pause
    exit /b 1
)

cls
echo.
echo ========================================================================
echo
echo     BACKEND COMPILADO EXITOSAMENTE!
echo
echo      FASTAPI 0.115.6 LISTO PARA USAR
echo
echo ========================================================================
echo.
echo   📊 INFORMACIÓN DE LA COMPILACIÓN:
echo   ─────────────────────────────────────────────────────────
echo   • Framework: FastAPI 0.115.6
echo   • ORM: SQLAlchemy 2.0.36
echo   • Base de datos: PostgreSQL 15
echo   • Python: 3.11+
echo   • Validación: Pydantic v2
echo   ─────────────────────────────────────────────────────────
echo.
echo   💡 Próximos pasos:
echo      1. Para iniciar: START_FUN.bat
echo      2. Backend en: http://localhost:8000
echo      3. Docs API en: http://localhost:8000/api/docs
echo      4. ReDoc en: http://localhost:8000/api/redoc
echo.
echo   🔍 Para ejecutar migraciones:
echo      docker exec uns-claudejp-backend alembic upgrade head
echo.

echo.
pause >nul
