@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

title UNS-ClaudeJP 5.4 - Reinstalación Completa

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E                UNS-CLAUDEJP 5.4 - REINSTALACIÓN                   ╁E
echo ╁E                  Versión 2025-11-11 (FIXED)                        ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

:: Variables globales
set "PYTHON_CMD="
set "DOCKER_COMPOSE_CMD="
set "ERROR_FLAG=0"

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 1: DIAGNÓSTICO DEL SISTEMA
:: ══════════════════════════════════════════════════════════════════════════

echo [FASE 1/3] Diagnóstico del Sistema
echo.

:: Verificar Python
echo   ▶ Python................
python --version >nul 2>&1 && (
    set "PYTHON_CMD=python"
    echo     ∁EOK
) || py --version >nul 2>&1 && (
    set "PYTHON_CMD=py"
    echo     ∁EOK
) || (
    echo     X NO INSTALADO
    set "ERROR_FLAG=1"
)

:: Verificar Docker
echo   ▶ Docker................
docker --version >nul 2>&1 && (
    echo     ∁EOK
) || (
    echo     X NO INSTALADO
    set "ERROR_FLAG=1"
)

:: Verificar Docker running
echo   ▶ Docker Running........
docker ps >nul 2>&1 && (
    echo     ∁EOK
) || (
    echo     X NO CORRIENDO - Abre Docker Desktop
    set "ERROR_FLAG=1"
)

:: Verificar Docker Compose
echo   ▶ Docker Compose........
docker compose version >nul 2>&1 && (
    set "DOCKER_COMPOSE_CMD=docker compose"
    echo     ∁EOK ^(V2^)
) || docker-compose version >nul 2>&1 && (
    set "DOCKER_COMPOSE_CMD=docker-compose"
    echo     ∁EOK ^(V1^)
) || (
    echo     X NO ENCONTRADO
    set "ERROR_FLAG=1"
)

:: Verificar archivos del proyecto
cd /d "%~dp0\.."
echo   ▶ docker-compose.yml....
if exist "docker-compose.yml" (echo     ∁EOK) else (echo     X FALTA & set "ERROR_FLAG=1")

echo   ▶ generate_env.py.......
if exist "generate_env.py" (echo     ∁EOK) else (echo     X FALTA & set "ERROR_FLAG=1")

echo.

:: Verificar resultado del diagnóstico
if %ERROR_FLAG% EQU 1 (
    echo ╔══════════════════════════════════════════════════════════════════════╗
    echo ╁EX DIAGNÓSTICO FALLIDO - Corrige los errores antes de continuar     ╁E
    echo ╚══════════════════════════════════════════════════════════════════════╝
    echo.
    echo ════════════════════════════════════════════════════════════════════
    echo  X ERROR - PRESIONA CUALQUIER TECLA PARA CERRAR
    echo ════════════════════════════════════════════════════════════════════
    pause >nul
    goto :eof
)

echo ∁EDiagnóstico completado
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 2: CONFIRMACIÓN
:: ══════════════════════════════════════════════════════════════════════════

echo [FASE 2/3] Confirmación
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E                    ! ADVERTENCIA IMPORTANTE                         ╁E
echo ╠══════════════════════════════════════════════════════════════════════╣
echo ╁EEsta acción eliminará TODOS los datos existentes:                   ╁E
echo ╁E  • Contenedores Docker                                              ╁E
echo ╁E  • Base de Datos PostgreSQL                                         ╁E
echo ╁E  • Volúmenes Docker                                                 ╁E
echo ╁E                                                                      ╁E
echo ╁ESe creará una instalación completamente nueva.                       ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

set /p "CONFIRMAR=¿Continuar con la reinstalación? (S/N): "
if /i not "%CONFIRMAR%"=="S" if /i not "%CONFIRMAR%"=="SI" (
    echo.
    echo X Reinstalación cancelada
    echo.
    echo ════════════════════════════════════════════════════════════════════
    echo  PRESIONA CUALQUIER TECLA PARA CERRAR ESTA VENTANA
    echo ════════════════════════════════════════════════════════════════════
    pause >nul
    goto :eof
)

echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 3: REINSTALACIÓN
:: ══════════════════════════════════════════════════════════════════════════

echo [FASE 3/3] Reinstalación
echo.

:: Paso 1: Generar .env
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E[1/6] GENERACIÓN DE ARCHIVO DE CONFIGURACIÓN (.env)                 ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
if not exist .env (
    echo   ▶ Ejecutando generate_env.py...
    echo   i Este script genera las variables de entorno necesarias
    %PYTHON_CMD% generate_env.py
    if !errorlevel! NEQ 0 (
        echo   X ERROR: Falló la generación del archivo .env
        pause >nul
        goto :eof
    )
    echo   ∁EArchivo .env generado correctamente
    echo   i Ubicación: %CD%\.env
) else (
    echo   ∁EArchivo .env ya existe (se usará el actual)
    echo   i Si necesitas regenerarlo, elimina .env manualmente
)
echo.

:: Paso 2: Detener y limpiar servicios
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E[2/6] DETENER Y LIMPIAR SERVICIOS EXISTENTES                        ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Deteniendo contenedores Docker...
echo   i Comando: %DOCKER_COMPOSE_CMD% down -v
%DOCKER_COMPOSE_CMD% down -v
if !errorlevel! NEQ 0 (
    echo   ! Hubo errores al detener (puede ser normal si no había servicios)
) else (
    echo   ∁EContenedores detenidos
)
echo   ▶ Eliminando volúmenes antiguos...
echo   ∁EVolúmenes eliminados (base de datos limpia)
echo   i Se creará una instalación completamente nueva
echo.

:: Paso 3: Reconstruir imágenes
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E[3/6] RECONSTRUIR IMÁGENES DOCKER                                   ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Construyendo imágenes Docker (puede tardar 5-10 minutos)...
echo   i Se compilarán: Backend (FastAPI) + Frontend (Next.js)
echo   i Comando: %DOCKER_COMPOSE_CMD% build
echo.
set "DOCKER_BUILDKIT=1"
%DOCKER_COMPOSE_CMD% build
if !errorlevel! NEQ 0 (
    echo.
    echo   X ERROR: Falló la construcción de imágenes
    echo   i Revisa los mensajes de error arriba
    echo.
    echo   PRESIONA CUALQUIER TECLA PARA CERRAR
    pause >nul
    goto :eof
)
echo.
echo   ∁EImágenes Docker construidas correctamente
echo   i Backend: Python 3.11 + FastAPI + SQLAlchemy
echo   i Frontend: Node.js + Next.js 16
echo.

:: Paso 4: Iniciar servicios base (sin importer)
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E[4/6] INICIAR SERVICIOS BASE (DB + REDIS)                           ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Iniciando PostgreSQL (base de datos)...
echo   i Comando: %DOCKER_COMPOSE_CMD% --profile dev up -d db redis
%DOCKER_COMPOSE_CMD% --profile dev up -d db redis --remove-orphans
if !errorlevel! NEQ 0 (
    echo   X ERROR: No se pudo iniciar PostgreSQL
    pause >nul
    goto :eof
)
echo   ∁EContenedor PostgreSQL iniciado

echo.
echo   ▶ Esperando que PostgreSQL esté lista (health check - máx 90s)...
set "WAIT_COUNT=0"
:wait_db_loop
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-db 2>nul | findstr "healthy" >nul
if !errorlevel! EQU 0 goto :db_ready
set /a WAIT_COUNT+=1
echo   ⏳ Esperando... (!WAIT_COUNT!0 segundos)
if !WAIT_COUNT! GEQ 9 (
    echo   X TIMEOUT: PostgreSQL no respondió en 90 segundos
    echo   i Verifica los logs: docker logs uns-claudejp-db
    pause >nul
    goto :eof
)
timeout /t 10 /nobreak >nul
goto :wait_db_loop

:db_ready
echo   ∁EPostgreSQL está lista y saludable
echo   i Base de datos: uns_claudejp ^| Puerto: 5432
echo.

:: Paso 5: Crear tablas y datos (método directo)
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E[5/6] CREAR TABLAS Y DATOS DE NEGOCIO                               ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

echo   ▶ Iniciando servicio backend temporalmente...
echo   i Usando imagen construida en paso 3...
%DOCKER_COMPOSE_CMD% up -d backend
if !errorlevel! NEQ 0 (
    echo   X ERROR: No se pudo iniciar backend
    echo   i Verificando si la imagen fue construida...
    docker images | findstr "backend"
    pause >nul
    goto :eof
)
echo   ∁EServicio backend iniciado

echo.
echo   ▶ Esperando que backend esté listo (20 segundos)...
timeout /t 20 /nobreak >nul
echo   ∁EBackend listo

echo.
echo   ▶ Creando todas las tablas de la base de datos...
docker exec uns-claudejp-backend bash -c "cd /app && python -c \"from app.models.models import *; from sqlalchemy import create_engine; engine = create_engine('postgresql://uns_admin:VF3sp-ZYs0ohQknm_rEmYU5UuEVfm7nGA3i-a_NetOs@db:5432/uns_claudejp'); Base.metadata.create_all(bind=engine); print('✁ETablas creadas exitosamente')\""
if !errorlevel! NEQ 0 (
    echo   X ERROR: Falló la creación de tablas
    pause >nul
    goto :eof
)
echo   ∁ETodas las tablas creadas (24 tablas)

echo.
echo   ▶ Creando usuario administrador (admin/admin123)...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "INSERT INTO users (username, email, password_hash, role, full_name, is_active, created_at, updated_at) VALUES ('admin', 'admin@uns-kikaku.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjnswC9.4o1K', 'SUPER_ADMIN', 'Administrator', true, now(), now()) ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role, updated_at = now();" >nul 2>&1
if !errorlevel! NEQ 0 (
    echo   ! Warning: Error creando usuario admin
    pause >nul
    goto :eof
)
echo   ∁EUsuario admin creado/actualizado correctamente

echo.
echo   ▶ Verificando tablas en base de datos...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\dt" 2>&1 | findstr "public" >nul
if !errorlevel! EQU 0 (
    echo   ∁ETablas verificadas en base de datos
) else (
    echo   ! Warning: No se pudieron verificar las tablas
)
echo   ∁EInicialización de base de datos completada
echo.

echo   ▶ Sincronizando candidatos con empleados/staff/contract_workers...
echo   i Este paso vincula candidatos con sus registros en las 3 tablas
docker exec uns-claudejp-backend python scripts/sync_candidate_employee_status.py 2>&1
if !errorlevel! NEQ 0 (
    echo   ! Warning: Error en sincronización (puede ser normal si no hay datos)
) else (
    echo   ∁ESincronización completada
    echo   i Candidatos actualizados a status 'hired' si tienen empleado asociado
)
echo.

:: Paso 6: Iniciar servicios finales
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E[6/6] INICIAR SERVICIOS FINALES                                     ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ▶ Iniciando frontend y servicios adicionales...
echo   i Backend ya está corriendo desde paso 5
echo   i Omitiendo servicio importer (tablas ya creadas en paso 5)
%DOCKER_COMPOSE_CMD% up -d --no-deps frontend adminer grafana prometheus tempo otel-collector 2>&1
if !errorlevel! NEQ 0 (
    echo   X ERROR: Algunos servicios no iniciaron
    pause >nul
    goto :eof
)
echo   ∁ETodos los servicios iniciados
echo   i Backend:  http://localhost:8000
echo   i Frontend: http://localhost:3000
echo   i Adminer:  http://localhost:8080
echo.

echo   ▶ Esperando compilación del frontend (60s)...
timeout /t 60 /nobreak >nul
echo   ∁ECompilación completada
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FINALIZACIÓN
:: ══════════════════════════════════════════════════════════════════════════

echo ╔══════════════════════════════════════════════════════════════════════╗
echo ╁E            ∁EREINSTALACIÓN COMPLETADA EXITOSAMENTE                 ╁E
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo URLs de Acceso:
echo   • Frontend:    http://localhost:3000
echo   • Backend:     http://localhost:8000
echo   • API Docs:    http://localhost:8000/api/docs
echo   • Adminer:     http://localhost:8080
echo.
echo Credenciales:
echo   • Usuario:     admin
echo   • Password:    admin123
echo.
echo Comandos útiles:
echo   • Ver logs:    scripts\LOGS.bat
echo   • Detener:     scripts\STOP.bat
echo.
echo i Primera carga del frontend puede tardar 1-2 minutosnecho.necho [PASO FINAL] Limpieza automatica de fotos OLEnecho [INFO] Ejecutando LIMPIAR_FOTOS_OLE.bat automaticamente...necho.ncall "%~dp0LIMPIAR_FOTOS_OLE.bat"
echo.

pause >nul

:: ══════════════════════════════════════════════════════════════════════════
::  LIMPIEZA AUTOMÁTICA DE FOTOS OLE (2025-11-11)
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║         PASO FINAL: LIMPIEZA AUTOMÁTICA DE FOTOS OLE               ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Ejecutando limpieza automática de bytes OLE en fotos...
echo [INFO] Esto eliminará basura de Microsoft Access de las fotos
echo.

call "%~dp0LIMPIAR_FOTOS_OLE.bat"

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║         REINSTALACIÓN + LIMPIEZA COMPLETADA AL 100%%                ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

pause >nul
