# 🔍 ANÁLISIS DE INCONSISTENCIAS - Theme y CSS
**UNS-ClaudeJP 5.4**  
**Fecha**: 2025-11-12  
**Scope**: Componentes UI + Páginas principales

---

## ❌ INCONSISTENCIAS ENCONTRADAS

### 🔴 INCONSISTENCIA #1: Badge Colors - Sin usar variables de tema
**Ubicación**: `frontend/app/(dashboard)/candidates/page.tsx` línea 112-141
**Problema**: Colores hardcodeados (amarillo, verde, rojo, azul) - NO respetan tema
**Impacto**: Si cambias el tema, badges NO cambian

### 🔴 INCONSISTENCIA #2: Button Variants - Success/Warning sin mapear
**Ubicación**: `frontend/components/ui/button.tsx` línea 26-29
**Problema**: Variants definidos pero NO mapeados a CSS variables
**Impacto**: Dark mode roto, no respeta tema

### 🔴 INCONSISTENCIA #3: Page Backgrounds - Diferentes en cada página
**Ubicación**: Múltiples páginas (candidates, dashboard, factories)
**Problema**: Cada página usa diferente background
**Impacto**: Falta unificación visual

### 🟠 INCONSISTENCIA #4: Border Radius - Mezclado en button.tsx
**Ubicación**: `frontend/components/ui/button.tsx` línea 12, 34
**Problema**: Usa rounded-xl, rounded-lg, rounded-full sin escala formal
**Impacto**: Sin escala clara, difícil mantener

### 🟠 INCONSISTENCIA #5: Badge Border Radius - Inconsistente
**Ubicación**: Múltiples páginas (candidates, factories, employees)
**Problema**: Mix de rounded-full y sin estandarizar
**Impacto**: Sin formalización

### 🟠 INCONSISTENCIA #6: Shadow Usage - No formalizados
**Ubicación**: `frontend/components/ui/button.tsx` línea 17, 19, 21
**Problema**: Shadows hardcodeados sin CSS variables
**Impacto**: Inconsistente entre componentes

### 🟡 INCONSISTENCIA #7: Spacing - Sin escala consistente
**Ubicación**: Múltiples archivos (candidates, factories, employees)
**Problema**: Padding variable (px-2 py-1 vs px-2.5 py-0.5)
**Impacto**: Sin formalización

### 🟡 INCONSISTENCIA #8: Text Colors - Dark mode inconsistente
**Ubicación**: Badges en múltiples páginas
**Problema**: Colores hardcodeados (text-yellow-800, text-green-800)
**Impacto**: Si cambias tema, text-colors NO se actualizan

### 🟡 INCONSISTENCIA #9: Form Fields - Input styling
**Ubicación**: input.tsx, enhanced-input.tsx, floating-input.tsx
**Problema**: 3 componentes diferentes sin claridad de uso
**Impacto**: Confusión, duplicación

### 🟡 INCONSISTENCIA #10: Card Components - Spacing interno
**Ubicación**: `frontend/components/ui/card.tsx`
**Problema**: Padding sin escala formal
**Impacto**: Difícil ajustar

---

## 📊 TABLA RESUMEN

| # | Tipo | Severidad | Archivo | Impacto |
|---|------|-----------|---------|---------|
| 1 | Hardcoded badge colors | 🔴 ALTO | candidates/page.tsx | No respeta tema |
| 2 | Button variants no mapeados | 🔴 ALTO | button.tsx + config | Dark mode roto |
| 3 | Page backgrounds inconsistentes | 🔴 ALTO | múltiples | Falta unificación |
| 4 | Border radius mezclado | 🟠 MEDIO | button.tsx | Sin escala |
| 5 | Badge radius inconsistente | 🟠 MEDIO | múltiples | Sin formalización |
| 6 | Shadows no formalizados | 🟠 MEDIO | button.tsx | Sin CSS vars |
| 7 | Spacing sin escala | 🟡 BAJO | múltiples | Sin personalización |
| 8 | Text colors hardcodeados | 🟡 BAJO | badges | No semántico |
| 9 | 3 tipos de inputs | 🟡 BAJO | múltiples | Confusión |
| 10 | Card spacing no escalable | 🟡 BAJO | card.tsx | Difícil ajustar |

---

**Status**: 🔴 **INCONSISTENCIAS ENCONTRADAS**

