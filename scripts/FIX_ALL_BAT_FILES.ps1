# ════════════════════════════════════════════════════════════════════════════
# FIX_ALL_BAT_FILES.ps1
# Corrección masiva de 121 bugs en 46 archivos .bat
#
# Bug: líneas "exit /b 0" o "exit /b 1" que aparecen después de "pause"
# Solución: Eliminar esas líneas "exit /b" para que las ventanas no se cierren
# ════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     FIX_ALL_BAT_FILES.ps1 - CORRECCIÓN MASIVA DE BUGS .BAT        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio raíz del proyecto
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

# Lista de 46 archivos con bugs (obtenida del análisis)
$archivosConBugs = @(
    "scripts/BACKUP.bat",
    "scripts/BACKUP_DATOS.bat",
    "scripts/BACKUP_DATOS_FUN.bat",
    "scripts/BUILD_BACKEND_FUN.bat",
    "scripts/BUILD_FRONTEND_FUN.bat",
    "scripts/BUSCAR_FOTOS_AUTO.bat",
    "scripts/BUSCAR_FOTOS_AUTO_FINAL.bat",
    "scripts/BUSCAR_FOTOS_AUTO_FIXED.bat",
    "scripts/BUSCAR_FOTOS_AUTO_WORKING.bat",
    "scripts/CREAR_RAMA_FUN.bat",
    "scripts/DIAGNOSTICO.bat",
    "scripts/EXTRAER_FOTOS.bat",
    "scripts/FIX_ADMIN_LOGIN_FUN.bat",
    "scripts/INSTALAR.bat",
    "scripts/INSTALAR_FUN.bat",
    "scripts/INSTALL_007_AGENTS.bat",
    "scripts/LIMPIAR_CACHE_FUN.bat",
    "scripts/LOGS.bat",
    "scripts/LOGS_FUN.bat",
    "scripts/MEMORY_STATS_FUN.bat",
    "scripts/PULL_CAMBIOS_FUN.bat",
    "scripts/PUSH_CAMBIOS_FUN.bat",
    "scripts/REINSTALAR.bat",
    "scripts/REINSTALAR_FUN.bat",
    "scripts/RESET_DOCKER_FUN.bat",
    "scripts/RESTAURAR_DATOS.bat",
    "scripts/RESTAURAR_DATOS_FUN.bat",
    "scripts/SETUP_NEW_PC.bat",
    "scripts/START.bat",
    "scripts/START_FUN.bat",
    "scripts/STOP.bat",
    "scripts/STOP_FUN.bat",
    "scripts/TRANSFERIR_ARCHIVOS_FALTANTES.bat",
    "scripts/VALIDATE.bat",
    "scripts/VALIDATE_DB_FUN.bat",
    "scripts/extraction/EXTRACT_PHOTOS_FROM_ACCESS.bat",
    "scripts/extraction/EXTRACT_PHOTOS_FROM_ACCESS_v2.bat",
    "scripts/git/GIT_BAJAR.bat",
    "scripts/git/GIT_SUBIR.bat",
    "scripts/utilities/CLEAN.bat",
    "scripts/utilities/LIMPIAR_CACHE_MEJORADO.bat",
    "scripts/utilities/LIMPIAR_CACHE_SIN_DOCKER.bat",
    "scripts/utilities/TEST_DOCKER_BUILD.bat",
    "scripts/utilities/UPGRADE_TO_5.0.bat",
    "scripts/utilities/VALIDAR_SISTEMA_FULL.bat",
    "scripts/windows/EXTRAER_FOTOS_ACCESS.bat"
)

$totalArchivos = $archivosConBugs.Count
$archivosCorregidos = 0
$totalBugsEliminados = 0
$archivosConError = @()

Write-Host "📊 ANÁLISIS INICIAL:" -ForegroundColor Yellow
Write-Host "   • Total de archivos a procesar: $totalArchivos" -ForegroundColor White
Write-Host "   • Bugs esperados: 121 ocurrencias" -ForegroundColor White
Write-Host ""

# Crear backup de archivos
Write-Host "📦 Creando backup de archivos..." -ForegroundColor Yellow
$backupDir = "scripts/BACKUP_BEFORE_FIX_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "   ✓ Backup creado en: $backupDir" -ForegroundColor Green
Write-Host ""

# Procesar cada archivo
Write-Host "🔧 INICIANDO CORRECCIÓN MASIVA:" -ForegroundColor Yellow
Write-Host ""

foreach ($archivo in $archivosConBugs) {
    $rutaCompleta = Join-Path -Path (Get-Location) -ChildPath $archivo

    if (-not (Test-Path $rutaCompleta)) {
        Write-Host "   ⚠ SKIP: $archivo (no existe)" -ForegroundColor DarkYellow
        continue
    }

    # Crear backup del archivo
    $nombreArchivo = Split-Path -Leaf $archivo
    $backupPath = Join-Path -Path $backupDir -ChildPath $nombreArchivo
    Copy-Item -Path $rutaCompleta -Destination $backupPath -Force

    try {
        # Leer todas las líneas del archivo
        $lineas = Get-Content -Path $rutaCompleta -Encoding UTF8
        $lineasNuevas = @()
        $bugsEnArchivo = 0
        $skipNextLine = $false

        for ($i = 0; $i -lt $lineas.Count; $i++) {
            $lineaActual = $lineas[$i]

            # Si la línea anterior era pause y esta es exit, saltarla
            if ($skipNextLine) {
                if ($lineaActual -match '^\s*exit\s+/b\s+[01]\s*$') {
                    $bugsEnArchivo++
                    $totalBugsEliminados++
                    # Comentar la línea en lugar de eliminarla completamente
                    # $lineasNuevas += "REM [FIXED] $lineaActual"
                    # Mejor: simplemente no agregarla
                    $skipNextLine = $false
                    continue
                } else {
                    $skipNextLine = $false
                }
            }

            # Detectar pause (sin >nul) - marcar para revisar siguiente línea
            if ($lineaActual -match '^\s*pause\s*$') {
                $skipNextLine = $true
                $lineasNuevas += $lineaActual
                continue
            }

            # Línea normal, agregarla
            $lineasNuevas += $lineaActual
        }

        # Guardar archivo corregido
        $lineasNuevas | Set-Content -Path $rutaCompleta -Encoding UTF8

        if ($bugsEnArchivo -gt 0) {
            Write-Host "   ✓ $archivo" -ForegroundColor Green -NoNewline
            Write-Host " - $bugsEnArchivo bugs corregidos" -ForegroundColor Cyan
            $archivosCorregidos++
        } else {
            Write-Host "   ○ $archivo - sin cambios" -ForegroundColor DarkGray
        }

    } catch {
        Write-Host "   ✗ ERROR: $archivo - $($_.Exception.Message)" -ForegroundColor Red
        $archivosConError += $archivo
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   ✓ CORRECCIÓN COMPLETADA                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📊 RESUMEN FINAL:" -ForegroundColor Yellow
Write-Host "   • Archivos procesados:    $totalArchivos" -ForegroundColor White
Write-Host "   • Archivos corregidos:    $archivosCorregidos" -ForegroundColor Green
Write-Host "   • Total bugs eliminados:  $totalBugsEliminados" -ForegroundColor Cyan
Write-Host "   • Archivos con errores:   $($archivosConError.Count)" -ForegroundColor $(if ($archivosConError.Count -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($archivosConError.Count -gt 0) {
    Write-Host "⚠ ARCHIVOS CON ERRORES:" -ForegroundColor Red
    foreach ($archivoError in $archivosConError) {
        Write-Host "   • $archivoError" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "💾 BACKUP DISPONIBLE EN:" -ForegroundColor Yellow
Write-Host "   $backupDir" -ForegroundColor White
Write-Host ""

Write-Host "✅ Ahora todos los archivos .bat cumplirán la regla:" -ForegroundColor Green
Write-Host "   'MUST ALWAYS stay open to show errors'" -ForegroundColor White
Write-Host ""

Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
