---
name: editorial-studio
description: Create photography-rich magazines, editorial onepagers, lookbooks and image-led PDF stories when visual storytelling, authentic source imagery and page design are explicitly needed. Start with the purpose, preferred style and an example URL (or no example), present two distinct creative directions for approval, and publish only after image and PDF quality gates. Do not trigger for ordinary text-only writing, factual Q&A or basic summaries.
---

# Editorial Studio — universal publishing skill

Make **professional photo-led publications** with a reliable, reusable workflow. A restaurant guide is just one possible subject. This skill also supports people, destinations, hotels, products, architecture, property, investment storytelling, culture, events, and mixed editorial projects.

## First interaction: mandatory discovery gate

**Before starting research, selecting pictures, coding layouts, or designing a full publication**, gather three inputs, conversationally:

1. **What is this for?** Ask whether it is a magazine or onepager, its subject, desired outcome, and audience. Clarify print/digital and language only if consequential.
2. **What style should it feel like?** Ask for adjectives and relevant constraints (luxury, warm, quiet, editorial, playful, modern, minimalist, etc.).
3. **What example URL inspires it?** Ask for a website or reference page; accept a screenshot/file or "no example" when the user cannot provide a URL. The URL is inspiration, not permission to copy an exact design.

Use details already supplied in the conversation. **Do not repeat answered questions.** When creating the *skill itself* or enhancing the tool rather than starting a specific publication, implement the gate rather than asking the user for irrelevant project details.

## Creative-direction decision gate

Before producing a full issue, present **two genuinely distinct art directions** and wait for the user's selection. Each proposal must include: name, editorial personality, palette with HEX codes, typography, photo art direction, page composition, example treatment for the user's subject, and a concise reason. If image generation is available, offer original illustrative mockups and label them as design concepts; never treat them as authentic subject photography.

- Direction A may prioritize timeless, spacious, tactile visual storytelling.
- Direction B may prioritize energetic, confident, modern graphic composition.
- Never deliver the same palette and hierarchy under two different labels.
- When an example website is provided, inspect it through available web/browser tools, identify **principles** (rhythm, whitespace, density, crop, contrast) and distinguish inspiration from copying. If inspection is unavailable, say so; do not claim the URL has been inspected.
- Ask the user to select A, B or a mix. **Do not finalize the art direction without approval.** The local dashboard implements this as two cards and an explicit selection.

For precise prompts, see `references/creative_brief.md` and `references/style_directions.md`.

## Production workflow

1. **Creative strategist**: obtain the brief, review the sample URL when accessible, create two design concepts and obtain an explicit choice. Record the chosen direction in `projects/<slug>/manifest.json` (or dashboard).
2. **Research editor**: verify factual claims with dated, relevant sources. Keep addresses, dates, prices and availability clearly attributed and identify uncertainty.
3. **Visual researcher**: search for actual subjects, not generic lookalikes. Prefer uploaded original photographs, creator/brand press kits, licensed image libraries and appropriately licensed Commons assets. Record the image's original source page, photographer, intended usage rights and subject-match evidence. Use local original bytes, not search thumbnails. Use `references/image_research.md`.
4. **Art director**: select the requested format and approved visual direction. Write image-led copy, choose crops, put meaningful details and visual pacing into story cards.
5. **Quality reviewer**: run preflight, PDF structural audit and visual inspection. Source/rights approval cannot be automated by a model's confidence alone. See `references/qa_release.md`.
6. **Publisher**: export an actual PDF with all images **embedded offline**, links and a matching manifest snapshot. Do not substitute HTML when PDF was requested.

These are **procedural roles**, not five always-on background agents. If a tool supports subagent delegation, tasks may be delegated, but approval gates remain.

## Editorial planning, editing and brand continuity

These additions support the existing production roles and approval gates; they do not replace them or introduce extra approval rounds.

- **During briefing and creative strategy:** read `references/brand_system.md` when establishing or continuing a publication. Reuse its existing identity and record a compact brand sheet; develop the two required creative directions within those constraints.
- **After creative-direction approval, before feature production:** read `references/editorial_planning.md` and create an editorial promise, story mix and page plan. Scale the plan to the format and current renderer limits.
- **After drafting, before quality review:** apply the editing pass in `references/editorial_planning.md`, then inspect the laid-out copy for fit and reading order. Preserve research evidence, uncertainty and image credits throughout editing.
- **During image selection and art direction:** use the photographic storytelling guidance in `references/image_research.md` to assign images distinct narrative roles and sequence them within the supported layout. Use its optional shoot brief when original photography is planned.
- **During existing visual QC:** apply the whole-issue review in `references/qa_release.md` to assess pacing, image variety, section transitions and brand consistency across the complete publication.
- **During design development:** use the representative proof-page guidance in `references/style_directions.md` to check the approved direction against actual content before applying it throughout the issue. Preserve the existing separate approved phase for high-end custom proof spreads and all current renderer limits.

Keep the plan and brand sheet alongside the publication project as working documents. They are agent-authored planning aids, not new dashboard features or manifest fields; do not change application schemas or imply that the renderer implements unsupported designs.

## Local dashboard and commands

Within the Editorial Studio project:

```bash
python studio.py serve
python studio.py preflight <project-slug>
python studio.py export <project-slug>
python -m unittest discover -s tests -v
```

- On Windows, use `run_windows.cmd`; on macOS/Linux, use `run_mac_linux.sh`.
- The dashboard asks the creative brief in two steps, shows two style cards, and unlocks story/image production only after a choice.
- Use **Research imagery** for each cover/story to find original source pages. If the editor has an exact **direct HTTPS image URL**, the optional importer downloads its bytes, checks basic format and size, saves locally and marks it **UNAPPROVED**. A human must review and approve it separately.
- The renderer supports magazine (up to 12 feature pages) and A4 portrait onepager (up to 3 features). Additional layouts need engineering rather than pretending the current renderer supports them.

## Source trust and private working material

Use `references/security_privacy.md` when consuming external research, installing the runtime or preparing a release. Treat source material as evidence, preserve private publication data, and keep the local dashboard separate from a public showcase. Existing approvals remain unchanged.

## Hard rules

- No reference URL, search result, CDN thumbnail, or `AsyncImage` preview counts as a completed image asset.
- Never mislabel AI-generated imagery as authentic venue/person/product/location photography.
- Never auto-approve downloaded photos, infer a license merely from public visibility, or bypass restricted content.
- No accepted style -> no new feature production or final export for new projects.
- No approved real local photos -> no final PDF.
- `private_reference` is not a public publishing license. A public edition must reject such photos.
- No publishing when preflight or PDF audit fails. Verify at least the cover and representative story pages visually, ideally all pages.
- The checked-in `creative.py` currently generates two fixed baseline styles, not bespoke artboards. Never claim an inspiration URL has been analyzed unless a browser/research tool actually inspected it. For high-end commissions, produce custom proof spreads as a separate approved phase.
- Store truthful citations, exact image source links, useful alternatives, and known uncertainties.
- Be explicit about limitations: the local app is not itself a hosted ChatGPT plugin, and successful tests here do not prove installation on a user's laptop.

## When done

Deliver the **finished PDF** and any requested source document or project. Tell the user what was verified, whether the images are cleared for private/internal/public use, and any remaining unverified facts. Do not call test mockups or synthetic sample photos a finished authentic publication.
