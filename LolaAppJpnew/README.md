# LolaAppJp - HR Management System

> 🚀 **Complete HR management system for Japanese staffing agencies (人材派遣会社)**

LolaAppJp is a comprehensive HR management platform designed specifically for Japanese temporary staffing agencies. It manages the complete lifecycle of dispatch workers from candidate screening to payroll processing.

## ✨ Features

### 📋 Core Modules

1. **Candidates Management (候補者管理)**
   - Rirekisho (履歴書) data entry with OCR
   - Photo extraction from documents
   - Zairyu card (在留カード) processing
   - Application status tracking

2. **入社連絡票 Workflow (New Hire Notification)**
   - 4-step approval process
   - Candidate → Employee conversion
   - Factory assignment
   - Apartment assignment

3. **Employee Management (従業員管理)**
   - Complete employee profiles
   - Factory/line assignments
   - Contract management
   - Re-hire workflow

4. **Factory Management (工場管理)**
   - Normalized database structure (Companies → Plants → Lines)
   - Cascading dropdowns
   - Work schedule configuration
   - Overtime rules per factory

5. **Apartments Management (寮管理)**
   - Intelligent auto-assignment with weighted scoring
     - 40% proximity to factory
     - 25% availability
     - 15% price affordability
     - 10% roommate compatibility
     - 10% transportation
   - Capacity tracking
   - Prorated rent calculations
   - Smart features (transfer suggestions, contract alerts)

6. **Yukyu System (有給休暇)**
   - LIFO deduction strategy
   - Fiscal year tracking
   - Automatic grant calculation
   - Expiration management

7. **Timer Cards (タイムカード)**
   - OCR processing from PDF uploads
   - Fuzzy matching for employee identification
   - Factory-specific rule application (work hours, breaks, overtime, time rounding)
   - Manual review workflow

8. **Payroll (給与計算)**
   - Automatic calculation from timer cards
   - Social insurance deductions
   - Apartment rent deductions
   - PDF payslip generation

### 🔐 Role-Based Access Control

Hierarchy: **ADMIN** > **TORISHIMARIYAKU** > **KEIRI** > **TANTOSHA** > **HAKEN_SHAIN** > **UKEOI**

- **ADMIN**: Full system access (super admin)
- **TORISHIMARIYAKU**: Director/Boss (取締役)
- **KEIRI**: Accounting/Administration (経理)
- **TANTOSHA**: Supervisor/Manager (担当者)
- **HAKEN_SHAIN**: Dispatch employee (派遣社員)
- **UKEOI**: Contract worker (請負)

## 🏗️ Architecture

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Next.js | 16.0.0 |
| **UI Framework** | React | 19.0.0 |
| **Type Safety** | TypeScript | 5.6 |
| **Styling** | Tailwind CSS | 3.4 |
| **Backend** | FastAPI | 0.115.6 |
| **Language** | Python | 3.11+ |
| **ORM** | SQLAlchemy | 2.0.36 |
| **Database** | PostgreSQL | 15 |
| **Cache** | Redis | 7 |
| **Reverse Proxy** | Nginx | Latest |
| **Observability** | OpenTelemetry + Prometheus + Grafana | Latest |

### Database Schema (13 Tables)

**Core Tables:**
- `users` - System users with roles
- `candidates` - Job candidates (履歴書)
- `employees` - Active employees
- `companies` - Client companies
- `plants` - Factory locations
- `lines` - Production lines
- `apartments` - Employee housing
- `apartment_assignments` - Housing history
- `yukyu_balances` - Paid vacation balances
- `yukyu_transactions` - Yukyu LIFO transactions
- `timer_cards` - Daily attendance
- `requests` - Workflow approvals (入社連絡票, 有休申請, etc.)
- `payroll_records` - Monthly payroll

### Docker Services (12)

1. **db** - PostgreSQL 15 database
2. **redis** - Redis cache
3. **backend** - FastAPI application (horizontally scalable)
4. **frontend** - Next.js application
5. **nginx** - Reverse proxy with load balancing
6. **adminer** - Database management UI
7. **otel-collector** - OpenTelemetry collector
8. **tempo** - Distributed tracing
9. **prometheus** - Metrics storage
10. **grafana** - Observability dashboards
11. **backup** - Automated database backups
12. **importer** - One-time data initialization

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** with Docker Desktop installed
- **Docker Desktop** running
- **8GB RAM** minimum
- **Ports available**: 80, 443, 3000, 5432, 6379, 8000, 8080, 3001, 9090

### Installation (Windows)

1. **Clone or extract the project**
   ```bash
   cd LolaAppJpnew
   ```

2. **Create `.env` file**
   ```bash
   copy .env.example .env
   ```

   Edit `.env` and update:
   - `DATABASE_PASSWORD` - Change from default
   - `SECRET_KEY` - Generate with: `openssl rand -hex 32`
   - `GRAFANA_ADMIN_PASSWORD` - Set admin password
   - `AZURE_CV_ENDPOINT` & `AZURE_CV_KEY` - (Optional) For OCR

3. **Start all services**
   ```bash
   cd scripts
   START.bat
   ```

4. **Wait for services to be ready** (~2-3 minutes first time)

5. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost/api
   - **API Docs**: http://localhost:8000/api/docs
   - **Database UI**: http://localhost:8080
   - **Grafana**: http://localhost:3001
   - **Prometheus**: http://localhost:9090

6. **Default Login**
   - Username: `admin`
   - Password: `admin123`

   **⚠️ IMPORTANT**: Change this password immediately after first login!

### Management Scripts

```bash
# Start all services
scripts\START.bat

# Stop all services
scripts\STOP.bat

# View logs (interactive menu)
scripts\LOGS.bat
```

## 📁 Project Structure

```
LolaAppJpnew/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/                # API routers
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   ├── core/               # Security, config, deps
│   │   └── main.py             # FastAPI app
│   ├── alembic/                # Database migrations
│   ├── scripts/                # Data management
│   └── Dockerfile
│
├── frontend/                   # Next.js 16 frontend
│   ├── app/                    # App Router pages
│   ├── components/             # React components
│   ├── lib/                    # Utilities
│   ├── stores/                 # Zustand stores
│   └── Dockerfile
│
├── docker/                     # Docker configurations
│   ├── nginx/                  # Nginx config
│   ├── postgres/               # DB init scripts
│   ├── grafana/                # Dashboards
│   ├── prometheus/             # Metrics config
│   └── backup/                 # Backup scripts
│
├── scripts/                    # Windows batch scripts
│   ├── START.bat               # Start services
│   ├── STOP.bat                # Stop services
│   └── LOGS.bat                # View logs
│
├── docker-compose.yml          # Service orchestration
├── .env.example                # Environment template
└── README.md                   # This file
```

## 🛠️ Development

### Backend Development

```bash
# Access backend container
docker exec -it lolaappjp-backend bash

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest backend/tests/ -v
```

### Frontend Development

```bash
# Access frontend container
docker exec -it lolaappjp-frontend sh

# Install dependencies
npm install

# Type check
npm run type-check

# Lint
npm run lint
```

### Database Access

```bash
# Via Adminer
Open http://localhost:8080
Server: db
Username: lola_admin
Password: (from .env)
Database: lolaappjp

# Via psql
docker exec -it lolaappjp-db psql -U lola_admin -d lolaappjp

# Useful commands
\dt                              # List tables
\d candidates                    # Describe table
SELECT COUNT(*) FROM employees;  # Query
```

## 🔍 Key Features Explained

### 入社連絡票 (Nyusha Renraku Hyo) Workflow

1. **Draft Creation** - HR creates new hire form linking to candidate
2. **Data Entry** - Input factory, wage, hire date, apartment
3. **Approval** - Manager approves
4. **Employee Creation** - System auto-creates employee record

**Important**: Candidates NEVER get deleted. If employee resigns and returns, same candidate creates new employee record.

### Intelligent Apartment Assignment

Scoring algorithm automatically suggests best apartments:
- **Proximity to factory** (40 points) - Distance calculation
- **Availability** (25 points) - Current occupancy vs capacity
- **Price affordability** (15 points) - Rent vs employee wage
- **Roommate compatibility** (10 points) - Gender, nationality, age
- **Transportation** (10 points) - Public transport access

### Timer Cards OCR Processing

1. **Upload PDF** - Monthly attendance sheet
2. **OCR Extraction** - Azure CV → EasyOCR → Tesseract (fallback)
3. **Employee Matching** - Fuzzy matching by name (>80% confidence)
4. **Rule Application** - Apply factory-specific work rules
5. **Manual Review** - Review low-confidence matches
6. **Approval** - Finalize for payroll

### Payroll Calculation

```
Gross Pay =
  (Regular Hours × Hourly Rate) +
  (Overtime Hours × Hourly Rate × 1.25) +
  (Night Hours × Hourly Rate × 1.25) +
  (Holiday Hours × Hourly Rate × 1.35) +
  (Yukyu Days × Daily Equivalent)

Deductions =
  Social Insurance +
  Health Insurance +
  Pension Insurance +
  Employment Insurance +
  Income Tax +
  Apartment Rent (if assigned)

Net Pay = Gross Pay - Deductions
```

## 📊 Observability

### Grafana Dashboards

Access Grafana at http://localhost:3001 (admin/admin)

**Pre-configured dashboards:**
- Backend API Performance
- Database Metrics
- Request Tracing
- Error Rates
- Resource Usage

### Prometheus Metrics

Access Prometheus at http://localhost:9090

**Available metrics:**
- HTTP request duration
- Database connection pool
- Cache hit rates
- OCR processing time
- Error counts by endpoint

### Distributed Tracing

Tempo integration provides end-to-end request tracing:
- Frontend → Nginx → Backend → Database
- OCR processing traces
- Slow query identification

## 🔒 Security

### Production Checklist

- [ ] Change `DATABASE_PASSWORD` in `.env`
- [ ] Generate new `SECRET_KEY` with `openssl rand -hex 32`
- [ ] Change `GRAFANA_ADMIN_PASSWORD`
- [ ] Change default user password (admin/admin123)
- [ ] Configure HTTPS with SSL certificates
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Configure email notifications
- [ ] Review CORS origins in `.env`

### Backup & Restore

**Automated Backups:**
- Daily backups at 02:00 JST (configurable in `.env`)
- 30-day retention (configurable)
- Stored in `./backups/` directory

**Manual Backup:**
```bash
docker exec lolaappjp-db pg_dump -U lola_admin lolaappjp > backup_$(date +%Y%m%d).sql
```

**Restore:**
```bash
cat backup_20251108.sql | docker exec -i lolaappjp-db psql -U lola_admin lolaappjp
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker info

# Check port availability
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# View logs
scripts\LOGS.bat
```

### Database connection error

```bash
# Verify database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Run migrations manually
docker exec lolaappjp-backend alembic upgrade head
```

### Frontend blank page

```bash
# Wait 1-2 minutes for compilation
# Check frontend logs
docker-compose logs -f frontend

# Rebuild frontend
docker-compose build frontend
docker-compose restart frontend
```

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs (Swagger)
- **Database Schema**: See `backend/app/models/models.py`
- **Architecture Diagrams**: See `docs/architecture/`
- **Development Guide**: See `docs/guides/development.md`

## 🤝 Contributing

This project is designed for Japanese staffing agencies. For customization or support, contact the development team.

## 📄 License

Proprietary - All rights reserved

## 🌏 Timezone

All timestamps are in **Asia/Tokyo (JST)** timezone.

## 📞 Support

For issues, questions, or feature requests, please consult the documentation or contact your system administrator.

---

**Made with ❤️ for Japanese HR professionals**
