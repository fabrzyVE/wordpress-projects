---
name: webflow-cms-qc
description: QC that Backyard Care Webflow CMS collection items (Neighborhoods + Services) match implementation-sheet.xlsx exactly, row for row. Dumps items via the Webflow MCP, diffs each mapped field against the sheet, then loops fix→re-verify until every auto-checked field passes (MISMATCH=0) and every REVIEW field is signed off. Use before publishing drafts or after any content edit.
---

# Webflow CMS ⇄ Implementation-Sheet QC

Verify every Webflow CMS item matches its sheet row exactly, per field, and
**loop until it passes**. The sheet (`implementation-sheet.xlsx`) is the source
of truth for copy; the CMS must match it.

Two collections, on the LIVE prod site `65ec5afbb779bee7cbcbcbaa`:

| Collection | ID | Sheet tab | Rows |
|---|---|---|---|
| Neighborhoods | `6a443ba62619d74e3e333feb` | `Neighborhoods` | 29 |
| Services (Location) | `6a4436951dd6278db3977334` | `Services` | 14 |

Items are matched **by `name`** (case-insensitive), not by list order — the
Services sheet-row names differ from CMS item names in places, so name-matching
is required and unmatched rows are reported as `MISSING`.

## Hard rules (from CLAUDE.md)

- **Drafts only. Never publish.** Fix with `update_collection_items` (writes
  drafts); never call `publish_collection_items`.
- Touch only these two collections. Do not modify other pages/collections.

## Field buckets

The comparator (`qc_cms.py`) sorts every field into a bucket:

- **auto** — plain 1:1 or cleanly-extractable text. Compared after
  normalization; a diff is a **MISMATCH** and must be fixed. This is the
  pass/fail gate.
- **review** — packed/re-authored/derived fields that can't be byte-compared:
  Services overview **cards** and **`detail-N-answers`** RichText (SVG icons +
  reflowed HTML), neighborhood **`hero-accent`** (a substring of the heading),
  and **`nearby-areas`** (a geographic-order multi-reference). Listed as
  **REVIEW** — judge these semantically; they never auto-fail.
- **out of scope (template-static)** — sheet sections with no per-item CMS
  field: Testimonials, FAQ, How-It-Works steps, Closing-CTA body, Areas-We-Serve
  chips, Other Services, Blog, Footer. These live on the template, not the item,
  so the QC does not check them. (If the design changes to make them dynamic,
  add them to the field map in `qc_cms.py`.)

Full column→slug maps live in `qc_cms.py` (`NEIGHBORHOODS`, `SERVICES`).

## Normalization (what counts as "equal")

Applied to both sides before comparing: HTML entities unescaped; smart
quotes/dashes/nbsp unified; whitespace collapsed; RichText tags stripped for
text-only compare. Known sheet-only annotations are stripped so they are NOT
false mismatches:
- leading role tags on headings — `H1: …` → `…`
- trailing/compound field markers in packed cells — `Number : 01 Subheading: X
  Description: <text> CTA: Learn More` → the segment after `Description:` only.

## Workflow — run the loop

1. **Dump CMS items** via the Webflow MCP `data_cms_tool` →
   `list_collection_items` for both collections (`limit: 100`). Use labels that
   contain `nbhd` and `svc` so the splitter routes them:
   ```
   actions: [
     {label: "nbhd-all", list_collection_items: {collection_id: "6a443ba62619d74e3e333feb", request: {limit: 100}}},
     {label: "svc-all",  list_collection_items: {collection_id: "6a4436951dd6278db3977334", request: {limit: 100}}}
   ]
   ```
   The result is large and will be **persisted to a file** (the tool prints the
   path). Split it into `qc/neighborhoods.json` + `qc/services.json`:
   ```
   python3 .claude/skills/webflow-cms-qc/split_dump.py <persisted-result-file> --outdir qc
   ```

2. **Compare:**
   ```
   python3 .claude/skills/webflow-cms-qc/qc_cms.py \
     --sheet implementation-sheet.xlsx \
     --services qc/services.json --neighborhoods qc/neighborhoods.json \
     --out qc/mismatches.json
   ```
   Prints a per-item report + a summary line
   (`MATCH=… MISMATCH=… REVIEW=… MISSING=…`), writes actionable items to
   `qc/mismatches.json`, and **exits non-zero while any MISMATCH/MISSING
   remains** — use the exit code as the loop condition.

3. **Fix** every MISMATCH/MISSING. For each entry in `qc/mismatches.json`, the
   `sheet` value is the correct target; write it back with `update_collection_items`
   (keep `isDraft: true`), keyed by the item `id` from the dump:
   ```
   update_collection_items: {collection_id: "<id>", request: {items: [
     {id: "<itemId>", isDraft: true, fieldData: {"<slug>": "<sheet value>"}}
   ]}}
   ```
   A `MISSING` "no CMS item" means a sheet row has no draft item — create it
   (`create_collection_items`, `isDraft: true`) only if the build is meant to
   cover that row; otherwise flag to the user.

4. **Re-dump the changed collection(s)** (step 1) and **re-run** (step 2).
   Repeat until `MISMATCH=0` and `MISSING=0`. Cap at ~6 iterations; if a field
   won't converge, stop and report it to the user rather than looping forever.

5. **Judge REVIEW fields.** Once auto checks are clean, review the REVIEW
   entries in `qc/mismatches.json` against the sheet — for the Services
   `detail-N-answers` RichText and overview cards this is best delegated to a
   **subagent** (paste the sheet cell + the CMS value, ask whether the CMS
   faithfully conveys the sheet copy; icons/markup are expected extras). Only
   the copy must match; the injected SVG icons and reflowed HTML are intended.

**Pass criteria:** `MISMATCH=0`, `MISSING=0`, and every REVIEW field signed off.

## Notes

- `qc/` is a scratch working dir (add to `.gitignore` if not already); the JSON
  dumps regenerate each run.
- No Webflow API token in this repo, so the script never calls Webflow — all
  reads/writes go through the MCP `data_cms_tool` in the loop above.
- Validated 2026-07-03 against the completed build: `MISMATCH=0, MISSING=0`
  (706 auto fields), i.e. zero false positives.
