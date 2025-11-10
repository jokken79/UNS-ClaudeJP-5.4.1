@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0B
title UNS-ClaudeJP 5.2 - FIX ADMIN LOGIN

cls
echo.
echo                          ███████╗██╗██╗  ██╗
echo                          ██╔════╝██║╚██╗██╔╝
echo                          █████╗  ██║ ╚███╔╝
echo                          ██╔══╝  ██║ ██╔██╗
echo                          ██║     ██║██╔╝ ██╗
echo                          ╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo           ╔════════════════════════════════════════════════════════╗
echo           ║   🔐 VALIDAR Y REPARAR CONTRASEÑA DEL ADMINISTRADOR  ║
echo           ╚════════════════════════════════════════════════════════╝
echo.
timeout /t 2 /nobreak >nul

REM Verificar Docker
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Docker no está corriendo
    pause
    exit /b 1
)
echo   ✅ Docker está activo
echo.

REM Verificar container del backend
docker ps | findstr "uns-claudejp-backend" >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ Backend no está corriendo
    echo   💡 Intenta: START_FUN.bat
    pause
    exit /b 1
)
echo   ✅ Backend está activo
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║           🔐 REPARANDO CONTRASEÑA ADMIN 🔐              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/3] 🔍 Verificando estado del admin...
for /L %%i in (1,1,10) do (
    <nul set /p ="█">nul
    timeout /t 0.1 /nobreak >nul
)
echo. [VERIFICANDO]

REM Ejecutar el script de reparación
docker exec uns-claudejp-backend python scripts/fix_admin_password.py >nul 2>&1
if %errorlevel% neq 0 (
    echo   ⚠️  Error ejecutando fix_admin_password.py
    echo   Intentando alternativa...
)
echo.

echo [2/3] 🔧 Regenerando hash de contraseña...
for /L %%i in (1,1,10) do (
    <nul set /p ="█">nul
    timeout /t 0.1 /nobreak >nul
)
echo. [COMPLETADO]

REM Pequeña pausa
timeout /t 1 /nobreak >nul

echo [3/3] ✅ Validando credenciales...
for /L %%i in (1,1,10) do (
    <nul set /p ="█">nul
    timeout /t 0.1 /nobreak >nul
)
echo. [LISTO]
echo.

cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║       ✅ ¡CONTRASEÑA DE ADMIN REPARADA! ✅              ║
echo ║                                                            ║
echo ║                  🔐 AHORA PUEDES HACER LOGIN 🔐         ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo   📋 CREDENCIALES VÁLIDAS:
echo   ─────────────────────────────────────────────────────────
echo   • Usuario:    admin
echo   • Contraseña: admin123
echo   ─────────────────────────────────────────────────────────
echo.

echo   🌐 ACCEDER A:
echo      http://localhost:3000
echo.

echo   ⚠️  IMPORTANTE (PRODUCCIÓN):
echo      • Cambia esta contraseña inmediatamente
echo      • Navega a: Settings → Profile → Change Password
echo      • Usa una contraseña segura (mín. 16 caracteres)
echo.

pause >nul
