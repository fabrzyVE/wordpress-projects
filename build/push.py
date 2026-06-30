#!/usr/bin/env python3
"""Push the generated Arkview location pages to arkviewbh.com as DRAFTS.

Steps: upload photo assets to the media library -> substitute {{IMG:file}} tokens
with the uploaded URLs -> create a draft "Locations" parent -> create/update each
page as a draft child -> verify the inline <style> survived WP sanitization.

Idempotent: media + pages are matched by slug and updated in place on re-runs.
State is written to build/wp_state.json.
"""
import os, re, json, base64, mimetypes, urllib.request, urllib.error, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
PAGES = os.path.join(ROOT, "pages")
STATE = os.path.join(ROOT, "build", "wp_state.json")
UA = "Mozilla/5.0 Chrome/124"

PHOTOS = ["hero-bg.png", "wedding-reception.png", "group-therapy.png", "common-areas.png",
          "admissions-office.png", "individual-therapy.png", "zach-whipperman.png",
          "Kimberly-Lindsey 1.png", "David-Root 1.png"]

def env():
    e = {}
    for line in open(os.path.join(ROOT, ".env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            e[k] = v.strip().strip('"')
    return e

E = env()
SITE = E["WORDPRESS_SITE"].rstrip("/") + "/"
AUTH = "Basic " + base64.b64encode(f'{E["WORDPRESS_USER"]}:{E["WORDPRESS_TOKEN"]}'.encode()).decode()

def req(method, path, data=None, headers=None, raw=False):
    url = path if path.startswith("http") else SITE + "wp-json/" + path.lstrip("/")
    h = {"Authorization": AUTH, "User-Agent": UA}
    if headers:
        h.update(headers)
    body = None
    if data is not None and not raw:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    elif raw:
        body = data
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as ex:
        try:
            return ex.code, json.loads(ex.read().decode())
        except Exception:
            return ex.code, {"error": str(ex)}

def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"media": {}, "parent": None, "pages": {}}

def save_state(s):
    json.dump(s, open(STATE, "w"), indent=2)

def find_page_by_slug(slug):
    st, d = req("GET", f"wp/v2/pages?slug={slug}&status=any&_fields=id,slug")
    if isinstance(d, list) and d:
        return d[0]["id"]
    return None

def upload_media(state):
    print("== media ==")
    for fn in PHOTOS:
        if fn in state["media"]:
            print(f"  skip (cached) {fn}")
            continue
        path = os.path.join(ASSETS, fn)
        data = open(path, "rb").read()
        ctype = mimetypes.guess_type(fn)[0] or "image/png"
        safe = re.sub(r"[^A-Za-z0-9.\-]+", "-", fn)
        st, d = req("POST", "wp/v2/media", data=data, raw=True, headers={
            "Content-Type": ctype,
            "Content-Disposition": f'attachment; filename="{safe}"',
        })
        if st in (200, 201):
            state["media"][fn] = {"id": d["id"], "url": d["source_url"]}
            print(f"  uploaded {fn} -> id {d['id']}")
        else:
            print(f"  FAIL {fn}: {st} {d.get('code') or d}")
            sys.exit(1)
        save_state(state)

def substitute(content, media):
    def rep(m):
        fn = m.group(1)
        return media[fn]["url"] if fn in media else m.group(0)
    return re.sub(r"\{\{IMG:([^}]+)\}\}", rep, content)

def wp_safe(content):
    # collapse newlines so wpautop has no blank lines to wrap into <p>/<br>
    return re.sub(r"[ \t]*\n[ \t]*", " ", content).strip()

def ensure_parent(state, title, slug, state_key):
    """Idempotently create/find a draft hub page that owns the /<slug>/* URL path."""
    if state.get(state_key):
        return state[state_key]
    pid = find_page_by_slug(slug)
    payload = {"title": title, "slug": slug, "status": "draft",
               "content": f"<!-- Arkview {slug} hub — placeholder parent for /{slug}/* URLs -->"}
    if pid:
        st, d = req("POST", f"wp/v2/pages/{pid}", payload)
    else:
        st, d = req("POST", "wp/v2/pages", payload)
    if st in (200, 201):
        state[state_key] = d["id"]
        save_state(state)
        print(f"== parent '{title}' -> id {d['id']} (draft) ==")
        return d["id"]
    print(f"  parent '{title}' FAIL: {st} {d}")
    sys.exit(1)

def load_records():
    """All page records (locations + areas) keyed by slug — index entries are matched
    by slug since key is not unique across the two sheets in general."""
    recs = json.load(open(os.path.join(ROOT, "build", "content.json")))
    apath = os.path.join(ROOT, "build", "areas.json")
    if os.path.exists(apath):
        recs += json.load(open(apath))
    return {p["slug"]: p for p in recs}

def push_pages(state, parents):
    index = json.load(open(os.path.join(PAGES, "index.json")))
    recs = load_records()
    print("== pages ==")
    for item in index:
        slug = item["slug"]
        cp = recs[slug]
        parent_id = parents[item.get("kind", "location")]
        content = open(os.path.join(PAGES, f"{slug}.content.html")).read()
        content = wp_safe(substitute(content, state["media"]))
        payload = {
            "title": cp["h1"],
            "slug": slug,
            "status": "draft",
            "parent": parent_id,
            "content": content,
            "excerpt": cp["meta_description"],
            # Astra per-page layout: full-width builder template, no sidebar, no theme title
            "meta": {
                "site-content-layout": "page-builder",
                "site-sidebar-layout": "no-sidebar",
                "site-post-title": "disabled",
            },
        }
        pid = state["pages"].get(slug) or find_page_by_slug(slug)
        if pid:
            st, d = req("POST", f"wp/v2/pages/{pid}", payload)
        else:
            st, d = req("POST", "wp/v2/pages", payload)
        if st not in (200, 201):
            print(f"  FAIL {slug}: {st} {d.get('code') or d}")
            continue
        state["pages"][slug] = d["id"]
        save_state(state)
        # verify <style> survived
        st2, d2 = req("GET", f"wp/v2/pages/{d['id']}?context=edit&_fields=content,link")
        raw = d2.get("content", {}).get("raw", "") if isinstance(d2, dict) else ""
        has_style = "<style>" in raw or "av-loc" in raw
        style_kept = "<style>" in raw
        flags = "" if item.get("hold") != True else "  [HOLD/coming-soon]"
        print(f"  {'OK' if has_style else 'WARN'} {slug} -> id {d['id']} | style_block={'yes' if style_kept else 'STRIPPED'} | len={len(raw)}{flags}")
        print(f"       edit: {SITE}wp-admin/post.php?post={d['id']}&action=edit")

def set_seo(state):
    """Push the sheet's Title Tag + Meta Description into Rank Math via its own
    REST route (the meta keys are not registered on the generic wp/v2 meta field)."""
    recs = load_records()
    index = json.load(open(os.path.join(PAGES, "index.json")))
    print("== SEO (Rank Math) ==")
    for item in index:
        pid = state["pages"].get(item["slug"])
        if not pid:
            continue
        cp = recs[item["slug"]]
        st, d = req("POST", "rankmath/v1/updateMeta", data={
            "objectID": pid, "objectType": "post",
            "meta": {
                "rank_math_title": cp["title_tag"],
                "rank_math_description": cp["meta_description"],
            },
        })
        ok = st == 200 and not (isinstance(d, dict) and d.get("code"))
        print(f"  {'OK' if ok else 'FAIL'} {item['slug']} -> title/desc set ({st})")

def main():
    state = load_state()
    upload_media(state)
    parents = {
        "location": ensure_parent(state, "Locations", "locations", "parent"),
        "area": ensure_parent(state, "Areas", "areas", "areas_parent"),
    }
    push_pages(state, parents)
    set_seo(state)
    print("\nState saved to build/wp_state.json")

if __name__ == "__main__":
    main()
