# Design Preferences Testing Guide

## ✅ Manual Testing Checklist

Este documento proporciona una guía completa para testear el sistema de Design Preferences manualmente en el navegador.

### 🚀 Pasos Previos

1. Asegúrate de que los servicios están corriendo:
   ```bash
   docker compose up -d
   ```

2. Navega a la URL:
   ```
   http://localhost:3000/design-preferences
   ```

---

## 📋 Test Suite 1: Page Load & UI Elements

### ✓ Test 1.1: Page loads successfully
**Paso:** Abre `http://localhost:3000/design-preferences`
**Esperado:**
- [ ] Página carga sin errores
- [ ] Se ve el título "Design Preferences"
- [ ] Se ve la descripción "Customize your visual experience"
- [ ] No hay errores en la consola (F12 → Console)

**Verificar:**
```javascript
// En DevTools Console
document.querySelector('h1').textContent // "Design Preferences"
```

---

### ✓ Test 1.2: Color Intensity Picker visible
**Paso:** Desplázate hacia abajo
**Esperado:**
- [ ] Se ve la sección "Color Intensity"
- [ ] Se ven dos botones: "Professional" y "Bold"
- [ ] El botón "Professional" está seleccionado (tiene check icon)

---

### ✓ Test 1.3: Animation Speed Picker visible
**Paso:** Desplázate hacia abajo
**Esperado:**
- [ ] Se ve la sección "Animation Speed"
- [ ] Se ven dos botones: "Smooth" y "Dynamic"
- [ ] El botón "Smooth" está seleccionado (tiene check icon)

---

### ✓ Test 1.4: Design Preview Panel visible
**Paso:** Mira la columna derecha
**Esperado:**
- [ ] Se ve el panel "Design Preview"
- [ ] Se ven badges mostrando "PROFESSIONAL" y "SMOOTH"
- [ ] Se ven muestras de colores
- [ ] Se ve una preview de animación

---

### ✓ Test 1.5: Alert message visible
**Paso:** En la parte superior
**Esperado:**
- [ ] Se ve el mensaje de alerta azul
- [ ] Texto: "Your preferences are saved automatically"
- [ ] Tiene icono de información

---

## 📋 Test Suite 2: Color Intensity Selector

### ✓ Test 2.1: Professional is default
**Paso:** Abre la página (sin cambios previos)
**Verificar en DevTools Console:**
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim()
// Resultado: "0.9"
```

**Esperado:**
- [ ] Valor es 0.9

---

### ✓ Test 2.2: Click Bold button
**Paso:** Haz clic en el botón "Bold"
**Esperado:**
- [ ] El botón "Bold" se selecciona (tiene check icon)
- [ ] El botón "Professional" se deselecciona
- [ ] Los colores en la preview cambian ligeramente más vibrantes

---

### ✓ Test 2.3: CSS variable changes to BOLD
**Paso:** Después de clickear Bold
**Verificar en DevTools Console:**
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim()
// Resultado: "1.3"
```

**Esperado:**
- [ ] Valor cambió a 1.3

---

### ✓ Test 2.4: Preview updates to BOLD
**Paso:** Mira el panel "Design Preview"
**Esperado:**
- [ ] El badge ahora muestra "BOLD"
- [ ] Los colores de ejemplo ahora son más vibrantes

---

### ✓ Test 2.5: Colors in dashboard change
**Paso:** Navega a `http://localhost:3000/dashboard`
**Esperado:**
- [ ] Los colores en el dashboard son más vibrantes
- [ ] Cards, botones, badges tienen colores más intensos
- [ ] Los cambios se aplican en TODA la app

---

## 📋 Test Suite 3: Animation Speed Selector

### ✓ Test 3.1: Smooth is default
**Paso:** Recarga la página (borra localStorage si es necesario)
**Verificar en DevTools Console:**
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim()
// Resultado: "1"
```

**Esperado:**
- [ ] Valor es 1

---

### ✓ Test 3.2: Click Dynamic button
**Paso:** Haz clic en el botón "Dynamic"
**Esperado:**
- [ ] El botón "Dynamic" se selecciona (tiene check icon)
- [ ] El botón "Smooth" se deselecciona
- [ ] El pequeño círculo de animación en el preview se mueve más rápido

---

### ✓ Test 3.3: CSS variable changes to DYNAMIC
**Paso:** Después de clickear Dynamic
**Verificar en DevTools Console:**
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim()
// Resultado: "0.7"
```

**Esperado:**
- [ ] Valor cambió a 0.7

---

### ✓ Test 3.4: Preview updates to DYNAMIC
**Paso:** Mira el panel "Design Preview"
**Esperado:**
- [ ] El badge ahora muestra "DYNAMIC"

---

### ✓ Test 3.5: Animations in dashboard are faster
**Paso:** Navega a `http://localhost:3000/dashboard`
**Esperado:**
- [ ] Las transiciones de página son más rápidas
- [ ] Los hovers en botones son más snappy
- [ ] Las animaciones de carga son más rápidas

---

## 📋 Test Suite 4: localStorage Persistence

### ✓ Test 4.1: Preferences saved to localStorage
**Paso:**
1. En Design Preferences, clickea "Bold"
2. Clickea "Dynamic"
3. Abre DevTools (F12) → Storage → localStorage

**Verificar:**
```javascript
localStorage.getItem('design-preferences')
// Resultado:
// {"colorIntensity":"BOLD","animationSpeed":"DYNAMIC"}
```

**Esperado:**
- [ ] Existe la clave "design-preferences"
- [ ] El valor contiene `"colorIntensity":"BOLD"`
- [ ] El valor contiene `"animationSpeed":"DYNAMIC"`

---

### ✓ Test 4.2: Preferences persist after page reload
**Paso:**
1. Establece BOLD + DYNAMIC (como en test anterior)
2. Presiona F5 para recargar la página
3. Espera a que cargue completamente

**Esperado:**
- [ ] El botón "Bold" está seleccionado
- [ ] El botón "Dynamic" está seleccionado
- [ ] CSS variables son correctos (1.3 y 0.7)
- [ ] Los colores en la preview son vibrantes
- [ ] Las animaciones son rápidas

**Verificar en DevTools Console:**
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--color-intensity').trim() // "1.3"
getComputedStyle(document.documentElement).getPropertyValue('--animation-speed-multiplier').trim() // "0.7"
```

---

### ✓ Test 4.3: Preferences persist across page navigation
**Paso:**
1. En Design Preferences, clickea "Bold" + "Dynamic"
2. Navega a `http://localhost:3000/dashboard`
3. Luego navega a otra página (ej: `http://localhost:3000/candidates`)
4. Vuelve a Design Preferences

**Esperado:**
- [ ] Bold + Dynamic siguen seleccionados
- [ ] Los valores CSS variables se mantienen
- [ ] Los colores vibrantes se mantienen en toda la app

---

### ✓ Test 4.4: Different preferences combinations work
**Paso:** Prueba cada combinación:

**PROFESSIONAL + SMOOTH:**
- [ ] Botones "Professional" y "Smooth" seleccionados
- [ ] Colores suave y profesionales
- [ ] Animaciones elegantes y lentas

**PROFESSIONAL + DYNAMIC:**
- [ ] Botones "Professional" y "Dynamic" seleccionados
- [ ] Colores suaves pero profesionales
- [ ] Animaciones rápidas

**BOLD + SMOOTH:**
- [ ] Botones "Bold" y "Smooth" seleccionados
- [ ] Colores vibrantes e intensos
- [ ] Animaciones elegantes y lentas (impactante)

**BOLD + DYNAMIC:**
- [ ] Botones "Bold" y "Dynamic" seleccionados
- [ ] Colores vibrantes e intensos
- [ ] Animaciones rápidas (muy responsivo)

---

## 📋 Test Suite 5: CSS Variables Application

### ✓ Test 5.1: Verify CSS variables are defined
**Verificar en DevTools Console:**
```javascript
const root = getComputedStyle(document.documentElement);
{
  colorIntensity: root.getPropertyValue('--color-intensity').trim(),
  animationSpeedMultiplier: root.getPropertyValue('--animation-speed-multiplier').trim(),
  durationFast: root.getPropertyValue('--duration-fast').trim(),
  durationNormal: root.getPropertyValue('--duration-normal').trim(),
  durationSlow: root.getPropertyValue('--duration-slow').trim(),
}
```

**Esperado:**
- [ ] `--color-intensity`: "0.9" o "1.3"
- [ ] `--animation-speed-multiplier`: "1" o "0.7"
- [ ] `--duration-fast`: contiene "150"
- [ ] `--duration-normal`: contiene "300"
- [ ] `--duration-slow`: contiene "500"

---

### ✓ Test 5.2: Verify theme color variables
**Verificar en DevTools Console:**
```javascript
const root = getComputedStyle(document.documentElement);
{
  primary: root.getPropertyValue('--primary').trim(),
  secondary: root.getPropertyValue('--secondary').trim(),
  accent: root.getPropertyValue('--accent').trim(),
  success: root.getPropertyValue('--success').trim(),
  warning: root.getPropertyValue('--warning').trim(),
  info: root.getPropertyValue('--info').trim(),
}
```

**Esperado:**
- [ ] Todas las variables tienen valores en formato HSL
- [ ] Formato: "número número% número%"
- [ ] Ejemplo: "210 80% 35%"

---

### ✓ Test 5.3: Verify no hardcoded colors in elements
**Verificar en DevTools:**
1. Abre DevTools (F12)
2. Inspecciona elementos (Inspector)
3. Haz clic en botones, cards, etc.

**Esperado:**
- [ ] No hay estilos inline con colores como `style="color: #abc123"`
- [ ] Los colores vienen de las clases Tailwind (ej: `bg-primary`)
- [ ] Los colores respetan las CSS variables

**Verificar en Console:**
```javascript
// Buscar elementos con inline styles de color
Array.from(document.querySelectorAll('*')).filter(el => {
  const style = el.getAttribute('style');
  return style && (style.includes('#') || style.includes('rgb'));
}).length
// Resultado: debería ser 0 o muy bajo (sin estilos inline de color)
```

---

## 📋 Test Suite 6: Theme Switching Integration

### ✓ Test 6.1: Colors respect Color Intensity setting
**Paso:**
1. Ve a Settings → Appearance → Themes
2. Selecciona cualquier tema (ej: "Neon Aurora")
3. Vuelve a Design Preferences
4. Cambia Color Intensity a BOLD

**Esperado:**
- [ ] El tema cambia a los nuevos colores (más vibrantes si es BOLD)
- [ ] Los colores en toda la app se actualizan
- [ ] No hay conflictos entre tema + intensidad

---

### ✓ Test 6.2: Animations respect Animation Speed setting
**Paso:**
1. En Design Preferences, clickea "Smooth"
2. Navega a cualquier página
3. Observa las transiciones (cambios de página, hovers, etc.)
4. Vuelve a Design Preferences
5. Clickea "Dynamic"
6. Navega nuevamente

**Esperado:**
- [ ] Con "Smooth": las animaciones son lentas y elegantes
- [ ] Con "Dynamic": las animaciones son rápidas y snappy
- [ ] Las transiciones de página son notablemente diferentes

---

## 📋 Test Suite 7: Accessibility

### ✓ Test 7.1: All buttons have text labels
**Paso:** En DevTools Console:
```javascript
Array.from(document.querySelectorAll('button')).map(btn => btn.textContent.trim()).filter(t => t)
```

**Esperado:**
- [ ] Todos los botones tienen texto visible
- [ ] No hay botones vacíos
- [ ] Texto es legible

---

### ✓ Test 7.2: Keyboard navigation works
**Paso:**
1. Presiona Tab para navegar entre elementos
2. Presiona Enter/Space en botones

**Esperado:**
- [ ] Los botones son navegables con Tab
- [ ] Se ven estilos de focus (anillo alrededor)
- [ ] Enter/Space activan los botones

---

### ✓ Test 7.3: Color contrast meets WCAG AA
**Paso:**
1. Ve a Settings → Appearance → Themes
2. Selecciona cada tema nuevo
3. Mira los textos y botones

**Esperado:**
- [ ] Texto legible en fondo claro
- [ ] Texto legible en fondo oscuro
- [ ] Contraste suficiente para leer cómodamente
- [ ] Todas las 5 nuevos temas cumplen WCAG AA

---

## 📋 Test Suite 8: Edge Cases

### ✓ Test 8.1: localStorage is cleared
**Paso:**
1. Abre DevTools → Storage → localStorage
2. Elimina "design-preferences"
3. Recarga la página

**Esperado:**
- [ ] Página carga sin errores
- [ ] Se aplican defaults (PROFESSIONAL + SMOOTH)
- [ ] CSS variables tienen valores correctos

---

### ✓ Test 8.2: Rapid clicking changes
**Paso:** Clickea rápidamente entre PROFESSIONAL y BOLD (5 veces)

**Esperado:**
- [ ] Todos los cambios se aplican correctamente
- [ ] No hay race conditions o conflictos
- [ ] Final state es consistente

---

### ✓ Test 8.3: Test with prefers-reduced-motion enabled
**Paso:**
1. En macOS: System Preferences → Accessibility → Display → Reduce motion
2. En Windows: Settings → Ease of Access → Display → Show animations
3. Recarga la página

**Esperado:**
- [ ] Las animaciones están deshabilitadas o muy rápidas
- [ ] No hay movimientos suave
- [ ] El sistema respeta la preferencia del usuario

---

## 🎯 Test Summary

### Test Results Template

```
Design Preferences Testing - [DATE]

UI Elements & Page Load:
✅ Page loads successfully
✅ Color Intensity Picker visible
✅ Animation Speed Picker visible
✅ Design Preview Panel visible
✅ Alert message visible

Color Intensity Tests:
✅ Professional is default
✅ Click Bold button
✅ CSS variable changes
✅ Preview updates
✅ Colors change in dashboard

Animation Speed Tests:
✅ Smooth is default
✅ Click Dynamic button
✅ CSS variable changes
✅ Preview updates
✅ Animations faster in dashboard

localStorage Persistence:
✅ Preferences saved
✅ Persist after reload
✅ Persist across navigation
✅ Combinations work

CSS Variables:
✅ All variables defined
✅ Color variables HSL format
✅ No hardcoded colors

Theme Integration:
✅ Color intensity respects theme
✅ Animation speed works globally

Accessibility:
✅ Buttons have text labels
✅ Keyboard navigation works
✅ WCAG AA contrast

Edge Cases:
✅ localStorage cleared
✅ Rapid clicking
✅ prefers-reduced-motion

Overall Status: ✅ PASS
```

---

## 🚀 Next Steps

Si todos los tests pasan:

1. ✅ La implementación está completa
2. ✅ El sistema es robusto
3. ✅ Los usuarios pueden personalizar su experiencia visual
4. ✅ Todas las preferencias se guardan y persisten

**¡La transformación visual está lista para producción!** 🎉
