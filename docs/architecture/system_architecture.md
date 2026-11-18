# AASHIMA ERP – System Architecture Documentation

**Business Entity**: AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers  
**Location**: 581, Turab Nagar, Ghaziabad, Uttar Pradesh, 201001, India  
**Architecture Pattern**: Modular Monorepo with Centralized Micro-Kernel Backend  
**Version**: 2.4.0 (Enterprise Release)  

---

## 1. High-Level System Architecture

The AASHIMA ERP software ecosystem is architected as three independent client applications communicating with a single, highly performant, resilient central backend powered by **Python FastAPI** and a normalized **PostgreSQL** database.

```mermaid
flowchart TD
    subgraph Clients["Frontend Client Tier"]
        AndroidApp["📱 AASHIMA Android App<br/>(Staff & Floor Operations)<br/>apps/mobile"]
        AdminDashboard["💻 Admin Web Portal<br/>(Management, Ledger & Invoicing)<br/>apps/admin-web"]
        CustomerPortal["🌐 Customer Web Portal<br/>(Live Order & Garment Tracking)<br/>apps/customer-web"]
    end

    subgraph Gateway["Reverse Proxy & Security Tier"]
        Nginx["Nginx Reverse Proxy & SSL Gateway<br/>Rate Limiting • Static Cache • CORS Guard"]
    end

    subgraph BackendAPI["Central Backend Tier (FastAPI)"]
        AuthModule["Auth & RBAC Service (JWT / OTP)"]
        BookingEngine["Booking & Multi-Garment Engine"]
        WorkflowEngine["Department Workflow Engine"]
        QRService["Cryptographic QR & Thermal Service"]
        BillingService["Billing, GST & Payment Ledger"]
        DeliveryModule["Transportation & Logistics"]
        NotifService["SMS & WhatsApp Notification Gateway"]
        ReportService["Reporting & BI Engine"]
    end

    subgraph Hardware["Workshop Hardware Tier"]
        BTPrinter["Bluetooth 58mm/80mm Thermal Printers"]
        A4Printer["Office A4 Laser Printer"]
        CameraScanner["Android Optical Barcode Scanner"]
    end

    subgraph DataStore["Data & Persistence Tier"]
        PostgresDB[("PostgreSQL 16 Database<br/>33 Normalized Entities")]
        MediaStorage[("Media & PDF Storage<br/>Invoices • Photos • QR SVGs")]
    end

    AndroidApp --> Nginx
    AdminDashboard --> Nginx
    CustomerPortal --> Nginx

    Nginx --> AuthModule
    Nginx --> BookingEngine
    Nginx --> WorkflowEngine
    Nginx --> QRService
    Nginx --> BillingService
    Nginx --> DeliveryModule
    Nginx --> NotifService
    Nginx --> ReportService

    AuthModule --> PostgresDB
    BookingEngine --> PostgresDB
    WorkflowEngine --> PostgresDB
    QRService --> PostgresDB
    BillingService --> PostgresDB
    DeliveryModule --> PostgresDB
    NotifService --> PostgresDB
    ReportService --> PostgresDB

    QRService --> MediaStorage
    BillingService --> MediaStorage

    AndroidApp -.-> BTPrinter
    AdminDashboard -.-> A4Printer
    AndroidApp -.-> CameraScanner
```

---

## 2. Component Architecture & Responsibility Separation

### 2.1 Application 1: AASHIMA Android Application (`apps/mobile/`)
- **Target Users**: Owner, Store Managers, Master Tailors (Master Iqbal), Finishing Masters (Master Ramesh Chandra), Counter Operators.
- **Form Factor**: Android Handheld POS and Tablets (390dp to 800dp).
- **Core Responsibilities**:
  - Counter order intake with multi-garment support.
  - Granular 0.25" precision tailoring measurement matrix (Coat, Pant, Shirt, Kurta/Pajama, Lehenga/Blouse).
  - High-speed camera QR code barcode scanning.
  - Department workflow stage transitions with karigar assignment.
  - Optical proof capture (intake condition photos).
  - ESC/POS 58mm and 80mm Bluetooth receipt and tag generation.
  - Cash and UPI advance collection.

### 2.2 Application 2: AASHIMA Admin Web Portal (`apps/admin-web/`)
- **Target Users**: Business Owner (Aashima Singhal), Chief Accountant (Rohan Sharma), Operations Supervisor.
- **Form Factor**: Desktop and Workshop Terminal Displays (1440px+).
- **Core Responsibilities**:
  - Global overview dashboard with live daybook positions, pipeline piece counts, and urgent delivery alerts.
  - Interactive Karkhana Pipeline Kanban board across 6 workshop wings.
  - Complete customer registry ledger with lifetime spend and past dues tracking.
  - Master measurement book with historical baseline comparisons.
  - GST invoicing, HSN/SAC code management, CGST/SGST/IGST calculations, and official tax invoice PDF generation.
  - Batch thermal roll generation for 58mm, 80mm, and A4 sticker sheets.
  - Expense ledger and operational P&L auditing.

### 2.3 Application 3: AASHIMA Customer Website (`apps/customer-web/`)
- **Target Users**: Boutique Patrons and Bridal Wear Clients.
- **Form Factor**: Responsive Mobile, Tablet, and Desktop.
- **Core Responsibilities**:
  - Public order tracking via Booking # + Registered Phone + 6-digit OTP verification.
  - Direct QR link resolution via unpredictable tokens.
  - 5-stage live status timeline with pulsating active node.
  - Visual inspection proof photo review.
  - Itemized bill breakdown with download tax invoice link.
  - Instant one-click WhatsApp and telephone workshop assistance.
  - Post-delivery feedback and fitting rating submission.
  - **Security Guarantee**: Strict read-only isolation; zero access to internal administrative or stage update endpoints.

### 2.4 Central Backend Service (`backend/`)
- **Framework**: Python 3.10+ with FastAPI.
- **ORM & Migrations**: SQLAlchemy 2.0 with Alembic versioning.
- **Financial Precision**: Strict `Decimal` types (`Numeric(12, 2)`) for all financial amounts, tax calculations, and discount deductions. Never uses floating-point arithmetic.
- **Authentication**: JWT access tokens (HS256) with short expiry, long-lived refresh tokens, and SMS/WhatsApp OTP verification.
- **Security**: Role-Based Access Control (RBAC) protecting all administrative endpoints from customer and unauthorized staff access.

---

## 3. Deployment & Infrastructure Architecture

```mermaid
flowchart LR
    subgraph HostServer["Production Linux Host (Dockerized)"]
        subgraph Proxy["Nginx Container (:80 / :443)"]
            ProxyConf["nginx.conf<br/>SSL Termination • Gzip<br/>Reverse Proxy Routing"]
        end

        subgraph Apps["Web Containers"]
            AdminContainer["admin-web Container<br/>Port 3001"]
            CustomerContainer["customer-web Container<br/>Port 3000"]
            MobileContainer["mobile-web Container<br/>Port 3002"]
        end

        subgraph Backend["FastAPI Container"]
            Uvicorn["Uvicorn ASGI Server<br/>Port 8000 • 4 Workers"]
        end

        subgraph DB["PostgreSQL Container"]
            Postgres["PostgreSQL 16 Engine<br/>Port 5432 • Dedicated Volume"]
        end
    end

    Users["Internet / Atelier LAN"] --> Proxy
    Proxy -->|/api/*| Backend
    Proxy -->|/media/*| Backend
    Proxy -->|admin.aashima.in| AdminContainer
    Proxy -->|aashima.in| CustomerContainer
    Proxy -->|pos.aashima.in| MobileContainer

    Backend --> Postgres
```
