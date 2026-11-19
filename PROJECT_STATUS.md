# AASHIMA ERP — Production Readiness Status

**Review date:** 18 November 2026
**Assessment:** **NOT PRODUCTION READY**
**Release decision:** Blocked by OTP operations, financial/data integrity, database adoption, recovery verification, and deployment checks.

## Verified state

| Area | State | Evidence / limit |
|---|---|---|
| Backend feature surface | Implemented, partly verified | API suite covers health, staff login, OTP flow, customer isolation, multi-quantity booking, QR scan, workflow transition, tracking, GST/non-GST invoices, payment/refund, and soft delete. |
| Customer privacy | Mitigated in code | Public tracking requires a customer JWT and checks QR/booking ownership and deletion status. Anonymous and authenticated cross-customer denial passed API/Playwright checks. |
| Admin authentication | Improved, partly verified | Hard-coded auto-login removed; Playwright confirms the sign-in form renders. Existing owner credentials still need rotation. |
| Role authorization | Implemented, partial matrix verified | Internal route groups declare role policies; Staff, Accountant, Delivery Staff, and Customer allow/deny checks passed. Manager/Owner full endpoint matrix and business policy review remain. |
| OTP security | Partly improved | HMAC digest at rest; uniform responses for unknown, cooldown, and registered phones; no delivery-status leak, OTP link, or log; five attempts/code. Production requires real provider credentials. IP throttling and live delivery remain unverified. |
| Database migrations | Clean-install path verified on SQLite | Follow-up baseline creates modeled schema; applied to isolated database. PostgreSQL and existing database adoption are unverified. |
| Seeding | Safer default | Additive by default; production cleanup is rejected and production owner bootstrap requires an explicit password. |
| Billing | Basic guardrails added | Collection amount is capped at balance; invoice creation syncs booking balances; refunds are role-restricted; repeat transaction references return the original receipt; PDFs refresh after payments/refunds. Authoritative ledger, request-key idempotency, concurrency, and GST discount treatment remain incomplete. |
| Frontend builds | Passed | `npm run build` succeeded for all three apps with the dependency-free static copier; static server, traversal check, and Chromium sign-in render passed. |
| Backend API tests | Passed | 10 passed on a fresh disposable SQLite database; 22 Pydantic deprecation warnings. Includes role matrix samples, OTP enumeration checks, quantity pricing, GST/non-GST reconciliation, refund, PDF ownership/refresh, and SQLite recovery. |
| Playwright | Smoke checks passed | 2 passed: admin sign-in displayed, anonymous tracking denied. Full business workflows are not covered. |
| Dependency audit | Passed | Removed Vite and `picomatch` from the dependency tree. Both online and offline `npm audit` report 0 vulnerabilities. |
| Docker/HTTPS/PostgreSQL | Not verified | Compose syntax was reviewed and its dependency indentation corrected; Docker is unavailable here. DB/backend stay private and the HTTP frontend binds to loopback for external TLS. No container/PostgreSQL/TLS deployment was run. |
| Backup/recovery | Partially improved | SQLite online snapshot/checksum and new-target restore tested on disposable DB. PostgreSQL, encrypted off-host retention, media recovery, and full restore drill remain unverified. |
| Integrations/hardware | Not verified | No SMS/WhatsApp credentials, printer, or camera workflow was available. |

## Remaining release gates

### P0 — required before production use

- Complete role-by-role API matrix tests and review policies against business duties.
- Add IP/device OTP limits, confirm provider delivery, and test account recovery and resend abuse.
- Reconcile all financial events from an authoritative ledger; add request-key idempotency and concurrency guarantees, and have an accountant review GST discount treatment.
- Validate existing database schema and document a reviewed Alembic stamp/adoption plan; verify on PostgreSQL.
- Configure and verify external HTTPS and a compatible CSP; basic Nginx headers are present and Compose binds HTTP to loopback for the TLS proxy.
- Verify PostgreSQL backup/restore, encrypted off-host retention, media recovery, and a full recovery drill.

### P1 — required for operational signoff

- Add input validation and managed upload/path handling; test PDF and receipt delivery.
- Add full browser workflows for customers, measurements, bookings, QR, department queues, payments/refunds, GST/non-GST invoices, reports, and settings.
- Complete mobile, accessibility, keyboard, and Hindi/English staff usability review.
- Add audit log policies, monitoring/alerting, database migration readiness checks, dependency lock for Python, and CI build/test runs.

## Test report

- Alembic clean install on disposable SQLite: passed through revision `37938752a9d1`.
- Backend API suite: **10 passed**, **22 deprecation warnings**.
- Playwright security smoke tests: **2 passed**.
- Frontend production builds: **3 passed**.
- `npm audit` and `npm audit --offline`: **0 vulnerabilities** after removing Vite/picomatch.
- Production PostgreSQL migration, Docker deployment, HTTPS, SMS/WhatsApp delivery, physical printing/scanning, backup, and recovery drill: not run.

See [PROJECT_AUDIT.md](PROJECT_AUDIT.md), [BUG_REPORT.md](BUG_REPORT.md), [SECURITY_AUDIT.md](SECURITY_AUDIT.md), [TEST_REPORT.md](TEST_REPORT.md), [deployment guide](docs/architecture/deployment_guide.md), and [backup/recovery guide](docs/architecture/backup_recovery_guide.md).
