# Editorial Studio — working rules for Codex

Use `.agents/skills/editorial-studio/SKILL.md` for all photo-led magazines and onepagers developed here.

## Do not skip creative discovery

1. Ask what publication/format is needed and for what subject, purpose and audience.
2. Ask the desired style.
3. Ask for a design inspiration URL or another sample.
4. Present two materially different directions and obtain explicit selection **before** building pages or sourcing imagery.
5. If the user already answered an intake question, retain it; don't ask again.

## Procedural editorial roles

Creative strategist -> Research editor -> Universal Photo Researcher -> Art director -> Quality reviewer -> Publisher. These are process roles, not a claim that autonomous background agents are operating. Work/Browser and other connected tools may be used as permitted, but avoid unsupported automation.

## Editorial invariants

- Subject may be a person, product, place, building, artwork, hotel, property or business. Do not make restaurant-specific assumptions.
- No arbitrary photos, fake identities, unlicensed third-party assets or hotlinked image placeholders.
- Search results are candidate sources only. A direct HTTPS image is only imported after explicit selection, and starts unapproved.
- For licensed/permission images, record evidence. For public editions, never use `private_reference` images.
- Never bypass quality checks or mark the PDF finished without real, local, approved images. Never ship synthetic test images as authentic subjects.
- Verify current factual claims with sources and dates; don't invent hours, prices, details, or image licensing.
- Keep output a self-contained PDF, then inspect representative rendered pages. Tests use synthetic images explicitly labelled as test fixtures.
- Do not claim Windows laptop deployment or external connections are tested unless actually verified.

## Commands

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m unittest discover -s tests -v
python studio.py serve
```
