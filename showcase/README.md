# Editorial Studio showcase

Live at https://magazine.10myth.com. This directory contains the source of the public showcase and installation guide, hosted through Sites on Cloudflare. The Editorial Studio GitHub source repository is public.

## Files

- `dist/index.html`: content, workflow and installation instructions.
- `dist/style.css`: responsive editorial design, animation and reduced-motion support.
- `dist/app.js`: accessible workflow/installation tabs and copy buttons.
- `dist/mark.svg`: original typographic mark.
- `dist/hero.mp4` and `dist/hero-poster.jpg`: original silent 16-second film and poster fallback; no personal photographs.

The film autoplays muted and loops inline. Its play/pause control remains available; reduced-motion preferences disable autoplay. A failed media load displays the poster image. Native video controls remain if JavaScript is unavailable.
- `.openai/hosting.json`: existing Site identity and static deployment directory. This is deployment configuration, not a publication manifest or a credential.

The cover illustration is an original typographic concept, explicitly labelled as such. Personal publications, photographs, user project manifests, credentials and dependency directories do not belong here. The reviewed public examples are separately authored demo material, explicitly approved for publication.

## Local preview

From this directory:

```sh
python -m http.server 8790 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8790. No build or dependency installation is required. Stop with Ctrl+C.

## Checks and publishing

Run `node --check dist/app.js`. Inspect desktop and mobile layouts; test tab selection with the mouse and arrow keys, copy buttons and expandable dashboard instructions. Check internal anchors and local resource paths. Installation commands must accurately describe public downloads and preserve existing installations.

The live Site uses its separately managed Sites source repository. A commit to this GitHub repository does **not** deploy the website. To publish changes, use the Sites skill with the existing `project_id` in `.openai/hosting.json`, obtain fresh repository access through the Sites tool, and synchronize only this directory's website source into that Site checkout. Preserve its identity; do not create a replacement Site. Follow the Sites source-helper, save-version and deployment workflow, then verify https://magazine.10myth.com over HTTPS.

Never store source-repository tokens in this directory. The main skill release ZIP intentionally excludes the showcase: `release-files.json` remains the explicit skill/application distribution inventory.

The opening hero uses a split layout on desktop. On mobile the primary setup CTA precedes the film. Check that the five tool choices remain equal and usable, and that the film retains its pause control.

## Optional support

The installation section links to https://buymeacoffee.com/hndrk in a separate tab. Support is optional and does not unlock features. Amount selection and payment are handled on Buy Me a Coffee; no payment widget, tracking script or card fields are embedded here.

## Grok Build setup
The Grok tab targets Grok Build, not the consumer chat app. Its complete-folder prompt uses `~/.grok/skills/editorial-studio` and asks for discovery verification. See https://docs.x.ai/build/features/skills-plugins-marketplaces. This is documentation-based compatibility; no Grok runtime installation test has been performed. Tab transitions follow user selection and honor reduced motion.

## Additional setup choices
Cursor and Gemini CLI have equal-width tabs, the same entrance animation and user-controlled prompt transitions. All motion respects reduced motion. Setup prompts follow https://cursor.com/help/customization/skills and https://geminicli.com/docs/cli/skills/ and preserve existing installations. These integrations have not been runtime-tested. Gemini discovery uses `/skills list`, not an assumed `/editorial-studio` command.

## Public example downloads

`dist/examples/` in this GitHub checkout contains three 600px cover previews and the exact download manifest. The larger PDFs and reproduction ZIPs are in the separately managed Sites source checkout, intended for its `dist/examples/` directory; their links use the explicit `https://magazine.10myth.com/examples/` origin. **Deployment is pending after a hosting archive upload failure on 8 November 2026.** These new downloads are not yet live. They are not bundled into the skill/application release archive. After deployment, obtain a matching reviewed asset from that origin when reconstructing a full Site checkout, verify its SHA-256 against the manifest, and preserve the filename. Never substitute a private publication.

The three examples are in English and use Direction A / Field Notes. Their source packets pin the tested renderer commit and reproduce the reviewed page pixels. The six-page case study contains only one substantive feature plus fixed framing/credits; keep that limitation visible. The photographic example is a credited curation, not our original photography. A scoped user approval permits the clearly labelled screenshot and original artwork in the two product examples. This does not grant a general media reuse licence.
