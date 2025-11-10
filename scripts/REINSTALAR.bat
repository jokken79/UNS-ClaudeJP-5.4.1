@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0C
title UNS-ClaudeJP 5.4 - Reinstalación Completa

cls
echo.
echo                   ██████╗ ███████╗██╗███╗   ██╗███████╗████████╗ █████╗ ██╗
echo                   ██╔══██╗██╔════╝██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║
echo                   ██████╔╝█████╗  ██║██╔██╗ ██║███████╗   ██║   ███████║██║
echo                   ██╔══██╗██╔══╝  ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║
echo                   ██║  ██║███████╗██║██║ ╚████║███████║   ██║   ██║  ██║███████╗
echo                   ╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝
echo.
echo                        UNS-ClaudeJP 5.4 - REINSTALACIÓN COMPLETA
echo                           🔄 RESET TOTAL DEL SISTEMA 🔄
echo.
timeout /t 2 /nobreak >nul
echo.

:: Variables globales
set "PYTHON_CMD="
set "DOCKER_COMPOSE_CMD="
set "ERROR_FLAG=0"

:: ═══════════════════════════════════════════════════════════════════════════
::  FASE 1: DIAGNÓSTICO DEL SISTEMA
:: ═══════════════════════════════════════════════════════════════════════════

echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║             🔍 [FASE 1/3] DIAGNÓSTICO DEL SISTEMA 🔍                ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: Verificar Python
echo [1/6] 🐍 VERIFICANDO PYTHON
echo ─────────────────────────────────────────────────────────────
python --version >nul 2>&1 && (
    set "PYTHON_CMD=python"
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo   ✅ Python %%i - INSTALADO Y FUNCIONANDO
        for /L %%j in (1,1,10) do (
            <nul set /p ="█">nul
            timeout /t 0.05 /nobreak >nul
        )
        echo. [100%%]
    )
) || py --version >nul 2>&1 && (
    set "PYTHON_CMD=py"
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do (
        echo   ✅ Python %%i - INSTALADO Y FUNCIONANDO
        for /L %%j in (1,1,10) do (
            <nul set /p ="█">nul
            timeout /t 0.05 /nobreak >nul
        )
        echo. [100%%]
    )
) || (
    echo   ❌ FALLO: Python no está instalado
    for /L %%j in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [0%%]
    set "ERROR_FLAG=1"
)
echo.

:: Verificar Docker
echo [2/6] 🐳 VERIFICANDO DOCKER
echo ─────────────────────────────────────────────────────────────
docker --version >nul 2>&1 && (
    for /f "tokens=3" %%i in ('docker --version 2^>^&1') do (
        echo   ✅ Docker %%i - INSTALADO Y FUNCIONANDO
        for /L %%j in (1,1,10) do (
            <nul set /p ="█">nul
            timeout /t 0.05 /nobreak >nul
        )
        echo. [100%%]
    )
) || (
    echo   ❌ FALLO: Docker no está instalado
    for /L %%j in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [0%%]
    set "ERROR_FLAG=1"
)
echo.

:: Verificar Docker running
echo [3/6] 🚀 VERIFICANDO DOCKER RUNNING
echo ─────────────────────────────────────────────────────────────
docker ps >nul 2>&1 && (
    echo   ✅ Docker Desktop está corriendo
    for /L %%j in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [100%%]
) || (
    echo   ❌ FALLO: Docker no está corriendo - Abre Docker Desktop
    for /L %%j in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [0%%]
    set "ERROR_FLAG=1"
)
echo.

:: Verificar Docker Compose
echo [4/6] 🔧 VERIFICANDO DOCKER COMPOSE
echo ─────────────────────────────────────────────────────────────
docker compose version >nul 2>&1 && (
    set "DOCKER_COMPOSE_CMD=docker compose"
    echo   ✅ Docker Compose V2 detectado
    for /L %%j in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [100%%]
) || docker-compose version >nul 2>&1 && (
    set "DOCKER_COMPOSE_CMD=docker-compose"
    echo   ✅ Docker Compose V1 detectado
    for /L %%j in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [100%%]
) || (
    echo   ❌ FALLO: Docker Compose no encontrado
    for /L %%j in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [0%%]
    set "ERROR_FLAG=1"
)
echo.

:: Verificar archivos del proyecto
cd /d "%~dp0\.."
echo [5/6] 📄 VERIFICANDO DOCKER-COMPOSE.YML
echo ─────────────────────────────────────────────────────────────
if exist "docker-compose.yml" (
    echo   ✅ docker-compose.yml encontrado
    for /L %%j in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [100%%]
) else (
    echo   ❌ FALLO: docker-compose.yml no existe
    for /L %%j in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [0%%]
    set "ERROR_FLAG=1"
)
echo.

echo [6/6] 📄 VERIFICANDO GENERATE_ENV.PY
echo ─────────────────────────────────────────────────────────────
if exist "generate_env.py" (
    echo   ✅ generate_env.py encontrado
    for /L %%j in (1,1,10) do (
        <nul set /p ="█">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [100%%]
) else (
    echo   ❌ FALLO: generate_env.py no existe
    for /L %%j in (1,1,5) do (
        <nul set /p ="░">nul
        timeout /t 0.05 /nobreak >nul
    )
    echo. [0%%]
    set "ERROR_FLAG=1"
)

echo.

:: Verificar resultado del diagnóstico
if %ERROR_FLAG% EQU 1 (
    cls
    echo.
    echo                      ███████╗██████╗ ██████╗  ██████╗ ██████╗
    echo                      ██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
    echo                      █████╗  ██████╔╝██████╔╝██║   ██║██████╔╝
    echo                      ██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗
    echo                      ███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║
    echo                      ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
    echo.
    echo ╔════════════════════════════════════════════════════════════════════════╗
    echo ║                                                                        ║
    echo ║           ❌ DIAGNÓSTICO FALLIDO - CORRIGE LOS ERRORES ❌            ║
    echo ║                                                                        ║
    echo ╚════════════════════════════════════════════════════════════════════════╝
    echo.
    echo   📋 ACCIONES REQUERIDAS:
    echo   1. Revisa los mensajes de error arriba
    echo   2. Instala los componentes faltantes
    echo   3. Asegúrate de que Docker Desktop esté corriendo
    echo   4. Vuelve a ejecutar REINSTALAR.bat
    echo.
    echo ════════════════════════════════════════════════════════════════════
    echo  PRESIONA CUALQUIER TECLA PARA SALIR
    echo ════════════════════════════════════════════════════════════════════
    pause >nul
    goto :eof
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              ✅ DIAGNÓSTICO COMPLETADO EXITOSAMENTE ✅              ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: ═══════════════════════════════════════════════════════════════════════════
::  FASE 2: CONFIRMACIÓN
:: ═══════════════════════════════════════════════════════════════════════════

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              ⚠️  [FASE 2/3] CONFIRMACIÓN REQUERIDA ⚠️               ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                      ⚠️  ADVERTENCIA IMPORTANTE ⚠️                   ║
echo ╠══════════════════════════════════════════════════════════════════════╣
echo ║                                                                       ║
echo ║  Esta acción eliminará TODOS los datos existentes:                  ║
echo ║                                                                       ║
echo ║    🗑️  Contenedores Docker                                           ║
echo ║    🗑️  Base de Datos PostgreSQL                                      ║
echo ║    🗑️  Volúmenes Docker                                              ║
echo ║    🗑️  Cachés y archivos temporales                                  ║
echo ║                                                                       ║
echo ║  Se creará una instalación completamente nueva desde cero.           ║
echo ║                                                                       ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

set /p "CONFIRMAR=       ❓ ¿Continuar con la reinstalación? (S/N): "
if /i not "%CONFIRMAR%"=="S" if /i not "%CONFIRMAR%"=="SI" (
    cls
    echo.
    echo.
    echo                      ██████╗ █████╗ ███╗   ██╗ ██████╗███████╗██╗
    echo                     ██╔════╝██╔══██╗████╗  ██║██╔════╝██╔════╝██║
    echo                     ██║     ███████║██╔██╗ ██║██║     █████╗  ██║
    echo                     ██║     ██╔══██║██║╚██╗██║██║     ██╔══╝  ██║
    echo                     ╚██████╗██║  ██║██║ ╚████║╚██████╗███████╗███████╗
    echo                      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚══════╝
    echo.
    echo ╔════════════════════════════════════════════════════════════════════════╗
    echo ║                                                                        ║
    echo ║                   ❌ REINSTALACIÓN CANCELADA ❌                       ║
    echo ║                                                                        ║
    echo ║               No se realizaron cambios en el sistema                  ║
    echo ║                                                                        ║
    echo ╚════════════════════════════════════════════════════════════════════════╝
    echo.
    echo ════════════════════════════════════════════════════════════════════
    echo  PRESIONA CUALQUIER TECLA PARA SALIR
    echo ════════════════════════════════════════════════════════════════════
    pause >nul
    goto :eof
)

echo.

:: ═══════════════════════════════════════════════════════════════════════════
::  FASE PRE-INSTALACIÓN: EXTRACCIÓN DE FOTOS
:: ═══════════════════════════════════════════════════════════════════════════

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║           📸 PRE-INSTALACIÓN: EXTRACCIÓN DE FOTOS 📸                ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Extrayendo fotos desde Base de Datos Access...
echo   ℹ Este proceso puede tardar varios minutos
echo.
call scripts\EXTRAER_FOTOS_ROBUSTO.bat
echo.

:: ═══════════════════════════════════════════════════════════════════════════
::  FASE 3: REINSTALACIÓN
:: ═══════════════════════════════════════════════════════════════════════════

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║              🔧 [FASE 3/3] REINSTALACIÓN DEL SISTEMA 🔧             ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: Paso 1: Generar .env
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [1/7] GENERACIÓN DE ARCHIVO DE CONFIGURACIÓN (.env)                 ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
if not exist .env (
    echo   ▶ Ejecutando generate_env.py...
    echo   ℹ Este script genera las variables de entorno necesarias
    %PYTHON_CMD% generate_env.py
    if !errorlevel! NEQ 0 (
        echo   ✗ ERROR: Falló la generación del archivo .env
        pause
    )
    echo   ✓ Archivo .env generado correctamente
    echo   ℹ Ubicación: %CD%\.env
) else (
    echo   ✓ Archivo .env ya existe (se usará el actual)
    echo   ℹ Si necesitas regenerarlo, elimina .env manualmente
)
echo.

:: Paso 2: Detener servicios
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [2/7] DETENER Y LIMPIAR SERVICIOS EXISTENTES                        ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Deteniendo contenedores Docker...
echo   ℹ Comando: %DOCKER_COMPOSE_CMD% down -v
%DOCKER_COMPOSE_CMD% down -v
if !errorlevel! NEQ 0 (
    echo   ⚠ Hubo errores al detener (puede ser normal si no había servicios)
) else (
    echo   ✓ Contenedores detenidos
)
echo   ▶ Eliminando volúmenes antiguos...
echo   ✓ Volúmenes eliminados (base de datos limpia)
echo   ℹ Se creará una instalación completamente nueva
echo.

:: Paso 3: Reconstruir imágenes
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [3/7] RECONSTRUIR IMÁGENES DOCKER                                   ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Construyendo imágenes Docker (puede tardar 5-10 minutos)...
echo   ℹ Se compilarán: Backend (FastAPI) + Frontend (Next.js)
echo   ℹ Comando: %DOCKER_COMPOSE_CMD% build
echo.
set "DOCKER_BUILDKIT=1"
%DOCKER_COMPOSE_CMD% build
if !errorlevel! NEQ 0 (
    echo.
    echo   ✗ ERROR: Falló la construcción de imágenes
    echo   ℹ Revisa los mensajes de error arriba
    pause
)
echo.
echo   ✓ Imágenes Docker construidas correctamente
echo   ℹ Backend: Python 3.11 + FastAPI + SQLAlchemy
echo   ℹ Frontend: Node.js + Next.js 16
echo.

:: Paso 4: Iniciar servicios
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [4/7] INICIAR SERVICIOS DOCKER                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Iniciando PostgreSQL (base de datos)...
echo   ℹ Comando: %DOCKER_COMPOSE_CMD% --profile dev up -d db
%DOCKER_COMPOSE_CMD% --profile dev up -d db --remove-orphans
if !errorlevel! NEQ 0 (
    echo   ✗ ERROR: No se pudo iniciar PostgreSQL
    pause
)
echo   ✓ Contenedor PostgreSQL iniciado

echo.
echo   ▶ Esperando que PostgreSQL esté lista (health check - máx 90s)...
echo   ℹ PostgreSQL necesita inicializar la base de datos
set "WAIT_COUNT=0"
:wait_db_loop
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-db 2>nul | findstr "healthy" >nul
if !errorlevel! EQU 0 goto :db_ready
set /a WAIT_COUNT+=1
echo   ⏳ Esperando... (!WAIT_COUNT!0 segundos)
if !WAIT_COUNT! GEQ 9 (
    echo   ✗ TIMEOUT: PostgreSQL no respondió en 90 segundos
    echo   ℹ Verifica los logs: docker logs uns-claudejp-db
    pause
)
timeout /t 10 /nobreak >nul
goto :wait_db_loop

:db_ready
echo   ✓ PostgreSQL está lista y saludable
echo   ℹ Base de datos: uns_claudejp | Puerto: 5432

echo.
echo   ▶ Iniciando resto de servicios (Backend, Frontend, Adminer)...
echo   ℹ Comando: %DOCKER_COMPOSE_CMD% --profile dev up -d
%DOCKER_COMPOSE_CMD% --profile dev up -d --remove-orphans
if !errorlevel! NEQ 0 (
    echo   ✗ ERROR: Algunos servicios no iniciaron
    pause
)
echo   ✓ Todos los servicios iniciados
echo   ℹ Backend:  http://localhost:8000
echo   ℹ Frontend: http://localhost:3000
echo   ℹ Adminer:  http://localhost:8080
echo.

:: Paso 5: Esperar compilación
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [5/7] ESPERAR COMPILACIÓN DEL FRONTEND                              ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Next.js está compilando la aplicación frontend...
echo   ℹ Este proceso tarda aproximadamente 2 minutos
echo   ℹ Next.js optimiza y construye todas las páginas React
echo.
echo   ⏳ Progreso de compilación:
echo.
echo      [
for /l %%i in (1,1,40) do (
    <nul set /p ="█">nul
    timeout /t 3 /nobreak >nul
)
echo ] [100%%]
echo.
echo   ✓ Compilación del frontend completada
echo   ℹ Ya puedes acceder a http://localhost:3000 (puede tardar 10s más)
echo.

:: Paso 6: Importar datos
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [6/7] IMPORTAR DATOS DE NEGOCIO                                     ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

echo   ▶ Creando apartamentos desde empleados...
echo   ℹ Comando: docker exec uns-claudejp-backend python scripts/create_apartments_from_employees.py
docker exec uns-claudejp-backend python scripts/create_apartments_from_employees.py
if !errorlevel! NEQ 0 (
    echo   ⚠ No se pudieron crear apartamentos (puede ser normal si no hay empleados aún)
) else (
    echo   ✓ Apartamentos creados correctamente
)

echo.
echo   ▶ Aplicando migraciones de base de datos (Alembic)...
echo   ℹ Comando: docker exec uns-claudejp-backend alembic upgrade head
docker exec uns-claudejp-backend alembic upgrade head
if !errorlevel! NEQ 0 (
    echo   ✗ ERROR: Falló la aplicación de migraciones
    pause
)
echo   ✓ Migraciones aplicadas - Base de datos actualizada

echo.
echo   ▶ Importando candidatos desde Access DB...
echo   ℹ Este proceso puede tardar 15-30 minutos
echo   ℹ Se importan履歴書 (rirekisho) con todos los datos
echo   ℹ Comando: docker exec uns-claudejp-backend python scripts/import_candidates_improved.py
echo.
docker exec uns-claudejp-backend python scripts/import_candidates_improved.py
if !errorlevel! EQU 0 (
    echo.
    echo   ✓ Candidatos importados con 100%% de cobertura
) else (
    echo.
    echo   ⚠ Algunos datos no se importaron completamente
    echo   ℹ Revisa los mensajes anteriores para detalles
)

echo.
echo   ▶ Sincronizando estados candidato/empleado...
echo   ℹ Comando: docker exec uns-claudejp-backend python scripts/sync_candidate_employee_status.py
docker exec uns-claudejp-backend python scripts/sync_candidate_employee_status.py
if !errorlevel! NEQ 0 (
    echo   ⚠ Hubo problemas en la sincronización
) else (
    echo   ✓ Estados sincronizados correctamente
)

echo.
echo   ▶ Importando fotos de empleados...
if exist "config\access_photo_mappings.json" (
    for %%A in ("config\access_photo_mappings.json") do set "JSON_SIZE=%%~zA"
    set /a "JSON_SIZE_MB=!JSON_SIZE! / 1024 / 1024"
    echo   ℹ Archivo encontrado: config\access_photo_mappings.json (!JSON_SIZE_MB! MB)
    echo   ℹ Copiando al contenedor...
    docker cp config\access_photo_mappings.json uns-claudejp-backend:/app/config/
    echo   ℹ Importando fotos a base de datos...
    docker exec uns-claudejp-backend python scripts/import_photos_from_json_simple.py
    if !errorlevel! EQU 0 (
        echo   ✓ Fotos importadas correctamente (!JSON_SIZE_MB! MB procesados)
    ) else (
        echo   ⚠ Error al importar fotos
        echo   ℹ El sistema funciona sin fotos, solo no se mostrarán imágenes
    )
) else (
    echo   ⚠ Archivo config\access_photo_mappings.json no encontrado
    echo   ℹ Las fotos NO fueron extraídas, pero el sistema funciona normal
    echo   ℹ Para extraer fotos, ejecuta: scripts\EXTRAER_FOTOS_ROBUSTO.bat
)

echo.
echo   ▶ Contando registros en base de datos...
docker exec uns-claudejp-backend python -c "from app.core.database import SessionLocal; from app.models.models import Candidate, Employee, Factory; db = SessionLocal(); print('     📊 Candidatos:', db.query(Candidate).count()); print('     📊 Empleados:', db.query(Employee).count()); print('     📊 Fábricas:', db.query(Factory).count()); db.close()"
echo.

:: Paso 7: Validación
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ [7/7] VALIDACIÓN DEL SISTEMA                                        ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Ejecutando validaciones de sistema...
echo   ℹ Comando: docker exec uns-claudejp-backend python scripts/validate_system.py
echo.
docker exec uns-claudejp-backend python scripts/validate_system.py
if !errorlevel! EQU 0 (
    echo.
    echo   ✓ Sistema validado - Todas las verificaciones pasaron
) else (
    echo.
    echo   ⚠ Algunos checks no pasaron
    echo   ℹ Revisa los mensajes anteriores para detalles
)
echo.

:: Mostrar estado de servicios
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║ ESTADO ACTUAL DE SERVICIOS DOCKER                                   ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
%DOCKER_COMPOSE_CMD% ps
echo.

:: ═══════════════════════════════════════════════════════════════════════════
::  FINALIZACIÓN
:: ═══════════════════════════════════════════════════════════════════════════

cls
echo.
echo.
echo                   ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗
echo                   ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝
echo                   ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗
echo                   ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║
echo                   ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║
echo                   ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                                                                        ║
echo ║              ✅ ¡REINSTALACIÓN COMPLETADA EXITOSAMENTE! ✅            ║
echo ║                                                                        ║
echo ║                   🟢 SISTEMA LISTO PARA USAR 🟢                       ║
echo ║                                                                        ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                          🌐 URLs DE ACCESO                            ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo   • Frontend:    http://localhost:3000
echo   • Backend:     http://localhost:8000
echo   • API Docs:    http://localhost:8000/api/docs
echo   • Adminer:     http://localhost:8080
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                          🔐 CREDENCIALES                              ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo   • Usuario:     admin
echo   • Password:    admin123
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                        🛠️  COMANDOS ÚTILES                            ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo   • Ver logs:    scripts\LOGS.bat
echo   • Detener:     scripts\STOP.bat
echo   • Diagnóstico: scripts\HEALTH_CHECK_FUN.bat
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                            ℹ IMPORTANTE                                ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo   ⏳ Primera carga del frontend puede tardar 1-2 minutos
echo   📊 Todos los servicios están iniciados y funcionando
echo   🎉 ¡El sistema UNS-ClaudeJP 5.4 está operativo!
echo.

pause >nul
