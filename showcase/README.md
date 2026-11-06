# Editorial Studio showcase

Live at https://magazine.10myth.com. This directory contains the source of the public showcase and installation guide, hosted through Sites on Cloudflare. The Editorial Studio GitHub repository remains private.

## Files

- `dist/index.html`: content, workflow and installation instructions.
- `dist/style.css`: responsive editorial design, animation and reduced-motion support.
- `dist/app.js`: accessible workflow/installation tabs and copy buttons.
- `dist/mark.svg`: original typographic mark.
- `dist/hero.mp4` and `dist/hero-poster.jpg`: original silent 16-second film and poster fallback; no personal photographs.

The film autoplays muted and loops inline. Its play/pause control remains available; reduced-motion preferences disable autoplay. A failed media load displays the poster image. Native video controls remain if JavaScript is unavailable.
- `.openai/hosting.json`: existing Site identity and static deployment directory. This is deployment configuration, not a publication manifest or a credential.

The cover illustration is an original typographic concept, explicitly labelled as such. No personal publications, photos, exported PDFs, user project manifests, credentials or dependency directories belong here.

## Local preview

From this directory:

```sh
python -m http.server 8790 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8790. No build or dependency installation is required. Stop with Ctrl+C.

## Checks and publishing

Run `node --check dist/app.js`. Inspect desktop and mobile layouts; test tab selection with the mouse and arrow keys, copy buttons and expandable dashboard instructions. Check internal anchors and local resource paths. Installation commands must continue to describe private-repository authentication accurately.

The live Site uses its separately managed Sites source repository. A commit to this GitHub repository does **not** deploy the website. To publish changes, use the Sites skill with the existing `project_id` in `.openai/hosting.json`, obtain fresh repository access through the Sites tool, and synchronize only this directory's website source into that Site checkout. Preserve its identity; do not create a replacement Site. Follow the Sites source-helper, save-version and deployment workflow, then verify https://magazine.10myth.com over HTTPS.

Never store source-repository tokens in this directory. The main skill release ZIP intentionally excludes the showcase: `release-files.json` remains the explicit skill/application distribution inventory.

The opening hero uses a split layout on desktop and places the full film immediately after the headline on mobile. Check the complete video and pause control at scroll position zero on small and large viewports.
