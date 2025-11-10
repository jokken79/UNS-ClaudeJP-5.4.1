@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ============================================================================
REM  UNS-ClaudeJP 5.0 - Script de Actualización Automática
REM  Actualiza la aplicación a Next.js 16 y React 19
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                  UNS-ClaudeJP 5.0 - ACTUALIZACIÓN                      ║
echo ║                  Next.js 16 + React 19 + Turbopack                     ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Cambiar al directorio raíz del proyecto
cd /d "%~dp0.."

echo [0/8] 🔍 Verificando archivo .env...
echo.

REM Verificar si existe el archivo .env
if not exist ".env" (
    echo ⚠️  Archivo .env no encontrado
    echo 📝 Creando archivo .env automáticamente...
    echo.

    REM Intentar generar con Python
    python generate_env.py >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Archivo .env creado con generate_env.py
    ) else (
        REM Si Python no está disponible, copiar desde .env.example
        if exist ".env.example" (
            copy .env.example .env >nul
            echo ✅ Archivo .env creado desde .env.example
        ) else (
            REM Crear .env básico manualmente
            (
                echo # Database Configuration
                echo POSTGRES_USER=uns_admin
                echo POSTGRES_PASSWORD=57UD10R
                echo POSTGRES_DB=uns_claudejp
                echo.
                echo # Backend Configuration
                echo SECRET_KEY=uns-claudejp-secret-key-change-in-production
                echo DATABASE_URL=postgresql://uns_admin:57UD10R@db:5432/uns_claudejp
                echo.
                echo # Frontend Configuration
                echo NEXT_PUBLIC_API_URL=http://localhost:8000
            ) > .env
            echo ✅ Archivo .env creado con valores por defecto
        )
    )
    echo.
    echo 💡 Tip: Revisa y personaliza el archivo .env según tus necesidades
    echo.
) else (
    echo ✅ Archivo .env encontrado
    echo.
)

echo [1/8] 📋 Verificando estado actual...
echo.
git status --short
echo.

echo [2/8] 🛑 Deteniendo containers actuales...
docker compose down
if !errorlevel! neq 0 (
    echo ❌ Error al detener containers
    pause
    exit /b 1
)
echo ✅ Containers detenidos
echo.

echo [3/8] 🗑️  Limpiando volúmenes de node_modules...
docker volume rm uns-claudejp-42_node_modules 2>nul
echo ✅ Volúmenes limpiados
echo.

echo [4/8] 🔨 Rebuilding imagen del frontend (esto puede tardar 5-10 minutos)...
echo    Instalando Next.js 16, React 19 y todas las dependencias...
echo.
docker compose build --no-cache frontend
if !errorlevel! neq 0 (
    echo ❌ Error en el build del frontend
    echo.
    echo 💡 Intenta ejecutar manualmente:
    echo    docker compose build --no-cache frontend
    pause
    exit /b 1
)
echo ✅ Frontend reconstruido con Next.js 16
echo.

echo [5/8] 🚀 Iniciando servicios actualizados...
docker compose up -d
if !errorlevel! neq 0 (
    echo ❌ Error al iniciar servicios
    pause
    exit /b 1
)
echo ✅ Servicios iniciados
echo.

echo [6/8] ⏳ Esperando a que el frontend compile (Turbopack)...
timeout /t 10 /nobreak >nul
echo.

echo [7/8] 📊 Verificando estado de los servicios...
echo.
docker compose ps
echo.

echo [8/8] ✅ Verificando configuración de base de datos...
echo.
docker logs uns-claudejp-db --tail 5 2>nul | findstr /C:"database system is ready" >nul
if !errorlevel! equ 0 (
    echo ✅ Base de datos PostgreSQL iniciada correctamente
) else (
    echo ⚠️  La base de datos puede tardar unos segundos más en iniciar
    echo    Ejecuta: docker logs uns-claudejp-db
)
echo.

echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                     ✅ ACTUALIZACIÓN COMPLETADA                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 UNS-ClaudeJP 5.0 está ahora ejecutándose con:
echo    • Next.js 16.0.0
echo    • React 19.0.0
echo    • Turbopack (bundler por defecto)
echo.
echo 🌐 URLs de acceso:
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/api/docs
echo    Adminer:   http://localhost:8080
echo.
echo 📝 Credenciales por defecto:
echo    Usuario: admin
echo    Password: admin123
echo.
echo 📊 Para ver los logs del frontend:
echo    scripts\LOGS.bat
echo    (y selecciona opción 2 - Frontend)
echo.
echo 🔍 Para verificar la versión de Next.js:
echo    docker exec -it uns-claudejp-frontend npm list next
echo.

REM Preguntar si desea ver los logs
echo.
set /p SHOW_LOGS="¿Deseas ver los logs del frontend ahora? (S/N): "
if /i "!SHOW_LOGS!"=="S" (
    echo.
    echo Mostrando logs del frontend (Ctrl+C para salir)...
    echo.
    timeout /t 2 /nobreak >nul
    docker logs -f uns-claudejp-frontend
)

echo.
echo ✅ Proceso completado. ¡Disfruta de Next.js 16!
echo.
pause
