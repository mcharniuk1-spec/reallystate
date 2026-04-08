---
name: security-audit
description: Perform security audits on codebases including legal gate enforcement, secret detection, injection checks, and compliance verification. Use when running safety gates or pre-launch audits.
---

# Security Audit

## Use When

- Running pre-merge or pre-launch security checks.
- Verifying legal gate enforcement across connectors.
- Checking for secrets, PII, or injection vulnerabilities.

## Audit Checklist

1. **Legal gates**: every connector fetch path calls `assert_live_http_allowed`.
2. **No live network in tests**: grep for `httpx|requests|urllib|socket|aiohttp` in `tests/`.
3. **Secret detection**: scan fixtures for `AKIA|AIza|secret|password|BEGIN PRIVATE KEY|Bearer`.
4. **Media storage**: confirm no binary blobs in PostgreSQL; only storage keys.
5. **SQL injection**: parameterized queries only; no string interpolation in SQL.
6. **XSS**: HTML output is escaped; no raw user input in templates.
7. **CORS**: API allows only expected origins.
8. **Auth/RBAC**: protected routes require valid tokens.

## Commands

```bash
rg "assert_live_http_allowed\(" src/bgrealestate/connectors
rg "httpx|requests|urllib|socket|aiohttp|urlopen|Client\(" tests
rg "AKIA|AIza|secret|password|BEGIN (RSA|OPENSSH|PRIVATE)" tests/fixtures -i
rg "bytea|blob|binary|large object|lo_" sql/schema.sql
```

## Output

```text
Legal gates: PASS/FAIL
Network isolation: PASS/FAIL
Secret scan: PASS/FAIL
Storage policy: PASS/FAIL
Injection risk: PASS/FAIL
Auth coverage: PASS/FAIL
```
