@echo off
setlocal EnableDelayedExpansion

title UNS-ClaudeJP 5.4 - Build Backend con Timeout Personalizado

echo.
echo ============================================================================
echo              BUILD BACKEND CON TIMEOUT PERSONALIZADO
echo ============================================================================
echo.
echo Este script te permite aumentar el timeout de pip si el build falla.
echo.
echo Timeout por defecto (ya configurado): 1000 segundos (16 minutos)
echo.
echo Opciones:
echo   [1] Usa el timeout por defecto (1000s) - RECOMENDADO
echo   [2] Aumenta a 2000 segundos (33 minutos) - Para conexiones muy lentas
echo   [3] Aumenta a 3000 segundos (50 minutos) - Para conexiones extremadamente lentas
echo   [0] CANCELAR
echo.

set /p "OPCION=Selecciona una opcion (0-3): "

if "%OPCION%"=="0" (
    echo.
    echo [X] Cancelado
    echo.
    pause >nul
    goto :eof
)

if "%OPCION%"=="1" (
    set "TIMEOUT=1000"
    goto :do_build
)

if "%OPCION%"=="2" (
    set "TIMEOUT=2000"
    goto :do_build
)

if "%OPCION%"=="3" (
    set "TIMEOUT=3000"
    goto :do_build
)

echo.
echo [X] Opcion invalida
echo.
pause >nul
goto :eof

:do_build
echo.
echo ============================================================================
echo  [*] Construyendo backend con timeout=%TIMEOUT% segundos
echo ============================================================================
echo.

set "DOCKER_BUILDKIT=1"
docker compose build backend --build-arg PIP_TIMEOUT=%TIMEOUT%

if !errorlevel! EQU 0 (
    echo.
    echo ============================================================================
    echo  [OK] Build completado exitosamente
    echo ============================================================================
    echo.
) else (
    echo.
    echo ============================================================================
    echo  [X] Build fallo
    echo  i Revisa los mensajes de error arriba
    echo  i Intenta:
    echo     - Aumentar el timeout (opcion 2 o 3)
    echo     - Limpiar cache: docker system prune -a
    echo     - Reiniciar Docker Desktop
    echo ============================================================================
    echo.
)

pause >nul
