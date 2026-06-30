---
name: figma-qc
description: Pixel-perfect QC for the Arkview location pages — render a page to per-section screenshots and diff them against the Figma design PNGs in designs/. Use when building or revising a location page and you need to confirm it matches the design before pushing drafts.
---

# Figma QC — Arkview Location Pages

Verify a generated location page matches the Figma design pixel-for-pixel, section by section.

## Design ↔ section map

The `designs/` folder holds 13 PNGs. They map to the 11 page sections (12–13 are the
global Astra footer, NOT page content):

| Design | Section | Screenshot |
|---|---|---|
| 1.png  | Hero (navy, H1, sub, 3 CTAs, trust bar) | `01-hero` |
| 2.png  | Intro + 2×2 stat cards | `02-intro` |
| 3.png  | Levels of Care (4 program cards) | `03-levels` |
| 4.png  | Environment image mosaic | `04-env` |
| 5.png  | Clinical / Care Team (3 people) | `05-team` |
| 6.png  | Insurance (6×2 logos + CTA bar) | `06-insurance` |
| 7.png  | What to Expect (navy, 3 steps) | `07-expect` |
| 8.png  | Local Impact (text + 4 stat bars) | `08-impact` |
| 9.png  | FAQ accordion | `09-faq` |
| 10.png | Final CTA + contact form (navy) | `10-final` |
| 11.png | Nearby Areas (town grid + CTA bar) | `11-nearby` |
| 12/13  | Global footer — out of scope | — |

## Design tokens (sampled from the PNGs — must match)

- Navy sections / headings: `#0F1D3B`; heading ink `#0B1937`
- Gold CTA (Call Now): `#EAB308`  ·  Green accent (Verify/Send/badges): `#74D59B`
- Light section bg: `#F7F8F8`  ·  card border `#E7EAF0`
- Headings: **Poppins** (600/700)  ·  body: **Inter**
- Section vertical padding ≈ 84px; container max-width 1200px

## Workflow

1. Regenerate content + pages:
   `python3 build/parse_content.py && python3 build/generate.py`
2. Screenshot a page (per-section PNGs into `qc/<slug>/`):
   ```
   SCRATCH=<scratchpad>
   PW_PATH=$SCRATCH/node_modules/playwright \
   LD_LIBRARY_PATH=$SCRATCH/libs/extracted/usr/lib/x86_64-linux-gnu \
   node build/screenshot.js <slug> 1280
   ```
   (Chromium needs the local `libasound` shim in `LD_LIBRARY_PATH`.)
3. For each section, compare `qc/<slug>/NN-name.png` against the mapped `designs/N.png`.
   **Delegate this to a subagent** with fresh context — reading many full-res
   screenshots pollutes the main context and trips the 2000px multi-image limit.
4. Log diffs, fix in `build/styles.py` / `build/generate.py`, re-run, repeat until clean.

## What to check per section (pixel-perfect checklist)

- **Layout:** column structure, grid counts, alignment, ordering, spacing rhythm.
- **Type:** heading vs body font, weight, relative size, line-height, letter-spacing.
- **Color:** backgrounds, text, button fills, badge colors match the tokens above.
- **Components:** eyebrow pills, button styles (gold/green/navy/outline), card chrome
  (radius, border, top-accent bars), icon presence + color.
- **Content:** copy comes from the sheet (source of truth); never reintroduce the
  word patient/client/customer (brand rule) even if the design comp shows it.
- **States:** FAQ is a native `<details>` accordion; form fields styled per design 10.

## Known intentional deviations from the comps

- **Stat cards (design 2):** comp shows "20+/95%/4/24-7"; we use the sheet's approved
  stats (55,000 sq ft, 1-of-1-2 in PA, Accredited, In-network) because the comp copy
  uses "Patient Satisfaction" which violates the brand no-"patient" rule.
- **Local-impact bars (design 8):** percentages are illustrative (figma fallback — the
  sheet has no bar data); labeled as estimates in the source note.
- Placeholder hrefs (`#verify-insurance`, `#av-contact`, Learn More `#`) await real targets.
