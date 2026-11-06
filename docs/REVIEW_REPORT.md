# Editorial Studio — Independent editorial and skill-architecture review

**Version reviewed:** v0.2; **revision implemented:** v0.3.0 private-beta candidate  
**Reviewer lenses:** award-caliber magazine art direction, photo editing, publishing operations, OpenAI Codex skill architecture, local-app security and GitHub distribution  
**Date:** 6 November 2026

## Executive assessment

Editorial Studio has the right core promise: **turn a brief into a photo-led publication without misrepresenting photos or silently shipping a broken PDF**. A creative intake, explicit style decision and a provenance gate already make it stronger than many ad hoc AI document-generation workflows. All 12 original unit tests passed in this review.

However, the output is still a working template, not an award-winning editorial system. The primary issue is not color or a font choice; it is the absence of adaptable art direction, visual story sequencing, trustworthy image sourcing and human-controlled compositional detail. Engineering also needs stronger regression tests, a clear threat model and install/release automation. The private-first plan is correct: use actual issues to reveal design and product flaws before inviting the general public.

**Overall judgement: promising private beta, not ready for a public production promise.**

## Qualitative scores (expert opinion, not external awards)

| Area | v0.2 | Why |
|---|---:|---|
| Product vision | 9/10 | Distinct problem, repeatable and broad beyond restaurants. |
| Editorial workflow | 7/10 | Clear order: brief → direction → content → imagery → approval. |
| Magazine design | 6/10 | Two decent foundations but almost identical structural grids. |
| Photography and curation | 5/10 | Source-link suggestions instead of real researcher; no crop control. |
| PDF fidelity | 6/10 | PDF is embedded and structurally checked, but overflow/diacritics and visual checks are incomplete. |
| Codex skill | 7/10 | Valid skill structure, progressive references, clear safety gates. |
| Security and GitHub distribution | 4/10 | Not initially repository-ready, no CI, missing explicit privacy boundary and security tests. |

## Top editorial findings (fix before calling it magazine-grade)

### E1 — Two styles are mostly preset treatments, not individualized art direction (high)

`creative.py` declares exactly two static themes; `propose_directions()` adjusts the rationale using the provided brief but never analyzes the reference URL. This is useful for a prototype but undersells the promise of bespoke editorial work. Propose **two actually different sample spreads**, each with subject-specific art direction and different page rhythm, not two covers that share an identical feature template. Require user selection and support a hybrid third path once principles are agreed.

**Acceptance:** for five unrelated briefs (architecture, property, product, travel and a founder profile), the direction cards should differ in layout, not just typography/palette; each sample must explain a visual decision based on the actual reference research.

### E2 — Every story uses the same large-photo-top / bottom-text structure (high)

`engine.story_page()` is efficient, but a 10-story magazine has 10 similar pages and quickly loses visual pacing. Add an art-direction graph and a page-sequence planner: cover, opener, long-form essay, three-photo reportage, split spread, portrait, pull quote, map or index, technical detail, closing image and sourced credits. A real publication needs quiet and loud moments and meaningful blank space.

**Acceptance:** no more than three consecutive spreads reuse the same grid; variation must communicate story importance, not visual randomness.

### E3 — No crop/focal-point editing (high)

`ImageOps.fit` uses a centered crop for every image. A portrait can lose the face, a building can lose the roofline, and a product detail can be cut off. Store focal points per target slot, an asset-wide safe crop, crop previews, and a human override. Resolution must be measured at **print DPI and actual placement size**, not only in raw image width × height.

### E4 — Typography is operational, not editorial (high)

Core PDF templates use standard Times and Helvetica faces and fixed sizes. They are dependable, but there is no modern typography system, multilingual glyph coverage test, baseline grid or widow/orphan control. Use licensed redistributable embedded fonts with explicit styles and fallbacks, language-aware hyphenation and line-breaking rules. Add image captions and pull quotes as first-class content objects.

### E5 — The visual quality gate is necessary but not sufficient (high)

`verify_pdf()` originally checked page totals, whether image objects were embedded and whether any PDF link existed. That **cannot detect off-page text, blank captions, inaccurate image-to-subject matches, unhelpful crops, bad contrast or unapproved wording**. Preflight must enforce text-fit constraints, while separate rendered-page QA checks visual hierarchy, text overlap, readability and composition. A manual human review remains the final gate.

### E6 — Credits did not scale with issue length (medium/high)

The original credit page used a single column with a bottom cutoff; later records could be omitted from the printed credits. The v0.3 revision paginates credits into several pages and includes visible source-page text and clickable links.

### E7 — Magazine-specific editorial features are missing (medium)

Add an actual masthead, issue number, bylines, publishing date, geographic context, complete image caption, section hierarchy, editorial voice guidance, a coherent legend, QR codes where useful and an endnotes/source register. Present facts and editorial judgement as distinct layers.

### E8 — Accessibility and print production remain future milestones (medium)

A4 RGB is fine for private reading but does not imply accessible PDFs or press-ready CMYK/PDF-X. Choose targets explicitly: PDF for reading, PDF for print, or page-layout source. For public distribution, add tagging, alternate text strategy, text-contrast rules, working hyperlink text, bleed and color-space/prepress checks.

## Photo Researcher and provenance

The current “Research imagery” button generates four search URLs in `creative.candidate_queries()` and imports a specific manually selected HTTPS image. That is **guided research**, not an agent that independently finds and approves usable originals.

For real production, I recommend a two-stage pipeline:

1. **Discovery:** official brand/artist/business press kit, original supplier, approved asset collection, Wikimedia Commons with exact license metadata or a contracted stock provider; search-result thumbnails are pointers only.
2. **Asset record:** image ID, original bytes, original page, exact subject-match evidence, creator, permitted uses, territory/duration/attribution conditions, derived crop IDs, fingerprint, editor and approval timestamp.

Photos must be shown as *candidate*, *verified subject*, *rights cleared* and *approved crop* rather than a single boolean. “Found on the website” does not establish permission. Some material may be suitable for private reference yet not public redistribution. A hypothetical proof record is not a substitute for evidence.

## Codex/ChatGPT skill creator review

**Good:** a real `.agents/skills/editorial-studio/SKILL.md` with `name` and `description`; an optional `agents/openai.yaml`; mode-specific reference files; instructions not to repeat answered questions; explicit A/B creative gate and honest statement that agents are process roles.

**Improve:** keep SKILL.md lean (ideally under a few hundred lines), and move complex editorial rubrics and design lexicons into focused references. Define trigger and non-trigger test prompts, including a short request for a text summary that should *not* activate image-led publishing. Provide one positive evaluation corpus per project type and one file-creation case with missing assets that must stop. Avoid teaching a model that a source link equals a licensed asset.

**Distribution boundary:** a checked-in skill is local/repo-scoped. A portable skill-only plugin with a `plugin.json` and `skills/` folder can be used in a local marketplace and eventually submitted to the public Plugins Directory. A plugin that must operate the actual dashboard would require an approved, authenticated MCP/backend connector; the private Python server cannot simply be made web-accessible without engineering and security work.

## Engineering and security audit

| Issue | Severity | v0.3 action | Outstanding work |
|---|---|---|---|
| Host/CSRF protection missing for local mutations | High | Host, JSON type, same-origin and per-process token checks added; HTTP tests | External security audit, request throttling |
| Approved photo can be replaced on disk silently | High | SHA-256 fingerprint verified at preflight | Immutable originals and derivative/crop IDs |
| User data could be accidentally published with repository | High | `/projects/` and `/output/` excluded from Git; tests now use generic fixtures | Scan Git history and releases before public |
| HTML tag shown literally in style headline | Medium | Fixed preview line-break construction and headline cleaning | Browser visual regression CI |
| Image provenance cutoff after long lists | Medium | Split into multiple credits pages with links | Source ledger export and provenance UI |
| Fixed text areas could silently truncate | High | Added preflight line-length checks for fixed templates | Multilingual typesetting and crop-aware checks |
| Universal product leaks restaurant language | Medium | Removed restaurant defaults in generic projects | Generalized story schemas |
| Dependency reproducibility | Medium | Bounded versions already present; dependabot added | Pin via lockfile & SBOM |
| Remote downloader DNS rebinding and hostile files | High | Existing basic checks retained, security warning added | IP-pinned network client and isolation before hosted use |
| Concurrent manifest updates | Medium | Existing atomic write only | File locks, revisions/migrations and backups |
| GitHub Actions and release binaries | High | CI source included | Validate GitHub-hosted runs, signed package builds |

## Changes actually implemented in the candidate v0.3 folder

- Private project data and output removed from the distributable tree; `.gitignore` added.
- Portable `plugin.json`, `skills/` mirror and repo marketplace added.
- GitHub CI, Dependabot, validation and release packaging scripts added.
- Local dashboard requests hardened with a local Host gate and per-process mutation token.
- Approved photo fingerprints and explicit invalidation when bytes differ.
- Multi-page photo credits with source links; distribution-aware page footer.
- Page-fit checks for intro and feature text; no silent release of overlong descriptions.
- Removed restaurant-only copy in generic story defaults.
- Fixed creative-direction markup issue.
- Test suite expanded from 12 to 19 tests (local pass; remote CI unverified).

## Priorities and acceptance thresholds

**Private beta readiness:** clean install tested on Windows; CI green on Windows/Ubuntu; a realistic sample magazine and onepager manually reviewed at 100% page scale; true asset fingerprints/credits, no personal files in Git; downloader threat review; no mislabeled imagery.

**Public beta readiness:** at least 5 cross-category editorial samples, 4+ truly different page archetypes, thumbnail+full-size page review, versioned project data, open-source license, vulnerability policy, documented release artifact checksum and clean real-user installation tests. These are gates, not claims that they have already passed.

**Public v1.0 ambition:** visually individual publications, controllable layout, source and rights traceability, repeatable offline PDF builds, legitimate team roles and a polished installer/plugin experience.

## Release strategy

Private GitHub repo first, with protected main and signed release assets only after a build matrix passes. Use two channels:

- **Skill-only:** `$skill-installer install https://github.com/OWNER/editorial-studio/tree/main/.agents/skills/editorial-studio` in Codex.
- **Studio application:** repository clone or GitHub Release ZIP with a native launcher. A true one-click experience ultimately requires a signed desktop installer.

For eventual ChatGPT-wide installation, maintain a portable plugin and use the official plugin review channel. Do not confuse GitHub visibility with approval in the public Plugins Directory.

## Bottom line

The most important next investment is **not** a cleverer PDF generation script. It is a reusable visual editorial system (design direction → page sequence → subject-true photography → crop supervision → quality proof). Keep the existing Python engine for its useful guardrails, then enhance templates and image rights handling in a measured release series. GitHub should host the reproducible **code and skill**, not readers' private magazine projects or arbitrary web photos.
