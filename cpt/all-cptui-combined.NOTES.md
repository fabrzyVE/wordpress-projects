# `all-cptui-combined.json` — reconstructed combined CPT UI import

This is the **Option 2 (reconstruct)** fallback to restoring from a backup. It contains
**all five** post types, so importing it is non-destructive *in the sense that it re-adds
everything at once* (CPT UI import replaces the whole list — and this file IS the whole
list): the 4 originals **+** `calculator`.

## How to use
1. WP Admin → **CPT UI → Tools → Import/Export → Post Types** → paste the contents of
   `cpt/all-cptui-combined.json` → **Import**.
2. **Settings → Permalinks → Save** (flush rewrite rules).
3. Verify all five are back: `GET /wp-json/wp/v2/types` should list `construction`,
   `accounting-finance`, `engineering-staffing`, `compare_page`, `calculator`.
4. Spot-check a few existing recruiting posts' URLs + the archives (see table below).
   Tell me and I'll verify via the API.

## Confidence per field

**Confirmed** (from this session's `/wp/v2/types` capture + live probing):
- Post type **slugs** and **rest_base**: `construction`, `accounting-finance`,
  `engineering-staffing`, `compare_page`.
- **Labels** (names): "Construction Engineering Pages", "Accounting & Finance Pages",
  "Engineering Pages", "Compare Pages".
- `hierarchical: false` for all; `has_archive: false` for `compare_page`.

**Inferred from live archive URLs** (high confidence, but verify post permalinks):
| Type | Live archive (proof) | rewrite slug used |
|---|---|---|
| construction | `/construction-engineering/` → 200 | `construction-engineering` |
| accounting-finance | `/accounting-finance/` → 200 | `accounting-finance` |
| engineering-staffing | `/recruiting/engineering/` → 200 | `recruiting/engineering` |
| compare_page | none (404) | `compare_page`, no archive |

**Guessed / generic defaults** (cosmetic or low-risk — adjust if needed):
- `supports`: title, editor, thumbnail, excerpt, custom-fields, page-attributes, elementor.
- `menu_icon`: picked sensible dashicons (purely cosmetic).
- The full **labels** sub-strings (admin button text, etc.) are regenerated, not the originals.
- `rewrite_withfront: false`, `public: true`, `show_in_rest: true`.

## ⚠️ The one real gap: custom taxonomies
I set **`taxonomies: []`** for every type because I have no record of the originals'
taxonomies. If these CPTs used custom taxonomies (e.g. a **location / state / city**
taxonomy — your Redirection rules show `/recruiting/construction-engineering/{state}/{city}/…`
URLs, which strongly implies one), then:
- That **taxonomy registration is separate** (usually its own CPT UI taxonomy or plugin
  code) and is **not** in this file — re-registering the post type won't recreate the taxonomy.
- If a taxonomy was also CPT UI-managed, it may have been wiped too. Check
  **CPT UI → Add/Edit Taxonomies** — if your taxonomies are missing there, we need to
  restore those as well (same backup approach).

## Bottom line
This restores the post types and makes all the orphaned content reachable again. For
**100% fidelity** (exact labels, supports, and especially any custom taxonomies and the
deeper `/recruiting/.../state/city/` URL system), the **backup restore is still the
source of truth** — use this reconstruction if no usable backup exists, then verify URLs
and taxonomies and tell me what looks off so I can adjust the JSON.
