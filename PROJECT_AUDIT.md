# AASHIMA ERP Project Audit

**Audit date:** 18 November 2026  
**Scope:** Repository source, schemas, API routes, frontend clients, database and migrations, test suite, environment templates, Docker, Nginx, backup scripts, and project documentation.

## Executive assessment

The repository contains a useful ERP prototype with three browser clients, a FastAPI API, SQLAlchemy models, workflow and billing services, and operational documentation. It is **not production ready**. Some existing documentation calls it verified and production ready, but that assertion is unsupported by the code and checks run during this audit.

Release remains blocked by incomplete OTP controls, financial and backup integrity risks, dependency exposure, and unverified end-to-end/deployment behavior. During this audit, source changes mitigated unauthenticated tracking disclosure, removed admin auto-login, added role policies to internal route groups, made seeding additive by default, added production configuration guards, and added a schema baseline migration. Supplied business SQLite databases were not opened for test writes, reset, migrated, or seeded; tests used separate disposable files.

## Repository map

| Area | Contents and observations |
|---|---|
| `apps/admin-web` | Static admin dashboard; now requires explicit staff sign-in. |
| `apps/mobile` | Static staff POS and QR scanner; QR scanning still loads `html5-qrcode` from its existing CDN URL. |
| `apps/customer-web` | Static OTP/QR customer tracking portal; tracking requests now send the customer session token. |
| `backend/app` | FastAPI routes, SQLAlchemy models, Pydantic schemas, services, configuration, and bearer-token dependencies. |
| `backend/migrations` | Original initial migration is empty; generated follow-up baseline creates current modeled tables. Existing database adoption requires a reviewed schema compare/stamp operation. |
| `backend/tests` | One API test module; now requires explicit test mode and a disposable database; teardown is additive and does not purge. |
| `infrastructure` | Dockerfiles, Docker Compose, and an Nginx reverse-proxy configuration. HTTPS is not configured despite documentation language. |
| `scripts` | SQLite file copy and PostgreSQL shell-string backup/restore utilities. PostgreSQL path lacks explicit credential handling and safe command construction. |
| `docs` | API catalogue, architecture, database overview, SOPs, user manuals, limitations, and deployment guide. Several claims conflict with the implementation. |

No `AGENTS.md` files were present. Git metadata exists. The repository includes `.env` and SQLite databases; secret values and customer data were not printed or included in this report.

## Functional implementation review

| Workflow | Repository evidence | Audit result |
|---|---|---|
| Staff authentication | `/auth/login`, JWT generation, mobile and admin sign-in | Implemented; admin auto-login removed. Password policy, login throttling, and session revocation are absent. |
| Role permissions | Route-level role dependencies | Policies cover reviewed internal route groups; API tests sample Staff, Accountant, Delivery Staff, and Customer allowed/denied actions. Manager/Owner matrix and business-policy review remain. |
| Customer registration/search | Customer CRUD and search routes | Implemented but not runtime verified. Uniqueness checks are not protected against races at the endpoint. |
| Measurements | Measurement templates, save route, mobile controls | Storage path exists; data range/unit validation and full workflow verification are absent. |
| Multi-garment bookings | Booking route creates garments, services, measurements, QR tokens, initial histories, and advance payment | API suite verifies multi-quantity totals; invalid/inactive and duplicate service IDs are rejected. Booking number generation by row count can still collide after deletions/concurrent requests. |
| QR scan/print | Staff scan and print routes, token generator | Scan was exercised in API tests. Print, camera hardware, and production base URL were not verified. QR URL now uses `PUBLIC_BASE_URL`. |
| Alteration/cleaning/finishing/delivery | Department queues and transition service | Implemented with transition checks and role policies; detailed workflow and role matrix remain untested. Delivery record operations do not reconcile garment workflow state. |
| Payments/refunds | Payment route and ledger service | API suite passed final collection/refund and duplicate transaction-reference retry; rejected floor-staff refund and invalid payment type; verified PDF refresh. Authoritative ledger, request-key idempotency, and concurrent uniqueness remain open. |
| GST/non-GST invoices | Invoice service and PDF generation | API suite verifies both invoice types and booking balance reconciliation, including non-GST discount/extra charge. GST discount tax treatment needs accountant review; duplicate invoice generation remains race-prone. |
| Customer tracking/OTP | Customer-scoped tracking and OTP send/verify endpoints | Tracking requires a customer JWT and constrains records to that customer. OTP storage uses a keyed digest; OTP-bearing links/log output were removed. IP/device throttling and live provider verification remain incomplete. |
| Reports/settings | Dashboard metrics and key/value settings endpoints | Role checks now apply. Settings have no validation/allowlist, and full role matrix is unverified. |
| PDF/printing | Customer and staff invoice PDF endpoints | API test verifies customer-owned PDF retrieval and denial for a different customer. Staff printing, physical printer, and thermal flows remain unverified. Resolved PDF paths are confined to configured invoice storage. |

The browser UI contains many controls and workflows. The two added Playwright security smoke tests passed; full business workflow, responsive/mobile, and hardware click-through was not completed.

## Database and backend review

- SQLAlchemy models define the primary business entities and some useful unique constraints and foreign keys.
- FastAPI and seed startup no longer call `Base.metadata.create_all()`.
- The original Alembic migration is a no-op; a generated follow-up baseline now creates the current schema on a clean database. Existing database adoption still requires schema comparison and a reviewed stamp procedure.
- SQLite foreign-key enforcement is not enabled explicitly.
- Several identifiers use `COUNT(*) + offset`, which is unsafe under concurrent requests and after removals.
- Booking creation, invoices, and payments use database commits but do not consistently guard exceptions with rollback or enforce idempotency.
- Soft-delete filters are inconsistent across related endpoints.
- Payment and booking totals are denormalized and are updated independently; no reconciliation/report is provided.
- Backup now uses SQLite's online backup API and PostgreSQL argument arrays; SQLite restore verifies checksum/integrity and refuses existing targets. PostgreSQL and full recovery remain unverified.

## Frontend and UX review

- There are three separate client applications; workspace manifests and lockfile have been added and installed for the verified builds.
- Admin dashboard now asks staff to sign in; the bundled auto-login was removed.
- Some navigation/client code is wired to real API endpoints; full workflow behavior, mobile breakpoints, accessibility, and keyboard use were not tested.
- The customer portal requires a customer session for tracking by booking number/phone/QR token. API coverage and an anonymous browser smoke check verify denial without that session.
- Token storage in `localStorage` makes tokens available to injected JavaScript; no CSP or other defense-in-depth is configured.
- Dynamic server/customer content is interpolated into `innerHTML` in several places; output escaping and a restrictive CSP need review.
- English-first labels and small text/control sizing do not meet the requested simple Hindi/English, large-control staff experience consistently.

## Build and test evidence

- Python 3.10 ran the suite on a fresh disposable SQLite database: **10 passed**, with 22 Pydantic deprecation warnings.
- Root `npm run build` succeeds for all three apps using a dependency-free static copier and local static server; the server passed an HTTP content and path traversal check.
- The installed Vite/picomatch tree was removed because GitHub reports a high-severity picomatch ReDoS through 4.0.7 with no patched release listed. Both online and offline `npm audit` report 0 vulnerabilities after the removal.
- Playwright smoke specs and a disposable-database guard were added. **2 browser smoke tests passed** for admin sign-in and anonymous tracking denial.
- Docker, PostgreSQL, HTTPS, external SMS/WhatsApp credentials, and physical printer/camera verification were not available for an end-to-end deployment check.

## Readiness decision

**Not production ready.** See [BUG_REPORT.md](BUG_REPORT.md), [SECURITY_AUDIT.md](SECURITY_AUDIT.md), [TEST_REPORT.md](TEST_REPORT.md), and [PROJECT_STATUS.md](PROJECT_STATUS.md) for tracked findings and required actions. Do not deploy with real customer data until critical security, migration, data-integrity, and test blockers are resolved.
