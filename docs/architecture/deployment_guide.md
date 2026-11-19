# AASHIMA ERP – Deployment Guide (Production Gate Open)

**Target Environment**: Linux Ubuntu 22.04 LTS / Debian 12 / Docker Engine  
**Domain Structure**:
- Customer Portal: `https://aashima.in`
- Admin Web Portal: `https://admin.aashima.in`
- Mobile POS Web App: `https://pos.aashima.in`
- Backend API: `https://api.aashima.in/api/v1`

---

## 1. Server Prerequisites
- Minimum 2 vCPU, 4GB RAM, 40GB SSD
- Docker Engine 24.0+ & Docker Compose v2.20+
- Valid domain DNS records pointing to host IP
- SSL certificates (Let's Encrypt Certbot)

---

## 2. Production deployment is currently blocked

Do not deploy the current application with real customer or financial data. The audit found unresolved OTP operations, financial integrity, dependency, backup/recovery, and deployment verification issues. Role policies and customer tracking controls were added, but broader authorization testing remains. See `PROJECT_STATUS.md` and `SECURITY_AUDIT.md`.

The following is a preparation checklist only. It is not a validated production runbook until the blockers are resolved and a clean PostgreSQL deployment plus recovery drill succeeds.

## 3. Preparation checklist

### Step 1: Clone Workspace & Configure Environment
```bash
git clone https://github.com/aashima-atelier/aashima-erp.git /opt/aashima-erp
cd /opt/aashima-erp
cp .env.example .env
nano .env
```
Set `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SECRET_KEY` (unique random value, 32+ characters), `PUBLIC_BASE_URL` (HTTPS domain), `ENVIRONMENT=production`, the selected SMS provider and its credentials, and exact `BACKEND_CORS_ORIGINS`. Set `BOOTSTRAP_OWNER_PASSWORD` (12+ characters) for the first owner seed; remove it from the environment after the owner is created and rotate the account through the approved account process. Do not use the example values as credentials. Keep `.env` out of source control and restrict file access.

### Step 2: Build images only after P0/P1 findings are closed
```bash
docker compose config
docker compose build --no-cache
```

### Step 3: Run migrations against a reviewed target database
```bash
docker compose run --rm backend python -m alembic -c backend/alembic.ini upgrade head
docker compose run --rm backend python -m backend.app.services.seed_data
```

### Step 4: Verify readiness, security, and recovery before routing customer traffic
```bash
curl http://127.0.0.1:8080/ready
```
Expected readiness response after the database is available:
```json
{
  "status": "ready"
}
```

---

## 4. Backups

The backup scripts now use consistent SQLite snapshots, checksums, argument-array PostgreSQL commands, and new-target-only restore behavior. They are not production-approved until PostgreSQL restore, encrypted off-host storage, retention, and a full recovery drill are verified. Follow [backup_recovery_guide.md](backup_recovery_guide.md).

---

## 5. HTTPS, logging, and infrastructure requirements

- Compose binds the HTTP frontend to `127.0.0.1:8080`; place it behind a separately managed TLS terminator with HTTP-to-HTTPS redirect and HSTS. Nginx adds basic content-type, referrer, frame, and permissions headers; CSP and external TLS are not supplied or verified by this repository.
- Keep PostgreSQL and backend ports private; expose only the TLS entry point.
- Configure structured redacted logs, alerting, readiness checks, disk monitoring, and access review.
- Complete a restore drill and record the recovery point and recovery time before launch.

## 6. Hardware verification
- Pair the ESC/POS printer via Bluetooth or USB:
  - Default baud rate: 9600 / 115200
  - Default width: 80mm (48 characters per line) or 58mm (32 characters per line)
- Print test ticket from the Admin Dashboard **Thermal Print Centre** to verify character alignment and barcode legibility.
