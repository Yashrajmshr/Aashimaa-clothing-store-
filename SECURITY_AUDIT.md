# AASHIMA ERP Security Audit

**Audit date:** 18 November 2026  
**Assessment:** Critical issues were found; several code mitigations were applied during this audit. Do not deploy with real customer/financial data until remaining high findings are resolved and verified.

## Findings

| ID | Severity | Area | Finding |
|---|---|---|---|
| SEC-01 | Mitigated, verify | Customer privacy | Tracking requires a customer JWT and constrains orders to the verified customer. Anonymous and authenticated cross-customer QR denial passed API/Playwright checks; customer invoice PDF ownership is API tested. |
| SEC-02 | Partly mitigated | Authentication | Admin browser auto-login is removed and sign-in UI passed a smoke test. Development seed still uses the known default when no owner bootstrap password is configured; deployed account rotation is required. |
| SEC-03 | Mitigated | Data protection | Seeding is additive by default and production rejects cleanup. Test suite now requires a dedicated disposable SQLite database and does not purge on teardown. |
| SEC-04 | Partly mitigated | OTP | OTP is stored as keyed digest and not logged or returned. Unknown, cooldown, and registered send responses are indistinguishable; five attempts/code. Production rejects mock/unsupported providers and missing credentials. IP/device limits and live delivery remain unverified. |
| SEC-05 | Partly mitigated | Authorization | Role policies now cover reviewed internal route groups. Tests verify staff is denied finance/settings and customers are denied staff finance APIs. Full endpoint/role matrix and business-owner policy review remain open. |
| SEC-06 | Partly mitigated | Secret management | Production settings reject sample/default secret, SQLite, and OTP bypass; Compose requires database/JWT secrets. Access tokens remain valid 24h and customer tokens 48h. |
| SEC-07 | Partly mitigated | Network | Wildcard CORS default and DB/backend host port mappings were removed. Frontend HTTP is loopback-bound for external TLS termination; Nginx has basic security headers, but TLS termination, CSP, and proxy behavior are not verified. |
| SEC-08 | High | Financial integrity | Collections are capped at balance; refunds are restricted to Manager/Accountant/Owner; known transaction-reference retries are deduplicated. Complete ledger reconciliation, request-key idempotency for payments without references, concurrent uniqueness, and count-based reference generation remain risks. |
| SEC-09 | Partly mitigated | Database integrity | Runtime `create_all()` was removed; a generated follow-up baseline passed on scratch SQLite. Existing DB adoption and PostgreSQL migration remain unverified. |
| SEC-10 | High | File handling | Photo URLs are accepted as arbitrary input; invoice PDF routes now constrain resolved paths to configured invoice storage. Upload validation/storage controls remain absent. |
| SEC-11 | Medium | Browser security | Access tokens are stored in `localStorage`; dynamic API values are interpolated into HTML. Basic Nginx headers are configured, but CSP and XSS testing remain absent. |
| SEC-12 | Medium | QR tokens | Tracking now requires customer ownership and checks QR revocation; token URL uses configured `PUBLIC_BASE_URL`. Production URL and expiration behavior remain unverified. |
| SEC-13 | Medium | Logging | OTP and provider response bodies are no longer logged. General workflow notification records still contain recipient details and message content, including customer/order information. |
| SEC-14 | Mitigated | Supply chain | Vite and its vulnerable picomatch dependency were removed. Online and offline `npm audit` report 0 vulnerabilities. Python requirements remain broad/unlocked and no SBOM exists. GitHub reports no patched picomatch release through 4.0.7 ([advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf)). |

## Positive controls observed

- Staff passwords use bcrypt.
- JWT decode restricts accepted algorithms to the configured algorithm and checks the access/refresh token type in dependencies.
- QR token generation uses a random UUID component and HMAC signature.
- SQLAlchemy parameterizes ordinary query values and defines several foreign keys and unique constraints.
- Customer JWT tokens are rejected by the staff dependency.

These controls do not offset the exposure and authorization failures above.

## Required remediation sequence

1. Review customer invoice access and rotate any owner credential that uses the old default; establish production account recovery.
2. Complete OTP IP/device throttling, provider failure handling, and live delivery verification.
3. Finish role/action matrix tests and review least-privilege policies with the business owner.
4. Configure external TLS, add a compatible CSP, and test reverse-proxy behavior and headers.
5. Complete database adoption and authoritative financial transaction/idempotency logic; verify on PostgreSQL.
6. Add managed upload validation, XSS defenses, encrypted off-host backups, and a complete recovery drill.

## Verification limitations

The API suite passed 10 tests on a disposable SQLite database; Playwright smoke tests passed 2 checks; all three static frontend builds passed; online and offline `npm audit` reported 0 vulnerabilities. No external credentials, PostgreSQL service, deployed HTTPS endpoint, printer, camera, Docker deployment, or PostgreSQL recovery drill were available.
