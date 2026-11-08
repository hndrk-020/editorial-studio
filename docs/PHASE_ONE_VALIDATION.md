# Phase-one installation and public examples

Reviewed on 7–8 November 2026. Public-facing examples, installation guidance and UI copy are in English. This records bounded checks, not a guarantee that every platform or security condition has been tested.

## Deployment status

The installation fix is public. The new homepage example cards and downloads are prepared and locally tested, but not yet live: the hosting service's file upload returned `OpenAI file blob upload ... error sending request` before saving a version. Removing duplicated PDFs from the source ZIPs reduced the deployment archive from 37.3 MB to 23.5 MB without changing the reviewed PDFs or approved imagery; the same upload error remained. The source was pushed to the existing Sites repository, and live version 8 was confirmed unchanged. No successful deployment or live download verification is claimed for these new examples.

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

See the [download manifest](../showcase/dist/examples/download-manifest.json) for the prepared files. Their planned website paths are present in the showcase source, but await deployment. The photographic PDF is approximately 14.9 MB; source ZIPs are each below 5 MB and omit a duplicate of the separately supplied reviewed PDF. These are digital RGB outputs, not certified press-ready files.

## Remaining verification limits

This is not a clean-OS/new-account test. macOS, Claude Code, Grok Build, Cursor and Gemini CLI runtime installation have not been tested. These tool choices retain explicit documentation-based status on the homepage. Android and physical offline-device tests were not performed. The local dashboard is for a single user on localhost; these checks do not authorize public-network exposure. Existing renderer limits and creative/image approval gates remain in force.
