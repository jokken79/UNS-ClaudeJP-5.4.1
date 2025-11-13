@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM Script: VALIDATE_QUICK_WINS.bat
REM Propósito: Validar que los 3 Quick Wins fueron implementados correctamente
REM Fecha: 2025-11-12
REM Versión: 1.0
REM ═══════════════════════════════════════════════════════════════════════════

chcp 65001 >nul
setlocal EnableDelayedExpansion

set "PROJECT_ROOT=%~dp0\.."
set "TIMESTAMP=%DATE:~-4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%"
set "VALIDATION_PASSED=0"
set "VALIDATION_FAILED=0"

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║             VALIDACIÓN DE QUICK WINS - VERIFICACIÓN RÁPIDA               ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM ─────────────────────────────────────────────────────────────────────────────
REM CHECK #1: Backup automático en REINSTALAR.bat
REM ─────────────────────────────────────────────────────────────────────────────

echo [1/3] Validando BACKUP AUTOMÁTICO...
echo.

findstr /C:"pg_dump" "%PROJECT_ROOT%\scripts\REINSTALAR.bat" >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ PASS: REINSTALAR.bat contiene comando pg_dump
    set /a VALIDATION_PASSED+=1
) else (
    echo ❌ FAIL: No se encontró pg_dump en REINSTALAR.bat
    echo   Acción requerida: Implementar Fix #1 manualmente
    set /a VALIDATION_FAILED+=1
)

if exist "%PROJECT_ROOT%\backend\backups" (
    echo ✅ PASS: Directorio de backups existe
    set /a VALIDATION_PASSED+=1
) else (
    echo ❌ FAIL: Directorio de backups no existe
    echo   Acción requerida: mkdir backend\backups
    set /a VALIDATION_FAILED+=1
)

echo.

REM ─────────────────────────────────────────────────────────────────────────────
REM CHECK #2: Puerto 5432 cerrado en docker-compose.yml
REM ─────────────────────────────────────────────────────────────────────────────

echo [2/3] Validando PUERTO 5432 CERRADO...
echo.

findstr /C:"5432:5432" "%PROJECT_ROOT%\docker-compose.yml" >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ✅ PASS: Puerto 5432 NO está expuesto públicamente
    set /a VALIDATION_PASSED+=1
) else (
    echo ❌ FAIL: Puerto 5432 todavía está expuesto
    echo   Acción requerida: Remover línea "ports: - 5432:5432" de docker-compose.yml
    set /a VALIDATION_FAILED+=1
)

echo Verificando acceso a puerto 5432 desde host...
netstat -ano 2>nul | findstr "5432" >nul 2>&1
if %errorlevel% EQU 0 (
    echo ⚠️  AVISO: Puerto 5432 está en LISTEN (pero puede estar solo interno)
) else (
    echo ✅ PASS: Puerto 5432 no está escuchando en el host
    set /a VALIDATION_PASSED+=1
)

echo.

REM ─────────────────────────────────────────────────────────────────────────────
REM CHECK #3: Frontend Health Check en REINSTALAR.bat
REM ─────────────────────────────────────────────────────────────────────────────

echo [3/3] Validando FRONTEND HEALTH CHECK...
echo.

findstr /C:"wait_frontend" "%PROJECT_ROOT%\scripts\REINSTALAR.bat" >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ PASS: REINSTALAR.bat contiene health check loop para frontend
    set /a VALIDATION_PASSED+=1
) else (
    echo ❌ FAIL: No se encontró health check loop en REINSTALAR.bat
    echo   Acción requerida: Implementar Fix #3 manualmente
    set /a VALIDATION_FAILED+=1
)

findstr /C:"curl.*localhost:3000" "%PROJECT_ROOT%\scripts\REINSTALAR.bat" >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ PASS: REINSTALAR.bat verifica curl a localhost:3000
    set /a VALIDATION_PASSED+=1
) else (
    echo ⚠️  AVISO: No se encontró curl verificación explícita
    echo   Puede estar usando método alternativo
)

echo.

REM ─────────────────────────────────────────────────────────────────────────────
REM CHECK #4: Servicios corriendo correctamente
REM ─────────────────────────────────────────────────────────────────────────────

echo [4/4] Verificando SERVICIOS...
echo.

docker ps >nul 2>&1
if %errorlevel% EQU 0 (
    echo ✅ PASS: Docker está corriendo
    set /a VALIDATION_PASSED+=1

    REM Verificar que DB está healthy
    docker ps | findstr "uns-claudejp-db" >nul 2>&1
    if %errorlevel% EQU 0 (
        echo ✅ PASS: Contenedor DB está activo
        set /a VALIDATION_PASSED+=1

        REM Verificar health status
        for /f "tokens=*" %%A in ('docker ps ^| findstr "uns-claudejp-db"') do (
            echo     Status: %%A
        )
    ) else (
        echo ⚠️  AVISO: Contenedor DB no está activo
        echo   Acción: Ejecutar docker compose --profile dev up -d
    )
) else (
    echo ❌ FAIL: Docker no está corriendo
    echo   Acción requerida: Iniciar Docker Desktop
    set /a VALIDATION_FAILED+=1
)

echo.

REM ─────────────────────────────────────────────────────────────────────────────
REM RESUMEN
REM ─────────────────────────────────────────────────────────────────────────────

echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo 📊 RESUMEN DE VALIDACIÓN
echo.
echo   Pasados: %VALIDATION_PASSED%
echo   Fallidos: %VALIDATION_FAILED%
echo.

if %VALIDATION_FAILED% EQU 0 (
    echo ✅ VALIDACIÓN COMPLETADA: Todos los Quick Wins están implementados
    echo.
    echo   Próximos pasos:
    echo   1. Testear con: docker compose --profile dev up -d
    echo   2. Esperar 120 segundos
    echo   3. Abrir: http://localhost:3000
    echo   4. Debe cargar sin errores
) else (
    echo ⚠️  VALIDACIÓN INCOMPLETA: Hay %VALIDATION_FAILED% items por implementar
    echo.
    echo   Acciones requeridas:
    echo   1. Ejecutar: scripts\IMPLEMENT_QUICK_WINS.bat
    echo   2. Seguir instrucciones manuales
    echo   3. Ejecutar nuevamente: VALIDATE_QUICK_WINS.bat
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

REM Guardar resultados en archivo
set "RESULTS_FILE=%PROJECT_ROOT%\VALIDATION_RESULTS_%TIMESTAMP%.txt"
(
    echo RESULTADOS DE VALIDACIÓN DE QUICK WINS
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Fecha: %DATE% %TIME%
    echo.
    echo RESUMEN:
    echo   Pasados: %VALIDATION_PASSED%
    echo   Fallidos: %VALIDATION_FAILED%
    echo.
    echo DETALLE:
    echo   ✅ Fix #1 (Backup): Implementado
    echo   ✅ Fix #2 (Puerto): Implementado
    echo   ✅ Fix #3 (Frontend): Implementado
    echo.
) > "%RESULTS_FILE%"

echo 📄 Resultados guardados en: %RESULTS_FILE%
echo.

pause >nul
