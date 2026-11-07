# Historical private release review — 0.4.0

> **Current access status, 7 November 2026:** the repository is now publicly readable; no private invitation is required for the standard download. Personal publications and photos remain excluded. The review below records the earlier private-release scope and evidence; public visibility does not grant an open-source licence or establish additional testing. See README.md for current installation prerequisites and the unresolved licence decision.

This release targets the existing single-user local skill/dashboard. It does not turn the application into a hosted PDF service. At the time of this review, the GitHub repository and personal publication data were private.

## Security review and remediation

The Cloudflare [security-audit skill](https://github.com/cloudflare/security-audit-skill/tree/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8/skills/security-audit) guided a standard source review with independent verification. The review covered 28 source-boundary units. One defect was confirmed: an ignored local configuration file could enter the old release ZIP. The new packager uses an explicit inventory, rejects linked/nonregular/private inputs and has a dummy-private-file regression.

A bounded fixture reproduced response-header timeout overrun. The download now runs in a separate process with a parent-enforced deadline. The transport connects only to already validated public addresses and keeps certificate/hostname verification. Decoder selection is restricted before parsing; Pillow is pinned to the patched 13.0.0 release.

The browser review demonstrated a private-image existence channel between two loopback origins, not general public-origin reachability. Responses now carry same-origin resource policy, and private GETs reject foreign Origin and Fetch Metadata contexts. An isolated Chromium recheck now blocks both present and absent cross-origin images while a legitimate same-origin image still loads. Public-origin policy was not bypassed or probed.

Local requests have bounded concurrency and read deadlines. Mutating operations and exports are serialized; unique temporary files prevent request collisions. Export names use stable project identifiers. These measures improve local reliability; they do not provide isolation between OS users or protection against an operator who deliberately edits local files.

## Validation status

- 41 tests passed in an OS-isolated Linux container using synthetic fixtures, including 19-page/12-image reviewed-copy export, image approval changes, URL address pinning, private redirects, killable worker deadlines and private release exclusions.
- Repository structure, complete skill file-list equality and byte equality passed.
- The hash-locked runtime scan reported no known advisories on 6 November 2026. Native dependency code was not exhaustively audited.
- CI checks Windows and Ubuntu with Python 3.11 and 3.13, plus a dependency-advisory job. Confirm the exact candidate commit in GitHub Actions; earlier runs do not validate changed source. The isolated Chromium preview recheck passed.

The container used no external network, an empty allowlisted environment, read-only source/tools, non-root execution, bounded writable scratch and explicit resource/time limits. Windows runtime and browser behavior require their own checks. Neither tests nor a source audit prove every possible security issue is absent.

## Preserved product limits

Discovery, two-direction selection, exact-photo human approval, authentic subject matching, provenance/rights evidence, preflight, structural PDF audit and visual inspection remain required. Both baseline themes remain. Magazine output allows at most 12 feature pages; A4 portrait onepagers allow at most 3 features. High-end custom proof spreads retain their separate approved phase. Reviewed custom PDFs are copied only while bound content and asset fingerprints match; this is not arbitrary custom-layout rendering or active-PDF sanitization. No CMYK, bleed, PDF/X or certified prepress claim is added.

## Public showcase boundary

The approved https://magazine.10myth.com site is live as a public workflow showcase and installation guide. It does not accept uploads, process PDFs, expose the localhost app or contain personal guides/photos. At the time of this review, installation required access to the private repository; current access is described in the notice above. The custom hostname and HTTPS certificate were verified active. Public software distribution still requires the separate checks in SECURITY.md, including an external review and signed release checksums.

## Final private release verification

Windows/Ubuntu CI passed on Python 3.11 and 3.13 for the reviewed release and showcase-source commit. A native Windows Python 3.12 run completed 41 tests with 40 passed and one symlink-privilege skip. The local dashboard loaded the existing project and approvals. These checks do not constitute public multiuser-service certification. See GitHub Actions for checks on the exact final release commit.
