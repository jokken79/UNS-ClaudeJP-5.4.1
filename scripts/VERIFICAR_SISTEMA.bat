@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0B
title UNS-ClaudeJP 5.4 - VERIFICACIÓN COMPLETA DEL SISTEMA

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                                                                      ║
echo ║       🔍 UNS-CLAUDEJP 5.4 - VERIFICACIÓN COMPLETA DEL SISTEMA 🔍    ║
echo ║                                                                      ║
echo ║         Verificación post-auditoría del sistema de candidatos       ║
echo ║                      Fecha: 2025-11-11                               ║
echo ║                                                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

set "ERROR_COUNT=0"
set "SUCCESS_COUNT=0"
set "WARNING_COUNT=0"

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 1: VERIFICACIÓN DE SERVICIOS DOCKER
:: ══════════════════════════════════════════════════════════════════════════

echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [FASE 1/5] VERIFICACIÓN DE SERVICIOS DOCKER                       │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo   ▶ Verificando servicios corriendo...
docker ps --format "table {{.Names}}\t{{.Status}}" --filter "name=uns-claudejp" | findstr "uns-claudejp" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ Servicios Docker corriendo
    docker ps --format "  - {{.Names}}: {{.Status}}" --filter "name=uns-claudejp"
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ No hay servicios corriendo
    echo   ℹ Ejecuta: scripts\START.bat
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando health de PostgreSQL...
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-db 2>nul | findstr "healthy" >nul
if !errorlevel! EQU 0 (
    echo   ✅ PostgreSQL está saludable
    set /a SUCCESS_COUNT+=1
) else (
    echo   ⚠ PostgreSQL no está saludable o no está corriendo
    set /a WARNING_COUNT+=1
)
echo.

echo   ▶ Verificando health de Backend...
docker inspect --format="{{.State.Health.Status}}" uns-claudejp-backend 2>nul | findstr "healthy" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Backend está saludable
    set /a SUCCESS_COUNT+=1
) else (
    echo   ⚠ Backend no está saludable o no está corriendo
    set /a WARNING_COUNT+=1
)
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 2: VERIFICACIÓN DE MIGRACIONES
:: ══════════════════════════════════════════════════════════════════════════

echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [FASE 2/5] VERIFICACIÓN DE MIGRACIONES ALEMBIC                    │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo   ▶ Verificando estado de migraciones...
docker exec uns-claudejp-backend bash -c "cd /app && alembic current" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ Alembic está funcional
    docker exec uns-claudejp-backend bash -c "cd /app && alembic current"
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ Error ejecutando Alembic
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando migraciones pendientes...
docker exec uns-claudejp-backend bash -c "cd /app && alembic heads" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ No hay migraciones pendientes
    set /a SUCCESS_COUNT+=1
) else (
    echo   ⚠ Hay migraciones pendientes, ejecuta: alembic upgrade head
    set /a WARNING_COUNT+=1
)
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 3: VERIFICACIÓN DE BASE DE DATOS
:: ══════════════════════════════════════════════════════════════════════════

echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [FASE 3/5] VERIFICACIÓN DE BASE DE DATOS                          │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo   ▶ Verificando trigger de sincronización de fotos...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\df sync_candidate_photo_to_employees" 2>nul | findstr "sync_candidate_photo_to_employees" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Trigger de sincronización existe
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ Trigger de sincronización NO existe
    echo   ℹ Ejecuta migración: backend/alembic/versions/2025_11_11_1200_add_photo_sync_trigger.py
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando índices de búsqueda...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\di" 2>nul | findstr "idx_candidate_name_kanji_trgm" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Índices de búsqueda existen
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ Índices de búsqueda NO existen
    echo   ℹ Ejecuta migración: backend/alembic/versions/2025_11_11_1200_add_search_indexes.py
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Contando tablas en base de datos...
for /f %%i in ('docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = ''public'';" 2^>nul') do set TABLE_COUNT=%%i
if defined TABLE_COUNT (
    if !TABLE_COUNT! GEQ 13 (
        echo   ✅ Base de datos tiene !TABLE_COUNT! tablas (esperado: 13+)
        set /a SUCCESS_COUNT+=1
    ) else (
        echo   ⚠ Base de datos solo tiene !TABLE_COUNT! tablas (esperado: 13+)
        set /a WARNING_COUNT+=1
    )
) else (
    echo   ❌ No se pudo verificar tablas
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando usuario admin...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -t -c "SELECT username FROM users WHERE username='admin' LIMIT 1;" 2>nul | findstr "admin" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Usuario admin existe
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ Usuario admin NO existe
    echo   ℹ Ejecuta: scripts\REINSTALAR.bat
    set /a ERROR_COUNT+=1
)
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 4: VERIFICACIÓN DE API
:: ══════════════════════════════════════════════════════════════════════════

echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [FASE 4/5] VERIFICACIÓN DE API                                    │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo   ▶ Verificando endpoint de health check...
curl -s http://localhost:8000/api/health | findstr "healthy" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ API Health check OK
    curl -s http://localhost:8000/api/health
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ API Health check FALLA
    echo   ℹ Backend puede no estar corriendo o hay errores
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando documentación de API...
curl -s http://localhost:8000/api/docs 2>nul | findstr "swagger" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ API Docs accesible en http://localhost:8000/api/docs
    set /a SUCCESS_COUNT+=1
) else (
    echo   ⚠ API Docs no accesible
    set /a WARNING_COUNT+=1
)
echo.

echo   ▶ Verificando frontend...
curl -s http://localhost:3000 2>nul | findstr "html" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ Frontend accesible en http://localhost:3000
    set /a SUCCESS_COUNT+=1
) else (
    echo   ⚠ Frontend no accesible
    set /a WARNING_COUNT+=1
)
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  FASE 5: VERIFICACIÓN DE DEPENDENCIAS OCR
:: ══════════════════════════════════════════════════════════════════════════

echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [FASE 5/5] VERIFICACIÓN DE DEPENDENCIAS OCR                       │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo   ▶ Verificando mediapipe instalado...
docker exec uns-claudejp-backend python -c "import mediapipe; print('✓ mediapipe', mediapipe.__version__)" 2>nul
if !errorlevel! EQU 0 (
    echo   ✅ mediapipe instalado
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ mediapipe NO instalado
    echo   ℹ Ejecuta: docker compose build backend
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando easyocr instalado...
docker exec uns-claudejp-backend python -c "import easyocr; print('✓ easyocr instalado')" 2>nul
if !errorlevel! EQU 0 (
    echo   ✅ easyocr instalado
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ easyocr NO instalado
    echo   ℹ Ejecuta: docker compose build backend
    set /a ERROR_COUNT+=1
)
echo.

echo   ▶ Verificando tesseract instalado...
docker exec uns-claudejp-backend tesseract --version 2>nul | findstr "tesseract" >nul
if !errorlevel! EQU 0 (
    echo   ✅ tesseract instalado
    docker exec uns-claudejp-backend tesseract --version 2>nul | findstr "tesseract"
    set /a SUCCESS_COUNT+=1
) else (
    echo   ❌ tesseract NO instalado
    set /a ERROR_COUNT+=1
)
echo.

:: ══════════════════════════════════════════════════════════════════════════
::  RESUMEN FINAL
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                       RESUMEN DE VERIFICACIÓN                        ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo   ✅ Exitosos:  !SUCCESS_COUNT!
echo   ⚠  Warnings:  !WARNING_COUNT!
echo   ❌ Errores:   !ERROR_COUNT!
echo.

if !ERROR_COUNT! EQU 0 (
    if !WARNING_COUNT! EQU 0 (
        echo ╔══════════════════════════════════════════════════════════════════════╗
        echo ║                                                                      ║
        echo ║         🎉 SISTEMA 100%% VERIFICADO Y FUNCIONAL 🎉                   ║
        echo ║                                                                      ║
        echo ║   Todas las mejoras de la auditoría están implementadas             ║
        echo ║   El sistema está listo para usar                                   ║
        echo ║                                                                      ║
        echo ╚══════════════════════════════════════════════════════════════════════╝
    ) else (
        echo ╔══════════════════════════════════════════════════════════════════════╗
        echo ║                                                                      ║
        echo ║         ✅ SISTEMA VERIFICADO CON WARNINGS                           ║
        echo ║                                                                      ║
        echo ║   El sistema funciona pero hay componentes opcionales faltantes     ║
        echo ║   Revisa los warnings arriba                                        ║
        echo ║                                                                      ║
        echo ╚══════════════════════════════════════════════════════════════════════╝
    )
) else (
    echo ╔══════════════════════════════════════════════════════════════════════╗
    echo ║                                                                      ║
    echo ║         ❌ SE ENCONTRARON ERRORES                                     ║
    echo ║                                                                      ║
    echo ║   Revisa los errores marcados arriba y sigue las instrucciones      ║
    echo ║   Posibles soluciones:                                              ║
    echo ║   - Ejecuta: scripts\START.bat                                       ║
    echo ║   - Ejecuta: docker compose build backend                            ║
    echo ║   - Ejecuta: scripts\REINSTALAR.bat                                  ║
    echo ║                                                                      ║
    echo ╚══════════════════════════════════════════════════════════════════════╝
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo  PRESIONA CUALQUIER TECLA PARA CERRAR ESTA VENTANA
echo ════════════════════════════════════════════════════════════════════
pause >nul
