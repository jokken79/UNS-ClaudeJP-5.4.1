# MAPEO COMPLETO DE ESTRUCTURA - UNS-ClaudeJP 5.4.1

**Generado:** 12 de Noviembre de 2025
**Versión del Proyecto:** 5.4.1
**Estado:** Análisis Completo

---

## 📊 RESUMEN EJECUTIVO

```
UNS-ClaudeJP 5.4.1 es un HR Management System (Sistema de Gestión de Recursos Humanos)
para agencias de staffing temporal (派遣社員) en Japón.

MÉTRICAS PRINCIPALES:
├── Frontend Pages:        28 páginas en app/(dashboard)/
├── Backend Routers:       27 archivos API + deps.py
├── Backend Services:      23+ servicios especializados
├── Backend Models:        13 tablas en PostgreSQL
├── Database Migrations:   8 versiones de Alembic
├── Frontend Components:   62 componentes reutilizables
├── Docker Services:       10 servicios (6 core + 4 observability)
└── Scripts:              50+ scripts batch y PowerShell
```

---

## 1. ESTRUCTURA DE DIRECTORIOS PRINCIPAL

```
UNS-ClaudeJP-5.4.1/
│
├── 📱 FRONTEND (Next.js 16 + React 19)
│   └── frontend/
│       ├── app/
│       │   ├── (dashboard)/          ← 28 páginas de la aplicación
│       │   ├── layout.tsx            ← Layout principal
│       │   └── page.tsx              ← Home page
│       ├── components/               ← 62 componentes reutilizables
│       ├── lib/                      ← Utilidades y configuración
│       │   ├── api.ts                ← Cliente Axios con JWT
│       │   ├── themes.ts             ← 12 temas predefinidos
│       │   ├── animations.ts
│       │   ├── font-utils.ts
│       │   └── ...
│       ├── stores/                   ← Zustand state management (9 stores)
│       ├── hooks/                    ← Custom React hooks
│       ├── contexts/                 ← React contexts
│       ├── public/                   ← Archivos estáticos
│       ├── package.json              ← Dependencias (reducidas en v5.4)
│       └── next.config.js            ← Configuración Next.js
│
├── 🔙 BACKEND (FastAPI + Python 3.11)
│   └── backend/
│       ├── app/
│       │   ├── api/                  ← 27 routers API
│       │   ├── models/               ← 13 tablas SQLAlchemy
│       │   │   ├── models.py         ← Modelos principales (703 líneas)
│       │   │   ├── payroll_models.py
│       │   │   └── mixins.py
│       │   ├── schemas/              ← 20 esquemas Pydantic
│       │   ├── services/             ← 23+ servicios de negocio
│       │   │   ├── payroll/          ← 7 servicios de nómina
│       │   │   └── ...
│       │   ├── core/                 ← Config, security, deps
│       │   │   ├── config.py
│       │   │   ├── database.py
│       │   │   ├── security.py
│       │   │   ├── middleware.py
│       │   │   └── observability.py
│       │   ├── utils/                ← Utilidades compartidas
│       │   ├── scripts/              ← Scripts de gestión de datos
│       │   └── main.py               ← FastAPI app factory
│       │
│       ├── alembic/                  ← Migraciones de base de datos
│       │   ├── versions/             ← 8 versiones de migraciones
│       │   ├── env.py
│       │   ├── script.py.mako
│       │   └── alembic.ini
│       │
│       ├── tests/                    ← Suite de pruebas pytest
│       ├── requirements.txt          ← Dependencias Python
│       ├── Dockerfile               ← Imagen Docker
│       └── .dockerignore
│
├── 🐳 DOCKER & SERVICES
│   ├── docker-compose.yml           ← Orquestación de 10 servicios
│   ├── docker-compose.prod.yml      ← Configuración producción
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   ├── Dockerfile.frontend-nextjs
│   │   └── observability/           ← Configuración Grafana, Prometheus, Tempo
│   │       ├── prometheus.yml
│   │       ├── tempo.yaml
│   │       ├── otel-collector-config.yaml
│   │       └── grafana/
│   │           ├── provisioning/
│   │           └── dashboards/
│   │
├── ⚙️ CONFIGURACIÓN
│   ├── .env                         ← Variables de entorno (gitignored)
│   ├── .env.example                 ← Ejemplo de configuración
│   ├── .env.production              ← Config producción
│   ├── config/
│   │   ├── employee_master.xlsm     ← Template Excel para import
│   │   ├── factories/               ← Configuraciones de fábricas
│   │   ├── company.json
│   │   ├── production_config.py
│   │   └── security_policies.py
│   │
├── 📚 DOCUMENTACIÓN
│   ├── docs/
│   │   ├── guides/                  ← Guías de desarrollo
│   │   ├── architecture/            ← Documentación de arquitectura
│   │   └── 04-troubleshooting/      ← Troubleshooting
│   │
├── 🛠️ SCRIPTS & AUTOMATIZACIÓN
│   ├── scripts/                     ← 50+ scripts batch y PowerShell
│   │   ├── START.bat
│   │   ├── STOP.bat
│   │   ├── LOGS.bat
│   │   ├── BACKUP_DATOS.bat
│   │   ├── BUILD_BACKEND_FUN.bat
│   │   ├── BUILD_FRONTEND_FUN.bat
│   │   └── ... (45+ más)
│   │
├── 🤖 AGENTES & ORQUESTACIÓN
│   ├── .claude/                     ← Sistema de orquestación de agentes
│   │   ├── agents.json              ← Configuración de agentes
│   │   ├── CLAUDE.md                ← Instrucciones de orquestación
│   │   └── [multiple-directories]/  ← 24+ directorios de agentes especializados
│   │
├── 📊 DATOS & RECURSOS
│   ├── base-datos/                  ← Base de datos Access antiguo
│   ├── BASEDATEJP/                  ← Datos históricos en japonés
│   ├── config/
│   │   └── factories/               ← Configuraciones de fábricas
│   ├── uploads/                     ← Archivos subidos por usuarios
│   ├── logs/                        ← Logs de aplicación
│   └── monitoring/                  ← Configuraciones de monitoreo
│
├── 🧪 TESTING
│   ├── tests/                       ← Suite de pruebas
│   └── test_screenshots/            ← Screenshots de pruebas E2E
│
├── 📝 ARCHIVOS RAÍZ
│   ├── CLAUDE.md                    ← Instrucciones para Claude Code
│   ├── README.md                    ← Documentación principal
│   ├── CHANGELOG_V5.4.1.md
│   ├── PROMPT_RECONSTRUCCION_COMPLETO.md
│   ├── .cursorrules                 ← Reglas para IA
│   ├── .env.example
│   ├── .gitignore
│   ├── package.json
│   ├── package-lock.json
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── .git/                        ← Repositorio Git
│
└── 📋 MÚLTIPLES REPORTES & DOCUMENTOS (50+ .md)
    ├── SALARY_SYSTEM_PRODUCTION_CHECKLIST.md
    ├── RBAC_TESTING_GUIDE.md
    ├── DEPLOYMENT_READINESS_SUMMARY.md
    ├── DASHBOARD_VALIDATION_REPORT.md
    ├── TIMER_CARD_REMEDIATION_FINAL_SUMMARY.md
    └── ... (muchos más)
```

---

## 2. FRONTEND - PÁGINAS DASHBOARD (28 PÁGINAS)

### Ubicación: `frontend/app/(dashboard)/`

```
frontend/app/(dashboard)/
│
├── 🏠 PÁGINA PRINCIPAL
│   └── dashboard/                   → Dashboard principal
│       ├── page.tsx
│       ├── layout.tsx
│       └── [módulos internos]
│
├── 👥 GESTIÓN DE PERSONAL
│   ├── candidates/                  → Candidatos (履歴書/Rirekisho)
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   └── new/
│   ├── employees/                   → Empleados (派遣社員)
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   └── components/
│   └── apartments/                  → Vivienda (住居管理)
│       ├── page.tsx
│       ├── [id]/
│       └── ...
│
├── 🏢 GESTIÓN DE EMPRESAS
│   ├── factories/                   → Fábricas/Clientes (派遣先)
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   └── components/
│   └── apartment-assignments/       → Asignación de viviendas
│       ├── page.tsx
│       └── components/
│
├── ⏰ ASISTENCIA Y TIEMPO
│   ├── timercards/                  → Tarjeta de tiempo (タイムカード)
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   └── components/
│   └── requests/                    → Solicitudes de empleados
│       ├── page.tsx
│       └── components/
│
├── 💰 NÓMINA Y SALARIOS
│   ├── payroll/                     → Sistema de nómina (給与)
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   ├── components/
│   │   └── ...
│   ├── salary/                      → Gestión de salarios
│   │   ├── page.tsx
│   │   └── [id]/
│   ├── rent-deductions/             → Descuentos de vivienda
│   │   ├── page.tsx
│   │   └── ...
│   └── additional-charges/          → Cargos adicionales
│       └── page.tsx
│
├── 📊 REPORTES Y ANÁLISIS
│   ├── reports/                     → Reportes generales
│   │   └── page.tsx
│   ├── apartment-reports/           → Reportes de viviendas
│   │   ├── page.tsx
│   │   └── [id]/
│   ├── apartment-calculations/      → Cálculos de vivienda
│   │   ├── page.tsx
│   │   └── components/
│   ├── apartment-assignments/       → Asignaciones
│   │   ├── page.tsx
│   │   └── [id]/
│   └── yukyu-reports/               → Reportes de incidencias (有給休暇)
│       ├── page.tsx
│       └── components/
│
├── 🏥 SOLICITUDES Y PERMISOS
│   ├── yukyu/                       → Solicitudes de vacaciones (有給休暇)
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   └── components/
│   ├── yukyu-requests/              → Bandeja de solicitudes
│   │   ├── page.tsx
│   │   └── components/
│   ├── yukyu-history/               → Historial de vacaciones
│   │   ├── page.tsx
│   │   └── components/
│   └── requests/                    → Solicitudes generales
│       ├── page.tsx
│       └── [id]/
│
├── 🎨 DISEÑO Y TEMAS
│   ├── design-system/               → Galería de componentes
│   │   └── page.tsx
│   └── [themes]/                    ← (Ver temas en lib/themes.ts)
│
├── ℹ️ INFORMACIÓN Y UTILIDADES
│   ├── help/                        → Centro de ayuda
│   │   └── page.tsx
│   ├── support/                     → Soporte
│   │   └── page.tsx
│   ├── privacy/                     → Política de privacidad
│   │   └── page.tsx
│   ├── terms/                       → Términos de servicio
│   │   └── page.tsx
│   └── construction/                → Página en construcción
│       └── page.tsx
│
├── 👨‍💼 ADMIN
│   ├── admin/                       → Panel de administración
│   │   ├── page.tsx
│   │   ├── users/
│   │   ├── settings/
│   │   └── ...
│   └── ...
│
└── 🧪 EJEMPLOS
    └── examples/                    → Ejemplos de componentes
        ├── page.tsx
        └── components/

TOTAL DE PÁGINAS: 28 páginas en app/(dashboard)/
TOTAL DE SUBRUTAS: 50+ subrutas dinámicas ([id]/, new/, etc.)
```

---

## 3. BACKEND - ROUTERS API (27 ROUTERS)

### Ubicación: `backend/app/api/`

```
backend/app/api/
│
├── 🔐 AUTENTICACIÓN
│   └── auth.py                      → Login, token refresh, logout
│       ├── POST /api/auth/login
│       ├── POST /api/auth/refresh
│       └── POST /api/auth/logout
│
├── 👥 GESTIÓN DE PERSONAL
│   ├── candidates.py                → CRUD + OCR de Rirekisho (履歴書)
│   │   ├── GET /api/candidates/
│   │   ├── POST /api/candidates/
│   │   ├── GET /api/candidates/{id}
│   │   ├── PUT /api/candidates/{id}
│   │   └── [OCR endpoints]
│   │
│   ├── employees.py                 → CRUD de empleados (派遣社員)
│   │   ├── GET /api/employees/
│   │   ├── POST /api/employees/
│   │   ├── GET /api/employees/{id}
│   │   └── PUT /api/employees/{id}
│   │
│   ├── apartments.py                → CRUD de viviendas
│   │   ├── GET /api/apartments/
│   │   ├── POST /api/apartments/
│   │   └── ...
│   │
│   ├── apartments_v2.py             → Sistema V2 de viviendas (nuevo)
│   │   ├── GET /api/apartments-v2/
│   │   ├── POST /api/apartments-v2/
│   │   └── ...
│   │
│   └── contracts.py                 → Gestión de contratos
│       ├── GET /api/contracts/
│       └── ...
│
├── 🏢 GESTIÓN DE EMPRESAS
│   └── factories.py                 → CRUD de clientes (派遣先)
│       ├── GET /api/factories/
│       ├── POST /api/factories/
│       └── ...
│
├── ⏰ ASISTENCIA Y TIEMPO
│   ├── timer_cards.py               → Tarjeta de tiempo (タイムカード)
│   │   ├── GET /api/timer-cards/
│   │   ├── POST /api/timer-cards/
│   │   └── ...
│   │
│   └── timer_cards_rbac_update.py   → Actualización RBAC de tarjetas
│       └── [endpoints especializados]
│
├── 💰 NÓMINA Y SALARIOS
│   ├── payroll.py                   → Sistema de nómina (給与)
│   │   ├── GET /api/payroll/
│   │   ├── POST /api/payroll/
│   │   ├── GET /api/payroll/{id}
│   │   └── ...
│   │
│   ├── salary.py                    → Gestión de salarios
│   │   ├── GET /api/salary/
│   │   ├── POST /api/salary/
│   │   └── ...
│   │
│   └── yukyu.py                     → Sistema de vacaciones (有給休暇)
│       ├── GET /api/yukyu/
│       ├── POST /api/yukyu/
│       ├── GET /api/yukyu/balances/
│       └── ...
│
├── 📋 SOLICITUDES Y WORKFLOWS
│   └── requests.py                  → Solicitudes de empleados
│       ├── GET /api/requests/
│       ├── POST /api/requests/
│       └── ...
│
├── 📊 REPORTES
│   └── reports.py                   → Generación de reportes
│       ├── GET /api/reports/
│       ├── POST /api/reports/
│       └── POST /api/reports/export
│
├── 🤖 OCR Y PROCESAMIENTO
│   ├── azure_ocr.py                 → OCR con Azure Computer Vision
│   │   ├── POST /api/azure-ocr/process
│   │   └── ...
│   │
│   └── import_export.py             → Importación/Exportación de datos
│       ├── POST /api/import/
│       ├── GET /api/export/
│       └── ...
│
├── 📧 NOTIFICACIONES
│   └── notifications.py             → Email, LINE, Slack
│       ├── POST /api/notifications/send-email
│       ├── POST /api/notifications/send-line
│       └── ...
│
├── ⚙️ CONFIGURACIÓN
│   ├── settings.py                  → Configuración del sistema
│   │   ├── GET /api/settings/
│   │   └── PUT /api/settings/
│   │
│   ├── role_permissions.py          → Gestión RBAC
│   │   ├── GET /api/role-permissions/
│   │   ├── PUT /api/role-permissions/
│   │   └── ...
│   │
│   └── pages.py                     → Páginas estáticas
│       ├── GET /api/pages/help
│       ├── GET /api/pages/privacy
│       └── ...
│
├── 👨‍💼 ADMINISTRACIÓN
│   ├── admin.py                     → Funciones de administrador
│   │   ├── POST /api/admin/users
│   │   ├── POST /api/admin/reset-password
│   │   └── ...
│   │
│   └── database.py                  → Utilidades de base de datos
│       ├── GET /api/database/health
│       ├── POST /api/database/backup
│       └── ...
│
├── 📊 ANALÍTICA
│   └── dashboard.py                 → Endpoints de dashboard
│       ├── GET /api/dashboard/stats
│       ├── GET /api/dashboard/charts
│       └── ...
│
├── 🔍 MONITOREO
│   └── monitoring.py                → Health checks + Prometheus
│       ├── GET /api/health
│       ├── GET /metrics
│       └── ...
│
├── 📥 IMPORTACIÓN RESILIENTE
│   └── resilient_import.py          → Importación robusta
│       ├── POST /api/resilient-import/
│       └── ...
│
└── 🔄 DEPENDENCIAS
    └── deps.py                      → Inyección de dependencias FastAPI
        ├── get_current_user()
        ├── get_db_session()
        └── ...

TOTAL DE ROUTERS: 27 archivos (.py)
TOTAL DE ENDPOINTS: 200+ endpoints REST
PREFIJO API: /api/
```

---

## 4. BACKEND - SERVICIOS (23+ SERVICES)

### Ubicación: `backend/app/services/`

```
backend/app/services/
│
├── 🔐 AUTENTICACIÓN
│   └── auth_service.py              → JWT, hash de contraseñas, sesiones
│
├── 👥 GESTIÓN DE PERSONAL
│   ├── candidate_service.py         → Lógica de candidatos
│   ├── employee_matching_service.py → Matching candidato-empleado
│   ├── apartment_service.py         → Gestión de viviendas
│   └── config_service.py            → Configuración de servicios
│
├── 📸 OCR Y DETECCIÓN
│   ├── hybrid_ocr_service.py        → Cascada OCR (Azure → EasyOCR → Tesseract)
│   ├── azure_ocr_service.py         → Azure Computer Vision (Primario)
│   ├── easyocr_service.py           → EasyOCR (Secundario)
│   ├── face_detection_service.py    → Detección de rostros
│   ├── timer_card_ocr_service.py    → OCR específico para tarjetas
│   └── photo_service.py             → Gestión de fotos
│
├── 💰 NÓMINA Y SALARIOS
│   ├── salary_service.py            → Gestión de salarios
│   ├── payroll_service.py           → Sistema de nómina
│   ├── payslip_service.py           → Generación de recibos
│   ├── salary_export_service.py     → Exportación de datos
│   ├── payroll_integration_service.py → Integración de nómina
│   └── payroll/
│       ├── deduction_calculator.py  → Cálculo de descuentos
│       ├── overtime_calculator.py   → Cálculo de horas extra
│       ├── rate_calculator.py       → Cálculo de tasas
│       ├── payroll_validator.py     → Validación de nómina
│       └── payslip_generator.py     → Generación de recibos
│
├── 📊 REPORTES
│   └── report_service.py            → Generación de reportes PDF
│
├── 📧 NOTIFICACIONES
│   └── notification_service.py      → Email, LINE, Slack
│
├── 📥 IMPORTACIÓN
│   ├── import_service.py            → Importación de datos
│   └── assignment_service.py        → Servicio de asignaciones
│
├── 🏥 VACACIONES Y PERMISOS
│   └── yukyu_service.py             → Sistema de vacaciones (有給休暇)
│
├── 📋 DEDUCCIÓN Y CARGOS
│   └── additional_charge_service.py → Cargos adicionales de vivienda
│   └── deduction_service.py         → Cálculo de descuentos
│
└── 📊 ANÁLISIS
    └── [varios servicios de análisis]

TOTAL DE SERVICIOS: 23+ archivos
PATRÓN: Separación por dominio (MVC/Clean Architecture)
```

---

## 5. BACKEND - MODELOS DE BASE DE DATOS (13 TABLAS)

### Ubicación: `backend/app/models/models.py` (703+ líneas)

```
TABLAS DE PERSONAL:
├── users                    → Usuarios del sistema
│   └── Campos: id, username, email, hashed_password, role, is_active
├── candidates              → Candidatos con datos de rirekisho (142+ campos)
│   └── Campos: id, full_name, email, phone, resume_data, photo_data_url, ...
├── employees               → Empleados en nómina (派遣社員)
│   └── Campos: id, full_name, employee_id, salary, factory_id, apartment_id, ...
├── contract_workers        → Trabajadores por contrato
│   └── Campos: similares a employees
└── staff                   → Personal administrativo
    └── Campos: specific admin fields

TABLAS DE NEGOCIOS:
├── factories               → Clientes/Sitios de trabajo (派遣先)
│   └── Campos: id, name, address, contact, industry, ...
├── apartments              → Viviendas para empleados (住居管理)
│   └── Campos: id, address, capacity, rent, utilities, ...
├── documents              → Documentos procesados
│   └── Campos: id, employee_id, doc_type, ocr_data, status, ...
└── contracts              → Contratos laborales
    └── Campos: id, employee_id, factory_id, start_date, end_date, ...

TABLAS DE OPERACIONES:
├── timer_cards            → Tarjetas de tiempo (タイムカード)
│   └── Campos: id, employee_id, date, hours_worked, overtime, ...
├── salary_calculations    → Cálculos de nómina
│   └── Campos: id, employee_id, month, base_salary, deductions, ...
├── requests               → Solicitudes de empleados
│   └── Campos: id, employee_id, type, status, reason, ...
└── audit_log              → Log de auditoría
    └── Campos: id, user_id, action, timestamp, details, ...

CARACTERÍSTICAS:
- 142 columnas en tabla candidates (con soporte para datos 100%)
- Relaciones normalizadas con FOREIGN KEYS
- Triggers para business logic automático
- Full-text search en campos relevantes
- Historial completo de cambios (audit_log)
```

---

## 6. BACKEND - ESQUEMAS PYDANTIC (20 SCHEMAS)

### Ubicación: `backend/app/schemas/`

```
base.py                  → Esquema base con timestamps
auth.py                  → Schemas de autenticación
candidate.py            → Candidatos (9483 líneas)
employee.py             → Empleados (10482 líneas)
factory.py              → Fábricas (9291 líneas)
apartment.py            → Viviendas (3056 líneas)
apartment_v2.py         → Viviendas V2 (25496 líneas)
timer_card.py           → Tarjetas de tiempo
payroll.py              → Nómina (10671 líneas)
salary.py               → Salarios (2491 líneas)
salary_unified.py       → Salarios unificados (39877 líneas)
request.py              → Solicitudes
contract.py             → Contratos
dashboard.py            → Dashboard stats
job.py                  → Trabajos
pagination.py           → Paginación
responses.py            → Respuestas estándar
settings.py             → Configuración
yukyu.py                → Vacaciones (7000 líneas)

TOTAL: 20 esquemas con validación Pydantic v2
```

---

## 7. FRONTEND - COMPONENTES (62 COMPONENTES)

### Ubicación: `frontend/components/`

```
COMPONENTES PRINCIPALES (Reutilizables):
├── ApartmentSelector.tsx
├── AzureOCRUploader.tsx
├── CandidateForm.tsx
├── CandidatePhoto.tsx
├── CandidateEvaluator.tsx
├── EmployeeForm.tsx (55409 bytes - muy complejo)
├── FactorySelector.tsx
├── LoadingSkeletons.tsx
├── OCRUploader.tsx
├── PageTransition.tsx
├── RirekishoPrintView.tsx
├── ErrorBoundary.tsx
├── TemplateManager.tsx
├── advanced-color-picker.tsx
├── animated-link.tsx
├── border-radius-visualizer.tsx
├── breadcrumb-nav.tsx
│
├── DIRECTORIOS ESPECIALIZADOS:
│   ├── apartments/           → Componentes de viviendas
│   ├── apartments/           → Componentes de cálculos
│   ├── calculations/         → Componentes de cálculos
│   ├── ThemeEditor/          → Editor de temas
│   ├── ui/                   → Shadcn/UI base components
│   └── [más subdirectorios]
│
├── ESTILOS Y TEMA:
│   ├── tailwind.config.js
│   ├── globals.css
│   └── [archivos de tema]
│
└── PATRONES:
    ├── Client Components: 'use client' para interactividad
    ├── Server Components: Componentes sin estado
    ├── Compound Pattern: Componentes que trabajan juntos
    └── Shadcn/UI Pattern: UI components reutilizables

TOTAL: 62 componentes
TIPOS: Forms, Tables, Modals, Cards, Pickers, etc.
```

---

## 8. FRONTEND - GESTIÓN DE ESTADO (9 STORES)

### Ubicación: `frontend/stores/` (Zustand)

```
auth-store.ts               → Estado de autenticación
    - user, token, login, logout

themeStore.ts              → Tema actual + preferencias (12 temas)
    - currentTheme, favorites, customThemes

fonts-store.ts             → Configuración de fuentes
    - selectedFont, availableFonts

settings-store.ts          → Configuración general
    - language, timezone, preferences

payroll-store.ts           → Estado de nómina
    - selectedMonth, calculations, filters

salary-store.ts            → Estado de salarios
    - selectedEmployee, salaryData

layout-store.ts            → Estado de layout
    - sidebarOpen, theme

visibilidad-template-store.ts → Visibilidad de templates
    - templateVisibility, userPrefs

dashboard-tabs-store.ts    → Tabs activos del dashboard
    - activeTab, tabHistory

PATRÓN: Zustand (lightweight state management)
```

---

## 9. FRONTEND - LIBRERÍAS UTILITARIAS

### Ubicación: `frontend/lib/`

```
api.ts                  → Cliente Axios con JWT (23168 bytes)
    - Interceptores de autenticación
    - Manejo de errores
    - Retry logic
    - Timeout handling

themes.ts              → Definiciones de temas (12 predefinidos)
    - default-light, default-dark
    - uns-kikaku, industrial
    - ocean-blue, mint-green, forest-green, sunset
    - royal-purple, vibrant-coral, monochrome, espresso

animations.ts          → Definiciones de animaciones (8186 bytes)
font-utils.ts          → Utilidades de fuentes (13194 bytes)
color-utils.ts         → Utilidades de color
css-export.ts          → Exportación de CSS
dashboard-data.ts      → Datos de dashboard (13827 bytes)
design-tokens.ts       → Tokens de diseño
form-animations.ts     → Animaciones de formularios
loading-utils.ts       → Utilidades de carga

SUBDIRECTORIOS:
├── api/                → Cliente API + helpers
├── constants/          → Constantes de la app
├── data/               → Datos estáticos
├── hooks/              → Custom React hooks
└── motion/             → Animaciones Framer Motion

TOTAL: 15+ librerías + subdirectorios
```

---

## 10. SERVICIOS DOCKER (10 SERVICIOS)

### Archivo: `docker-compose.yml`

```
SERVICIOS CORE (6):
├── 1. db (PostgreSQL 15-alpine)
│   ├── Puerto: 5432
│   ├── Volume: postgres_data
│   ├── Health check: pg_isready
│   └── Inicio: Primero
│
├── 2. redis (Redis 7-alpine)
│   ├── Puerto: 6379
│   ├── Maxmemory: 256mb (LRU policy)
│   ├── Volume: redis_data
│   └── Health check: redis-cli ping
│
├── 3. importer (One-time setup service)
│   ├── Función: Inicialización de datos
│   ├── Tareas:
│   │   ├── Ejecutar migraciones Alembic
│   │   ├── Seed datos demo
│   │   ├── Importar empleados
│   │   ├── Importar candidatos (100% mapping)
│   │   ├── Crear viviendas
│   │   ├── Sincronizar estado
│   │   └── Importar fotos
│   └── Perfil: dev, prod
│
├── 4. backend (FastAPI)
│   ├── Puerto: 8000
│   ├── Hot reload: Sí
│   ├── Dependencias: db (healthy), redis (healthy), importer (completado)
│   ├── Health check: GET /api/health
│   └── Comando: uvicorn app.main:app --reload
│
├── 5. frontend (Next.js 16)
│   ├── Puerto: 3000
│   ├── Hot reload: Sí (Turbopack)
│   ├── Dependencias: backend (healthy)
│   ├── Health check: HTTP GET /
│   └── Comando: npm run dev
│
└── 6. adminer (Database UI)
    ├── Puerto: 8080
    ├── Dependencias: db (healthy)
    └── Acceso: admin / [password]

SERVICIOS OBSERVABILITY (4) - NUEVO EN v5.4:
├── 7. otel-collector (OpenTelemetry)
│   ├── Puertos: 4317 (gRPC), 4318 (HTTP), 13133 (health)
│   ├── Función: Recopila traces, metrics, logs
│   └── Config: docker/observability/otel-collector-config.yaml
│
├── 8. tempo (Grafana Tempo)
│   ├── Puerto: 3200
│   ├── Función: Almacena traces distribuidas
│   ├── Volume: tempo_data
│   └── Health check: GET /status
│
├── 9. prometheus (Prometheus)
│   ├── Puerto: 9090
│   ├── Función: Almacena métricas
│   ├── Volume: prometheus_data
│   ├── Config: docker/observability/prometheus.yml
│   └── Health check: GET /-/ready
│
└── 10. grafana (Grafana)
    ├── Puerto: 3001 (mapeado desde 3000)
    ├── Función: Dashboard de observabilidad
    ├── Credenciales: admin / admin
    ├── Volumes: grafana_data + provisioning + dashboards
    └── Dependencias: prometheus, tempo

VOLÚMENES:
├── postgres_data     → Persistencia PostgreSQL
├── redis_data        → Persistencia Redis
├── grafana_data      → Datos de Grafana
├── prometheus_data   → Datos de Prometheus
├── tempo_data        → Datos de Tempo
└── uploads/          → Archivos subidos

REDES:
└── uns-network (bridge) → Comunicación entre servicios

STARTUP ORDER:
db → redis → otel-collector → tempo → prometheus → importer → backend → frontend → adminer → grafana

HEALTH CHECKS:
- Todos los servicios tienen health checks configurados
- Los servicios dependen de health checks previos
- Reintentos automáticos si fallan
- Timeouts configurados
```

---

## 11. CONFIGURACIÓN Y VARIABLES DE ENTORNO

### Archivo: `.env.example`

```
SECCIONES DE CONFIGURACIÓN:

1. DATABASE CONFIGURATION
   ├── POSTGRES_DB
   ├── POSTGRES_USER
   ├── POSTGRES_PASSWORD ⚠️ OBLIGATORIO
   └── DATABASE_URL

2. SECURITY & JWT
   ├── SECRET_KEY ⚠️ OBLIGATORIO
   ├── ALGORITHM (HS256)
   ├── ACCESS_TOKEN_EXPIRE_MINUTES (480 min = 8h)
   ├── JWT_AUDIENCE
   └── JWT_ISSUER

3. APPLICATION
   ├── APP_NAME (UNS-ClaudeJP 5.4.1)
   ├── APP_VERSION (5.4.1)
   ├── ENVIRONMENT (development/production)
   ├── DEBUG (true/false)
   ├── FRONTEND_URL
   └── BACKEND_CORS_ORIGINS

4. FILE STORAGE
   ├── UPLOAD_DIR
   ├── MAX_UPLOAD_SIZE
   ├── REPORTS_DIR
   ├── LOG_FILE
   └── LOG_LEVEL

5. OCR & AI PROVIDERS (OPCIONALES)
   ├── OCR_ENABLED
   ├── TESSERACT_LANG (jpn+eng)
   ├── GEMINI_API_KEY
   ├── GOOGLE_CLOUD_VISION_ENABLED
   ├── GOOGLE_CLOUD_VISION_API_KEY
   ├── AZURE_COMPUTER_VISION_ENDPOINT
   ├── AZURE_COMPUTER_VISION_KEY
   └── AZURE_COMPUTER_VISION_API_VERSION

6. NOTIFICATIONS (OPCIONALES)
   ├── LINE_CHANNEL_ACCESS_TOKEN
   ├── SMTP_SERVER
   ├── SMTP_PORT
   ├── SMTP_USER
   ├── SMTP_PASSWORD
   └── SMTP_FROM

7. OBSERVABILITY
   ├── ENABLE_TELEMETRY
   ├── OTEL_SERVICE_NAME
   ├── OTEL_EXPORTER_OTLP_ENDPOINT
   ├── OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
   ├── OTEL_METRICS_EXPORT_INTERVAL_MS
   └── PROMETHEUS_METRICS_PATH

8. FRONTEND SHARED
   ├── NEXT_PUBLIC_API_URL
   ├── NEXT_PUBLIC_APP_VERSION
   ├── NEXT_PUBLIC_APP_NAME
   ├── NEXT_PUBLIC_OTEL_EXPORTER_URL
   ├── NEXT_PUBLIC_GRAFANA_URL
   └── NEXT_PUBLIC_DEMO_USER/PASS

ARCHIVOS RELACIONADOS:
├── .env                    → Config local (gitignored)
├── .env.example           → Plantilla
├── .env.production        → Config producción
└── .cursorrules           → Reglas para IA assistants
```

---

## 12. ESTRUCTURA DE SCRIPTS (50+ SCRIPTS)

### Ubicación: `scripts/` (Principalmente Windows Batch)

```
SCRIPTS DE SISTEMA:
├── START.bat              → Inicia todos los servicios
├── STOP.bat               → Detiene todos los servicios
├── LOGS.bat               → Menú interactivo de logs
├── REINSTALAR.bat         → Reinstalación completa
├── HEALTH_CHECK_FUN.bat   → Verificación de salud del sistema
├── DIAGNOSTICO_FUN.bat    → Diagnóstico del sistema
│
├── SCRIPTS DE BASE DE DATOS:
│   ├── BACKUP_DATOS.bat   → Backup de base de datos
│   ├── BACKUP_DATOS_FUN.bat
│   ├── RESTAURAR_DATOS.bat → Restaurar base de datos
│   └── MIGRACION_*.bat     → Scripts de migración
│
├── SCRIPTS DE CONSTRUCCIÓN:
│   ├── BUILD_BACKEND_FUN.bat
│   ├── BUILD_FRONTEND_FUN.bat
│   └── EJECUTAR_REBUILD_Y_TEST.bat
│
├── SCRIPTS DE FOTOS:
│   ├── EXTRAER_FOTOS_ROBUSTO.bat
│   ├── BUSCAR_FOTOS.bat
│   ├── BUSCAR_FOTOS_AUTO.bat
│   ├── CARGAR_FOTOS.bat
│   └── [variaciones de fotos]
│
├── SCRIPTS DE ADMINISTRACIÓN:
│   ├── FIX_ADMIN_LOGIN_FUN.bat
│   ├── CREAR_RAMA_FUN.bat
│   ├── CREAR_ESTRUCTURA_*.bat
│   ├── INSTALAR_FUN.bat
│   ├── ARREGLAR_MIGRACIONES.bat
│   └── ...
│
├── SCRIPTS DE GENERACIÓN:
│   ├── GENERATE_DOCS.bat
│   ├── CREAR_AGENTES_DOMINIO.bat
│   ├── CREAR_AGENTES_ELITE.bat
│   └── ...
│
├── SCRIPTS POWERSHELL:
│   ├── FIX_ALL_BAT_FILES.ps1
│   ├── FIX_NEVER_CLOSE_BATS.ps1
│   ├── COPY_FACTORIES.ps1
│   └── DEBUG_ACCESS_NAMES.ps1
│
└── SCRIPTS SHELL (Linux/macOS):
    ├── generate_env.py
    ├── reorganizar_archivos_md.sh
    ├── test_apartments_v2.sh
    ├── test_apartments_workflow.sh
    └── RUN_THESE_TESTS_IN_DOCKER.sh

TOTAL: 50+ scripts batch, PowerShell y shell
GARANTÍA: Todos los .bat files permanecen abiertos (pause >nul)
```

---

## 13. MIGRACIONES DE BASE DE DATOS

### Ubicación: `backend/alembic/versions/`

```
SISTEMA DE MIGRACIONES ALEMBIC:
├── Versión 0001    → Tablas iniciales
├── Versión 0002    → Extensiones (full-text search, etc)
├── Versión 0003    → Modelos de nómina
├── Versión 0004    → Viviendas (apartments)
├── Versión 0005    → Campos adicionales
├── Versión 0006    → Vacaciones (yukyu)
├── Versión 0007    → Funciones SQL
├── Versión 0008    → Ajustes finales
│
└── TOTAL: 8 versiones de migraciones

CARACTERÍSTICAS:
- Automigración con `alembic upgrade head`
- Reversión con `alembic downgrade -1`
- Control de versiones de schema
- Historial completo guardado en base de datos
- Funciones SQL para operaciones complejas
```

---

## 14. DIRECTORIOS ESPECIALES

### `.claude/` - Sistema de Orquestación

```
.claude/
├── agents.json                      ← Configuración de agentes
├── CLAUDE.md                        ← Instrucciones de orquestación
│
├── DIRECTORIOS DE AGENTES (24+):
│   ├── archived/                    → Agentes archivados
│   ├── elite/                       → Agentes de élite
│   ├── product/                     → Agentes de producto
│   ├── templates/                   → Templates para agentes
│   ├── ai-analysis/                 → Análisis de IA
│   ├── automation/                  → Automatización
│   ├── personalities/               → Personalidades de agentes
│   ├── performance-optimizers/      → Optimizadores
│   ├── infrastructure/              → Infraestructura
│   ├── orchestration/               ← Orquestación
│   ├── deprecated/                  → Descontinuados
│   ├── backend/                     → Agentes backend
│   ├── domain-specialists/          → Especialistas de dominio
│   ├── context-orchestrators/       → Orquestadores de contexto
│   ├── data/                        → Datos y análisis
│   ├── es/                          → Español
│   ├── security/                    → Seguridad
│   ├── database/                    → Base de datos
│   ├── safety-specialists/          → Especialistas en seguridad
│   ├── frontend/                    → Agentes frontend
│   ├── business/                    → Lógica de negocio
│   ├── scripts/                     → Scripts
│   ├── choreography/                → Coreografía
│   ├── ai/                          → IA general
│   ├── design/                      → Diseño
│   ├── creative/                    → Creativo
│   └── universal/                   → Universal

PROPÓSITO: Sistema de delegación de tareas a subagentes especializados
```

### `docs/` - Documentación

```
docs/
├── guides/                          → Guías de desarrollo
│   ├── development-patterns.md
│   ├── themes.md
│   ├── templates.md
│   ├── design-tools.md
│   ├── ocr-integration.md
│   ├── authentication.md
│   └── common-issues.md
│
├── architecture/                    → Documentación de arquitectura
│   ├── frontend-structure.md
│   ├── database-schema.md
│   └── system-overview.md
│
├── 04-troubleshooting/             → Solución de problemas
│   ├── TROUBLESHOOTING.md
│   └── [guías específicas]
│
└── [múltiples subdirectorios de documentación]
```

### `docker/observability/` - Stack de Observabilidad

```
docker/observability/
├── otel-collector-config.yaml       ← Config OpenTelemetry
├── prometheus.yml                   ← Config Prometheus
├── tempo.yaml                       ← Config Grafana Tempo
│
└── grafana/
    ├── provisioning/                ← Datasources y configuración
    │   ├── dashboards.yml
    │   └── datasources/
    │       ├── prometheus.yml
    │       └── tempo.yml
    │
    └── dashboards/                  ← Dashboards predefinidos
        ├── backend-metrics.json
        ├── distributed-traces.json
        └── performance.json
```

---

## 15. ARCHIVOS DE CONFIGURACIÓN PRINCIPALES

```
RAÍZ DEL PROYECTO:

Configuración:
├── .env.example                    ← Plantilla de variables
├── .env.production                 ← Config producción
├── .env                            ← Config local (gitignored)
│
├── docker-compose.yml              ← Orquestación dev
├── docker-compose.prod.yml         ← Orquestación prod
│
├── .gitignore                      ← Archivos ignorados por git
├── .cursorrules                    ← Reglas para Claude Code
│
├── CLAUDE.md                       ← Instrucciones para Claude
├── README.md                       ← Documentación principal
├── CHANGELOG_V5.4.1.md             ← Cambios de versión
│
├── package.json                    ← Dependencias raíz (mínimo)
├── package-lock.json               ← Lock de dependencias
│
├── .git/                           ← Repositorio Git
├── .github/                        ← Configuración GitHub

Backend:
├── backend/requirements.txt         ← Dependencias Python
├── backend/Dockerfile              ← Imagen Docker backend
├── backend/app/main.py            ← Punto de entrada FastAPI
├── backend/pyproject.toml          ← Config Python
│
Frontend:
├── frontend/package.json            ← Dependencias Node
├── frontend/next.config.js         ← Config Next.js
├── frontend/tailwind.config.js     ← Config Tailwind
├── frontend/tsconfig.json          ← Config TypeScript
├── frontend/Dockerfile            ← Imagen Docker frontend
│
Docker:
├── docker/Dockerfile.backend        ← Build backend
├── docker/Dockerfile.frontend       ← Build frontend
└── docker/observability/            ← Stacks de monitoreo

Configuración de Negocio:
├── config/company.json              ← Datos de empresa
├── config/employee_master.xlsm      ← Template Excel
├── config/factories/                ← Config de fábricas
└── config/production_config.py      ← Config producción
```

---

## 16. ESTADÍSTICAS DE CÓDIGO

```
FRONTEND:
├── Páginas:              28 principales + 50+ subrutas
├── Componentes:          62 componentes reutilizables
├── Stores:               9 stores Zustand
├── Librerías:            15+ utilidades
├── Líneas de código:     ~150,000+ (estimado)
├── Lenguajes:            TypeScript, JSX, CSS, Tailwind
└── Framework:            Next.js 16 + React 19

BACKEND:
├── Routers:              27 archivos API
├── Servicios:            23+ servicios de negocio
├── Modelos:              4 archivos (703+ líneas models.py)
├── Esquemas:             20 esquemas Pydantic
├── Migraciones:          8 versiones Alembic
├── Líneas de código:     ~200,000+ (estimado)
├── Lenguaje:             Python 3.11
└── Framework:            FastAPI 0.115.6

BASE DE DATOS:
├── Tablas:               13 tablas relacionales
├── Campos:               200+ campos totales
├── Índices:              20+ índices para performance
├── Triggers:             10+ triggers para lógica automática
├── Vistas:               5+ vistas para reportes
└── Motor:                PostgreSQL 15

DOCUMENTACIÓN:
├── Archivos .md:         50+ documentos
├── Reportes:             25+ reportes de análisis
├── Guías:                15+ guías de desarrollo
└── Total caracteres:     ~5,000,000+ caracteres

CONFIGURACIÓN:
├── Servicios Docker:     10 servicios
├── Volúmenes:            5 volúmenes persistentes
├── Variables .env:       40+ variables de configuración
└── Scripts:              50+ scripts batch/powershell/shell
```

---

## 17. MODELO DE DEPENDENCIAS

### Dependencias del Sistema (Startup Order)

```
1. PostgreSQL DB (postgres:15-alpine)
   ↓ (wait for healthy)
   
2. Redis Cache (redis:7-alpine)
   ↓ (wait for healthy)
   
3. OpenTelemetry Collector (otel/opentelemetry-collector)
4. Grafana Tempo (grafana/tempo:2.5.0)
5. Prometheus (prom/prometheus:v2.52.0)
   ↓ (all observability ready)
   
6. Importer Service (one-time setup)
   ├─ Ejecuta migraciones Alembic
   ├─ Seed datos demo
   ├─ Importa empleados
   ├─ Importa candidatos
   ├─ Crea viviendas
   ├─ Importa fotos
   ├─ Vincula empleados-candidatos
   ├─ Vincula empleados-fábricas
   └─ Genera funciones SQL
   ↓ (wait for completion)
   
7. FastAPI Backend (port 8000)
   ├─ Depende de: db, redis, importer
   ├─ Health check: /api/health
   └─ Expone: REST API + OpenTelemetry
   ↓ (wait for healthy)
   
8. Next.js Frontend (port 3000)
   ├─ Depende de: backend
   ├─ Health check: HTTP GET /
   └─ Expone: Web UI
   ↓ (parallel)
   
9. Database Manager (Adminer, port 8080)
   ├─ Depende de: db
   └─ Expone: SQL client web UI
   
10. Grafana Dashboards (port 3001)
    ├─ Depende de: prometheus, tempo
    └─ Expone: Observability dashboards
```

---

## 18. TABLA COMPARATIVA DE TECNOLOGÍAS

```
┌─────────────────┬──────────────────┬─────────────────────┬──────────────┐
│ Capa            │ Tecnología       │ Versión             │ Propósito    │
├─────────────────┼──────────────────┼─────────────────────┼──────────────┤
│ FRONTEND        │                  │                     │              │
│ Framework       │ Next.js          │ 16.0.0              │ SSR/SSG      │
│ Librería UI     │ React            │ 19.0.0              │ Components   │
│ Lenguaje        │ TypeScript       │ 5.6                 │ Type safety  │
│ Estilos         │ Tailwind CSS     │ 3.4                 │ Styling      │
│ Bundler         │ Turbopack        │ included            │ Fast build   │
│ UI Components   │ Shadcn/ui        │ latest              │ Accesibles   │
│ Estado          │ Zustand          │ latest              │ Lightweight  │
│ HTTP Client     │ Axios            │ latest              │ Requests     │
│ Testing         │ Vitest           │ latest              │ Unit tests   │
│ E2E Testing     │ Playwright       │ latest              │ E2E tests    │
├─────────────────┼──────────────────┼─────────────────────┼──────────────┤
│ BACKEND         │                  │                     │              │
│ Framework       │ FastAPI          │ 0.115.6             │ REST API     │
│ Lenguaje        │ Python           │ 3.11+               │ Backend      │
│ ORM             │ SQLAlchemy       │ 2.0.36              │ Database     │
│ Validación      │ Pydantic         │ 2.10.5              │ Validation   │
│ Migraciones     │ Alembic          │ 1.17.0              │ Schema mgmt  │
│ Async           │ asyncio          │ built-in            │ Concurrency  │
│ Testing         │ pytest           │ latest              │ Unit tests   │
│ OCR Primario    │ Azure Vision     │ API                 │ Document OCR │
│ OCR Secundario  │ EasyOCR          │ latest              │ Fallback     │
│ OCR Fallback    │ Tesseract        │ installed           │ Last resort  │
├─────────────────┼──────────────────┼─────────────────────┼──────────────┤
│ DATABASE        │                  │                     │              │
│ Motor           │ PostgreSQL       │ 15                  │ RDBMS        │
│ Driver          │ psycopg2         │ latest              │ Connection   │
│ Schema          │ SQL              │ v8+ migrations      │ Schema       │
├─────────────────┼──────────────────┼─────────────────────┼──────────────┤
│ CACHE           │                  │                     │              │
│ Motor           │ Redis            │ 7-alpine            │ Caching      │
│ Protocolo       │ RESP             │ native              │ Connection   │
├─────────────────┼──────────────────┼─────────────────────┼──────────────┤
│ OBSERVABILITY   │                  │                     │              │
│ Tracing         │ OpenTelemetry    │ latest              │ Distributed  │
│ Spans Storage   │ Grafana Tempo    │ 2.5.0               │ Trace DB     │
│ Metrics         │ Prometheus       │ v2.52.0             │ Metrics DB   │
│ Dashboards      │ Grafana          │ 11.2.0              │ Visualization│
│ Collector       │ OTel Collector   │ 0.103.0             │ Aggregation  │
├─────────────────┼──────────────────┼─────────────────────┼──────────────┤
│ DEVOPS          │                  │                     │              │
│ Containers      │ Docker           │ latest              │ Containeriza│
│ Orquestación    │ Docker Compose   │ v3                  │ Orchestration│
│ CI/CD           │ GitHub Actions   │ workflows           │ Automation   │
│ VCS             │ Git              │ latest              │ Version ctrl│
└─────────────────┴──────────────────┴─────────────────────┴──────────────┘
```

---

## 19. RUTAS DE API PRINCIPALES

```
AUTENTICACIÓN:
POST   /api/auth/login                    → Iniciar sesión
POST   /api/auth/refresh                  → Refrescar token
POST   /api/auth/logout                   → Cerrar sesión

CANDIDATOS:
GET    /api/candidates                    → Listar candidatos
POST   /api/candidates                    → Crear candidato
GET    /api/candidates/{id}               → Obtener candidato
PUT    /api/candidates/{id}               → Actualizar candidato
DELETE /api/candidates/{id}               → Eliminar candidato
POST   /api/candidates/ocr/upload         → Procesar OCR

EMPLEADOS:
GET    /api/employees                     → Listar empleados
POST   /api/employees                     → Crear empleado
GET    /api/employees/{id}                → Obtener empleado
PUT    /api/employees/{id}                → Actualizar empleado
DELETE /api/employees/{id}                → Eliminar empleado

FÁBRICAS:
GET    /api/factories                     → Listar fábricas
POST   /api/factories                     → Crear fábrica
GET    /api/factories/{id}                → Obtener fábrica
PUT    /api/factories/{id}                → Actualizar fábrica

VIVIENDAS:
GET    /api/apartments                    → Listar viviendas
POST   /api/apartments                    → Crear vivienda
GET    /api/apartments/{id}               → Obtener vivienda
PUT    /api/apartments/{id}               → Actualizar vivienda

NÓMINA:
GET    /api/payroll                       → Listar nóminas
POST   /api/payroll                       → Crear nómina
GET    /api/payroll/{id}                  → Obtener nómina
PUT    /api/payroll/{id}                  → Actualizar nómina
POST   /api/payroll/calculate             → Calcular nómina

SALARIOS:
GET    /api/salary                        → Listar salarios
POST   /api/salary                        → Crear salario
PUT    /api/salary/{id}                   → Actualizar salario

VACACIONES:
GET    /api/yukyu                         → Listar solicitudes
GET    /api/yukyu/balances                → Obtener saldos
POST   /api/yukyu                         → Crear solicitud
PUT    /api/yukyu/{id}                    → Actualizar solicitud

REPORTES:
GET    /api/reports                       → Listar reportes
POST   /api/reports                       → Generar reporte
GET    /api/reports/{id}/download         → Descargar reporte

SALUD DEL SISTEMA:
GET    /api/health                        → Health check
GET    /metrics                           → Métricas Prometheus

TOTAL: 200+ endpoints REST
```

---

## 20. CARACTERÍSTICAS CLAVE DEL PROYECTO

```
FUNCIONALIDAD PRINCIPAL:
✅ Gestión completa de candidatos (履歴書 - Rirekisho)
   - 142+ campos de datos con OCR 100%
   - Procesamiento automático de documentos
   - Extracción de fotos con MediaPipe
   - Búsqueda y filtrado avanzado

✅ Gestión de empleados (派遣社員 - Haken Shain)
   - Asignación a fábricas y viviendas
   - Historial de contrataciones
   - Seguimiento de estatus

✅ Sistema de viviendas (住居管理)
   - Gestión de apartamentos
   - Cálculos de renta y servicios
   - Relaciones apartamento-fábrica
   - Sistema V2 mejorado

✅ Control de asistencia (タイムカード - Timer Cards)
   - Registro de horas trabajadas
   - Cálculo de horas extra
   - OCR de tarjetas de tiempo
   - RBAC por rol

✅ Sistema de nómina (給与 - Kyuyo)
   - Cálculos de salarios
   - Gestión de descuentos
   - Cálculos de horas extra
   - Generación de recibos de nómina

✅ Sistema de vacaciones (有給休暇 - Yukyu)
   - Solicitudes de vacaciones
   - Seguimiento de saldos
   - Aprobaciones y rechazos
   - Reportes de incidencias

✅ OCR Híbrido (Cascade)
   - Azure Computer Vision (Primario)
   - EasyOCR (Secundario)
   - Tesseract (Fallback)
   - Soporte completo para Japonés

✅ Sistema de Temas (12 predefinidos + infinitos personalizados)
   - Temas claros y oscuros
   - Temas corporativos
   - Temas naturales
   - Sistema de favoritos
   - Validación WCAG

✅ RBAC - Control de Acceso Basado en Roles
   - SUPER_ADMIN > ADMIN > COORDINATOR > KANRININSHA > EMPLOYEE > CONTRACT_WORKER
   - Permisos granulares por endpoint
   - Auditoría completa

✅ Observabilidad (OpenTelemetry)
   - Distributed tracing con Tempo
   - Métricas con Prometheus
   - Dashboards con Grafana
   - Health checks automáticos

SEGURIDAD:
✅ JWT con HS256
✅ Hash de contraseñas con bcrypt
✅ CORS configurado
✅ Validación de inputs con Pydantic
✅ Audit log completo
✅ Encriptación de datos sensibles

PERFORMANCE:
✅ Caché Redis
✅ Índices de base de datos
✅ Paginación de resultados
✅ Compresión de respuestas
✅ Hot reload en desarrollo

INTERNACIONALIZACIÓN:
✅ Interfaz en Inglés y Japonés
✅ Soporte para caracteres japoneses
✅ Localización de fechas y horas
✅ Zona horaria Asia/Tokio

DATA IMPORT/EXPORT:
✅ Importación desde Excel
✅ Exportación a Excel
✅ Importación resiliente (con reintentos)
✅ Mapeo 100% de campos
```

---

## RESUMEN FINAL

```
PROYECTO:            UNS-ClaudeJP 5.4.1
DESCRIPCIÓN:         HR Management System para Agencias de Staffing Temporal Japonesas
VERSION:             5.4.1 (Latest)
ESTATUS:             Producción lista
TECNOLOGÍAS:         Next.js 16, React 19, FastAPI 0.115.6, PostgreSQL 15

ESTADÍSTICAS:
├── Páginas frontend:          28 principales
├── Routers backend:           27 API endpoints
├── Servicios:                 23+ especializados
├── Componentes:               62 reutilizables
├── Tablas de base de datos:   13 (200+ campos)
├── Servicios Docker:          10 (6 core + 4 observability)
├── Migraciones:               8 versiones Alembic
├── Scripts:                   50+ (batch, PowerShell, Shell)
├── Archivos de documentación: 50+ reportes y guías
├── Líneas de código:          ~350,000+ (estimado)
│
└── Almacenamiento:
    ├── PostgreSQL: 13 tablas + 20+ índices
    ├── Redis: Caché de sesiones
    ├── Uploads: Fotos y documentos
    └── Logs: Auditoría completa

CARACTERÍSTICAS PRINCIPALES:
✅ Gestión integral de candidatos y empleados
✅ Control de asistencia con OCR
✅ Sistema de nómina y salarios completo
✅ Gestión de viviendas y asignaciones
✅ Sistema de vacaciones con saldos
✅ OCR Híbrido (Azure → EasyOCR → Tesseract)
✅ RBAC con 6 niveles de permisos
✅ 12 temas + personalización infinita
✅ Observabilidad con OpenTelemetry
✅ Dashboards con Grafana
✅ Health checks automáticos
✅ Audit log completo
✅ Backup y restore automático
✅ Soporte multiidioma (EN/JA)

SEGURIDAD:
✅ JWT Authentication
✅ Password hashing
✅ CORS configurado
✅ Input validation
✅ Audit logging
✅ Role-based access control

DEPLOYMENT:
✅ Docker Compose para dev/prod
✅ Health checks en todos los servicios
✅ Startup order automático
✅ Volumes para persistencia
✅ Networking interno

DESARROLLO:
✅ Hot reload en frontend y backend
✅ TypeScript para type safety
✅ Pydantic para validación
✅ Testing con pytest y Vitest
✅ E2E testing con Playwright
✅ Git version control
✅ Pre-commit hooks

DOCUMENTACIÓN:
✅ 50+ guías y reportes
✅ Troubleshooting completo
✅ API documentation (Swagger)
✅ Architecture documentation
✅ Development guides
✅ Deployment checklists

LIMPIEZA EN v5.4:
- Removidas 17 dependencias frontend innecesarias
- Removidas 5 dependencias backend innecesarias
- Reducida documentación: 67% menos archivos .md duplicados
- Sistema de observabilidad integrado
- Refactorización de dashboard con tabs
- Mejoras de performance

PRÓXIMOS PASOS RECOMENDADOS:
1. Validar todos los endpoints REST
2. Ejecutar test suite completo
3. Realizar backup de base de datos
4. Documentar procesos operacionales
5. Configurar CI/CD con GitHub Actions
6. Implementar alertas en Grafana
7. Establecer política de rotación de logs
8. Configurar SSL/TLS para producción
```

---

**Documento generado:** 12 de Noviembre de 2025
**Versión:** 1.0 Completo
**Estado:** Análisis exhaustivo completado
