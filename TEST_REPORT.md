# AASHIMA ERP Test Report

**Run date:** 18 November 2026  
**Result:** Targeted checks pass; coverage is incomplete and production deployment is not verified.

## Automated results

| Check | Result | What it covered |
|---|---|---|
| Backend API suite | **10 passed**, 22 Pydantic deprecation warnings | Health/readiness, production configuration guards, owner login, OTP enumeration/lockout behavior, Staff/Accountant/Delivery role samples, multi-quantity booking totals, invalid service rejection, QR scan, workflow transition, authenticated cross-customer tracking denial, GST and non-GST invoices, invoice ownership/refresh, payment/refund and transaction-reference retry, soft deletion, and SQLite backup/restore to a new verified target. |
| Playwright | **2 passed** | Admin renders an explicit staff sign-in form; anonymous tracking receives HTTP 401. |
| Frontend production builds | **3 passed** | Admin, customer, and mobile dependency-free static copies. |
| Static server | Passed | Admin HTML and module served successfully; Windows-style path traversal was rejected. |
| Chromium smoke check | Passed | Built admin sign-in rendered from the new static output. |
| Python compilation | Passed | `backend` modules compiled with Python 3.10. |
| JavaScript syntax | Passed | Admin, customer, and mobile entry points parsed by Node. |
| Compose YAML parse | Passed | YAML structure parsed and services `db`, `backend`, and `frontend` were present. Docker Compose itself was unavailable, so interpolation and container validation did not run. |
| Alembic clean install | Passed on a separate disposable SQLite database | Schema baseline revision `37938752a9d1`; this does not verify PostgreSQL or adoption of an existing business database. |
| Backup/restore | SQLite passed on disposable data | Online snapshot, SHA-256 verification, SQLite integrity check, and refusal to overwrite an existing restore target. PostgreSQL path was unavailable. |
| Dependency audit | **Passed** | Vite/picomatch removed; both online and offline `npm audit` report 0 vulnerabilities. |

API tests used a fresh SQLite file under `backend/tests` with `ENVIRONMENT=test` and `AASHIMA_TESTING=1`. The guarded fixture only drops/recreates that explicitly named disposable test database. Supplied business SQLite files were not used by the test suite.

## Tests not performed

- Full browser walkthrough of customer registration/search, gents/ladies measurements, all garment departments, reports, settings, printing, mobile layout, accessibility, and every navigation/button.
- Invoice print, GST discount tax treatment, duplicate requests, or concurrent payment/invoice operations.
- SMS/WhatsApp delivery: the local environment had no Fast2SMS or Twilio credentials. No OTP was sent through an external provider.
- PostgreSQL migration, Docker build/run, TLS termination, production CORS, reverse-proxy/header behavior, CSP, or external health monitoring.
- Printer/camera hardware, PostgreSQL backup consistency, and a complete application recovery drill.
- Customer QR tracking and invoice PDF denial for a different authenticated customer are covered by API checks.

## Final session rerun note

The successful API and Playwright results above are from the earlier completed verification run. During the final desktop-session rerun, Python 3.10 source compilation and all three frontend builds completed, and the offline npm audit again reported zero vulnerabilities. The API test invocation did not produce a completed result before the session timed out. Playwright could not launch its browser from the session's configured cache and could not connect to `127.0.0.1:8000` because local socket access was denied. These rerun attempts do not replace or change the earlier passing results; repeat them in a normal development or CI environment before release.

## Reproduction

From the repository root in PowerShell, choose a new filename ending `_test.db` in `backend/tests` for each run:

```powershell
$env:ENVIRONMENT = 'test'
$env:AASHIMA_TESTING = '1'
$env:DATABASE_URL = 'sqlite:///d:/ashiana/backend/tests/aashima_local_test.db'
$env:SECRET_KEY = 'disposable-test-secret-key-1234567890'
$env:DEFAULT_OTP_BYPASS = '123456'
python -m pytest -q backend/tests/test_api_suite.py
npm run build
npm run test:e2e
```

Playwright requires the API to be available at `http://127.0.0.1:8000` (or set `E2E_BASE_URL`). Do not point test commands at the normal business database.

## Readiness conclusion

The test evidence supports the targeted security and billing changes described in [PROJECT_STATUS.md](PROJECT_STATUS.md). It does not establish full functional coverage or production readiness. Complete the outstanding workflows, PostgreSQL/Docker/TLS checks, and recovery drill before release.
