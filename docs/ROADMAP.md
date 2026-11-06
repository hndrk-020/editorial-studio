# Editorial Studio release roadmap

## P0: private beta reliability (0.3.x)

- Finalize localhost API test coverage and independent security review; apply request rate limits and strengthen downloader DNS/IP pinning before any hosted deployment.
- Run GitHub Actions on real Windows, Ubuntu and (later) macOS. Test launch with no Python installed (expected clear guidance) and with Python installed (expected working dashboard).
- Stabilize JSON project schema, migrations, backups and output versioning. Prevent concurrent manifest lost updates.
- Add screenshot-based review for every output page with overlay/overflow checks. Maintain fixture assets with non-authentic labels and no copyrighted imagery.
- Use Unicode-capable embedded typefaces with redistribution licenses; validate diacritics and clipping in multiple languages.

## P1: magazine-grade editorial experience (0.4)

- **Design director:** input a design reference, analyze its *principles* and produce two *project-specific* artboards, not just recolored presets.
- **Page archetypes:** cover, photo essay, opener spread, image grid, portrait feature, map, quote, directory, comparative cards, long-form article and back cover.
- **Art director controls:** focal point, crop, portrait/landscape alternatives, selective typography, grid width, caption alignment, and layout variants.
- **Proofing:** content-fit warnings, orphan/widow control, typographic scale, image resolution at actual print size, editorial hierarchy and accessibility/contrast checks.
- **Content model:** independent story sections, captions, sources, photo usage rights and date-scoped facts. No restaurant-specific schema fields in generic projects.

## P2: Photo Researcher (0.5)

- Prefer original uploads and authenticated press libraries. Integrate optional providers with documented licenses and terms.
- Build a candidate table: original page, original file, photographer/agency, exact pictured subject, image dimensions, geographic/context match, model-suggested crop, rights evidence and expiration date.
- Never infer copyright permission from a search engine preview. Preserve original bytes and verified sha256, plus derivative exports.
- Store an explicit approval actor, timestamp, intended distribution, rights conditions and credit text; reapproval required after material changes.
- Support explicit rejection reasons and non-destructive replacements rather than forcing a user to restart.

## P3: publishing and collaboration (0.6-0.9)

- Publishable templates for A4, A5, US Letter, digital landscape, 16:9, and social dimensions; PDF/X via a dedicated prepress toolchain only after validation.
- Side-by-side PDF preview and digital flipbook; QR/links checked before export. Preserve a portable offline PDF.
- Versioned issues, change logs, project-level editorial approval and issue archives.
- Optional team mode with roles and access control, instead of exposing the local single-user HTTP server.
- Recurring project imports with deduplication, editor approval, and image aging checks.

## V1.0: public product launch

- Reproducible signed desktop installer and clear update channel, a tested plugin or skill-only install path, accessibility and privacy documentation, licenses, security review, and five publicly shareable example projects.
- Success measures: zero missing images, zero unclipped text failures in preflight, all source/rights fields present, clean install on supported operating systems and successful reproduction of each sample issue.
