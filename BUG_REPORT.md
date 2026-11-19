# AASHIMA ERP Bug Report

**Audit date:** 18 November 2026  
**Status convention:** Open findings are based on source review unless a test is explicitly noted.

## Critical

### BUG-001 — Public tracking discloses private order details — mitigated

- **Original evidence:** The endpoint accepted a booking number or phone without customer authentication and returned customer name/unit, garment names, instructions, photos, due date, invoice URL, and balances.
- **Impact:** A guessable booking number or known mobile number exposes sensitive personal, operational, and financial data.
- **Change made:** The route requires a customer JWT, checks booking/garment ownership and soft-delete state, and honors QR revocation. Anonymous and authenticated cross-customer QR denial passed API/Playwright checks.

### BUG-002 — Admin client logs in with a bundled owner password — client fixed

- **Original evidence:** `apps/admin-web/src/main.js` posted a literal owner username/password during initialization.
- **Impact:** Anyone who can load the admin application can obtain owner access if the seeded account/password remains active.
- **Change made:** Auto-login removed; admin asks staff for credentials. Playwright sign-in screen check passed. Development seed still uses the known default if no bootstrap password is supplied; rotate any deployed owner account that may use it.

### BUG-003 — Production seeding purged transactional data — safeguards applied

- **Original evidence:** The seed function defaulted to deleting transactional records; tests invoked it before and after.
- **Impact:** Running the documented seed command against the production database irreversibly removes business records.
- **Change made:** Default seeding is additive, production cleanup is blocked, production owner bootstrap requires an explicit password, and tests use disposable SQLite files without destructive teardown.

## High

### BUG-004 — OTP exposure/throttling — partly mitigated

- **Original evidence:** OTP was stored and logged in plaintext, placed in a WhatsApp URL returned to the requester, and had no effective attempt/resend ceiling.
- **Impact:** Log readers or a caller initiating OTP delivery can obtain the code; repeated requests enable abuse and guessing.
- **Change made:** OTP uses a keyed digest at rest; no code/status is returned or logged; unknown, registered, and cooldown sends share the same response; failures are limited to five per code. Production requires Fast2SMS or Twilio credentials. Provider delivery and IP/device throttling remain open.

### BUG-005 — Internal API authorization was not role-scoped — partially fixed

- **Original evidence:** `require_roles()` existed but route decorators used `get_current_user` throughout; authenticated staff could call billing, settings, customer, and delivery operations.
- **Impact:** Least privilege is not enforced for accountant, delivery, and floor staff accounts.
- **Change made:** Role checks now cover the reviewed internal API route groups. API tests confirm staff denial for finance/settings and customer denial for staff finance routes. Full role/action matrix testing and business policy review remain required.

### BUG-006 — Financial operations permit inconsistent balances and refunds — basic guardrails applied

- **Original evidence:** Payments could exceed due balances; refunds increased collection totals. Invoice reconciliation also has gaps.
- **Impact:** Over-collection, false paid balances, and inaccurate books/invoices.
- **Change made:** Payments cannot exceed due balance; refunds reduce paid amount and increase dues, cannot exceed currently paid amount, and require Manager/Accountant/Owner. Payment type/mode values are validated; matching transaction-reference retries return the original payment/receipt. Booking/invoice balances reconcile on invoice creation; PDFs refresh after payment/refund changes. Request-key idempotency without transaction references, concurrent accounting, and GST discount tax treatment remain open.

### BUG-007 — Initial database migration did not create schema — clean-install migration added

- **Original evidence:** Initial migration was empty; app created tables during import.
- **Impact:** A clean production database cannot be initialized or safely upgraded using the documented Alembic process; runtime startup can mutate schema unexpectedly.
- **Change made:** A follow-up schema baseline now creates the modeled tables; clean migration passed on disposable SQLite. Runtime `create_all()` was removed. Existing database adoption and PostgreSQL migration remain unverified.

### BUG-008 — Identifier generation is collision-prone

- **Evidence:** Booking, invoice, payment, receipt, expense, delivery, and customer references are derived from row counts plus offsets.
- **Impact:** Concurrent transactions, soft deletion, or historical data changes can produce duplicate identifiers and failed or misdirected operations.
- **Required fix:** Use database sequences or a concurrency-safe allocator with unique-constraint retry; add idempotency keys where clients may retry.

### BUG-009 — Docker ports/defaults — partially fixed

- **Original evidence:** Compose published database/backend ports and used known credentials; Nginx was HTTP-only.
- **Impact:** Sensitive services are directly reachable, and default secrets undermine all JWT protection.
- **Change made:** DB/backend host port mappings and Compose secret fallbacks were removed; production settings reject default secrets, bypass OTP, SQLite, and a non-HTTPS public base URL. Frontend HTTP binds to loopback for external TLS. Basic Nginx security headers are configured; external TLS, CSP, and proxy behavior remain unverified.

### BUG-010 — Backup/restore scripts lacked safe snapshots and target protections — partially fixed

- **Original evidence:** SQLite backup copied the live file; PostgreSQL commands used shell interpolation; restore overwrote the configured SQLite file without checksum or integrity verification.
- **Impact:** Inconsistent backup, command injection risk from configuration, or unrecoverable overwrite.
- **Change made:** SQLite backup uses the online backup API and restore requires a new target, checksum, and integrity check. PostgreSQL commands use argument arrays; restore creates a distinct database and refuses existing targets. SQLite restore is tested on disposable data.
- **Remaining:** Verify PostgreSQL backup/restore, encrypted off-host storage, retention, media recovery, and a full recovery drill.

## Medium

### BUG-011 — Frontend build/dependency issue — mitigated

- **Change made:** Added npm workspaces, lockfile, and Playwright config, then removed Vite/picomatch because the advisory affects picomatch through 4.0.7 and has no patched version. The static build/server replacement passed all three builds, an HTTP/path traversal check, and a Chromium sign-in render. Online and offline `npm audit` both report 0 vulnerabilities.

### BUG-012 — Production QR links were localhost URLs — fixed in source

- **Original evidence:** Booking creation persisted a localhost URL.
- **Impact:** Scanned tags on customer devices point to their own localhost and do not reach the service.
- **Change made:** QR links use the configured `PUBLIC_BASE_URL`; production Compose requires it. Deployment-domain behavior still needs verification.

### BUG-013 — Health endpoint always reports healthy — readiness endpoint added

- **Evidence:** `/health` returns a static success response and does not check database connectivity or migration state.
- **Change made:** Added `/ready` to check database connectivity and return 503 when unavailable. Migration state and other dependent services are not checked.

### BUG-014 — Test suite isolation — safeguards and API coverage improved

- **Change made:** Suite requires `ENVIRONMENT=test`, `AASHIMA_TESTING=1`, and a SQLite filename ending `_test.db`; it no longer purges on teardown. API suite passed 10/10. Two Playwright smoke tests passed. Full business workflow E2E coverage remains open.

### BUG-015 — Upload paths need security controls; invoice PDF path containment added

- **Evidence:** Photo endpoint accepts an arbitrary `photo_url` string. There is no upload content/type/size handling.
- **Change made:** Staff and customer invoice PDF routes resolve files under the configured invoice directory; customer route verifies ownership. API test checks valid download and foreign-customer denial.
- **Required fix:** Restrict photo references to managed storage and validate upload MIME/size.

## Open validation items

- Verify real customer/staff workflows in a browser, including measurements, QR camera, receipts, refunds, invoice print, and mobile layout.
- Verify email/SMS/WhatsApp provider configuration, delivery callbacks, and rate limits with approved credentials.
- Verify PostgreSQL migrations and backups on a disposable PostgreSQL instance.
- Run dependency vulnerability scanning and define a supported dependency update cadence.
