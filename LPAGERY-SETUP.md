# LPagery Setup — generate Calculator Pages from a CSV

This wires the calculator template into LPagery so you can bulk-generate
`calculator` posts at `/calculators/{slug}/` and add more later by re-running with
an updated CSV. Data source: **CSV upload** · Assets: **inline in the template**.

## Already done (by me, via REST)
- ✅ `calculator` CPT registered (archive `/calculators/`).
- ✅ **LPagery template post created** — a draft `calculator` post holding the raw,
  *un-substituted* template (with `{placeholders}` and inline CSS/JS intact):
  - **Template post ID: `109730`** — "TEMPLATE — Calculator Page (LPagery · do not publish)"
  - Edit: `https://wearetrueline.com/wp-admin/post.php?post=109730&action=edit`
  - **Leave it as a draft. Never publish it** (it's the source LPagery clones.)
- ✅ Data file ready: `data/calculator-pages.csv` (3 rows: Construction, Accounting & Finance, Legal).

## Step 1 — Open LPagery → create a process
WP Admin → **LPagery → Create / New Process**.
- **Template / source page:** select **TEMPLATE — Calculator Page** (post 109730).
- **Target post type:** **Calculator Pages** (`calculator`).
- **Status of generated pages:** **Draft** (review before publishing).

## Step 2 — Upload the data
Choose **CSV / file upload** and upload `data/calculator-pages.csv`.
(LPagery reads the header row as the available placeholder columns.)

## Step 3 — Map columns
LPagery auto-matches columns to `{tokens}` by name. Confirm this mapping:

| CSV column | Maps to | Notes |
|---|---|---|
| `title` | **Post title** | the page's title |
| `slug` | **Post slug / URL** | → `/calculators/<slug>/` |
| `industry` | `{industry}` | hero crumb, hero, "What Drives Your Fee", form |
| `hero_headline` | `{hero_headline}` | H1 |
| `hero_subtext` | `{hero_subtext}` | hero paragraph |
| `phone` | `{phone}` | display phone |
| `phone_link` | `{phone_link}` | `tel:` digits |
| `fee_driver_industry` | `{fee_driver_industry}` | Location-card industry sentence |
| `meta_title` | Yoast SEO title | optional (map if LPagery shows Yoast fields) |
| `meta_description` | Yoast meta description | optional |
| `typical_fee_pct`, `time_to_fill` | — | **leave unmapped** (Typical Industry Standards is now hardcoded 20-30% / 30-45 days / 60 Days per the design) |

## Step 4 — TEST ONE before bulk
Generate **just the first row (Construction)** first, then open the generated draft and
confirm:
- All `{placeholders}` are filled (no literal `{industry}` left anywhere).
- The inline CSS/JS survived — the page is styled and the FAQ accordion works.
  *(LPagery only replaces exact mapped tokens, so the CSS `{ }` braces are untouched —
  but verify once to be safe.)*

If the one page looks right, generate the remaining rows.

## Step 5 — Review & publish
You'll get 3 draft `calculator` posts:
- `/calculators/construction-recruiter-cost-calculator/`
- `/calculators/accounting-finance-recruiter-cost-calculator/`
- `/calculators/legal-recruiter-cost-calculator/`

Review each, then publish.

## Step 6 — Retire the 3 manual draft Pages
The earlier hand-made drafts are now superseded by the LPagery-generated CPT posts.
Once you're happy with the generated versions, tell me and I'll **delete pages
109716 / 109717 / 109718** (or you can trash them in Pages). They're drafts, so nothing
public is affected.

---

## Adding more industries later
1. Add a row to `data/calculator-pages.csv` (or your LPagery data) with all the columns above.
2. Re-run the LPagery process (it can update existing + create new via the connected set).

⚠️ **Two things that are static and won't auto-update per row:**
- The **"Calculators by Industry"** grid is hardcoded to the 3 cards
  (Construction / Accounting & Finance / Legal). A new industry won't appear there
  until we add a card (+ its industry-card image). Tell me and I'll add it to the template.
- The **industry dropdown** in the calculator form lists a fixed set of verticals.

## If you edit the design later
Edit `template/calculator-page.{html,css,js}` → `python3 build.py` → update the **template
post 109730** with the new `dist/calculator-page.wp.html`, then re-run LPagery to push the
change to all generated pages (LPagery can update its connected set). I can do the post-109730
update via REST whenever you want.
