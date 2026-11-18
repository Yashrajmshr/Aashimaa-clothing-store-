# AASHIMA ERP – Production Deployment & DevOps Guide

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

## 2. Step-by-Step Deployment Procedure

### Step 1: Clone Workspace & Configure Environment
```bash
git clone https://github.com/aashima-atelier/aashima-erp.git /opt/aashima-erp
cd /opt/aashima-erp
cp .env.example .env
nano .env
```
Ensure `POSTGRES_PASSWORD`, `SECRET_KEY`, and production domain names are set.

### Step 2: Build & Launch Docker Services
```bash
docker compose build --no-cache
docker compose up -d
```

### Step 3: Run Database Migrations & Seed Default Services
```bash
docker compose exec backend py -m alembic -c backend/alembic.ini upgrade head
docker compose exec backend py -m backend.app.services.seed_data
```

### Step 4: Verify Service Health
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{
  "status": "healthy",
  "business": "AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers",
  "location": "581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India",
  "version": "2.4.0",
  "environment": "production"
}
```

---

## 3. Automated Backup Configuration (Cron)
Add a crontab entry to execute daily automated backups at 02:00 AM IST:
```cron
0 2 * * * cd /opt/aashima-erp && docker compose exec -T backend py scripts/backup_db.py >> /var/log/aashima_backup.log 2>&1
```

---

## 4. Hardware Verification & Thermal Printing
- Pair the ESC/POS printer via Bluetooth or USB:
  - Default baud rate: 9600 / 115200
  - Default width: 80mm (48 characters per line) or 58mm (32 characters per line)
- Print test ticket from the Admin Dashboard **Thermal Print Centre** to verify character alignment and barcode legibility.
