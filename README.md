# AASHIMA ERP – Business Management Application

> **Readiness notice (18 November 2026):** This repository is not production ready. Do not deploy it with real customer or financial data. See [PROJECT_STATUS.md](PROJECT_STATUS.md), [PROJECT_AUDIT.md](PROJECT_AUDIT.md), [SECURITY_AUDIT.md](SECURITY_AUDIT.md), and [TEST_REPORT.md](TEST_REPORT.md).

**Boutique Divisions**:
1. **AASHIMA Women's World** (Haute Couture Bridal Wear, Pure Silk Sarees, Heavy Lehengas, Organic Dry Cleaning & Zari Finishing)
2. **AASHIMA Stitchers 'N' Drapers** (Gentlemen Bespoke Tailoring, Bandhgalas, Sherwanis, Suits & Alterations)

**Flagship Atelier Location**: 581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India  
**Visual Source of Truth**: Google Stitch Regal Atelier ERP Design System  
**Software Ecosystem Version**: 2.4.0 (Enterprise Release)  

---

## 1. Architectural Monorepo Overview

The system is engineered as three independent client applications powered by one unified, high-performance central FastAPI backend:

```
AASHIMA-ERP/
│
├── apps/
│   ├── mobile/             # APPLICATION 1: Android POS App for Owner & Artisans
│   │   ├── src/            # Full Stitch screens (Dashboard, Booking, Matrix, QR Scanner)
│   │   └── index.html      # Responsive Android frame with camera scanner & thermal print
│   │
│   ├── admin-web/          # APPLICATION 2: Admin Web Dashboard
│   │   ├── src/            # Enterprise atelier portal (Daybook, Pipeline Kanban, Invoicing)
│   │   └── index.html      # Full-width desktop dashboard layout (1440px+)
│   │
│   └── customer-web/       # APPLICATION 3: Public Customer Live Tracking Website
│       ├── src/            # Live 5-stage tracking with pulsing node & OTP auth
│       └── index.html      # Luxury responsive atelier web portal
│
├── backend/                # CENTRAL BACKEND: Python FastAPI
│   ├── app/
│   │   ├── api/v1/         # 12 Modular REST API routers (Auth, Bookings, QR, Billing, etc.)
│   │   ├── core/           # Security (bcrypt), DB session, Business config, Settings
│   │   ├── models/         # 33 Normalized SQLAlchemy tables (PostgreSQL/SQLite)
│   │   ├── schemas/        # Pydantic v2 validation schemas
│   │   └── services/       # QR generator, Workflow engine, Billing/PDF, Reports, Seed
│   ├── migrations/         # Alembic database migrations
│   ├── tests/              # API tests (must use a disposable test database)
│   ├── alembic.ini         # Alembic configuration
│   └── requirements.txt    # Production dependencies
│
├── infrastructure/         # DEVOPS & INFRASTRUCTURE
│   ├── docker/             # Production Dockerfiles (Backend & Frontend Nginx)
│   ├── nginx/              # Nginx reverse proxy configuration & SSL routing
│   └── backups/            # Automated gzip database backup archives
│
├── docs/                   # COMPLETE TECHNICAL DOCUMENTATION
│   ├── architecture/       # High-level architecture, deployment & limitations
│   ├── database/           # 33-table ER diagram & Data dictionary
│   ├── diagrams/           # UML & Business process flowcharts (Mermaid)
│   ├── api/                # Complete API endpoint catalogue
│   ├── sop/                # SOP-001 through SOP-020 (Full Operational Manual)
│   └── user-manuals/       # Owner, Staff, Accountant, Delivery & Customer guides
│
├── scripts/                # Database backup & restore utilities
├── .env.example            # Configuration template
├── docker-compose.yml      # Orchestrated multi-container production stack
├── DESIGN_AUDIT.md         # Google Stitch design inspection & token audit
└── PROJECT_STATUS.md       # Complete verification status matrix
```

---

## 2. Core Functional Highlights

- **Visual Fidelity to Google Stitch**: Preserves all colors (Imperial Burgundy `#5B132B`, Rose Blush `#D9889E`, Regal Gold `#C59B4B`), Playfair Display and Plus Jakarta Sans typography, and component ergonomics.
- **Normalized Business Schema**: Database models use Decimal financial precision (`NUMERIC(12, 2)`) and Alembic versioning.
- **Multi-Garment Booking**: Every booking supports multiple articles, each with unique tags (`ASH-8842-G01`), individual services, rack assignments, and independent stage tracking.
- **Cryptographic QR Tracking**: Unpredictable HMAC-signed tokens with optical camera scanning and ESC/POS 58mm/80mm thermal claim slips.
- **Tailoring Measurement Matrix**: 10 key anchor measurements with 0.25" precision steppers and past fitting history baselines.
- **GST Invoicing & Ledger**: Itemized SAC 998822 (5% GST) and SAC 999712 (18% GST) calculations with automated signed A4 PDF downloads.
- **Customer Live Tracking**: 5-stage live status tracker with pulsing node, intake macro inspection photos, and read-only security isolation.
- **Standard Operating Procedures**: Comprehensive SOP-001 to SOP-020 covering daily shop floor operations, financial closing, and emergency recovery.

---

## 3. Quickstart & Local Development

### Prerequisites
- Python 3.10+ (with `pip`)
- Node.js 18+ / modern web browser
- PostgreSQL 16 (optional; SQLite active by default in local dev)

### 1. Initialize an isolated development database
```powershell
# In project root
$env:PYTHONPATH="."

# Apply the reviewed schema migrations first
py -m alembic -c backend/alembic.ini upgrade head

# Add foundational records (this no longer purges transactional data)
py -m backend.app.services.seed_data

# Launch FastAPI development server
py -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at:
- **Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **ReDoc**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

### 2. Run API tests only against a separate disposable database
```powershell
$env:PYTHONPATH="."
$env:ENVIRONMENT="test"
$env:AASHIMA_TESTING="1"
$env:DATABASE_URL="sqlite:///d:/ashiana/backend/tests/aashima_test.db"
$env:SECRET_KEY="test-only-random-secret-key-of-at-least-32-characters"
$env:DEFAULT_OTP_BYPASS="123456"
py -m pytest backend/tests/test_api_suite.py -v
```

The current API suite has not completed successfully in the audit environment. Do not infer a passing result from this quickstart.

### 3. Open Frontend Applications
Each frontend application is ready to serve:
- **Android Mobile POS**: [apps/mobile/index.html](apps/mobile/index.html) (Optimized 390dp mobile frame with camera QR scanner)
- **Admin Web Dashboard**: [apps/admin-web/index.html](apps/admin-web/index.html) (Full enterprise atelier portal)
- **Customer Website**: [apps/customer-web/index.html](apps/customer-web/index.html) (Live tracking & bill download)

---

## 4. Docker deployment preparation

Production deployment is blocked pending the P0/P1 actions in `PROJECT_STATUS.md`. The Compose configuration requires explicit secrets; Docker, TLS, production PostgreSQL, and recovery have not been validated.

To run the complete production ecosystem with Nginx, PostgreSQL, and FastAPI:
```bash
docker compose build
docker compose up -d
```
All routing is automatically managed:
- Customer Website: `http://localhost/`
- Admin Dashboard: `http://localhost/admin/`
- Android POS: `http://localhost/mobile/`
- Backend API: `http://localhost/api/v1/`
