# Changelog

## 0.4.0 - Hardened private release candidate (2026-11-06)

- Explicit release inventory excludes untracked private configuration, photographs and manifests.
- Hash-locked runtime with patched Pillow; pinned CI actions and dependency scanning.
- Numeric-address HTTPS pinning and a killable download worker enforce an overall deadline.
- Restrict image decoding to JPEG, PNG and WebP; preserve human approval and provenance.
- Block cross-origin private previews; bound request concurrency, reads and ambiguous framing.
- Serialize local state changes, use unique temporary files and stable project export names.
- Add synthetic 19-page/12-image custom-edition and security regression coverage.
- Keep both skill copies identical and add source-trust/private-material guidance.
- Preserve all editorial gates, both renderer themes and format limitations.

## 0.3.0 - GitHub-ready private beta candidate (2026-11-06)

- Split local user projects and export files from public source tree.
- Added a portable plugin manifest and repository marketplace alongside the Codex skill.
- Added cross-platform CI and repository/packaging validation.
- Added Host and local-session-token requirements for dashboard mutation requests.
- Bound each approved image to a SHA-256 fingerprint; replaced bytes fail preflight.
- Stopped generic publication pages from displaying restaurant-only fallback copy.
- Corrected footer distribution label for private/internal/public editions.
- Paginated image credits for longer magazines and linked source pages.
- Added preflight checks for text that cannot fit the current fixed layouts.
- Fixed literal line-break markup appearing in creative direction previews.

## 0.2.0 - Prototype

- Creative brief, two fixed art directions, basic image provenance, direct URL import and PDF gate.
