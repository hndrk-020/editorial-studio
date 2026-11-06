# Art direction criteria

Creative direction is not a loose list of adjectives. Offer TWO options with materially different design decisions.

## Proposal recipe

Each concept must have:
- A distinctive, relevant name (not "Style 1" / "Style 2").
- One-line promise and editorial personality.
- Palette: 4–5 hex colors and explicit dominance/usage.
- Typography: serif/sans hierarchy and relative scale.
- Photography: subject type, lighting, authenticity, crop and visual rhythm.
- Composition: cover, story spread, card/chapter and caption treatment.
- A concrete sample applied to the user's topic.
- Tradeoff: what the direction gives up for its strength.

## The two local renderer themes

**Field Notes** uses deep green ink on warm ivory, muted terracotta, classic serif title hierarchy and generous photographic space. Best for documentary, travel, art and premium personal magazines.

**Bold Perspective** uses dark graphite ink, warm peach paper, energetic coral accent, emphatic sans-serif titles and graphic bars. Best for ventures, creators, product stories and contemporary editorial pieces.

The dashboard's two proposals are **deterministic starting points**. A Codex/Work art director can refine their content after actually inspecting the reference URL. The current PDF engine implements two distinct color and headline treatments; complex fully custom layouts need further rendering work.

## Final art-director checkpoints

- Is the cover impressive but truthful?
- Are image focal points preserved without awkward crops?
- Is every headline legible and distinguishable from metadata?
- Does the same visual system apply across all chapters?
- Is this an actual publication for the brief, not a restaurant template with labels renamed?

## Design development and representative proof pages

After the existing creative-direction selection, use the editorial plan, brand sheet and representative researched content to check how the direction works in practice before extending it across the issue. This is a design-development pass within the existing art-director role, not a replacement for the two-direction gate. Routine proofs within supported layouts create no additional approval round; high-end custom proof spreads remain a separate approved phase as required by the main skill.

### Choose representative content

For a magazine, aim to exercise three different demands using pages already planned for the issue:

- **Cover:** test the masthead/title hierarchy, strongest relevant photograph, crop and headline contrast.
- **Feature opener:** test the story's entry point, relationship between headline and main image, introductory copy and caption placement.
- **Text-heavy page:** test the longest realistic copy, subheads where supported, reading order, caption/credit legibility and overflow.

These are representative functions, not three additional pages or mandatory new layout types. Combine functions where appropriate. For the A4 portrait onepager, proof the actual single page with representative content across its existing feature slots. Stay within the magazine's maximum of 12 feature pages and the onepager's maximum of 3 features; do not add a spread or page type the renderer cannot produce.

Use actual edited copy and approved local photographs when available. If missing assets prevent a rendered proof under existing gates, prepare a clearly labelled planning sketch or specification and record the unresolved dependency. Do not bypass preflight or asset approval, unlock export, or present synthetic or placeholder imagery as an authentic finished publication. Existing rules for clearly labelled concept illustrations still apply.

### Define the working design system

Capture decisions alongside the brand sheet or editorial plan, keeping enduring identity separate from issue treatment:

- Page geometry: intended margins, alignment/grid and column relationships.
- Type hierarchy: title, introductory copy, body, caption and credit roles; available fonts, sizes and line spacing where the implementation supports them.
- Spacing and hierarchy: recurring gaps, white space, image-to-text balance and contrast.
- Image treatment: placement, crop/focal point, caption association and sequencing.
- Recurring elements: section identifiers, folios and navigation where already supported.

For each decision that exceeds existing controls, distinguish the desired specification from the renderer's actual behavior. The current engine provides Field Notes and Bold Perspective with distinct color and headline treatments; this guidance does not add configurable grids, arbitrary typography, multi-image layouts, custom mastheads or bespoke spreads. Use supported content, crop, ordering and theme choices; identify remaining design changes as engineering needs rather than silently changing the renderer or promising implementation.

### Inspect and carry decisions forward

Render supported proof pages through the existing export and QA workflow. Inspect at intended viewing size and thumbnail scale, checking hierarchy, realistic copy fit, focal points, contrast, caption/credit association and consistency with the approved brand sheet. Judge both the image-led and dense-content cases; do not validate a system using only a short headline and ideal photograph.

Record the tested pages, working decisions, corrections and any implementation limits in a short proof note alongside the project. These notes are planning aids, not dashboard functionality or new manifest fields. Reuse successful decisions throughout the issue and revisit affected proofs if content or design changes materially. After corrections, follow the existing preflight, export/audit and visual checks; proof review does not replace whole-issue review or any release condition. Do not claim print readiness, bleed or CMYK support from a screen proof; those remain outside v0.3.
