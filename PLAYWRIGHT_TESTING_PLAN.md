# 🎭 Playwright E2E Testing Plan - UNS-ClaudeJP 5.4.1

## Test Suites Disponibles (15 archivos)

### Core Tests
1. **01-login-dashboard.spec.ts** - Login y Dashboard
2. **navigation.spec.ts** - Navegación general
3. **candidates.spec.ts** - Gestión de candidatos

### Yukyu (Annual Leave) System Tests
4. **02-yukyu-main.spec.ts** - Sistema principal de Yukyu
5. **03-yukyu-requests.spec.ts** - Solicitudes de leave
6. **04-yukyu-request-create.spec.ts** - Crear solicitudes
7. **05-yukyu-reports.spec.ts** - Reportes de Yukyu
8. **06-admin-yukyu.spec.ts** - Admin panel Yukyu
9. **07-payroll-yukyu.spec.ts** - Payroll integration
10. **08-yukyu-history.spec.ts** - Historial de Yukyu
11. **yukyu-all.spec.ts** - Suite completa Yukyu

### Payroll & HR Tests
12. **payroll.spec.ts** - Sistema de payroll
13. **apartments.spec.ts** - Gestión de apartamentos
14. **09-salary-system-e2e.spec.ts** - Sistema de salarios

### Admin Tests
15. **admin-panel-comprehensive-test.spec.ts** - Panel administrativo completo

---

## 📋 Configuración de Playwright

**Archivo**: `frontend/playwright.config.ts`

- **Test Directory**: `./e2e/`
- **Base URL**: `http://localhost:3000` (configurable via env)
- **Browsers**: Chromium (Firefox y Safari disponibles pero comentados)
- **Timeouts**: 
  - Test timeout: 30 segundos
  - Action timeout: 10 segundos
  - Navigation timeout: 30 segundos
- **Reporters**: HTML, Lista, JSON
- **Screenshots**: Solo en fallos
- **Videos**: Solo en reintentos
- **Dev Server**: npm run dev (auto-started)

---

## 🚀 Cómo Ejecutar los Tests

### Prerequisitos

```bash
# 1. Asegurar que los servicios estén corriendo
docker compose up -d

# 2. Esperar a que frontend esté listo (localhost:3000)
docker compose logs -f frontend | grep "ready"

# 3. Entrar al contenedor frontend
docker exec -it uns-claudejp-frontend bash
```

### Ejecutar Todos los Tests

```bash
# Dentro del contenedor o localmente
cd frontend
npm run test:e2e
```

### Ejecutar un Test Específico

```bash
# Login y Dashboard
npm run test:e2e -- 01-login-dashboard.spec.ts

# Sistema Yukyu completo
npm run test:e2e -- yukyu-all.spec.ts

# Payroll
npm run test:e2e -- payroll.spec.ts

# Admin panel
npm run test:e2e -- admin-panel-comprehensive-test.spec.ts
```

### Ejecutar Tests en Modo Debug

```bash
# Con interfaz de Playwright Inspector
npm run test:e2e -- --debug

# Con headed mode (ver browser)
npm run test:e2e -- --headed

# Con slowMo (para ver acciones en detalle)
npm run test:e2e -- --headed --workers=1 --slow-mo=500
```

### Ver Reportes

```bash
# Generar reporte HTML
npm run test:e2e

# Abrir reporte
npx playwright show-report

# O ver directamente
open playwright-report/index.html
```

---

## 📊 Test Execution Strategy

### Fase 1: Smoke Tests (5 min)
```bash
npm run test:e2e -- 01-login-dashboard.spec.ts navigation.spec.ts
```
**Verifica**: Login, navegación básica, que la app está lista

### Fase 2: Core Features (15 min)
```bash
npm run test:e2e -- candidates.spec.ts apartments.spec.ts
```
**Verifica**: Funcionalidades principales

### Fase 3: Yukyu System (20 min)
```bash
npm run test:e2e -- yukyu-all.spec.ts
```
**Verifica**: Sistema completo de leave management

### Fase 4: Payroll & Admin (15 min)
```bash
npm run test:e2e -- payroll.spec.ts admin-panel-comprehensive-test.spec.ts
```
**Verifica**: Payroll y admin functions

### Fase 5: Full Suite (60 min)
```bash
npm run test:e2e
```
**Verifica**: Todo junto

---

## 🎯 Expected Test Results

### Success Indicators ✅
- [ ] Todos los tests pasan (no fallos inesperados)
- [ ] Login y autenticación funcionan
- [ ] Navegación entre páginas sin errores
- [ ] Candidatos pueden crearse/editarse/eliminarse
- [ ] Sistema de Yukyu (leave) funciona completamente
- [ ] Payroll calcula correctamente
- [ ] Admin panel es accesible y funcional

### Things to Check
- No console errors durante tests
- Tiempos de carga aceptables
- Sin timeouts
- Todas las transiciones de página correctas

---

## 🐛 Debugging Tests

### Si un test falla:

```bash
# 1. Ejecutar solo ese test con debug
npm run test:e2e -- failing-test.spec.ts --debug

# 2. Ver screenshot/video de fallo
# Los archivos están en: playwright-report/

# 3. Ver traces (si están habilitados)
npx playwright show-trace trace.zip

# 4. Revisar logs en paralelo
docker compose logs -f backend frontend
```

### Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `Timeout: Waiting for navigation to "/"` | Backend lento | Aumentar timeout o revisar backend logs |
| `Cannot find element` | DOM no cargó | Aumentar timeout o revisar selector |
| `401 Unauthorized` | Token expirado o login falló | Revisar autenticación |
| `Connection refused` | Servicios no están corriendo | `docker compose up -d` |

---

## 📈 CI/CD Integration

### En GitHub Actions/CI:

```yaml
# Los tests se ejecutan con:
# - Workers: 1 (secuencial, más confiable en CI)
# - Retries: 2 (reintentos en caso de fallos flaky)
# - Screenshots: Solo en fallos
# - Videos: Solo en reintentos
```

---

## 💡 Best Practices

1. **Ejecutar tests en orden**: Algunos tests dependen de estado previo
2. **Usar headed mode para debugging**: `--headed` muestra el browser
3. **Revisar reportes HTML**: Mejor forma de ver qué falló
4. **Ejecutar localmente antes de pushear**: Evita CI failures
5. **Revisar logs en paralelo**: `docker compose logs -f`

---

## 🎬 Pasos para Testing Completo (Recomendado)

```bash
# 1. Verificar que servicios están corriendo
docker compose ps

# 2. Esperar a que frontend esté listo
sleep 10

# 3. Ejecutar smoke tests primero
cd frontend
npm run test:e2e -- 01-login-dashboard.spec.ts

# 4. Si smoke tests pasan, ejecutar full suite
npm run test:e2e

# 5. Ver reportes
npx playwright show-report

# 6. Revisar cualquier fallo
# Revisar playwright-report/ y videos/
```

---

## 📝 Resultado Esperado

**Exitoso**: 
```
  15 passed (2m 30s)
  HTML report generated: playwright-report/index.html
```

**Con fallos**:
```
  13 passed, 2 failed (2m 45s)
  Check: playwright-report/ for screenshots/videos
```

---

## 🔗 Recursos

- [Playwright Docs](https://playwright.dev)
- [Playwright Test Runners](https://playwright.dev/docs/intro)
- [Debugging Guide](https://playwright.dev/docs/debug)
- [Configuration](https://playwright.dev/docs/test-configuration)

---

## ✅ Post-Testing Checklist

- [ ] Todos los tests ejecutados sin errores
- [ ] Reportes HTML revisados
- [ ] Fallos documentados (si existen)
- [ ] Backend logs revisados para errores
- [ ] Docker services todos healthy
- [ ] Performance aceptable
- [ ] Ready para staging deployment

