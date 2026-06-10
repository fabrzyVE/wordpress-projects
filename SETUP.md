# Trueline Calculator Pages — Setup Guide

A reusable **LPagery template** that renders the "Recruiter Cost Calculator" landing
page (pixel-matched to the Figma in `/figma`) and bulk-generates one page per industry
from a CSV. Ships with 3 ready rows: **Construction**, **Accounting & Finance**, **Legal**.

Everything here was built **locally first** — nothing has been pushed to
`wearetrueline.com`. Follow the steps below to deploy when you're ready.

---

## What's in this repo

```
template/
  calculator-page.html        Source markup (standalone preview — open in a browser)
  calculator-page.css         All styling, scoped under .tl-calc
  calculator-page.js          FAQ accordion, stepper, clickbait-popup hook, HubSpot submit
  build.py                    Inlines CSS+JS -> dist/ (run after any edit)
  dist/
    calculator-page.wp.html   >>> PASTE THIS INTO WORDPRESS <<< (body-only block)
    calculator-page.combined.html   Full standalone HTML (preview/QA)
    preview-construction.html  Preview with Construction data + local images
cpt/
  calculator-pages-cptui.json CPT UI import file (preferred CPT setup)
  register-calculator-cpt.php Code fallback for registering the CPT
data/
  calculator-pages.csv        LPagery data source (3 industries)
SETUP.md                      This file
```

After editing any source file in `template/`, rebuild with:

```bash
cd template && python3 build.py
```

---

## Step 1 — Upload the images

Upload everything in `/images` to the WordPress Media Library. Easiest path:
create an `/wp-content/uploads/calculator/` folder (e.g. via FTP or the Media
Library) and put these files there:

- `hero-bg.png`
- `fit-section-bg.png`
- `hire-form-hubspot-bg.png`
- `construction-industry-card.png`
- `accounting-finance-industry-card.png`
- `legal-industry-card.png`
- `trueline-logo.png` *(footer logo — reuse the existing brand logo at
  `/wp-content/uploads/2024/04/Frame-2.png` if you prefer)*

> The `*.png:Zone.Identifier` files are Windows download-metadata junk — ignore/don't upload them.

## Step 2 — Point the template at your uploads URL

The template uses the token `__ASSET_BASE__` for every static image. Replace it
with your real uploads URL, then rebuild:

```bash
cd template
sed -i 's#__ASSET_BASE__#https://wearetrueline.com/wp-content/uploads/calculator#g' calculator-page.css calculator-page.html
python3 build.py
```

(There are 5 occurrences across the CSS + HTML.)

## Step 3 — Create the "Calculator Pages" CPT

> ⚠️ **DO NOT use CPT UI → Import for this on a site that already has CPT UI types.**
> CPT UI's import **replaces the entire post-type list**, which will de-register your
> existing types (`construction`, `accounting-finance`, etc.). See
> `cpt/RESTORE-CPTS.md` if that already happened. Use one of the non-destructive
> methods below instead.

**Recommended (no code, no overwrite) — add it via the CPT UI form:**
WP Admin → **CPT UI → Add/Edit Post Types → Add New Post Type**, and enter the values
from `cpt/calculator-pages-cptui.json` (slug `calculator`, label `Calculator Pages`,
Show in REST: true, REST base `calculator`, Has Archive `calculators`, Menu Icon
`dashicons-calculator`, Supports: Title/Editor/Featured Image/Excerpt/Custom
Fields/Page Attributes), then **Add Post Type**. This *appends* — it won't touch other types.

**Or (code, future-proof):** add `cpt/register-calculator-cpt.php` to a site-specific
plugin / child-theme `functions.php` — registers `calculator` outside CPT UI entirely.

The provided `cpt/calculator-pages-cptui.json` is a **reference for the field values**
(and is only safe to *import* as part of a combined JSON that already contains all your
existing types).

**Fallback (code):** if you'd rather register it in code, add
`cpt/register-calculator-cpt.php` to a site-specific plugin or a *Code Snippets*
entry. It's guarded so it won't double-register if CPT UI already did.

## Step 4 — Build the LPagery template page

1. Create a new **Calculator Pages** post (this is your *template*, not a final page).
2. Edit with the **plain WordPress editor**: add a **Custom HTML** block and paste
   the entire contents of `template/dist/calculator-page.wp.html`.
   *(If you prefer Elementor: add an **HTML widget** and paste the same block.)*
3. Publish/Save. Title it something obvious like `TEMPLATE — Calculator Page`.
4. WP Admin → **LPagery → Create Process** → choose this post as the template,
   and the CPT `Calculator Pages` as the output post type.

> The template uses single-curly LPagery placeholders (`{industry}`, `{hero_headline}`,
> etc.) which map 1:1 to the CSV column headers. CSS braces (`{ }`) are left untouched
> because LPagery only substitutes tokens that exactly match a column name.

## Step 5 — Wire the HubSpot form ("Ready to Hire?")

The "Ready to Hire?" form is a **native, pixel-matched form** that submits straight
into HubSpot via the Forms API. Open `template/calculator-page.js` and fill the
config block at the top:

```js
var HUBSPOT = {
  portalId: "YOUR_PORTAL_ID",   // HubSpot → Settings → Account Defaults (Hub ID)
  formGuid: "YOUR_FORM_GUID",   // the GUID from your form's embed/share code
  region:   "na1"               // "na1" (US) or "eu1"
};
```

Create a HubSpot form whose internal field names match the inputs:
`fullname`, `email`, `role_hiring_for`, `phone`, `message`, `industry_interest`.
Rebuild (`python3 build.py`) and re-paste the WP block. Until configured, the form
shows a friendly "not configured yet" message instead of failing silently.

## Step 6 — Wire the clickbait calculator popup (do later)

By design, the calculator inputs are **not** computed — the **Get My Custom Estimate**
and **Get a Custom Quote** buttons are lead-bait that should open a second form in a
popup. You have **Popup Maker** installed:

1. Create a popup in **Popup Maker** containing your real lead form.
2. Note its numeric **popup ID**.
3. Set `QUOTE_POPUP_ID` at the top of `calculator-page.js`, rebuild, re-paste.

Until set, those buttons gracefully scroll to the "Ready to Hire?" form.

## Step 7 — Generate the 3 pages

1. WP Admin → **LPagery → your process → Import data**.
2. Upload `data/calculator-pages.csv` (or paste it / connect a Google Sheet with the
   same columns).
3. Map columns: `title` → page title, `slug` → slug; the rest map to the matching
   placeholders automatically. Optionally map `meta_title` / `meta_description` to
   Yoast SEO fields.
4. **Generate**. You'll get three live Calculator Pages:
   - `/calculators/construction-recruiter-cost-calculator/`
   - `/calculators/accounting-finance-recruiter-cost-calculator/`
   - `/calculators/legal-recruiter-cost-calculator/`

To add more industries later, just add a CSV row — no template changes needed.

---

## Placeholder reference

| Placeholder              | Example (Construction)                                   |
|--------------------------|----------------------------------------------------------|
| `{industry}`             | Construction                                             |
| `{hero_headline}`        | How Much Does a Construction Recruiter Cost? 2026 …      |
| `{hero_subtext}`         | Industry standard for construction recruiter fees is …  |
| `{phone}`                | (800) 201-0906                                          |
| `{phone_link}`           | 8002010906                                              |
| `{typical_fee_pct}`      | 20-25%                                                  |
| `{time_to_fill}`         | 30-45 days                                              |
| `{fee_driver_industry}`  | Construction roles also factor certification…           |

`title`, `slug`, `meta_title`, `meta_description` are CSV columns consumed by
LPagery/Yoast rather than in-body placeholders.

---

## Notes / deliberate TODOs

- **Calculator math:** intentionally none — it's a lead-capture clickbait per spec.
  The fee tables/benchmarks shown are static industry data from the Figma.
- **Comparison + fee tables + FAQ** are identical across all industries (matches the
  Figma "hub" content). Only the hero, the "Typical Industry Standards" stats, and the
  Location fee-driver sentence change per industry.
- **HubSpot field names** must match what you create in HubSpot, or submissions 400.
- The `-hubspot` Figma suffix referred only to the "Ready to Hire?" section, which is
  the form wired to HubSpot here.
