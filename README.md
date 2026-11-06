# Editorial Studio

**Photo-led publications with an editorial brief, two art directions, real image provenance and verified offline PDFs.**

> **Private beta candidate · v0.3.0 · not yet an award-winning design system or publicly installable desktop binary.**

## What it does

Editorial Studio supports photo magazines, travel and property guides, architecture essays, cultural reports, founder profiles and visual onepagers. Every publication begins with the subject, objective, audience, preferred style and optional inspiration URL. It presents two directions before drafting pages. Sources and photographs are checked individually; a missing or unapproved image blocks PDF export.

Currently implemented: a local dashboard, two fixed visual themes, a human-supervised photo-link researcher, a direct HTTPS image importer, a PDF renderer (A4 portrait), preflight checks and an image/link audit. Image research is **not autonomous**; the dashboard provides suggested search URLs, not a crawler.

## Quick start

For a complete Windows walkthrough, see the [local skill installation guide](docs/LOCAL_INSTALLATION.md), including verification, updates, private-repository access and optional dashboard setup.

**Windows:** Install Python 3.11+ from https://python.org/downloads/ and enable Python on PATH. Download the repository or ZIP, extract it, then double-click `run_windows.cmd`. First start requires internet for dependencies. The local studio opens at `http://127.0.0.1:8765`.

**macOS/Linux:** `chmod +x run_mac_linux.sh && ./run_mac_linux.sh` (Python 3.11+ required).

**Codex skill:** Open this repository in Codex; it auto-discovers `.agents/skills/editorial-studio/SKILL.md`. Ask:

```text
$editorial-studio Create a photography-led architecture onepager for design readers. Start with the brief, review my inspiration URL, and show two distinct creative directions before production.
```

The skill runs instructions. It does **not** install a hosted app or automatically install Python dependencies.

## Architecture

```text
studio.py             Local HTTP dashboard (localhost only)
engine.py             PDF composition, asset gate, source credits and PDF audit
creative.py           Creative brief and two fixed visual presets
photo_researcher.py   Human-directed image downloading with size/type checks
static/               Dashboard frontend
.agents/skills/       Repo-local Codex skill
plugins/              Portable skill-only plugin candidate
.agents/plugins/      Repo-local plugin marketplace
scripts/              Distribution and repository validators
tests/                Synthetic-fixture regression tests
projects/             Local user publications (Git-ignored)
output/               Generated PDFs (Git-ignored)
```

## Publication workflow

1. Create a publication and complete the brief. A sample URL is optional; if supplied, the **agent must inspect it** before claiming to have incorporated the reference. The offline dashboard does not automatically analyze websites.
2. Compare Field Notes and Bold Perspective; make an explicit selection. These are fixed themes, not fully original designs automatically generated from the URL.
3. Write features, confirm current facts, find real images and record source/credit/rights evidence. Original image bytes must be downloaded or uploaded; search preview URLs are not publishable images.
4. Approve each exact asset separately. SHA-256 fingerprints detect unapproved local file replacement.
5. Pass preflight, PDF structure checks, and a manual visual review before sharing the PDF.

## Run the test suite

```bash
python -m pip install -r requirements.txt
python scripts/validate_repository.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Tests contain **synthetic, explicitly labeled fixtures only**. They do not prove a visual photo match, a rights grant, or a Windows production installation.

## GitHub private-first and installation

Read [GitHub private → public release guide](docs/GITHUB_PRIVATE_TO_PUBLIC.md). For now, start with a **private GitHub repository**. Do not commit personal projects or the Cascais photo library. Keep project data in `projects/` and all exports in `output/`; both directories are excluded from Git.

For Codex, the supported copy/paste path is `$skill-installer` with the GitHub directory URL after you create the repo. For ChatGPT-wide plugin discovery, use the portable `plugins/editorial-studio/` and `.agents/plugins/marketplace.json` with the Plugin Directory; public directory distribution has a separate submission/review process. The plugin **does not bundle the running local dashboard**.

## Status and limitations

- 19 regression tests passing locally as of 2026-11-06; CI still needs a real GitHub run on Windows and Ubuntu.
- Current PDF designs are functional but visually repetitive. More page archetypes and crop/focal-point controls are part of the next design milestone.
- Image provenance is recorded but approval is manual. The source/rights fields cannot cryptographically prove licensing.
- The HTTP image fetcher's anti-SSRF checks have **not** received an external security audit. Do not expose this app or downloader on a public network.
- Current export is A4 RGB, not certified CMYK with bleed, PDF/X, or a prepress report.
- No open-source license is granted yet: choose one during the public-release review.

See [independent editorial and technical review](docs/REVIEW_REPORT.md), [roadmap](docs/ROADMAP.md), [security policy](SECURITY.md) and [changelog](CHANGELOG.md).
