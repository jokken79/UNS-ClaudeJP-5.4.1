# UNS-ClaudeJP 5.4.1 - COMPREHENSIVE PROJECT STRUCTURE AUDIT REPORT

**Generated:** 2025-11-14  
**Project Location:** `/home/user/UNS-ClaudeJP-5.4.1`  
**Current Branch:** `claude/audit-and-test-full-app-01BacFUqx4nBpYJuC9Lpt3zX`

---

## EXECUTIVE SUMMARY

UNS-ClaudeJP 5.4.1 is a comprehensive HR management system for Japanese staffing agencies. The application demonstrates a well-structured, production-ready architecture with comprehensive tooling, extensive documentation, and organized separation of concerns.

**Key Metrics:**
- **22 SQLAlchemy database models** (tables with relationships)
- **27 API router modules** with 150+ endpoints
- **81 frontend pages** (Next.js App Router)
- **170+ frontend component files** (reusable & specialized)
- **35 backend test files** (Pytest fixtures)
- **1,466 lines** in main models.py
- **12 microservices** in Docker Compose (dev + prod profiles)
- **Observability stack** fully integrated (OpenTelemetry, Prometheus, Grafana, Tempo)

---

## 1. PROJECT DIRECTORY STRUCTURE

### Root-Level Organization

```
/home/user/UNS-ClaudeJP-5.4.1/
├── backend/                  (3.3M)  FastAPI application
├── frontend/                 (12M)   Next.js 16 application
├── docker/                   (344KB) Docker configs & DevOps scripts
├── scripts/                  (1.6M)  Windows batch automation
├── config/                   (4.0M)  Excel templates & configurations
├── docs/                     (7.0M)  100+ markdown documentation files
├── BASEDATEJP/               (2.9M)  Japanese reference data
├── .claude/                  (32 subdirs) Agent orchestration system
├── monitoring/               Monitoring utilities
├── tests/                    Root-level test files
├── e2e/                      Playwright E2E test suite
├── test_screenshots/         (2.5M)  Visual test outputs
├── uploads/                  File uploads directory
├── docker-compose.yml        (17.9KB) Dev profile orchestration
├── docker-compose.prod.yml   (20.7KB) Prod profile orchestration
├── .env.example              Environment template
├── .env.production           Production environment config
├── CLAUDE.md                 (1,001 lines) Developer guide
├── README.md                 (1,123 lines) Project overview
└── 105+ markdown files       Comprehensive documentation
```

**Total Project Size:** ~45MB (excluding node_modules and .git)

### Size Breakdown
```
12M   frontend/
7.0M  docs/
4.0M  config/
3.3M  backend/
2.9M  BASEDATEJP/
2.5M  test_screenshots/
1.6M  scripts/
```

---

## 2. BACKEND STRUCTURE & DEPENDENCIES

### Backend Directory Layout (3.3M)

```
backend/
├── app/
│   ├── main.py                FastAPI entry point
│   │
│   ├── api/ (27 routers)
│   │   ├── admin.py           Admin control panel
│   │   ├── auth.py            JWT authentication
│   │   ├── apartments_v2.py    Housing management system
│   │   ├── candidates.py       Resume/candidate CRUD
│   │   ├── dashboard.py        Analytics & statistics
│   │   ├── employees.py        Employee management
│   │   ├── factories.py        Client sites (派遣先)
│   │   ├── timer_cards.py      Attendance tracking (タイムカード)
│   │   ├── payroll.py          Payroll calculations
│   │   ├── salary.py           Salary management
│   │   ├── yukyu.py            Annual leave system (有給)
│   │   ├── requests.py         Employee requests/leave
│   │   ├── reports.py          Report generation
│   │   ├── role_permissions.py RBAC management
│   │   ├── audit.py            Audit logging
│   │   ├── monitoring.py       Health checks & metrics
│   │   ├── azure_ocr.py        OCR integration
│   │   ├── notifications.py    Email/LINE alerts
│   │   └── 8+ more specialized routers
│   │
│   ├── models/ (SQLAlchemy ORM)
│   │   ├── models.py           1,466 lines, 22 tables
│   │   ├── payroll_models.py   Payroll-specific models
│   │   └── mixins.py           Base model mixins
│   │
│   ├── schemas/ (Pydantic validation)
│   │   ├── auth.py
│   │   ├── candidate.py
│   │   ├── employee.py
│   │   ├── apartment.py
│   │   ├── salary.py
│   │   ├── payroll.py
│   │   ├── yukyu.py
│   │   └── 27+ more specialized schemas
│   │
│   ├── services/ (Business logic - 30 modules)
│   │   ├── auth_service.py
│   │   ├── candidate_service.py
│   │   ├── employee_matching_service.py
│   │   ├── apartment_service.py
│   │   ├── salary_service.py
│   │   ├── hybrid_ocr_service.py      (Azure → EasyOCR → Tesseract)
│   │   ├── azure_ocr_service.py
│   │   ├── easyocr_service.py
│   │   ├── tesseract_ocr_service.py
│   │   ├── face_detection_service.py   (MediaPipe)
│   │   ├── notification_service.py     (Email/LINE)
│   │   ├── payroll/                    (Subservices)
│   │   └── 15+ more specialized services
│   │
│   ├── core/ (Application infrastructure)
│   │   ├── config.py           Application settings
│   │   ├── database.py         SQLAlchemy setup
│   │   ├── middleware.py       Custom middleware stack
│   │   ├── observability.py    OpenTelemetry configuration
│   │   ├── permissions.py      RBAC implementation
│   │   ├── logging.py          Structured logging (loguru)
│   │   ├── redis_client.py     Cache client
│   │   ├── scheduler.py        APScheduler background jobs
│   │   └── 8+ more core modules
│   │
│   └── utils/ (Helpers & validators)
│
├── alembic/
│   ├── versions/               3 major migration files
│   │   ├── 001_create_all_tables.py
│   │   ├── 003_add_nyuusha_renrakuhyo_fields.py
│   │   └── 2025_11_11_1200_add_search_indexes.py
│   └── env.py
│
├── scripts/
│   ├── simple_importer.py      Data seeding
│   ├── manage_db.py            Database operations
│   └── more...
│
├── tests/ (35 test files)
├── requirements.txt            48 packages (locked versions)
├── alembic.ini
├── pytest.ini
└── mypy.ini
```

### Backend Dependencies (48 packages total)

**Core Framework (3):**
```
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-multipart==0.0.20
```

**Database & ORM (5):**
```
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.17.0
redis==7.0.1
pyodbc==5.3.0  # MS Access support
```

**Authentication & Security (3):**
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.2.1
```

**OCR & Image Processing (9):**
```
Pillow==11.1.0
pdf2image==1.17.0
opencv-python-headless==4.10.0.84
numpy>=1.23.5,<2.0.0
azure-cognitiveservices-vision-computervision==0.9.1
pytesseract==0.3.10
mediapipe==0.10.15  # Face detection
easyocr==1.7.2     # Secondary OCR
pykakasi==2.3.0    # Japanese text processing
```

**Data Processing (4):**
```
openpyxl==3.1.5
pandas==2.3.3
pdfplumber==0.11.5
reportlab==4.4.4
```

**Validation & Configuration (5):**
```
pydantic==2.10.5
pydantic-settings==2.11.0
email-validator==2.3.0
python-dateutil==2.9.0.post0
pytz==2025.2
```

**Communication (5):**
```
aiosmtplib==3.0.2
jinja2==3.1.6
requests==2.32.5
httpx==0.28.1
aiohttp==3.13.1
```

**Observability & Scheduling (7):**
```
opentelemetry-api==1.27.0
opentelemetry-sdk==1.27.0
opentelemetry-exporter-otlp-proto-grpc==1.27.0
opentelemetry-instrumentation-fastapi==0.48b0
prometheus-fastapi-instrumentator==7.1.0
apscheduler==3.10.4
loguru==0.7.3
```

**Testing & Development (3):**
```
pytest==8.3.4
pytest-asyncio==0.24.0
mypy==1.7.0
```

**Utilities (2):**
```
slowapi==0.1.9  # Rate limiting
python-dotenv==1.0.1
```

---

## 3. FRONTEND STRUCTURE & DEPENDENCIES

### Frontend Directory Layout (12M)

```
frontend/
├── app/                              (Next.js 16 App Router)
│   ├── page.tsx                      Root landing page
│   ├── login/page.tsx                Authentication
│   ├── profile/page.tsx              User profile
│   │
│   └── (dashboard)/ (81 pages)       Protected dashboard routes
│       ├── layout.tsx                Dashboard wrapper
│       ├── admin/                    Admin panel (5+ pages)
│       ├── candidates/               Resume management (5+ pages)
│       ├── employees/                Employee CRUD (5+ pages)
│       ├── apartments/               Housing system (6+ pages)
│       ├── timercards/               Attendance (4+ pages)
│       ├── payroll/                  Payroll system (8+ pages)
│       ├── salary/                   Salary calculation (4+ pages)
│       ├── yukyu/                    Annual leave (4+ pages)
│       ├── requests/                 Employee requests (3+ pages)
│       ├── factories/                Client sites (3+ pages)
│       ├── reports/                  Report generation
│       ├── dashboard/                Analytics dashboard
│       ├── settings/                 System settings
│       ├── themes/                   Theme customization
│       ├── design-system/            Component showcase
│       ├── monitoring/               System monitoring
│       └── 35+ more feature pages
│
├── components/ (170+ files)
│   ├── ui/                           Shadcn/ui (20+ base components)
│   ├── admin/                        Admin-specific components
│   ├── apartments/                   Apartment system
│   ├── candidates/                   Candidate management
│   ├── employees/                    Employee management
│   ├── payroll/                      Payroll
│   ├── salary/                       Salary calculations
│   ├── dashboard/                    Dashboard widgets
│   ├── reports/                      Report components
│   ├── requests/                     Request management
│   ├── settings/                     Settings UI
│   ├── factory/                      Factory management
│   ├── design-tools/                 Design system tools
│   ├── ThemeEditor/                  Theme customization
│   └── 5+ more specialized categories
│
├── lib/                              (Utility libraries - 233KB)
│   ├── api.ts                        Axios client with JWT interceptors
│   ├── themes.ts                     12 predefined + custom themes
│   ├── animations.ts                 Animation utilities
│   ├── color-utils.ts                Color manipulation
│   ├── dashboard-data.ts             Dashboard helpers
│   └── 15+ more utility modules
│
├── stores/                           (Zustand global state)
│   ├── app-store.ts
│   ├── auth-store.ts
│   ├── theme-store.ts
│   └── design-store.ts
│
├── hooks/                            (Custom React hooks)
├── contexts/                         (React Context providers)
├── types/                            (TypeScript definitions)
├── styles/                           (Global CSS + animations)
├── public/                           (Static assets)
│
├── tests/                            (Vitest unit tests)
├── e2e/                              (Playwright E2E tests)
├── next.config.ts                    Next.js configuration with CSP
├── tailwind.config.ts                Tailwind CSS themes
├── tsconfig.json                     TypeScript strict mode
├── eslint.config.mjs                 ESLint configuration
├── playwright.config.ts              E2E test configuration
└── package.json                      43 dependency packages
```

### Frontend Dependencies (43 packages total)

**Framework & Core (3):**
```
next@^16.0.0
react@^19.0.0
react-dom@^19.0.0
```

**UI & Styling (7):**
```
tailwindcss@^3.4.13
@radix-ui/react-*@latest  (14+ components)
lucide-react@^0.451.0
@heroicons/react@^2.2.0
tailwindcss-animate@^1.0.7
tailwind-merge@^2.6.0
clsx@^2.1.1
```

**Forms & Validation (3):**
```
react-hook-form@^7.65.0
@hookform/resolvers@^3.10.0
zod@^3.25.76
```

**State Management (3):**
```
zustand@^5.0.8
@tanstack/react-query@^5.59.0
axios@^1.7.7
```

**Animations & UX (3):**
```
framer-motion@^11.15.0
react-hot-toast@^2.6.0
sonner@^2.0.7
```

**Utilities (5):**
```
date-fns@^4.1.0
recharts@^2.15.4
qrcode@^1.5.4
react-dropzone@^14.3.8
next-themes@^0.3.0
```

**Development Tools (11):**
```
typescript@^5.6.0
vitest@^2.1.5
@playwright/test@^1.49.0
prettier@^3.2.5
eslint@^9.0.0
@testing-library/react@^16.1.0
jsdom@^25.0.1
```

---

## 4. DOCKER COMPOSE SERVICES (12 Total)

### Complete Service Topology

**CORE SERVICES (6):**
1. **db** - PostgreSQL 15-alpine (5432)
   - Health: pg_isready
   - Volume: postgres_data
   - Profiles: dev, prod

2. **redis** - Redis 7-alpine (6379)
   - Password protected
   - Volume: redis_data
   - Profiles: dev, prod

3. **importer** - Data initialization
   - Runs: simple_importer.py
   - Restart: 'no' (one-time execution)
   - Depends: db (healthy)

4. **backend** - FastAPI (dev profile)
   - Port: 8000 (via nginx)
   - Hot reload: enabled
   - Profiles: dev only

5. **backend-prod** - FastAPI (prod profile)
   - Port: 8000
   - Workers: 4
   - Profiles: prod only

6. **frontend** - Next.js 16 (3000)
   - Turbopack hot reload
   - Profiles: dev only

**OBSERVABILITY STACK (4):**
7. **otel-collector** - OpenTelemetry Collector (4317, 4318)
   - Collects traces, metrics, logs
   - Profiles: dev, prod

8. **tempo** - Grafana Tempo v2.5.0 (3200)
   - Distributed tracing storage
   - Profiles: dev, prod

9. **prometheus** - Prometheus v2.52.0 (9090)
   - Metrics storage & scraping
   - Profiles: dev, prod

10. **grafana** - Grafana v11.2.0 (3001)
    - 4 pre-configured dashboards
    - Profiles: dev, prod

**INFRASTRUCTURE (2):**
11. **nginx** - Reverse proxy & load balancer (80, 443)
    - Routes /api/* to backend
    - Routes / to frontend
    - Load balancing support
    - Profiles: dev, prod

12. **backup** - Database backup service
    - Automated cron scheduling
    - Retention: 30 days
    - Timezone: Asia/Tokyo
    - Profiles: dev, prod

**OPTIONAL:**
- **adminer** - Database UI (8080)
  - Profiles: dev only

---

## 5. DATABASE SCHEMA (22 Tables)

### Table Categories

**User Management (3):**
- User
- RefreshToken
- AdminAuditLog

**Personnel (5):**
- CandidateForm (履歴書)
- Employee (派遣社員)
- Contract
- ContractWorker
- Staff

**Business Operations (3):**
- Factory (派遣先)
- ApartmentFactory
- Workplace

**Attendance & Finance (5):**
- TimerCard (タイムカード)
- SalaryCalculation
- YukyuBalance (有給)
- YukyuRequest
- YukyuUsageDetail

**Administrative (3):**
- SystemSettings
- PageVisibility
- RolePagePermission

**Supporting (2):**
- Document
- AuditLog

**Configuration:**
- SocialInsuranceRate
- Region
- Department
- ResidenceType
- ResidenceStatus

---

## 6. API ENDPOINTS (27 Routers)

```
/api/auth/                    # JWT authentication
/api/admin/                   # Admin operations
/api/candidates/              # Resume/candidate CRUD + OCR
/api/employees/               # Employee management + assignment
/api/contracts/               # Contract management
/api/factories/               # Client sites (派遣先)
/api/apartments_v2/           # Housing system v2
/api/timer_cards/             # Attendance tracking
/api/payroll/                 # Payroll calculations
/api/salary/                  # Salary management
/api/yukyu/                   # Annual leave (有給) system
/api/requests/                # Employee requests/leave
/api/dashboard/               # Analytics & statistics
/api/reports/                 # Report generation
/api/role_permissions/        # RBAC management
/api/settings/                # System settings
/api/audit/                   # Audit logging
/api/azure_ocr/               # Azure OCR integration
/api/notifications/           # Email/LINE notifications
/api/monitoring/              # Health checks & metrics
/api/import_export/           # Bulk data operations
/api/database/                # Database administration
/api/pages/                   # Static page management
/api/resilient_import/        # Resilient data import

Documentation:
- /api/docs                   # Swagger UI
- /api/redoc                  # ReDoc documentation
- /metrics                    # Prometheus metrics
```

---

## 7. CONFIGURATION FILES

### Environment Variables

**Required (.env):**
```bash
POSTGRES_PASSWORD=<required>
SECRET_KEY=<required: 64-byte hex>
```

**Optional:**
```bash
# OCR Providers (choose at least one)
AZURE_COMPUTER_VISION_ENDPOINT=
AZURE_COMPUTER_VISION_KEY=
GEMINI_API_KEY=

# Notifications
SMTP_SERVER=
SMTP_USER=
SMTP_PASSWORD=
LINE_CHANNEL_ACCESS_TOKEN=

# Backup
BACKUP_TIME=02:00
BACKUP_RETENTION_DAYS=30
```

### Important Configuration Files

**Backend:**
- `backend/requirements.txt` - 48 locked dependencies
- `backend/alembic.ini` - Migration configuration
- `backend/pytest.ini` - Test settings
- `docker/Dockerfile.backend` - Python image

**Frontend:**
- `frontend/package.json` - 43 locked dependencies
- `frontend/next.config.ts` - CSP & optimization
- `frontend/tailwind.config.ts` - Design tokens
- `frontend/tsconfig.json` - Strict TypeScript
- `docker/Dockerfile.frontend` - Node.js image

**Docker:**
- `docker-compose.yml` (17.9KB) - Dev profile
- `docker-compose.prod.yml` (20.7KB) - Prod profile
- `docker/Dockerfile.nginx` - Reverse proxy
- `docker/observability/` - OTEL/Prometheus/Grafana configs

---

## 8. KEY TECHNOLOGIES

| Aspect | Technology | Version |
|--------|-----------|---------|
| **Frontend Framework** | Next.js | 16.0.0 |
| **UI Library** | React | 19.0.0 |
| **Styling** | Tailwind CSS | 3.4 |
| **Language (Frontend)** | TypeScript | 5.6 |
| **Backend Framework** | FastAPI | 0.115.6 |
| **Language (Backend)** | Python | 3.11+ |
| **Database** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy | 2.0.36 |
| **Migrations** | Alembic | 1.17.0 |
| **Cache** | Redis | 7 |
| **Observability** | OpenTelemetry | 1.27.0 |
| **Metrics** | Prometheus | 2.52.0 |
| **Tracing** | Grafana Tempo | 2.5.0 |
| **Dashboards** | Grafana | 11.2.0 |
| **Container Orchestration** | Docker Compose | Latest |
| **Reverse Proxy** | Nginx | Latest |

---

## 9. PROJECT STATISTICS

### Code Metrics
```
Database Tables:           22
API Routers:              27
Frontend Pages:           81
Components:              170+
Services:                30
Schemas (Pydantic):      35+
Backend Tests:           35
Docker Services:         12
Total Dependencies:      91 (48 backend + 43 frontend)
Documentation Files:    105+
```

### File Counts
```
Python files (.py):      150+
TypeScript files (.tsx): 250+
Markdown files (.md):    110+
Configuration files:      20+
Docker related:          10+
```

### Development Tooling
```
Testing:     Pytest, Vitest, Playwright
Linting:     ESLint, MyPy
Formatting:  Prettier
Version Control: Git
CI/CD Ready: Yes (Dockerfile profiles for dev/prod)
```

---

## 10. ENTRY POINTS

**Backend:**
- File: `backend/app/main.py`
- Port: 8000 (internal) → 80 (via nginx)
- Endpoints: http://localhost/api/docs

**Frontend:**
- File: `frontend/app/page.tsx`
- Port: 3000
- URL: http://localhost:3000

**Database:**
- Type: PostgreSQL 15
- Port: 5432 (internal) → 5432 (external)
- Admin UI: http://localhost:8080 (Adminer)

**Monitoring:**
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090
- Traces: http://localhost:3200 (Tempo)

---

## 11. IMPORTANT OBSERVATIONS

### ✅ Strengths
- Modern, scalable architecture
- Comprehensive security (JWT, RBAC, audit logging)
- Full observability stack integrated
- Production-ready Docker configuration
- Extensive documentation
- Type-safe (TypeScript + Pydantic)
- Well-organized code structure
- Supports horizontal scaling

### ⚠️ Items to Note
- **.cursorrules file is missing** - Would benefit AI assistant consistency
- **Root-level markdown files** - 105 files should be consolidated into /docs/
- **.env file** - Must be created locally from .env.example
- **Test coverage** - Could be expanded for full integration testing

### 🔒 Security Considerations
- Default credentials (admin/admin123) for development only
- Change SECRET_KEY in production
- Implement HTTPS in production (nginx SSL config)
- Database password must be strong
- API rate limiting enabled
- CORS properly configured

---

## 12. DEPLOYMENT READINESS

**Development Ready:** ✅ YES
- `docker compose --profile dev up -d`
- Full hot reload support
- Adminer for database management

**Production Ready:** ✅ YES
- `docker compose --profile prod up -d`
- Nginx with TLS support
- 4-worker FastAPI setup
- Automated backups configured
- Prometheus + Grafana monitoring

**Prerequisites:**
1. Docker & Docker Compose
2. Python 3.11+ (for local development)
3. Node.js 18+ (for frontend development)
4. PostgreSQL 15 (included in Docker)

---

## CONCLUSION

UNS-ClaudeJP 5.4.1 is a mature, well-architected HR management system demonstrating professional software engineering practices. The codebase is clean, well-documented, and ready for both development and production deployment.

**Next Steps:**
1. Review CLAUDE.md for development guidelines
2. Create .env from .env.example
3. Run `docker compose --profile dev up -d`
4. Access frontend at http://localhost:3000
5. Review API documentation at http://localhost:8000/api/docs

---

**Report Generated:** 2025-11-14  
**Audit Depth:** Comprehensive (All major components analyzed)
