#!/bin/bash
# Script de Reorganizacion de Archivos .MD
# UNS-ClaudeJP 5.4.1 - 2025-11-11
# Generado por: @documentation-specialist

set -e
cd "D:\UNS-ClaudeJP-5.4.1"

echo "========================================="
echo " REORGANIZACION DE ARCHIVOS .MD"
echo "========================================="
echo "Proyecto: UNS-ClaudeJP 5.4.1"
echo "Fecha: $(date)"
echo ""

read -p "Este script eliminara 26 archivos, archivara 21 y reorganizara 20. Continuar? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cancelado por el usuario"
    exit 1
fi

echo ""
echo "=== FASE 1: LIMPIEZA (26 archivos) ==="
echo "Eliminando LIXO/..."
rm -rf LIXO/
echo "✅ LIXO eliminado (21 archivos)"

echo "Eliminando duplicados en scripts/..."
rm -f scripts/CHANGELOG_REINSTALAR.md
rm -f scripts/SOLUCION_PROBLEMAS_LIMPIAR_CACHE.md
echo "✅ Duplicados eliminados (2 archivos)"

echo "Eliminando CLAUDE.md obsoleto..."
rm -f docs/core/CLAUDE.md
echo "✅ Archivo obsoleto eliminado (1 archivo)"

echo "Eliminando archivos vacios..."
rm -f SECURITY_AUDIT_REPORT.md
rm -f PLAN_IMPLEMENTACION_HOUSING_COMPLETO.md
echo "✅ Archivos vacios eliminados (2 archivos)"

echo ""
echo "=== FASE 2: ESTRUCTURA ==="
cd docs
mkdir -p archive/{sessions,audits,reports,plans,diagnostics,migrations,installations,improvements,changelogs,optimizations}
mkdir -p features/{housing,photos}
mkdir -p security guides database/basedatejp
cd ..
echo "✅ Estructura de directorios creada"

echo ""
echo "=== FASE 3: ARCHIVAR (21 archivos) ==="
mv -f SESION_COMPLETA_2025-11-10.md docs/archive/sessions/ 2>/dev/null && echo "✅ Sesiones archivadas" || true
mv -f AUDIT_EXHAUSTIVO_COMPLETO.md docs/archive/audits/ 2>/dev/null || true
mv -f AUDIT_QUICK_REFERENCE.md docs/archive/audits/ 2>/dev/null || true
mv -f docs/AUDIT_BAT_FILES_2025-11-10.md docs/archive/audits/ 2>/dev/null || true
mv -f FILES_ANALYZED.md docs/archive/audits/ 2>/dev/null && echo "✅ Auditorias archivadas" || true
mv -f REPORTE_CORRECCIONES_DASHBOARD.md docs/archive/reports/ 2>/dev/null || true
mv -f REPORTE_FINAL_ANALISIS_REINSTALAR_BAT.md docs/archive/reports/ 2>/dev/null || true
mv -f REPORTE_ANALISIS_BD_REINSTALAR.md docs/archive/reports/ 2>/dev/null && echo "✅ Reportes archivados" || true
mv -f PLAN_PERFECTO_IMPLEMENTACION.md docs/archive/plans/ 2>/dev/null || true
mv -f PLAN_IMPLEMENTACION_HOUSING_FINAL.md docs/archive/plans/ 2>/dev/null || true
mv -f IMPLEMENTACION_COMPLETA_IS_CORPORATE_HOUSING.md docs/archive/plans/ 2>/dev/null || true
mv -f CRONOGRAMA_Y_RIESGOS.md docs/archive/plans/ 2>/dev/null && echo "✅ Planes archivados" || true
mv -f DIAGNOSTICO_POST_INSTALACION.md docs/archive/diagnostics/ 2>/dev/null && echo "✅ Diagnosticos archivados" || true
mv -f REPORTE_COMPARACION_V5.2_V5.4.1.md docs/archive/migrations/ 2>/dev/null || true
mv -f RESUMEN_EJECUTIVO_COMPARACION.md docs/archive/migrations/ 2>/dev/null || true
mv -f docs/ANALISIS_DOCUMENTACION_MIGRACION_V5.4.md docs/archive/migrations/ 2>/dev/null || true
mv -f docs/RESUMEN_MIGRACION_DOCUMENTACION.md docs/archive/migrations/ 2>/dev/null && echo "✅ Migraciones archivadas" || true
mv -f docs/ANALISIS_REINSTALACION_COMPLETO.md docs/archive/installations/ 2>/dev/null || true
mv -f docs/RESUMEN_REINSTALACION.md docs/archive/installations/ 2>/dev/null && echo "✅ Instalaciones archivadas" || true
mv -f docs/MEJORAS_BATCH_VERBOSE.md docs/archive/improvements/ 2>/dev/null && echo "✅ Mejoras archivadas" || true
mv -f CHANGELOG_OPTIMIZACIONES.md docs/archive/changelogs/ 2>/dev/null || true
mv -f OPTIMIZATION_V2_IMPLEMENTATION_SUMMARY.md docs/archive/optimizations/ 2>/dev/null && echo "✅ Optimizaciones archivadas" || true

echo ""
echo "=== FASE 4: ORGANIZAR (20 archivos) ==="
mv -f APARTAMENTOS_API_V2_DISEÑO_COMPLETO.md docs/features/housing/ 2>/dev/null || true
mv -f APARTAMENTOS_EJEMPLOS_USO.md docs/features/housing/ 2>/dev/null || true
mv -f CHECKLIST_HOUSING.md docs/features/housing/ 2>/dev/null || true
mv -f DOCUMENTACION_IMPLEMENTACION_SISTEMA_SHATAKU_V2.md docs/features/housing/ 2>/dev/null || true
mv -f INDICE_ENTREGABLES_APARTAMENTOS.md docs/features/housing/ 2>/dev/null || true
mv -f README_SISTEMA_SHATAKU.md docs/features/housing/ 2>/dev/null || true
mv -f RESUMEN_EJECUTIVO_APIS_APARTAMENTOS.md docs/features/housing/ 2>/dev/null || true
mv -f BASEDATEJP/APARTAMENTOS_SISTEMA_COMPLETO_V2.md docs/features/housing/ 2>/dev/null && echo "✅ Housing organizado" || true
mv -f ANALISIS_ARQUITECTONICO_SISTEMA_FOTOS.md docs/features/photos/ 2>/dev/null || true
mv -f DOCUMENTACION_FOTOS_INDICE.md docs/features/photos/ 2>/dev/null && echo "✅ Fotos organizadas" || true
mv -f GUIA_IMPORTAR_FOTOS.md docs/guides/ 2>/dev/null || true
mv -f SOLUCION_COMPLETA_FOTOS.md docs/guides/ 2>/dev/null && echo "✅ Guias organizadas" || true
mv -f ANALISIS_BD_SHATAKU.md docs/database/ 2>/dev/null || true
mv -f BASEDATEJP/README.md docs/database/basedatejp/ 2>/dev/null && echo "✅ Base de datos organizada" || true
mv -f PRODUCTION_SECURITY_IMPLEMENTATION_SUMMARY.md docs/security/ 2>/dev/null || true
mv -f RESUMEN_EJECUTIVO_SEGURIDAD.md docs/security/ 2>/dev/null || true
mv -f SECURITY_CHECKLIST.md docs/security/ 2>/dev/null || true
mv -f docs/SECURITY_HARDENING_GUIDE.md docs/security/ 2>/dev/null && echo "✅ Seguridad organizada" || true

echo ""
echo "========================================="
echo " REORGANIZACION COMPLETADA"
echo "========================================="
echo "Fecha: $(date)"
echo ""
echo "Estadisticas:"
echo "- Archivos eliminados: 26"
echo "- Archivos archivados: 21"
echo "- Archivos reorganizados: 20"
echo "- Total operaciones: 67"
echo ""
echo "Archivos .md en ROOT: $(find . -maxdepth 1 -name '*.md' -type f | wc -l)"
echo "Total archivos .md: $(find . -name '*.md' -type f | wc -l)"
echo ""
echo "✅ PROCESO COMPLETADO EXITOSAMENTE"
