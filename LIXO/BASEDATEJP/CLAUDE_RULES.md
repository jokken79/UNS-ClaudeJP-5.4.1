# CLAUDE_RULES.md - Reglas Críticas

> **🚨 LEE ESTE ARCHIVO ANTES DE HACER CUALQUIER CAMBIO**
>
> Este archivo contiene las reglas MÁS CRÍTICAS del proyecto que NUNCA debes violar.

## 🚨 REGLAS CRÍTICAS - NUNCA VIOLAR

### 1. **NUNCA BORRAR CÓDIGO FUNCIONAL**
- **Si algo funciona, NO SE TOCA** - Solo se agrega o mejora
- **Nunca borrar archivos** - Especialmente batch files (.bat), Docker configs, o archivos en `.claude/`
- **Siempre preguntar antes de modificar** - Código existente

### 2. **ARCHIVOS PROTEGIDOS - NO TOCAR**

#### Scripts Batch (Sistema Crítico)
- ❌ Todos los `.bat` en `scripts/` - Sistema depende de estos
- **Razón:** Automatización completa del sistema
- **Regla especial:** `.bat` files MUST NEVER close automatically
  - ✅ Always add `pause >nul` at the END
  - ❌ NEVER use `exit /b 1` after `pause`

#### Configuración y Orquestación
- ❌ `docker-compose.yml` - Orquestación de 6 servicios
- ❌ `.env` - Variables de entorno y secretos
- ❌ `backend/alembic/versions/` - Historial de migraciones

#### Sistema de Agentes
- ❌ `.claude/` directory - Sistema de orquestación
- ❌ `.claude/agents.json` - Configuración de agentes

#### Código Core
- ❌ `backend/app/models/models.py` - Modelos DB (703+ líneas)

### 3. **COMPATIBILIDAD WINDOWS (OBLIGATORIO)**
- **Todos los scripts deben funcionar en cualquier PC Windows con Docker Desktop**
- Usar rutas estilo Windows (backslashes `\` no `/`)
- PowerShell y cmd.exe compatible
- **NO dependencias WSL/Linux**

### 4. **BACKUP ANTES DE CAMBIOS GRANDES**
- Sugerir crear rama Git antes de cambios grandes
- Confirmar antes de modificar código existente
- Verificar que no rompa Docker orchestration

### 5. **NORMA DE GESTIÓN .md OBLIGATORIA**
**Antes de crear CUALQUIER archivo .md:**
- ✅ BUSCAR si existe archivo .md similar
- ✅ REUTILIZAR EXISTENTE agregando contenido con fecha: `## 📅 YYYY-MM-DD - [TÍTULO]`
- ✅ EVITAR DUPLICACIÓN: Prefiero editar existente que crear nuevo
- ❌ EXCEPCIÓN: Solo crear nuevo .md si tema es completamente diferente

## 🔐 DESARROLLO - CREDENCIALES

### ⚠️ PROHIBIDO (hasta nuevo aviso)
- ❌ NO cambiar contraseña del usuario `admin`
- ❌ NO cambiar usuario `admin` a otro nombre
- ❌ NO deshabilitar o eliminar usuario `admin`
- ❌ NO aplicar políticas de seguridad de producción

### ✅ PERMITIDO
- ✅ Usar `admin/admin123` para todas las pruebas
- ✅ Crear usuarios adicionales de prueba

**RAZÓN:** Sistema en MODO DESARROLLO para facilitar desarrollo y pruebas

## 🎨 STACK - VERSIONES FIJAS

### **NUNCA CAMBIAR** sin aprobación explícita

**Backend:**
- FastAPI: 0.115.6
- SQLAlchemy: 2.0.36
- Python: 3.11+

**Frontend:**
- Next.js: 16.0.0
- React: 19.0.0
- TypeScript: 5.6
- Tailwind: 3.4

**Database:**
- PostgreSQL: 15

## 🚫 NUNCA HACER

- ❌ Cambiar versiones de paquetes
- ❌ Modificar arquitectura (DB, framework)
- ❌ Eliminar triggers de base de datos
- ❌ Cambiar jerarquía de roles (6 roles fijos)
- ❌ Usar SQL directo (siempre ORM)
- ❌ Usar Pages Router (solo App Router)
- ❌ Deshabilitar validaciones
- ❌ Exponer credenciales
- ❌ Implementar todo de golpe

## ✅ SIEMPRE HACER

- ✅ Leer prompt antes de implementar
- ✅ Mostrar código antes de crear archivos
- ✅ Usar Pydantic (backend) y Zod (frontend)
- ✅ Usar Shadcn/ui components
- ✅ Implementar en fases
- ✅ Probar cada módulo antes de continuar
- ✅ Preguntar cuando hay dudas
- ✅ Documentar decisiones

## 🤖 PARA IAs (Claude, Copilot, etc.)

### **FLUJO OBLIGATORIO:**
```
📖 Leer prompt → 🤔 Entender → 💬 Mostrar código → ✅ Aprobar →
   👨‍💻 Implementar → 🧪 Probar → ✅ Confirmar → ➡️ Siguiente tarea
```

### **ANTES DE ESCRIBIR CÓDIGO:**
1. Lee sección correspondiente del prompt
2. Entiende requisitos COMPLETAMENTE
3. Verifica ejemplos de código
4. Confirma versiones de dependencias

### **FORMATO DE COMUNICACIÓN:**

**Antes de Implementar:**
```
📋 Propuesta de Implementación
Módulo: [nombre]
Archivos a crear: [lista]
Código propuesto: [MOSTRAR CÓDIGO COMPLETO]
¿Aprobado para crear archivos?
```

**Al Encontrar Error:**
```
❌ Error: [descripción]
📍 Ubicación: [archivo:línea]
🔍 Causa: [análisis]
💡 Solución propuesta: [opción]
¿Procedo?
```

## 🔗 RELACIÓN CRÍTICA: Candidates ↔ Employees

**Estrategia de Matching (OBLIGATORIA):**

1. **PRINCIPAL** - `full_name_roman` + `date_of_birth`
2. **FALLBACK** - `rirekisho_id`
3. **ÚLTIMA OPCIÓN** - Fuzzy matching

**¿Por qué NO furigana?**
- Puede cambiar entre tablas
- No es confiable

## 📋 CHECKLIST ANTES DE HACER CAMBIOS

**Verify all:**
- [ ] Leí CLAUDE_RULES.md completo
- [ ] No voy a tocar archivos protegidos
- [ ] Uso Windows-compatible paths
- [ ] No cambio versiones fijas
- [ ] No elimino código funcional
- [ ] Tengo aprobación del usuario
- [ ] Voy a documentar cambios

---

**⚠️ REMEMBER: It's better to ask and be safe than to modify and break**
