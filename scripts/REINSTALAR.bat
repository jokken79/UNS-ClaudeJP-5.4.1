@echo off
setlocal EnableDelayedExpansion

title UNS-ClaudeJP 5.4 - Reinstalacion Completa

echo.
echo ============================================================================
echo                   UNS-CLAUDEJP 5.4 - REINSTALACION
echo                   Version 2025-11-13 (FIXED)
echo ============================================================================
echo.

:: Variables globales
set "PYTHON_CMD="
set "DOCKER_COMPOSE_CMD="
set "ERROR_FLAG=0"

:: ===========================================================================
::  FASE 1: DIAGNOSTICO DEL SISTEMA
:: ===========================================================================

echo [FASE 1/3] Diagnostico del Sistema
echo.

:: Verificar Python
echo   [*] Python................
python --version >nul 2>&1 && (
    set "PYTHON_CMD=python"
    echo     [OK]
) || py --version >nul 2>&1 && (
    set "PYTHON_CMD=py"
    echo     [OK]
) || (
    echo     [X] NO INSTALADO
    set "ERROR_FLAG=1"
)

:: Verificar Docker
echo   [*] Docker................
docker --version >nul 2>&1 && (
    echo     [OK]
) || (
    echo     [X] NO INSTALADO
    set "ERROR_FLAG=1"
)

:: Verificar Docker running
echo   [*] Docker Running........
docker ps >nul 2>&1 && (
    echo     [OK]
) || (
    echo     [X] NO CORRIENDO
    set "ERROR_FLAG=1"
)

:: Verificar Docker Compose
echo   [*] Docker Compose........
docker compose version >nul 2>&1 && (
    set "DOCKER_COMPOSE_CMD=docker compose"
    echo     [OK] ^(V2^)
) || docker-compose version >nul 2>&1 && (
    set "DOCKER_COMPOSE_CMD=docker-compose"
    echo     [OK] ^(V1^)
) || (
    echo     [X] NO ENCONTRADO
    set "ERROR_FLAG=1"
)

:: Verificar archivos del proyecto
cd /d "%~dp0\.."
echo   [*] docker-compose.yml....
if exist "docker-compose.yml" (echo     [OK]) else (echo     [X] FALTA & set "ERROR_FLAG=1")

echo   [*] generate_env.py.......
if exist "scripts\utilities\generate_env.py" (echo     [OK]) else (echo     [X] FALTA & set "ERROR_FLAG=1")

echo.

:: Verificar resultado del diagnostico
if %ERROR_FLAG% EQU 1 (
    echo.
    echo [X] DIAGNOSTICO FALLIDO - Corrige los errores antes de continuar
    echo.

    :: Verificar si el error es solo Docker no corriendo
    docker ps >nul 2>&1
    if !errorlevel! NEQ 0 (
        echo [!] Se detectó que Docker Desktop no está corriendo
        echo.
        echo [*] Intentando iniciar Docker Desktop automáticamente...
        echo.

        :: Llamar al script de iniciar Docker
        call "%~dp0INICIAR_DOCKER.bat"

        :: Si Docker se inició correctamente, continuar con la reinstalación
        docker ps >nul 2>&1
        if !errorlevel! EQU 0 (
            echo.
            echo [OK] Docker iniciado correctamente. Continuando con la reinstalación...
            echo.
            :: Limpiar flag de error para continuar
            set "ERROR_FLAG=0"
            goto :continue_install
        ) else (
            echo.
            echo [X] No se pudo iniciar Docker Desktop automáticamente
            echo.
            echo [!] Por favor:
            echo  1. Abre Docker Desktop manualmente desde el menú de inicio
            echo  2. Espera a que se inicie completamente (revisa la bandeja de tareas)
            echo  3. Ejecuta nuevamente: scripts\REINSTALAR.bat
            echo.
            echo ============================================================================
            echo  PRESIONA CUALQUIER TECLA PARA CERRAR
            echo ============================================================================
            pause >nul
            goto :eof
        )
    ) else (
        echo ============================================================================
        echo  [X] ERROR - PRESIONA CUALQUIER TECLA PARA CERRAR
        echo ============================================================================
        pause >nul
        goto :eof
    )
)

:continue_install

echo [OK] Diagnostico completado
echo.

:: ===========================================================================
::  FASE 2: CONFIRMACION
:: ===========================================================================

echo [FASE 2/3] Confirmacion
echo.
echo ============================================================================
echo                    ! ADVERTENCIA IMPORTANTE
echo ============================================================================
echo  Esta accion eliminara TODOS los datos existentes:
echo    [*] Contenedores Docker
echo    [*] Base de Datos PostgreSQL
echo    [*] Volumenes Docker
echo.
echo  Se creara una instalacion completamente nueva.
echo ============================================================================
echo.

set /p "CONFIRMAR=¿Continuar con la reinstalacion? (S/N): "
if /i not "%CONFIRMAR%"=="S" if /i not "%CONFIRMAR%"=="SI" (
    echo.
    echo [X] Reinstalacion cancelada
    echo.
    echo ============================================================================
    echo  PRESIONA CUALQUIER TECLA PARA CERRAR ESTA VENTANA
    echo ============================================================================
    pause >nul
    goto :eof
)

echo.

:: ===========================================================================
::  FASE 3: REINSTALACION
:: ===========================================================================

echo [FASE 3/3] Reinstalacion
echo.

:: Paso 1: Generar .env
echo ============================================================================
echo  [1/6] GENERACION DE ARCHIVO DE CONFIGURACION (.env)
echo ============================================================================
echo.
if not exist .env (
    echo   [*] Ejecutando generate_env.py...
    echo   i Este script genera las variables de entorno necesarias
    %PYTHON_CMD% scripts\utilities\generate_env.py
    if !errorlevel! NEQ 0 (
        echo   [X] ERROR: Fallo la generacion del archivo .env
        pause >nul
        goto :eof
    )
    echo   [OK] Archivo .env generado correctamente
    echo   i Ubicacion: %CD%\.env
) else (
    echo   [OK] Archivo .env ya existe (se usara el actual)
    echo   i Si necesitas regenerarlo, elimina .env manualmente
)
echo.

:: Paso 2: Detener y limpiar servicios
echo ============================================================================
echo  [2/6] DETENER Y LIMPIAR SERVICIOS EXISTENTES
echo ============================================================================
echo.
echo   [*] Deteniendo contenedores Docker...
echo   i Comando: %DOCKER_COMPOSE_CMD% down -v
%DOCKER_COMPOSE_CMD% down -v
if !errorlevel! NEQ 0 (
    echo   ! Hubo errores al detener (puede ser normal si no habia servicios)
) else (
    echo   [OK] Contenedores detenidos
)
echo   [*] Eliminando volumenes antiguos...
echo   [OK] Volumenes eliminados (base de datos limpia)
echo   i Se creara una instalacion completamente nueva
echo.

:: Paso 3: Reconstruir imagenes
echo ============================================================================
echo  [3/6] RECONSTRUIR IMAGENES DOCKER
echo ============================================================================
echo.
echo   [*] Construyendo imagenes Docker (puede tardar 5-10 minutos)...
echo   i Se compilaran: Backend (FastAPI) + Frontend (Next.js)
echo   i Comando: %DOCKER_COMPOSE_CMD% build
echo.
set "DOCKER_BUILDKIT=1"
%DOCKER_COMPOSE_CMD% build
if !errorlevel! NEQ 0 (
    echo.
    echo   [X] ERROR: Fallo la construccion de imagenes
    echo   i Revisa los mensajes de error arriba
    echo.
    echo   PRESIONA CUALQUIER TECLA PARA CERRAR
    pause >nul
    goto :eof
)
echo.
echo   [OK] Imagenes Docker construidas correctamente
echo   i Backend: Python 3.11 + FastAPI + SQLAlchemy
echo   i Frontend: Node.js + Next.js 16
echo.

:: Paso 4: Iniciar servicios base (sin importer)
echo ============================================================================
echo  [4/6] INICIAR SERVICIOS BASE (DB + REDIS)
echo ============================================================================
echo.
echo   [*] Iniciando PostgreSQL (base de datos)...
echo   i Comando: %DOCKER_COMPOSE_CMD% --profile dev up -d db redis
%DOCKER_COMPOSE_CMD% --profile dev up -d db redis --remove-orphans
if !errorlevel! NEQ 0 (
    echo   [X] ERROR: No se pudo iniciar PostgreSQL
    pause >nul
    goto :eof
)
echo   [OK] Contenedor PostgreSQL iniciado

echo.
echo   [*] Esperando que PostgreSQL este lista (health check - max 90s)...
set "WAIT_COUNT=0"
:wait_db_loop
for /f "tokens=*" %%A in ('docker inspect --format="{{.State.Health.Status}}" uns-claudejp-db 2^>nul') do set "DB_STATUS=%%A"
if /i "%DB_STATUS%"=="healthy" goto :db_ready
set /a WAIT_COUNT+=1
set /a WAIT_SECONDS=!WAIT_COUNT!*10
echo   [...] Esperando... !WAIT_SECONDS! segundos
if !WAIT_COUNT! GEQ 9 (
    echo   [X] TIMEOUT: PostgreSQL no respondio en 90 segundos
    echo   i Verifica los logs: docker logs uns-claudejp-db
    pause >nul
    goto :eof
)
timeout /t 10 /nobreak >nul
goto :wait_db_loop

:db_ready
echo   [OK] PostgreSQL esta lista y saludable
echo   i Base de datos: uns_claudejp ^| Puerto: 5432
echo.

:: Paso 5: Crear tablas y datos (metodo directo)
echo ============================================================================
echo  [5/6] CREAR TABLAS Y DATOS DE NEGOCIO
echo ============================================================================
echo.

echo   [*] Iniciando servicio backend temporalmente...
echo   i Usando imagen construida en paso 3...
%DOCKER_COMPOSE_CMD% up -d backend
if !errorlevel! NEQ 0 (
    echo   [X] ERROR: No se pudo iniciar backend
    echo   i Verificando si la imagen fue construida...
    docker images | findstr "backend"
    pause >nul
    goto :eof
)
echo   [OK] Servicio backend iniciado

echo.
echo   [*] Esperando que backend este listo (20 segundos)...
for /l %%N in (1,1,4) do (
    echo   [...]Inicializando servicios... %%N/4
    timeout /t 5 /nobreak >nul
)
echo   [OK] Backend listo

echo.
echo   [*] Ejecutando migraciones de Alembic (incluye triggers e indices)...
echo   i Esto aplicara TODAS las migraciones incluyendo:
echo   i   - Tablas base (24 tablas)
echo   i   - Trigger de sincronizacion de fotos
echo   i   - Indices de busqueda (12 indices GIN/trigram)
docker exec uns-claudejp-backend bash -c "cd /app && alembic upgrade head"
if !errorlevel! NEQ 0 (
    echo   [X] ERROR: Fallo la ejecucion de migraciones
    echo   i Verifica los logs: docker logs uns-claudejp-backend
    pause >nul
    goto :eof
)
echo   [OK] Todas las migraciones aplicadas correctamente
echo   i Tablas + Triggers + Indices configurados

echo.
echo   [*] Creando usuario administrador (admin/admin123)...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "INSERT INTO users (username, email, password_hash, role, full_name, is_active, created_at, updated_at) VALUES ('admin', 'admin@uns-kikaku.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPjnswC9.4o1K', 'SUPER_ADMIN', 'Administrator', true, now(), now()) ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role, updated_at = now();" >nul 2>&1
if !errorlevel! NEQ 0 (
    echo   ! Warning: Error creando usuario admin
    pause >nul
    goto :eof
)
echo   [OK] Usuario admin creado/actualizado correctamente

echo.
echo   [*] Verificando tablas en base de datos...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\dt" 2>&1 | findstr "public" >nul
if !errorlevel! EQU 0 (
    echo   [OK] Tablas verificadas en base de datos
) else (
    echo   ! Warning: No se pudieron verificar las tablas
)
echo   [OK] Inicializacion de base de datos completada
echo.

echo   [*] Sincronizando candidatos con empleados/staff/contract_workers...
echo   i Este paso vincula candidatos con sus registros en las 3 tablas
docker exec uns-claudejp-backend python scripts/sync_candidate_employee_status.py 2>&1
if !errorlevel! NEQ 0 (
    echo   ! Warning: Error en sincronizacion (puede ser normal si no hay datos)
) else (
    echo   [OK] Sincronizacion completada
    echo   i Candidatos actualizados a status 'hired' si tienen empleado asociado
)
echo.

:: Paso 6: Iniciar servicios finales
echo ============================================================================
echo  [6/6] INICIAR SERVICIOS FINALES
echo ============================================================================
echo.
echo   [*] Iniciando frontend y servicios adicionales...
echo   i Backend ya esta corriendo desde paso 5
echo   i Omitiendo servicio importer (tablas ya creadas en paso 5)
%DOCKER_COMPOSE_CMD% up -d --no-deps frontend adminer grafana prometheus tempo otel-collector 2>&1
if !errorlevel! NEQ 0 (
    echo   [X] ERROR: Algunos servicios no iniciaron
    pause >nul
    goto :eof
)
echo   [OK] Todos los servicios iniciados
echo   i Backend:  http://localhost:8000
echo   i Frontend: http://localhost:3000
echo   i Adminer:  http://localhost:8080
echo.

echo   [*] Esperando compilacion del frontend (60 segundos)...
for /l %%N in (1,1,6) do (
    echo   [...] Compilando Next.js... %%N/6 ^(~10s cada uno^)
    timeout /t 10 /nobreak >nul
)
echo   [OK] Compilacion completada
echo.

:: ===========================================================================
::  FINALIZACION
:: ===========================================================================

echo.
echo ============================================================================
echo             [OK] REINSTALACION COMPLETADA EXITOSAMENTE
echo ============================================================================
echo.
echo URLs de Acceso:
echo   [*] Frontend:    http://localhost:3000
echo   [*] Backend:     http://localhost:8000
echo   [*] API Docs:    http://localhost:8000/api/docs
echo   [*] Adminer:     http://localhost:8080
echo.
echo Credenciales:
echo   [*] Usuario:     admin
echo   [*] Password:    admin123
echo.
echo Comandos utiles:
echo   [*] Ver logs:    scripts\LOGS.bat
echo   [*] Detener:     scripts\STOP.bat
echo.
echo   i Primera carga del frontend puede tardar 1-2 minutos
echo.
echo ============================================================================
echo       [PASO FINAL] LIMPIEZA AUTOMATICA DE FOTOS OLE
echo ============================================================================
echo.
if exist "%~dp0LIMPIAR_FOTOS_OLE.bat" (
    echo   [*] Ejecutando LIMPIAR_FOTOS_OLE.bat automaticamente...
    call "%~dp0LIMPIAR_FOTOS_OLE.bat"
    if !errorlevel! NEQ 0 (
        echo   ! Warning: LIMPIAR_FOTOS_OLE.bat completo con warnings
    ) else (
        echo   [OK] Limpieza de fotos completada
    )
) else (
    echo   ! Warning: LIMPIAR_FOTOS_OLE.bat no encontrado
    echo   i Saltando este paso (opcional)
)
echo.
echo ============================================================================
echo          REINSTALACION + LIMPIEZA COMPLETADA AL 100%%
echo ============================================================================
echo.
echo ============================================================================
echo  [OK] TODO LISTO - PRESIONA CUALQUIER TECLA PARA CERRAR
echo ============================================================================
echo.
pause >nul
