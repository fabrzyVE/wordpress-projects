#!/usr/bin/env python3
"""
Backyard Care — Webflow CMS ⇄ implementation-sheet QC comparator.

Compares each Webflow collection item against its matching row in
implementation-sheet.xlsx and reports, per item + field:

  MATCH     auto check passed (normalized text is identical)
  MISMATCH  auto check failed  -> fix required, exit code 1
  REVIEW    field needs semantic/human judgement (compound RichText,
            derived values, ordering) -> listed, NOT auto-failed
  MISSING   item in sheet has no matching CMS item (or vice-versa)

The CMS side is NOT fetched here (no Webflow API token in this repo).
The caller (the QC skill) dumps items via the Webflow MCP
`list_collection_items` and saves them to the JSON files this script reads.

Usage:
  python3 qc_cms.py \
      --sheet implementation-sheet.xlsx \
      --services qc/services.json \
      --neighborhoods qc/neighborhoods.json \
      --out qc/mismatches.json

Any --services / --neighborhoods path that is omitted is skipped.
Exit code is 1 if there is >=1 MISMATCH or MISSING, else 0.
"""
import argparse
import html
import json
import re
import sys

import openpyxl

PHONE = "470-291-5029"


# ── text normalisation ──────────────────────────────────────────────────────
def norm(s, strip_tags=False):
    """Normalise for comparison: unescape entities, optionally strip HTML,
    unify smart quotes/dashes, collapse whitespace."""
    if s is None:
        return ""
    s = str(s)
    s = html.unescape(s)
    if strip_tags:
        s = re.sub(r"<[^>]+>", " ", s)
    trans = {
        "’": "'", "‘": "'", "′": "'",
        "“": '"', "”": '"',
        "–": "-", "—": "-", "−": "-",
        " ": " ", "…": "...",
    }
    for k, v in trans.items():
        s = s.replace(k, v)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ── compound-cell extractors ────────────────────────────────────────────────
# Compound sheet cells label their sub-values, e.g.
#   "Number : 01 Subheading: Mosquito Control Description: <text> CTA: Learn More"
# The CMS stores only some segments (here `service-N-desc` = the Description
# text, WITHOUT the trailing "CTA: Learn More"). `seg(label)` returns the text
# after `label:` up to the next known marker (or end of cell).
MARKERS = [
    "Number", "Subheading", "Paragraph", "Description", "CTA", "Icon", "Stars",
    "Testimonial", "question", "answer", "Button", "filename", "alt", "text",
    "H3", "li", "Tel",
]


def seg(label):
    def f(cell):
        cell = cell or ""
        m = re.search(re.escape(label) + r"\s*:\s*", cell, re.I)
        if not m:
            return cell
        rest = cell[m.end():]
        nxt = None
        for mk in MARKERS:
            mm = re.search(r"\b" + re.escape(mk) + r"\s*:", rest, re.I)
            if mm and (nxt is None or mm.start() < nxt):
                nxt = mm.start()
        return rest[:nxt] if nxt is not None else rest
    return f


IDENTITY = lambda c: c
# Strip a leading role annotation the sheet sometimes adds to a heading cell,
# e.g. "H1: Mosquito Control in Atlanta, GA" -> "Mosquito Control in Atlanta, GA".
NOLEAD = lambda c: re.sub(r"^\s*(H[1-6]|Heading)\s*:\s*", "", c or "", flags=re.I)


# ── field maps  (col index is 0-based into the sheet row) ───────────────────
# bucket: "auto"   -> normalized-exact comparison, contributes to pass/fail
#         "review" -> listed for human/agent judgement, never auto-fails
# strip_tags -> strip HTML from the CMS value before comparing (RichText)
NEIGHBORHOODS = [
    # (cms_slug,            col, extractor,                 bucket,   strip_tags)
    ("meta-title",           1, IDENTITY,                   "auto",  False),
    ("meta-description",     2, IDENTITY,                   "auto",  False),
    ("hero-heading",         3, IDENTITY,                   "auto",  False),
    ("hero-paragraph",       4, IDENTITY,                   "auto",  False),
    ("overview-heading",     8, IDENTITY,                   "auto",  False),
    ("overview-paragraph",   9, IDENTITY,                   "auto",  False),
    ("challenge-1-title",   12, seg("Subheading"),          "auto",  False),
    ("challenge-1-body",    12, seg("Paragraph"),           "auto",  False),
    ("challenge-2-title",   13, seg("Subheading"),          "auto",  False),
    ("challenge-2-body",    13, seg("Paragraph"),           "auto",  False),
    ("challenge-3-title",   14, seg("Subheading"),          "auto",  False),
    ("challenge-3-body",    14, seg("Paragraph"),           "auto",  False),
    ("how-we-care-heading", 15, IDENTITY,                   "auto",  False),
    ("service-1-desc",      16, seg("Description"),         "auto",  False),
    ("service-2-desc",      17, seg("Description"),         "auto",  False),
    ("service-3-desc",      18, seg("Description"),         "auto",  False),
    ("service-4-desc",      19, seg("Description"),         "auto",  False),
    ("inline-cta-heading",  20, IDENTITY,                   "auto",  False),
    ("why-byc-heading",     22, IDENTITY,                   "auto",  False),
    ("close-accent",        39, IDENTITY,                   "auto",  False),
    # derived / non-text — judged, not auto-compared:
    ("hero-accent",          3, IDENTITY,                   "review", False),
    ("nearby-areas",        45, IDENTITY,                   "review", False),
]

SERVICES = [
    ("meta-title",           1, IDENTITY,                   "auto",  False),
    ("meta-description",     2, IDENTITY,                   "auto",  False),
    ("hero-heading",         3, NOLEAD,                     "auto",  False),
    ("hero-paragraph",       4, IDENTITY,                   "auto",  False),
    ("inline-cta-heading",  32, IDENTITY,                   "auto",  False),
    # Overview cards + Service-Detail RichText are packed/re-authored from the
    # sheet + Figma; compare semantically, do not auto-fail on whitespace/SVG:
    ("card-1-label",         9, IDENTITY,                   "review", False),
    ("card-1-title",         9, IDENTITY,                   "review", False),
    ("card-1-description",   9, IDENTITY,                   "review", False),
    ("card-2-label",        10, IDENTITY,                   "review", False),
    ("card-2-description",  10, IDENTITY,                   "review", False),
    ("card-3-label",        11, IDENTITY,                   "review", False),
    ("card-3-description",  11, IDENTITY,                   "review", False),
    ("detail-1-heading",    13, IDENTITY,                   "review", False),
    ("detail-1-answers",    14, IDENTITY,                   "review", True),
    ("detail-2-heading",    19, IDENTITY,                   "review", False),
    ("detail-2-answers",    20, IDENTITY,                   "review", True),
    ("detail-3-heading",    25, IDENTITY,                   "review", False),
    ("detail-3-answers",    26, IDENTITY,                   "review", True),
]

# fields whose CMS value is a fixed constant, not sourced from a sheet column
CONSTANTS = {"phone": PHONE}


# ── sheet loader ────────────────────────────────────────────────────────────
def load_sheet(path, sheet_name):
    """Return {normalized_name: (display_name, [cell values by col idx])}.
    Row 0 = section groups, row 1 = field labels, row 2+ = data (col0 = name).
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    out = {}
    for r in rows[2:]:
        if not r or all(c is None for c in r):
            continue
        name = r[0]
        if name is None:
            continue
        out[norm(name).lower()] = (str(name), list(r))
    return out


# ── cms loader (accepts raw MCP result, {items:[...]}, or [...]) ─────────────
def load_cms(path):
    with open(path) as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        if "result" in data and isinstance(data["result"], dict):
            data = data["result"]
        data = data.get("items", data)
    if not isinstance(data, list):
        raise SystemExit(f"{path}: could not find an items array")
    items = {}
    for it in data:
        fd = it.get("fieldData", it)
        name = fd.get("name")
        if name is None:
            continue
        items[norm(name).lower()] = fd
    return items


def cms_text(val, strip_tags):
    """Extract a comparable string from a CMS field value."""
    if val is None:
        return ""
    if isinstance(val, dict):          # image/file/etc — not text-compared
        return val.get("url", "") or val.get("alt", "")
    if isinstance(val, list):
        return f"[{len(val)} refs]"
    return norm(val, strip_tags=strip_tags)


# ── comparison ──────────────────────────────────────────────────────────────
def compare(collection, sheet, cms, fieldmap):
    results = []
    matched = set()
    for key, (disp, row) in sorted(sheet.items()):
        fd = cms.get(key)
        if fd is None:
            results.append(dict(collection=collection, name=disp, slug="",
                                field="(item)", status="MISSING",
                                detail="no CMS item with this name"))
            continue
        matched.add(key)
        for slug, col, extract, bucket, strip_tags in fieldmap:
            raw = row[col] if col < len(row) else None
            expected = norm(extract(str(raw) if raw is not None else ""))
            actual = cms_text(fd.get(slug), strip_tags)
            ok = expected == actual
            if bucket == "auto":
                status = "MATCH" if ok else "MISMATCH"
            else:
                status = "MATCH" if ok else "REVIEW"
            results.append(dict(
                collection=collection, name=disp, slug=fd.get("slug", ""),
                field=slug, status=status,
                sheet=expected, cms=actual,
            ))
        # constants
        for slug, const in CONSTANTS.items():
            if slug in fd:
                actual = cms_text(fd.get(slug), False)
                status = "MATCH" if actual == norm(const) else "MISMATCH"
                results.append(dict(collection=collection, name=disp,
                                    slug=fd.get("slug", ""), field=slug,
                                    status=status, sheet=const, cms=actual))
    # CMS items with no sheet row
    for key, fd in cms.items():
        if key not in matched:
            results.append(dict(collection=collection, name=fd.get("name", key),
                                slug=fd.get("slug", ""), field="(item)",
                                status="MISSING", detail="no sheet row"))
    return results


# ── reporting ───────────────────────────────────────────────────────────────
def report(results):
    order = {"MISMATCH": 0, "MISSING": 1, "REVIEW": 2, "MATCH": 3}
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print("=" * 72)
    print("Webflow CMS ⇄ implementation-sheet QC")
    print("=" * 72)
    by_item = {}
    for r in results:
        by_item.setdefault((r["collection"], r["name"]), []).append(r)

    for (coll, name), rs in sorted(by_item.items()):
        bad = [r for r in rs if r["status"] in ("MISMATCH", "MISSING")]
        rev = [r for r in rs if r["status"] == "REVIEW"]
        if not bad and not rev:
            print(f"  ✓ [{coll}] {name}  ({len(rs)} fields OK)")
            continue
        print(f"  ✗ [{coll}] {name}")
        for r in bad:
            print(f"      MISMATCH {r['field']}")
            if "sheet" in r:
                print(f"        sheet: {r['sheet'][:120]!r}")
                print(f"        cms  : {r['cms'][:120]!r}")
            elif "detail" in r:
                print(f"        {r['detail']}")
        for r in rev:
            print(f"      REVIEW   {r['field']}  (judge semantically)")

    print("-" * 72)
    print("  " + "  ".join(f"{k}={counts.get(k,0)}" for k in
          ("MATCH", "MISMATCH", "REVIEW", "MISSING")))
    print("=" * 72)
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default="implementation-sheet.xlsx")
    ap.add_argument("--services")
    ap.add_argument("--neighborhoods")
    ap.add_argument("--out", default="qc/mismatches.json")
    args = ap.parse_args()

    results = []
    if args.neighborhoods:
        sheet = load_sheet(args.sheet, "Neighborhoods")
        cms = load_cms(args.neighborhoods)
        results += compare("neighborhoods", sheet, cms, NEIGHBORHOODS)
    if args.services:
        sheet = load_sheet(args.sheet, "Services")
        cms = load_cms(args.services)
        results += compare("services", sheet, cms, SERVICES)

    if not results:
        print("Nothing compared — pass --services and/or --neighborhoods.")
        return 2

    counts = report(results)

    actionable = [r for r in results
                  if r["status"] in ("MISMATCH", "MISSING", "REVIEW")]
    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(actionable, fh, indent=2)
    print(f"\nActionable items -> {args.out}  ({len(actionable)})")

    return 1 if (counts.get("MISMATCH") or counts.get("MISSING")) else 0


if __name__ == "__main__":
    sys.exit(main())
