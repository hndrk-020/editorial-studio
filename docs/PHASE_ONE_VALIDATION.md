# Phase-one installation and public examples

Reviewed on 7–9 November 2026. Public-facing examples, installation guidance and UI copy are in English. This records bounded checks, not a guarantee that every platform or security condition has been tested.

## Deployment status

The new homepage and all three English examples are live at [magazine.10myth.com](https://magazine.10myth.com/#examples), Sites version 9, from source commit `f582e7d84d617927a39596a726050153521c91c6`. The compressed archive upload repeatedly returned `OpenAI file blob upload ... error sending request`. Uploading an uncompressed TAR containing the exact same 17 files succeeded; no content, approved imagery, TLS settings or access controls were changed. This is a verified packaging workaround, not a claim about the transport's underlying root cause. The deployment completed successfully on 8 November and live verification finished on 9 November 2026.

All three PDFs and three source ZIPs were downloaded from their live homepage links and matched the approved SHA-256 hashes and byte sizes. ZIP integrity and PDF page counts (1, 6 and 8) passed; the live JSON checksum manifest matched the reviewed inventory. Desktop (1440px) and mobile (390px) layout checks found loaded covers and no horizontal overflow. Browser capture of the wider desktop viewport was clipped; the DOM geometry checks and normal-viewport screenshot provide the recorded evidence. All five installation copy buttons produced their intended prompt in the browser clipboard. No browser JavaScript errors were observed.

Following the live Windows instructions through GitHub's normal **Code → Download ZIP** click downloaded source commit `d38d69d1f89fb640bcf90415524fe50981917f1a`. All 75 tracked files matched, allowing the declared CRLF conversion for two `.cmd` files. The isolated Windows installer and `--check` passed; the direct Skill Installer route also copied all nine skill files exactly. The existing global installation remained byte-for-byte unchanged. A download-helper timeout was resolved by using the normal browser click; the live links themselves worked.

A new ephemeral, read-only Codex session on 9 November discovered that exact browser-downloaded installation and read its skill, editorial-planning and brand-system references. It did not use the global skill as evidence or start a publication. The separate PDF application's earlier runtime checks below remain applicable; no new application code was introduced by this deployment.

## Installation evidence

- Downloaded the public repository using GitHub's browser **Code → Download ZIP** route. All 70 tracked files matched commit `76cd018c1aa56ff5fd6d3e372ff7c201be837bea`; the two `.cmd` files had only the CRLF conversion declared in `.gitattributes`.
- Ran the downloaded Windows installer in a fresh, isolated profile with spaces in its path. All nine skill files copied exactly and `--check` passed. Existing user installations were preserved.
- Codex's bundled Skill Installer independently downloaded the public skill into a separate temporary destination. All nine files matched the committed source.
- A fresh, ephemeral, read-only Codex session discovered the browser-ZIP installation and read `SKILL.md`, `editorial_planning.md` and `brand_system.md` from that exact project-local copy.
- Created a fresh Python 3.12 environment in the downloaded source and installed the hash-locked dependencies. All ten readiness checks passed.
- Started only the isolated localhost dashboard. Dashboard, JavaScript, session, image previews, preflight, export and PDF download returned successful responses. The approved startup demo exported one page with two embedded images and one hyperlink; its page pixels matched the reviewed PDF. Project and image-approval bytes stayed unchanged.
- Browser inspection confirmed visible image previews, the estimated progress bar/ETA, server-confirmed completion and the PDF link. A subsequent copy-only UI patch corrected English singular/plural forms and the generic cover label; that final JavaScript was also checked in the isolated dashboard. Progress is a browser estimate while awaiting one export request, not server-stage telemetry.
- All five landing-page copy buttons produced their exact prompt in the browser clipboard. Desktop and 390px mobile layouts were inspected; no horizontal overflow, broken loaded cover images or JavaScript errors were observed. Native operating-system clipboard integration was not re-tested in this phase.

## Automated checks

- Native Windows full suite: **56 tests run, 54 passed, two expected platform skips** (Unix-only dangling-link test and unavailable Windows symlink creation privilege).
- Ubuntu WSL installation tests: **14 run, eight passed, six Windows-only skips**. No full WSL runtime suite was run because that environment lacked the locked dependencies.
- GitHub CI on commit `76cd018`: all four Windows/Ubuntu × Python 3.11/3.13 jobs and the dependency audit passed. [Recorded run](https://github.com/hndrk-020/editorial-studio/actions/runs/42361502293). Later commits run the same workflow; consult [current Actions](https://github.com/hndrk-020/editorial-studio/actions) for their result.
- Repository validator, Skill Creator quick validator and whitespace checks passed. Both complete skill copies matched all nine filenames and bytes; all seven linked local references existed.
- The tracked-file boundary and source allowlist continue to exclude personal publications, photos, manifests, local settings and business working material.

## Three reproducible public examples

| Example | Verified output | Scope |
| --- | --- | --- |
| Startup introduction | 1 page, 2 embedded images, 1 hyperlink | Own-product introduction; labelled historical screenshot and original artwork |
| Creator case study | 6 pages, 2 image pages, 3 hyperlinks | One substantive feature plus fixed framing/credits; own design process, no customer outcome claims |
| Curation portfolio | 8 pages, 4 image pages, 7 hyperlinks | Four credited public-domain landscapes; not our original photography |

The owner approved all eight exact placements from six source images, including the scoped screenshot/artwork exception. The photos and crops remain unchanged. Preflight, structural audit, every-page visual review and all seven unique destination links passed. Fresh extraction of each final source ZIP verified every packaged file hash and reproduced all 15 pages pixel-for-pixel. PDF bytes can vary with document metadata; page pixels were compared.

Each packet pins immutable source commit `76cd018c1aa56ff5fd6d3e372ff7c201be837bea`. A privacy/content scan found no personal publication references, private filesystem paths, personal email addresses, credentials, PDF attachments, JavaScript or launch actions. Source photography remains credited. The MIT grant applies to software, skill instructions and documentation; media retains its stated rights.

See the [live examples](https://magazine.10myth.com/#examples) and [download manifest](../showcase/dist/examples/download-manifest.json). The photographic PDF is approximately 14.9 MB; source ZIPs are each below 5 MB and omit a duplicate of the separately supplied reviewed PDF. These are digital RGB outputs, not certified press-ready files.

## Remaining verification limits

This is not a clean-OS/new-account test. macOS, Claude Code, Grok Build, Cursor and Gemini CLI runtime installation have not been tested. These tool choices retain explicit documentation-based status on the homepage. Android and physical offline-device tests were not performed. The local dashboard is for a single user on localhost; these checks do not authorize public-network exposure. Existing renderer limits and creative/image approval gates remain in force.
