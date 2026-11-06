# Security policy

Editorial Studio is a local single-user prototype. It is not a hosted application or a multiuser service.

## Reporting issues

Until a dedicated security contact is configured, report vulnerabilities privately to the repository owner through GitHub's **Report a vulnerability** feature, if enabled. Do not disclose exploitable details in public issues.

## Current boundaries

- The dashboard binds to `127.0.0.1` and checks Host, request Origin, JSON type and a random per-process token for mutations.
- Local projects, output PDFs and uploaded photos are ignored by Git and must not be committed.
- The external HTTPS image importer includes DNS and size checks, but the TLS/DNS connection has not been penetration-tested for DNS rebinding or malicious content. Do not deploy this importer on an internet-facing server.
- Photo ownership and usage permission are manually reviewed; no automated approval can prove rights.
- Do not use the app to process confidential assets on shared or untrusted computers.
- Dependencies use bounded ranges, not cryptographic lockfiles. Pin/harden before publishing installers or a hosted offering.

## Before public distribution

Require an external security review, request-volume limits, asset metadata and CSRF integration tests on Windows, signed release checksums, dependency scanning and a clear vulnerability reporting channel.
