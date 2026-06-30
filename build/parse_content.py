#!/usr/bin/env python3
"""Parse the Core worksheet of implementation_sheet.xlsx into clean structured
JSON, one record per location page. Source of truth for copy = the sheet."""
import openpyxl, json, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "implementation_sheet.xlsx")

# Program length shown on the card badge = the trailing duration token (e.g.
# "3–4 weeks"), NOT an in-sentence cadence like "5 days/week".
DUR_RE = re.compile(r'([0-9][0-9–‐\-\s]*\s*(?:days|weeks))\s*\.?\s*$', re.I)

def split_pipes(s):
    return [p.strip() for p in s.split('|') if p.strip()]

def strip_h2(s):
    return re.sub(r'^H2:\s*', '', s.strip())

def parse_levels(raw):
    lines = raw.split('\n', 1)
    title = strip_h2(lines[0])
    body = lines[1] if len(lines) > 1 else ''
    cards = []
    for chunk in split_pipes(body):
        if ' — ' in chunk or ' - ' in chunk:
            name, rest = re.split(r'\s[—-]\s', chunk, maxsplit=1)
        else:
            name, rest = chunk, ''
        name = name.strip().rstrip('.')
        dur = ''
        m = DUR_RE.search(rest)
        if m:
            dur = m.group(1).strip()
            rest = rest[:m.start()].strip()
        rest = rest.strip().rstrip('.').strip()
        if rest:
            rest = rest + '.'
        cards.append({"name": name, "desc": rest, "duration": dur})
    return {"title": title, "cards": cards}

def badge_for(name):
    n = name.lower()
    if 'detox' in n: return ("MEDICAL", "navy")
    if 'residential' in n: return ("RESIDENTIAL", "slate")
    if 'partial' in n or 'php' in n: return ("PHP", "green")
    if 'intensive' in n or 'iop' in n: return ("IOP", "navy")
    if 'mat' in n or 'medication' in n: return ("MAT", "slate")
    if 'virtual' in n: return ("VIRTUAL", "green")
    return ("CARE", "navy")

def parse_team(raw):
    out = []
    for chunk in split_pipes(raw):
        name, rest = re.split(r'\s—\s', chunk, maxsplit=1)
        title, desc = rest.split(':', 1)
        out.append({"name": name.strip(), "title": title.strip(), "desc": desc.strip()})
    return out

def parse_expect(raw):
    out = []
    for line in raw.split('\n'):
        line = line.strip()
        if not line: continue
        m = re.match(r'^(\d{2})\s*[··]\s*(.+)$', line)
        if not m: continue
        num, rest = m.group(1), m.group(2)
        if ' — ' in rest:
            title, desc = rest.split(' — ', 1)
        else:
            title, desc = rest, ''
        out.append({"num": num, "title": title.strip(), "desc": desc.strip()})
    return out

def parse_faqs(raw):
    out = []
    cur = None
    for line in raw.split('\n'):
        s = line.strip()
        if not s: continue
        if s.startswith('### '):
            if cur: out.append(cur)
            cur = {"q": s[4:].strip(), "a": ""}
        elif cur is not None:
            cur["a"] = (cur["a"] + ' ' + s).strip()
    if cur: out.append(cur)
    return out

def parse_insurance(raw):
    m = re.search(r'\[Logos:\s*(.+?)\]', raw)
    logos = []
    if m:
        logos = [x.strip() for x in re.split(r'[··]', m.group(1)) if x.strip()]
    body = re.split(r'\s*\[Logos:', raw)[0].strip()
    return {"body": body, "logos": logos}

def parse_environment(raw):
    s = strip_h2(raw)
    if ' — ' in s:
        title, sub = s.split(' — ', 1)
    else:
        title, sub = s, ''
    return {"title": title.strip(), "sub": sub.strip()}

def parse_final_cta(raw):
    lines = raw.split('\n', 1)
    title = strip_h2(lines[0])
    sub = lines[1].strip() if len(lines) > 1 else ''
    sub = re.sub(r'\[[^\]]*\]', '', sub)
    sub = re.sub(r'\([^)]*\)', '', sub).strip()
    return {"title": title, "sub": sub}

def split_dots(s):
    s = re.sub(r'\([^)]*\)', '', s)
    return [x.strip() for x in re.split(r'[··]', s) if x.strip()]

def parse_stat_cards(raw):
    # Constant across pages; render faithful number+label cards from sheet phrases.
    return [
        {"big": "55,000 sq ft", "label": "All services under one roof"},
        {"big": "1 of 1–2 in PA", "label": "Separate facilities for mental health & addiction"},
        {"big": "Accredited", "label": "By The Joint Commission"},
        {"big": "In-network", "label": "With most major insurers"},
    ]

def parse_row(ws, headers, r, kind):
    """Build one page record from row r. Shared by the Core (location) and Areas
    sheets; Areas lacks Address/Phone but adds Nearest Facility + Distance, so all
    sheet-specific lookups use rec.get(...) with a blank default."""
    key = ws.cell(row=r, column=1).value
    if key in (None, ""):
        return None
    rec = {}
    for col, h in headers.items():
        v = ws[f"{col}{r}"].value
        rec[h] = str(v).strip() if v not in (None, "") else ""
    p = {
        "kind": kind,
        "key": str(key).strip(),
        "county": rec.get("County", ""),
        "slug": rec["Slug"].strip('/').split('/')[-1] if rec.get("Slug") else "",
        "slug_full": rec.get("Slug", ""),
        "address": rec.get("Address", ""),
        "phone": rec.get("Phone", ""),
        "nearest_facility": rec.get("Nearest Facility", ""),
        "distance_mi": rec.get("Distance (mi)", ""),
        "distance_min": rec.get("Distance (min)", ""),
        "programs": rec.get("Programs", ""),
        "title_tag": rec.get("Title Tag", ""),
        "meta_description": rec.get("Meta Description", ""),
        "h1": rec.get("H1", ""),
        "hero_sub": rec.get("Hero Subheadline", ""),
        "trust_bar": split_dots(rec.get("Trust Bar", "")),
        "intro": rec.get("Intro", ""),
        "stat_cards": parse_stat_cards(rec.get("Stat Cards", "")),
        "levels": parse_levels(rec.get("Levels of Care", "")),
        "environment": parse_environment(rec.get("Environment", "")),
        "image_grid": [re.sub(r'\([^)]*\)', '', x).strip() for x in split_pipes(rec.get("Image Grid", ""))],
        "team": parse_team(rec.get("Clinical Team", "")),
        "insurance": parse_insurance(rec.get("Insurance", "")),
        "expect": parse_expect(rec.get("What to Expect", "")),
        "local_impact": rec.get("Local Impact", ""),
        "faqs": parse_faqs(rec.get("FAQs", "")),
        "final_cta": parse_final_cta(rec.get("Final CTA", "")),
        "nearby": split_dots(rec.get("Nearby Areas", "")),
    }
    for c in p["levels"]["cards"]:
        b, color = badge_for(c["name"])
        c["badge"], c["badge_color"] = b, color
    return p

def parse_sheet(wb, sheet, kind, row_start, row_end):
    ws = wb[sheet]
    headers = {c.column_letter: str(c.value).strip() for c in ws[2] if c.value not in (None, "")}
    pages = []
    for r in range(row_start, row_end + 1):
        p = parse_row(ws, headers, r, kind)
        if p:
            pages.append(p)
    return pages

def main():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    here = os.path.dirname(os.path.abspath(__file__))
    # Core → content.json (4 location pages, rows 3–6); Areas → areas.json (rows 3–50)
    for sheet, kind, rows, fname in [
        ("Core", "location", (3, 6), "content.json"),
        ("Areas", "area", (3, 50), "areas.json"),
    ]:
        pages = parse_sheet(wb, sheet, kind, *rows)
        out = os.path.join(here, fname)
        with open(out, "w") as f:
            json.dump(pages, f, indent=2, ensure_ascii=False)
        print("wrote", out, "-", len(pages), kind, "pages")

if __name__ == "__main__":
    main()
