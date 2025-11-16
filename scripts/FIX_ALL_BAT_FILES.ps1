# Script para corregir TODOS los archivos .bat que se cierran automáticamente
# Remueve "exit /b X" que aparece DESPUÉS de "pause"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  CORRIGIENDO ARCHIVOS .BAT - NUNCA SE CERRARÁN AUTOMÁTICAMENTE" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot

# Buscar todos los archivos .bat en scripts/ (incluyendo subdirectorios)
$batFiles = Get-ChildItem -Path $scriptRoot -Filter "*.bat" -Recurse

$fixedCount = 0
$skippedCount = 0
$errorCount = 0

foreach ($file in $batFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        $originalContent = $content

        # Patron 1: Remover "exit /b X" que viene después de "pause >nul" o "pause"
        $pattern1 = '(?s)(pause\s*>?\s*nul?\s*\r?\n)(?:.*?\r?\n)*?(exit\s+\/b\s+\d+)'
        $content = $content -replace $pattern1, '$1'

        # Patron 2: Remover "exit /b X" al final del archivo si hay un pause antes
        $pattern2 = '(?s)(pause\s*>?\s*nul?\s*\r?\n.*?)(\r?\nexit\s+\/b\s+\d+\s*\r?\n?)$'
        $content = $content -replace $pattern2, '$1'

        # Verificar si hubo cambios
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            Write-Host "[OK] Corregido: $($file.Name)" -ForegroundColor Green
            $fixedCount++
        } else {
            Write-Host "[SKIP] Sin cambios: $($file.Name)" -ForegroundColor Gray
            $skippedCount++
        }
    }
    catch {
        Write-Host "[ERROR] Fallo al procesar: $($file.Name)" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  RESUMEN" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Total archivos encontrados: $($batFiles.Count)" -ForegroundColor White
Write-Host "  Archivos corregidos:        $fixedCount" -ForegroundColor Green
Write-Host "  Sin cambios:                $skippedCount" -ForegroundColor Gray
Write-Host "  Errores:                    $errorCount" -ForegroundColor Red
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

if ($fixedCount -gt 0) {
    Write-Host "[OK] Todos los archivos .bat ahora NUNCA se cerrarán automáticamente!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
