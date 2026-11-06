# Security policy

Editorial Studio is a local single-user application. It is not a hosted application or a multiuser service.

## Reporting issues

Until a dedicated security contact is configured, report vulnerabilities privately to the repository owner through GitHub's **Report a vulnerability** feature, if enabled. Do not disclose exploitable details in public issues.

## Current boundaries

- The dashboard binds to `127.0.0.1` and checks Host, request Origin, JSON type and a random per-process token for mutations.
- Local projects, output PDFs and uploaded photos are ignored by Git and must not be committed.
- The HTTPS importer pins validated public addresses while preserving TLS hostname verification. A separate, killable worker bounds DNS, connection, headers and transfer time. Images remain subject to human approval. Do not deploy this importer on an internet-facing server.
- Photo ownership and usage permission are manually reviewed; no automated approval can prove rights.
- Do not use the app to process confidential assets on shared or untrusted computers.
- Runtime dependencies are pinned with wheel hashes in requirements.lock. CI checks known advisories; a clean scan is not proof that every dependency path is safe.
- Private reads reject cross-origin browser requests and carry same-origin resource policy. The local token is a browser request guard, not OS-user authentication; use a trusted single-user computer.
- Release ZIPs use release-files.json rather than directory enumeration. Never add private working material to that inventory.
- Source review and sandbox tests are recorded in the release-readiness document. They do not certify a hosted or multiuser deployment.

## Before public distribution

Require an external security review, request-volume limits, asset metadata and CSRF integration tests on Windows, signed release checksums, dependency scanning and a clear vulnerability reporting channel.
