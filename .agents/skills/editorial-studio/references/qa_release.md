# PDF release protocol

1. **Brief and art-direction gate:** check the required brief and a selected direction. For new projects without it, do not publish.
2. **Editorial facts:** dates, names, claims, availability and prices must have credible evidence and uncertainty appropriately disclosed.
3. **Asset gate:** every image slot must have an actual verified local image >=1100x700 pixels; source, photographer/organization credit, usage basis and subject approval. No missing slots; no image URL-only placeholders.
4. **Distribution rights:** reject `private_reference` assets in public editions; flag them as a warning for personal/internal review where appropriate. Do not equate this technical gate with legal review.
5. **Preflight:** `python studio.py preflight SLUG` must return `pass: true`.
6. **Export + structural audit:** `python studio.py export SLUG` generates an actual PDF, verifies its expected page count, photograph-bearing pages and hyperlink annotations, and saves a JSON snapshot.
7. **Visual QC:** render each page to PNG using `fitz` or an approved PDF renderer. Inspect all pages at thumbnail scale and high-priority pages at full resolution. Fix clipped text, poor crops and illegible details. Print readiness/CMYK/bleed is not included in v0.3.
8. **Offline check:** disconnect network and confirm PDF still shows images. Confirm the PDF opens in an Android/desktop reader.
9. **Delivery:** provide a verified PDF link as the primary deliverable, indicate whether other editable assets are available, and be honest if a step could not be tested on the user's Windows device.

If a quality condition fails, issue a clear error with a remedy. Never publish a test layout with synthetic photo placeholders and call it the finished subject-specific edition.

## Whole-issue review within visual QC

Extend step 7's existing thumbnail inspection into a review of the complete publication before delivery. Use the latest exported PDF, editorial plan and approved brand sheet; this is part of existing quality review, not an additional creative approval round.

- **Editorial arc:** does the opening establish the issue's promise, does each feature add something distinct, and does the ending feel deliberate? Check that the actual order and any contents/navigation agree with the publication.
- **Pacing and transitions:** inspect the cover-to-opening transition, section changes and closing sequence. Look for runs of equally dense pages or repeated layouts; use supported variations in copy length, image emphasis and ordering where they improve the reading experience.
- **Photographic narrative:** check context, subject variety, image roles and sequencing across the issue. Identify accidental duplicates, repetitive crops or visual juxtapositions that imply unsupported relationships. Inspect questioned images and captions at full resolution.
- **Brand continuity:** compare typography, color roles, voice, captions and recurring navigation against the approved brand sheet. Distinguish intentional issue variations from unintended drift. Avoid requiring every page to share one composition.
- **Reading experience:** check hierarchy and legibility at the intended viewing size as well as thumbnail scale. Preserve useful white space, credits and factual qualifications when adjusting copy or composition.

For a onepager, assess the reading path and balance among its features instead of imposing magazine sections or spreads. Work within the current renderer; flag changes requiring engineering rather than claiming they are implemented.

Keep a short working review note identifying pages, actionable findings, corrections and any unresolved limitations. Separate subjective refinements from failures of existing release conditions. Correct material problems before delivery; after changes, rerun affected editorial and asset checks plus the existing preflight, export/structural audit and visual QC on the new PDF. Deliver the version actually reviewed and retain the existing matching manifest snapshot requirement. Never claim a review was performed without inspecting the output.
