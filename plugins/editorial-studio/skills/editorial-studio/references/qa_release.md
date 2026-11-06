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
