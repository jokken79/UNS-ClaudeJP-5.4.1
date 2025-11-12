# RESUMEN RÁPIDO - ESTRUCTURA DEL PROYECTO

**Última actualización:** 12 de Noviembre de 2025

---

## TABLA RESUMIDA - COMPONENTES CLAVE

| Componente | Ubicación | Cantidad | Descripción |
|---|---|---|---|
| **FRONTEND PAGES** | `frontend/app/(dashboard)/` | 28 | Páginas principales del dashboard |
| **SUBRUTAS** | `frontend/app/(dashboard)/*/` | 50+ | Rutas dinámicas ([id]/, new/, etc.) |
| **COMPONENTES** | `frontend/components/` | 62 | Componentes React reutilizables |
| **STORES** | `frontend/stores/` | 9 | Zustand state management |
| **LIBRERÍAS** | `frontend/lib/` | 15+ | Utilidades y helpers |
| **HOOKS** | `frontend/hooks/` | 10+ | Custom React hooks |
| **API ROUTERS** | `backend/app/api/` | 27 | Endpoints FastAPI |
| **SERVICIOS** | `backend/app/services/` | 23+ | Lógica de negocio |
| **ESQUEMAS** | `backend/app/schemas/` | 20 | Validación Pydantic |
| **MODELOS** | `backend/app/models/` | 4 | SQLAlchemy models |
| **TABLAS DB** | PostgreSQL | 13 | Tablas relacionales |
| **MIGRACIONES** | `backend/alembic/versions/` | 8 | Versiones de schema |
| **SERVICIOS DOCKER** | `docker-compose.yml` | 10 | Contenedores orquestados |
| **SCRIPTS** | `scripts/` | 50+ | Batch, PowerShell, Shell |
| **DOCUMENTACIÓN** | `docs/` + raíz | 50+ | Guías, reportes, análisis |

---

## ESTADÍSTICAS RÁPIDAS

```
FRONTEND (Next.js 16 + React 19)
├── Líneas de código: ~150,000+
├── TypeScript: 95%+ de cobertura
├── Componentes: 62 reutilizables
├── Páginas: 28 en dashboard
└── Dependencias: 50+ (optimizadas en v5.4)

BACKEND (FastAPI + Python 3.11)
├── Líneas de código: ~200,000+
├── Endpoints: 200+ REST APIs
├── Servicios: 23+ especializados
├── Migraciones: 8 versiones
└── Dependencias: 30+ (optimizadas en v5.4)

DATABASE (PostgreSQL 15)
├── Tablas: 13 relacionales
├── Campos: 200+ totales
├── Índices: 20+ para performance
├── Triggers: 10+ para lógica automática
└── Vistas: 5+ para reportes

DOCKER & DEVOPS
├── Servicios: 10 totales
├── Volúmenes: 5 persistentes
├── Redes: 1 bridge (uns-network)
├── Health checks: Todos configurados
└── Startup time: ~3-5 minutos

DOCUMENTACIÓN
├── Archivos .md: 50+
├── Reportes: 25+ análisis
├── Guías: 15+ desarrollo
└── Total caracteres: 5,000,000+
```

---

## PÁGINAS FRONTEND (28 TOTAL)

```
GESTIÓN DE PERSONAL (3)
├── candidates       → Candidatos (履歴書)
├── employees        → Empleados (派遣社員)
└── apartments       → Viviendas (住居管理)

GESTIÓN DE EMPRESAS (2)
├── factories        → Clientes/Sitios
└── apartment-assignments → Asignación viviendas

ASISTENCIA Y TIEMPO (2)
├── timercards       → Tarjeta de tiempo
└── requests         → Solicitudes empleados

NÓMINA Y SALARIOS (4)
├── payroll          → Sistema de nómina
├── salary           → Gestión de salarios
├── rent-deductions  → Descuentos vivienda
└── additional-charges → Cargos adicionales

REPORTES (4)
├── reports          → Reportes generales
├── apartment-reports → Reportes viviendas
├── apartment-calculations → Cálculos vivienda
└── yukyu-reports    → Reportes vacaciones

VACACIONES (3)
├── yukyu            → Solicitudes de vacaciones
├── yukyu-requests   → Bandeja de solicitudes
└── yukyu-history    → Historial

INFORMACIÓN (5)
├── dashboard        → Dashboard principal
├── design-system    → Galería de componentes
├── help             → Centro de ayuda
├── privacy          → Privacidad
├── support          → Soporte
├── terms            → Términos
└── construction     → Construcción

ADMINISTRACIÓN (1)
└── admin            → Panel admin
```

---

## ROUTERS API (27 TOTAL)

```
AUTENTICACIÓN (1)
└── auth.py

PERSONAL (4)
├── candidates.py
├── employees.py
├── apartments.py
├── apartments_v2.py
└── contracts.py

EMPRESAS (1)
└── factories.py

TIEMPO (2)
├── timer_cards.py
└── timer_cards_rbac_update.py

NÓMINA (3)
├── payroll.py
├── salary.py
└── yukyu.py

SOLICITUDES (1)
└── requests.py

REPORTES (1)
└── reports.py

OCR (2)
├── azure_ocr.py
└── import_export.py

NOTIFICACIONES (1)
└── notifications.py

CONFIGURACIÓN (3)
├── settings.py
├── role_permissions.py
└── pages.py

ADMINISTRACIÓN (2)
├── admin.py
└── database.py

ANALÍTICA (1)
└── dashboard.py

MONITOREO (1)
└── monitoring.py

IMPORTACIÓN (1)
└── resilient_import.py

DEPENDENCIAS (1)
└── deps.py
```

---

## SERVICIOS (23+ TOTAL)

```
AUTENTICACIÓN
└── auth_service.py

PERSONAL
├── candidate_service.py
├── employee_matching_service.py
├── apartment_service.py
└── config_service.py

OCR & DETECCIÓN
├── hybrid_ocr_service.py
├── azure_ocr_service.py
├── easyocr_service.py
├── face_detection_service.py
├── timer_card_ocr_service.py
└── photo_service.py

NÓMINA & SALARIOS
├── salary_service.py
├── payroll_service.py
├── payslip_service.py
├── salary_export_service.py
├── payroll_integration_service.py
├── payroll/
│   ├── deduction_calculator.py
│   ├── overtime_calculator.py
│   ├── rate_calculator.py
│   ├── payroll_validator.py
│   └── payslip_generator.py

REPORTES
└── report_service.py

NOTIFICACIONES
└── notification_service.py

IMPORTACIÓN
├── import_service.py
└── assignment_service.py

VACACIONES
└── yukyu_service.py

CARGOS
├── additional_charge_service.py
└── deduction_service.py
```

---

## ESTRUCTURA DE CARPETAS (RESUMEN)

```
UNS-ClaudeJP-5.4.1/
├── frontend/                    (Next.js 16)
│   ├── app/(dashboard)/         (28 páginas)
│   ├── components/              (62 componentes)
│   ├── lib/                     (15+ librerías)
│   ├── stores/                  (9 stores)
│   ├── hooks/                   (10+ hooks)
│   ├── contexts/                (Contexts)
│   └── public/                  (Assets)
│
├── backend/                     (FastAPI)
│   ├── app/
│   │   ├── api/                 (27 routers)
│   │   ├── services/            (23+ servicios)
│   │   ├── schemas/             (20 schemas)
│   │   ├── models/              (4 files)
│   │   └── core/                (Config)
│   ├── alembic/versions/        (8 migraciones)
│   ├── tests/                   (Test suite)
│   └── scripts/                 (Data mgmt)
│
├── docker/                      (Configuración Docker)
│   ├── Dockerfile.*
│   └── observability/
│       ├── prometheus.yml
│       ├── tempo.yaml
│       ├── otel-collector-config.yaml
│       └── grafana/
│
├── scripts/                     (50+ scripts)
│   ├── START.bat
│   ├── STOP.bat
│   ├── BACKUP_DATOS.bat
│   └── [45+ más]
│
├── config/                      (Configuración)
│   ├── employee_master.xlsm
│   ├── company.json
│   └── factories/
│
├── docs/                        (Documentación)
│   ├── guides/
│   ├── architecture/
│   └── 04-troubleshooting/
│
├── .claude/                     (24+ agentes)
│   ├── agents.json
│   ├── CLAUDE.md
│   └── [24+ directorios]
│
└── [Raíz del proyecto]
    ├── CLAUDE.md               (Instrucciones para Claude)
    ├── README.md               (Documentación principal)
    ├── docker-compose.yml      (Orquestación)
    ├── .env.example            (Template env)
    ├── .cursorrules            (Reglas para IA)
    └── [50+ reportes .md]
```

---

## SERVICIOS DOCKER (10 TOTAL)

```
CORE SERVICES (6)
├── 1. db           (PostgreSQL 15)      → Puerto 5432
├── 2. redis        (Redis 7)            → Puerto 6379
├── 3. importer     (Setup service)      → One-time
├── 4. backend      (FastAPI)            → Puerto 8000
├── 5. frontend     (Next.js 16)         → Puerto 3000
└── 6. adminer      (Database UI)        → Puerto 8080

OBSERVABILITY (4) - NUEVO EN v5.4
├── 7. otel-collector (OpenTelemetry)   → Puertos 4317, 4318
├── 8. tempo        (Grafana Tempo)     → Puerto 3200
├── 9. prometheus   (Prometheus)        → Puerto 9090
└── 10. grafana     (Grafana)           → Puerto 3001

ORDEN DE INICIO:
db → redis → otel-collector → tempo → prometheus → importer → 
backend → frontend → adminer → grafana
```

---

## TECNOLOGÍAS PRINCIPALES

```
FRONTEND
├── Framework:      Next.js 16.0.0
├── Librería:       React 19.0.0
├── Lenguaje:       TypeScript 5.6
├── Estilos:        Tailwind CSS 3.4
├── Bundler:        Turbopack (Next.js 16)
├── Componentes:    Shadcn/ui
├── Estado:         Zustand
├── HTTP:           Axios
├── Testing:        Vitest + Playwright
└── Versión:        Próxima v5.4.1

BACKEND
├── Framework:      FastAPI 0.115.6
├── Lenguaje:       Python 3.11+
├── ORM:            SQLAlchemy 2.0.36
├── Validación:     Pydantic 2.10.5
├── Migraciones:    Alembic 1.17.0
├── Async:          asyncio
├── Testing:        pytest
├── OCR:            Azure Vision + EasyOCR + Tesseract
└── Versión:        5.4.1

DATABASE
├── Motor:          PostgreSQL 15
├── Versión:        15-alpine
└── Driver:         psycopg2

CACHE
├── Motor:          Redis 7
└── Política:       allkeys-lru

OBSERVABILITY
├── Tracing:        OpenTelemetry
├── Spans:          Grafana Tempo 2.5.0
├── Métricas:       Prometheus v2.52.0
├── Dashboards:     Grafana 11.2.0
└── Collector:      OTel Collector 0.103.0

DEVOPS
├── Containers:     Docker
├── Orquestación:   Docker Compose v3
├── VCS:            Git
└── CI/CD:          GitHub Actions (ready)
```

---

## TABLA DE PUERTOS

| Servicio | Puerto | Propósito | Acceso |
|---|---|---|---|
| Frontend | 3000 | Interfaz web | `http://localhost:3000` |
| Backend API | 8000 | REST API | `http://localhost:8000` |
| Swagger Docs | 8000 | API Docs | `http://localhost:8000/api/docs` |
| Database | 5432 | PostgreSQL | `localhost:5432` |
| Database UI | 8080 | Adminer | `http://localhost:8080` |
| Redis | 6379 | Cache | `localhost:6379` |
| Prometheus | 9090 | Métricas | `http://localhost:9090` |
| Tempo | 3200 | Traces | `http://localhost:3200` |
| Grafana | 3001 | Dashboards | `http://localhost:3001` |
| OTel Collector | 4317 | gRPC | `localhost:4317` |
| OTel Collector | 4318 | HTTP | `localhost:4318` |

---

## TABLA DE CONFIGURACIÓN

| Variable | Tipo | Obligatorio | Ejemplo |
|---|---|---|---|
| POSTGRES_PASSWORD | String | ✅ | `strong-password` |
| SECRET_KEY | String | ✅ | `a1b2c3d4...` (64 chars) |
| DATABASE_URL | URL | ✅ | `postgresql://...` |
| ENVIRONMENT | Enum | ❌ | `development` \| `production` |
| APP_VERSION | String | ❌ | `5.4.1` |
| FRONTEND_URL | URL | ❌ | `http://localhost:3000` |
| AZURE_COMPUTER_VISION_ENDPOINT | URL | ❌ | Azure endpoint |
| AZURE_COMPUTER_VISION_KEY | String | ❌ | Azure API key |
| SMTP_SERVER | String | ❌ | `smtp.gmail.com` |
| SMTP_USER | String | ❌ | `user@gmail.com` |
| SMTP_PASSWORD | String | ❌ | App password |
| LINE_CHANNEL_ACCESS_TOKEN | String | ❌ | LINE token |
| ENABLE_TELEMETRY | Boolean | ❌ | `true` |

---

## CHECKLIST DE DIRECTORIOS

```
✅ frontend/app/(dashboard)/           → 28 páginas
✅ frontend/components/                → 62 componentes
✅ frontend/lib/                       → 15+ librerías
✅ frontend/stores/                    → 9 stores
✅ frontend/hooks/                     → 10+ hooks
✅ backend/app/api/                    → 27 routers
✅ backend/app/services/               → 23+ servicios
✅ backend/app/schemas/                → 20 schemas
✅ backend/app/models/                 → 4 archivos
✅ backend/alembic/versions/           → 8 migraciones
✅ docker/                             → 3 Dockerfiles
✅ docker/observability/               → Stack observability
✅ scripts/                            → 50+ scripts
✅ config/                             → Config files
✅ docs/                               → 50+ documentos
✅ .claude/                            → 24+ agentes
✅ docker-compose.yml                  → Orquestación
✅ .env.example                        → Template env
✅ CLAUDE.md                           → Instrucciones
✅ README.md                           → Documentación
```

---

## COMANDOS RÁPIDOS

```bash
# INICIAR SERVICIOS
cd scripts && START.bat                    # Windows
docker compose up -d                       # Linux/Mac

# DETENER SERVICIOS
cd scripts && STOP.bat                     # Windows
docker compose down                        # Linux/Mac

# VER LOGS
cd scripts && LOGS.bat                     # Windows
docker compose logs -f                     # Linux/Mac

# BACKEND
docker exec -it uns-claudejp-backend bash
cd /app && alembic upgrade head            # Migraciones
pytest backend/tests/                      # Tests

# FRONTEND
docker exec -it uns-claudejp-frontend bash
npm run type-check                         # TypeScript
npm run build                              # Build

# DATABASE
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp
\dt                                        # Listar tablas
SELECT COUNT(*) FROM candidates;           # Contar candidatos

# BACKUP
cd scripts && BACKUP_DATOS.bat             # Windows
docker exec uns-claudejp-db pg_dump -U uns_admin uns_claudejp > backup.sql

# HEALTH CHECK
cd scripts && HEALTH_CHECK_FUN.bat         # Windows
curl http://localhost:8000/api/health      # Linux/Mac

# ADMINER
http://localhost:8080                      # Web UI

# GRAFANA
http://localhost:3001                      # admin/admin
```

---

## CHECKLIST PREDEPLOY

```
□ Verificar .env configurado correctamente
□ Ejecutar docker compose up -d
□ Verificar health checks de todos los servicios
□ Ejecutar migraciones: alembic upgrade head
□ Seed datos demo: python scripts/manage_db.py seed
□ Importar empleados desde Excel
□ Importar candidatos con OCR
□ Verificar login admin (admin/admin123)
□ Verificar páginas principales cargan
□ Testear endpoints principales con Swagger
□ Verificar dashboard muestra datos
□ Verificar reportes generan PDF
□ Testear OCR con documento
□ Verificar notificaciones (email/LINE)
□ Verificar observabilidad en Grafana
□ Ejecutar pruebas: pytest backend/tests/
□ Crear backup de base de datos
□ Documentar passwords y secrets seguros
□ Activar SSL/TLS para producción
```

---

**Documento generado:** 12 de Noviembre de 2025
**Última versión:** Completa
**Estado:** Listo para referencia rápida
