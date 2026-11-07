# Editorial Studio

**Photo-led publications with an editorial brief, two art directions, real image provenance and verified offline PDFs.**

Visit [magazine.10myth.com](https://magazine.10myth.com) for the public showcase and step-by-step installation guide. The source is public; no repository invitation is required to install. The website source is in [showcase/](showcase/README.md).

> **Public source · v0.4.0 · local workflow and dashboard.**

## What it does

Editorial Studio supports photo magazines, travel and property guides, architecture essays, cultural reports, founder profiles and visual onepagers. Every publication begins with the subject, objective, audience, preferred style and optional inspiration URL. It presents two directions before drafting pages. Sources and photographs are checked individually; a missing or unapproved image blocks PDF export.

Currently implemented: a local dashboard, two fixed visual themes, a human-supervised photo-link researcher, a direct HTTPS image importer, a PDF renderer (A4 portrait), preflight checks and an image/link audit. Image research is **not autonomous**; the dashboard provides suggested search URLs, not a crawler.

## Quick start

**Two setup steps: install the skill in your AI tool, then set up the local PDF app if you want this project's renderer.** Follow the [installation-to-first-PDF guide](docs/LOCAL_INSTALLATION.md), including safe updates and verification.

**Codex, skill only:**

```text
$skill-installer install https://github.com/hndrk-020/editorial-studio/tree/main/.agents/skills/editorial-studio
```

Start a new turn and ask `$editorial-studio` to report its loaded `SKILL.md` path and confirm it can read the editorial planning and brand references. An existing destination is preserved by the bundled installer; follow the guide for a deliberate update.

**Local PDF app, Windows:** Install Python 3.11+ from https://python.org/downloads/ and enable Python on PATH. Keep the complete extracted repository, then double-click `run_windows.cmd`. First start requires internet for hash-locked dependencies. The local studio opens at `http://127.0.0.1:8765`.

**Local PDF app, macOS/Linux:** `chmod +x run_mac_linux.sh && ./run_mac_linux.sh` (Python 3.11+ required; macOS has not been runtime-tested here).

**Read-only setup check:** run `run_windows.cmd --check` or `./run_mac_linux.sh --check` from the repository. This diagnoses skill references, app files, Python and dependencies without downloads, changing publications, creating an environment or starting the dashboard.

**Codex skill:** Open this repository in Codex; it auto-discovers `.agents/skills/editorial-studio/SKILL.md`. Ask:

```text
$editorial-studio Create a photography-led architecture onepager for design readers. Start with the brief, review my inspiration URL, and show two distinct creative directions before production.
```

The skill provides instructions and references. It does **not** include the PDF application, install a hosted app or automatically install Python dependencies. To use this project's renderer, keep the full repository and follow the Python application setup above.

The dashboard and PDF export run locally. Installing the skill does not upload publications; content you share with your chosen AI tool is handled under that provider's settings and terms. You need your own access to that AI tool.

Installation evidence (7 November 2026): the Windows source installer copied all nine skill files unchanged to an isolated test profile, and a fresh Codex process loaded the project-local skill and its references. This was not a clean-machine test or a verified public ZIP-download journey. Claude Code, Grok Build, Cursor and Gemini CLI setup prompts follow their vendors' documentation but have not been runtime-tested here.

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

Read [GitHub private → public release guide](docs/GITHUB_PRIVATE_TO_PUBLIC.md). This repository is publicly readable. The linked guide retains the original private-first release process as historical guidance. Do not commit personal projects or photo libraries. Keep project data in `projects/` and all exports in `output/`; both directories are excluded from Git.

Personal publications, photo approvals, local settings, account details and business planning are not product source. Keep business working material outside this repository. Public examples belong here only after a deliberate rights, privacy and publication review; do not copy a personal project into the showcase. The release packager uses an explicit source inventory rather than collecting everything in the workspace.

For Codex, the supported copy/paste path is `$skill-installer` with the existing public GitHub directory URL. For ChatGPT-wide plugin discovery, use the portable `plugins/editorial-studio/` and `.agents/plugins/marketplace.json` with the Plugin Directory; public directory distribution has a separate submission/review process. The plugin **does not bundle the running local dashboard**.

## Status and limitations

- 41 regression tests passed in an isolated Linux environment on 2026-11-06. See [release readiness](docs/RELEASE_READINESS.md) for current platform validation and limits.
- Current PDF designs are functional but visually repetitive. More page archetypes and crop/focal-point controls are part of the next design milestone.
- Image provenance is recorded but approval is manual. The source/rights fields cannot cryptographically prove licensing.
- Source review and bounded security fixtures cover packaging, URL/decoder boundaries and browser protections. This is not an external certification or a guarantee against all vulnerabilities. Do not expose the local dashboard or downloader on a public network.
- Current export is A4 RGB, not certified CMYK with bleed, PDF/X, or a prepress report.
- Software, skill instructions and documentation are licensed under the [MIT License](LICENSE). Example photographs and other media retain their separately recorded rights; the software licence does not grant rights to third-party media or branding. Personal publications and photographs are excluded from the public repository.

See [release readiness](docs/RELEASE_READINESS.md), [independent editorial and technical review](docs/REVIEW_REPORT.md), [roadmap](docs/ROADMAP.md), [security policy](SECURITY.md) and [changelog](CHANGELOG.md).
