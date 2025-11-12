@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
color 0B
title 入社連絡票 - Rebuild y Testing

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                                                                      ║
echo ║       🚀 入社連絡票 (NYŪSHA RENRAKUHYŌ) - REBUILD Y TEST 🚀         ║
echo ║                                                                      ║
echo ║         Sistema de Notificación de Nuevos Empleados                ║
echo ║                                                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo Este script realizará:
echo   1. Stop de servicios Docker
echo   2. Rebuild del backend (aplica migración automáticamente)
echo   3. Start de servicios Docker
echo   4. Verificación de migración aplicada
echo   5. Instrucciones de testing manual
echo.
echo ════════════════════════════════════════════════════════════════════
pause

:: ══════════════════════════════════════════════════════════════════════════
::  PASO 1: STOP SERVICES
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [PASO 1/5] DETENIENDO SERVICIOS DOCKER                            │
echo └────────────────────────────────────────────────────────────────────┘
echo.

docker compose down
if !errorlevel! NEQ 0 (
    echo ❌ Error deteniendo servicios
    echo ℹ Asegúrate que Docker Desktop esté corriendo
    pause
    exit /b 1
)

echo ✅ Servicios detenidos correctamente
timeout /t 3 >nul

:: ══════════════════════════════════════════════════════════════════════════
::  PASO 2: REBUILD BACKEND
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [PASO 2/5] REBUILD DEL BACKEND (Aplica migración)                 │
echo └────────────────────────────────────────────────────────────────────┘
echo.
echo ⏳ Este proceso tomará 2-5 minutos...
echo    - Construyendo imagen de Docker
echo    - Instalando dependencias
echo    - Preparando migración de base de datos
echo.

docker compose build backend
if !errorlevel! NEQ 0 (
    echo ❌ Error en rebuild del backend
    pause
    exit /b 1
)

echo ✅ Backend rebuildeado correctamente
timeout /t 2 >nul

:: ══════════════════════════════════════════════════════════════════════════
::  PASO 3: START SERVICES
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [PASO 3/5] INICIANDO SERVICIOS                                    │
echo └────────────────────────────────────────────────────────────────────┘
echo.
echo ⏳ Iniciando servicios Docker...
echo    Esto tomará 30-60 segundos
echo.

docker compose --profile dev up -d
if !errorlevel! NEQ 0 (
    echo ❌ Error iniciando servicios
    pause
    exit /b 1
)

echo ✅ Servicios iniciados
echo.
echo ⏳ Esperando 30 segundos para que servicios estén listos...
timeout /t 30 >nul

:: ══════════════════════════════════════════════════════════════════════════
::  PASO 4: VERIFY MIGRATION
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [PASO 4/5] VERIFICANDO MIGRACIÓN APLICADA                         │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo   ▶ Verificando estado de migración Alembic...
docker exec uns-claudejp-backend bash -c "cd /app && alembic current" >nul 2>&1
if !errorlevel! EQU 0 (
    echo   ✅ Alembic está funcional
    echo.
    echo   📊 Migración actual:
    docker exec uns-claudejp-backend bash -c "cd /app && alembic current"
    echo.
) else (
    echo   ⚠ Error verificando Alembic
    echo   ℹ El servicio puede estar iniciando todavía, espera 30s más
)

echo.
echo   ▶ Verificando estructura de tabla requests...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\d requests" 2>nul | findstr "candidate_id" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Columna candidate_id existe
) else (
    echo   ❌ Columna candidate_id NO existe
    echo   ℹ Ejecuta manualmente: docker exec uns-claudejp-backend bash -c "cd /app && alembic upgrade head"
)

docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\d requests" 2>nul | findstr "employee_data" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Columna employee_data existe
) else (
    echo   ❌ Columna employee_data NO existe
)

echo.
echo   ▶ Verificando índice...
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\di" 2>nul | findstr "idx_requests_candidate" >nul
if !errorlevel! EQU 0 (
    echo   ✅ Índice idx_requests_candidate_id existe
) else (
    echo   ⚠ Índice NO encontrado (puede ser normal si la migración no se aplicó aún)
)

:: ══════════════════════════════════════════════════════════════════════════
::  PASO 5: TESTING INSTRUCTIONS
:: ══════════════════════════════════════════════════════════════════════════

echo.
echo ┌────────────────────────────────────────────────────────────────────┐
echo │ [PASO 5/5] INSTRUCCIONES DE TESTING MANUAL                        │
echo └────────────────────────────────────────────────────────────────────┘
echo.

echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║                                                                      ║
echo ║         ✅ REBUILD COMPLETO - LISTO PARA TESTING                    ║
echo ║                                                                      ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 WORKFLOW DE TESTING:
echo.
echo ┌─ FASE 1: APROBAR CANDIDATO ────────────────────────────────────────┐
echo │                                                                      │
echo │  1. Abre: http://localhost:3000/candidates                         │
echo │  2. Login: admin / admin123                                        │
echo │  3. Encuentra un candidato con status "pending"                    │
echo │  4. Click en el candidato para ver detalles                        │
echo │  5. Click botón 👍 "承認" (Aprobar)                                 │
echo │                                                                      │
echo │  ✅ VERIFICAR: Mensaje de "候補者を承認しました"                     │
echo │  ✅ VERIFICAR: Status cambió a "approved"                           │
echo │                                                                      │
echo └──────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─ FASE 2: VERIFICAR 入社連絡票 CREADO ──────────────────────────────┐
echo │                                                                      │
echo │  6. Ve a: http://localhost:3000/requests                           │
echo │  7. En el filtro "全種類" selecciona "入社連絡票"                   │
echo │                                                                      │
echo │  ✅ VERIFICAR: Aparece nuevo request con badge naranja 👤          │
echo │  ✅ VERIFICAR: Muestra "📋 候補者 #X の入社手続き"                   │
echo │  ✅ VERIFICAR: Status es "審査中" (Pending)                         │
echo │                                                                      │
echo └──────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─ FASE 3: LLENAR DATOS DE EMPLEADO ─────────────────────────────────┐
echo │                                                                      │
echo │  8. Click en el request de 入社連絡票                               │
echo │  9. Verifica que aparecen los datos del candidato (read-only)      │
echo │ 10. Llena el formulario de datos de empleado:                      │
echo │     - Factory ID: FAC-001                                           │
echo │     - Hire Date: (fecha de hoy)                                     │
echo │     - Jikyu: 1500                                                   │
echo │     - Position: 製造スタッフ                                        │
echo │     - Contract Type: 正社員                                         │
echo │ 11. Click botón "保存 (Save)"                                       │
echo │                                                                      │
echo │  ✅ VERIFICAR: Mensaje "従業員データを保存しました"                 │
echo │                                                                      │
echo └──────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─ FASE 4: APROBAR Y CREAR EMPLEADO ─────────────────────────────────┐
echo │                                                                      │
echo │ 12. Click botón "承認して従業員作成"                                │
echo │ 13. Confirma en el diálogo                                          │
echo │                                                                      │
echo │  ✅ VERIFICAR: Alert muestra "入社連絡票が承認されました！"         │
echo │  ✅ VERIFICAR: Redirect a /employees/{hakenmoto_id}                 │
echo │  ✅ VERIFICAR: Empleado creado con todos los datos                  │
echo │                                                                      │
echo └──────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─ FASE 5: VERIFICAR BASE DE DATOS ──────────────────────────────────┐
echo │                                                                      │
echo │ 14. Verifica candidato status:                                      │
echo │     - Ve a /candidates/{id}                                         │
echo │     - Status debe ser "hired" o "採用済み"                          │
echo │                                                                      │
echo │ 15. Verifica request archivado:                                     │
echo │     - Ve a /requests                                                │
echo │     - Filtra por status "済"                                        │
echo │     - Debe aparecer el request con status "completed"               │
echo │                                                                      │
echo └──────────────────────────────────────────────────────────────────────┘
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo 📚 DOCUMENTACIÓN DISPONIBLE:
echo    - docs\DESIGN_NYUUSHA_RENRAKUHYO.md
echo    - docs\IMPLEMENTATION_SUMMARY_NYUUSHA_RENRAKUHYO.md
echo    - docs\NEXT_STEPS_NYUUSHA_WORKFLOW.md
echo.
echo 🔍 SI HAY PROBLEMAS:
echo    - Ver logs: docker logs uns-claudejp-backend --tail 100
echo    - Ver logs: docker logs uns-claudejp-frontend --tail 100
echo    - Verificar DB: docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo ✅ REBUILD Y VERIFICACIÓN COMPLETADOS
echo.
echo 🚀 Sistema listo para testing del workflow de 入社連絡票!
echo.
echo ════════════════════════════════════════════════════════════════════
echo  PRESIONA CUALQUIER TECLA PARA CERRAR ESTA VENTANA
echo ════════════════════════════════════════════════════════════════════
pause >nul
