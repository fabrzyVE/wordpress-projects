#!/usr/bin/env python3
"""Generate Arkview location pages from build/content.json.

Outputs per page (slug):
  pages/<slug>.html          standalone (for QC screenshots; assets via ../assets)
  pages/<slug>.content.html  inner content for WordPress (assets via {{IMG:file}} tokens)
"""
import json, os, re, html, sys
from icons import icon, arrow, chevron
from styles import CSS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
PAGES = os.path.join(ROOT, "pages")
CANONICAL_PHONE = "(717) 744-0756"
URL_VERIFY = "https://arkviewbh.com/insurance-verification/"
URL_CONTACT = "https://arkviewbh.com/contact/"
URL_STAFF = "https://arkviewbh.com/about/staff/"
URL_LEARN = "https://arkviewbh.com/contact/"

IMG_GRID_FILES = {
    "Welcoming Reception": "wedding-reception.png",
    "Group Therapy Lounge": "group-therapy.png",
    "Common Areas": "common-areas.png",
    "Admissions Office": "admissions-office.png",
    "Individual Therapy Rooms": "individual-therapy.png",
}
TEAM_FILES = {
    "Zach Whipperman": "zach-whipperman.png",
    "Kimberly Lindsey": "Kimberly-Lindsey 1.png",
    "David Root": "David-Root 1.png",
}
HERO_FILE = "hero-bg.png"
# Local-impact stat bars are illustrative (figma fallback — not in content sheet)
IMPACT_BARS = [
    ("Alcohol Use Disorder", 82, "% with primary alcohol diagnosis"),
    ("Opioid Use Disorder", 65, "% of PA admissions involve opioids"),
    ("Co-occurring Mental Health", 58, "% with dual diagnosis needs"),
    ("Stimulant Use (Meth)", 31, "% increase in PA over 3 years"),
]

ORDER_COLORS = ["navy", "slate", "green", "navy", "slate", "green"]

def card_fallback(name):
    """Fill in desc + duration for the sparse referral cards (York/PA) so every
    program card has a complete set of fields. Facts are drawn from the sheet."""
    n = name.lower()
    if "detox" in n or "residential" in n:
        return {"name": "Detox & Residential",
                "desc": "Medically supervised detox and live-in residential treatment, available at our Mechanicsburg campus.",
                "duration": "At Mechanicsburg"}
    if "virtual" in n:
        return {"name": "Virtual IOP",
                "desc": "The same intensive outpatient program delivered online, available statewide across Pennsylvania.",
                "duration": "Statewide"}
    if "medication" in n or "mat" in n:
        return {"name": "Medication-Assisted Treatment",
                "desc": "FDA-approved medication combined with counseling to support recovery and reduce cravings.",
                "duration": "Ongoing"}
    return {"name": name, "desc": "Evidence-based care tailored to your needs. Speak with our team for details.",
            "duration": "Varies"}

def e(s): return html.escape(s or "", quote=True)
def tel(phone):
    d = re.sub(r"\D", "", phone or "")
    return "tel:+1" + d if d else "tel:+17177440756"

class Mode:
    def __init__(self, standalone):
        self.standalone = standalone
    def img(self, fname):
        return f"../assets/{fname}" if self.standalone else f"{{{{IMG:{fname}}}}}"

# ---------- shared button rows ----------
def cta_row(p, theme):
    call = tel(CANONICAL_PHONE)
    if theme == "hero":
        call_cls, verify, contact = "av-btn-gold", "av-btn-navy", "av-btn-out-light"
    elif theme == "dark":            # admissions process (navy section)
        call_cls, verify, contact = "av-btn-gold-black", "av-btn-navy2", "av-btn-white"
    else:                             # light sections (serving, levels)
        call_cls, verify, contact = "av-btn-gold", "av-btn-navy", "av-btn-out"
    return f"""<div class="av-btns">
      <a class="av-btn {call_cls}" href="{call}">{icon('phone_icon')} Call Now</a>
      <a class="av-btn {verify}" href="{URL_VERIFY}">{icon('guard_icon')} Verify Insurance</a>
      <a class="av-btn {contact}" href="{URL_CONTACT}">Contact Form</a>
    </div>"""

# ---------- sections ----------
def s_hero(p, m):
    sub = e(p["hero_sub"]).replace("[PRE-LAUNCH] ", "")
    trust = "".join(
        f'<div class="av-trust-item">{icon("guard-checkmark-icon")}<span>{e(t)}</span></div>'
        for t in p["trust_bar"])
    return f"""<section class="av-hero">
  <div class="av-hero-bg" style="background-image:url('{m.img(HERO_FILE)}')"></div>
  <div class="av-wrap av-hero-inner">
    <div class="av-hero-col">
      <h1 class="av-h1">{e(p['h1'])}</h1>
      <p class="av-hero-sub">{sub}</p>
      {cta_row(p,'hero')}
    </div>
  </div>
  <div class="av-trust"><div class="av-wrap av-trust-inner">{trust}</div></div>
</section>"""

def s_intro(p, m):
    intro = e(p["intro"])
    paras = "".join(f"<p>{x.strip()}</p>" for x in re.split(r'(?<=\.)\s{2,}', intro) if x.strip()) or f"<p>{intro}</p>"
    stats = "".join(
        f'<div class="av-stat"><div class="av-stat-big">{e(s["big"])}</div>'
        f'<div class="av-stat-label">{e(s["label"])}</div></div>' for s in p["stat_cards"])
    eyebrow = f"SERVING {p['key'].upper()}, PA" if p['key'] != 'Pennsylvania' else "SERVING PENNSYLVANIA"
    # design H2 differs from H1; locations use the explicit map, areas fall back to a
    # city-aware generic (they aren't in INTRO_H2).
    h2 = INTRO_H2.get(p['key'], f"Behavioral Health and Addiction Treatment in {p['key']}")
    return f"""<section class="av-sec av-intro"><div class="av-wrap av-intro-grid">
    <div>
      <span class="av-eyebrow av-eyebrow-plain">{e(eyebrow)}</span>
      <h2 class="av-h2">{e(h2)}</h2>
      <div class="av-intro-body">{paras}</div>
      {cta_row(p,'light')}
    </div>
    <div class="av-stats">{stats}</div>
  </div></section>"""

def s_levels(p, m):
    cards = ""
    for i, c in enumerate(p["levels"]["cards"][:4]):   # max 4 program cards
        # styling is ORDER-dependent, not program-dependent (figma): navy, slate, green, repeat
        color = ORDER_COLORS[i % len(ORDER_COLORS)]
        name, desc, dur = c["name"], c["desc"], c["duration"]
        # complete the sparse referral cards so every card has desc + duration + CTA
        if not desc:
            ref = card_fallback(name)
            name, desc, dur = ref["name"], ref["desc"], ref["duration"]
        dur_html = f'<span class="av-card-dur">{e(dur)}</span>' if dur else "<span></span>"
        foot = f'<div class="av-card-foot">{dur_html}<a class="av-learn" href="{URL_LEARN}">Learn More {arrow()}</a></div>'
        cards += f"""<div class="av-card"><div class="av-card-top {color}"></div>
        <div class="av-card-body">
          <span class="av-badge {color}">{e(c['badge'])}</span>
          <h3>{e(name)}</h3>
          <p class="av-card-desc">{e(desc)}</p>
          {foot}
        </div></div>"""
    return f"""<section class="av-sec av-loc-bg"><div class="av-wrap">
    <div class="av-sec-head">
      <span class="av-eyebrow">Levels of Care</span>
      <h2 class="av-h2">{e(p['levels']['title'])}</h2>
      <p>A full continuum of evidence-based care designed to meet you wherever you are in your recovery.</p>
    </div>
    <div class="av-cards">{cards}</div>
    <div class="av-loc-cta">{cta_row(p,'light')}</div>
  </div></section>"""

def s_env(p, m):
    tiles = ""
    for i, label in enumerate(p["image_grid"][:5]):
        f = IMG_GRID_FILES.get(label, "common-areas.png")
        cls = f"av-tile av-tile-{i+1}"
        tiles += f'<div class="{cls}"><img src="{m.img(f)}" alt="{e(label)}"><span class="av-tile-label">{e(label)}</span></div>'
    return f"""<section class="av-sec"><div class="av-wrap">
    <div class="av-env-head">
      <div><span class="av-eyebrow av-eyebrow-plain">The Environment</span>
        <h2 class="av-h2">{e(p['environment']['title'])}</h2></div>
      <p>{e(p['environment']['sub'])}</p>
    </div>
    <div class="av-env-grid">{tiles}</div>
  </div></section>"""

# Real care team — the same five people, photos, and roles as the live /about/staff
# page (WPBakery markup, already in the CMS). Rebuilt cleanly from that page's cards:
# unique element IDs, ez-toc spans, and runtime full-width inline styles are dropped
# (display-irrelevant); the `staffInner`/`ult-modal-img`/`uvc-*` classes our scoped
# CSS targets are kept. Five cards lay out 3-then-2, centered, matching /about/staff.
STAFF = [
    ("Cassandra Harris", "Chief Operating Officer", "https://arkviewbh.com/wp-content/uploads/2025/04/staff_01.jpg"),
    ("Jon Seal", "Director of Admissions", "https://arkviewbh.com/wp-content/uploads/2025/11/Jon-Seal.jpg"),
    ("Zach Whipperman", "Director of Community Outreach", "https://arkviewbh.com/wp-content/uploads/2025/04/staff_02.jpg"),
    ("Kimberly Lindsey", "Behavioral Health Technician Supervisor", "https://arkviewbh.com/wp-content/uploads/2025/12/Kimberly-Lindsey.jpg"),
    ("David Root", "Clinical Director", "https://arkviewbh.com/wp-content/uploads/2025/12/David-Root.jpg"),
]

def _staff_card(name, role, img):
    return (f'<div class="staffInner wpb_column vc_column_container vc_col-sm-4">'
            f'<div class="vc_column-inner"><div class="wpb_wrapper">'
            f'<div class="ult-modal-input-wrapper ult-adjust-bottom-margin">'
            f'<img decoding="async" loading="lazy" src="{img}" alt="{e(name)}" '
            f'class="ult-modal-img overlay-show ult-align-center"></div>'
            f'<div class="uvc-heading ult-adjust-bottom-margin" data-halign="center" style="text-align:center">'
            f'<div class="uvc-main-heading"><h3 style="font-weight:normal;margin-bottom:10px;">{e(name)}</h3></div>'
            f'<div class="uvc-sub-heading" style="font-weight:normal;margin-bottom:0;">'
            f'<h5><em>{e(role)}</em></h5></div></div></div></div></div>')

STAFF_MARKUP = ('<div class="vc_row wpb_row vc_row-fluid av-staff-row">'
                + "".join(_staff_card(*s) for s in STAFF) + '</div>')

def s_team(p, m):
    return f"""<section class="av-sec av-team-sec">
  <div class="av-team-bg" style="background-image:url('{m.img(HERO_FILE)}')"></div>
  <div class="av-wrap">
    <div class="av-team-head">
      <div><span class="av-eyebrow av-eyebrow-green">Who You'll Meet</span>
        <h2 class="av-h2">Your Care Team</h2></div>
      <a class="av-viewstaff" href="{URL_STAFF}">View Full Staff {arrow()}</a>
    </div>
    {STAFF_MARKUP}
  </div></section>"""

def s_insurance(p, m):
    logos = p["insurance"]["logos"]
    cells = "".join(f'<div class="av-ins-cell">{e(l)}</div>' for l in logos)
    return f"""<section class="av-sec av-coverage"><div class="av-wrap">
    <div class="av-sec-head">
      <span class="av-eyebrow">Coverage</span>
      <h2 class="av-h2">Insurance We Accept</h2>
      <p>{e(p['insurance']['body'])}</p>
    </div>
    <div class="av-ins-grid">{cells}</div>
    <div class="av-ins-bar">
      <div><h3>Not sure if you're covered?</h3>
        <p>Our admissions team will verify your benefits free of charge, usually within minutes.</p></div>
      <div class="av-btns">
        <a class="av-btn av-btn-green-black" href="{URL_VERIFY}">{icon('guard_icon')} Verify Insurance</a>
        <a class="av-btn av-btn-gold-white" href="{tel(CANONICAL_PHONE)}">{icon('phone_icon')} Call Now</a>
      </div>
    </div>
  </div></section>"""

EXPECT_ICONS = ["phone_icon", "heart-handshake-icon", "guard-checkmark-icon"]
def s_expect(p, m):
    steps = ""
    for i, st in enumerate(p["expect"]):
        steps += f"""<div class="av-step">
        <div class="av-step-top"><div class="av-step-ico">{icon(EXPECT_ICONS[i%3])}</div>
          <div class="av-step-num">{e(st['num'])}</div></div>
        <h3>{e(st['title'])}</h3><p>{e(st['desc'])}</p></div>"""
    return f"""<section class="av-sec av-dark"><div class="av-wrap">
    <div class="av-sec-head">
      <span class="av-eyebrow av-eyebrow-green">Admissions Process</span>
      <h2 class="av-h2">What to Expect</h2>
      <p>Starting treatment can feel overwhelming. We've designed our admissions process to be as simple and stress-free as possible.</p>
    </div>
    <div class="av-steps">{steps}</div>
    <div class="av-loc-cta">{cta_row(p,'dark')}</div>
  </div></section>"""

def s_impact(p, m):
    paras = "".join(f"<p>{x.strip()}</p>" for x in p["local_impact"].split("\n") if x.strip())
    bars = ""
    for name, pct, sub in IMPACT_BARS:
        bars += f"""<div><div class="av-bar-top"><span class="av-bar-name">{e(name)}</span>
        <span class="av-bar-pct">{pct}%</span></div>
        <div class="av-bar-track"><div class="av-bar-fill" style="width:{pct}%"></div></div>
        <div class="av-bar-sub">{e(sub)}</div></div>"""
    title = IMPACT_H2.get(p['key'], f"Addiction and Mental Health in {p['key']} and {p['county']} County")
    return f"""<section class="av-sec av-impact"><div class="av-wrap av-impact-grid">
    <div>
      <span class="av-eyebrow av-eyebrow-plain">Local Impact</span>
      <h2 class="av-h2">{e(title)}</h2>
      <div class="av-impact-body">{paras}</div>
    </div>
    <div><div class="av-bars">{bars}</div>
      <p class="av-impact-src">Source: PA DDAP annual report. Statistics are statewide estimates, shown for illustrative purposes.</p>
    </div>
  </div></section>"""

def s_faq(p, m):
    items = ""
    for f in p["faqs"]:
        items += f"""<details class="av-faq"><summary>{e(f['q'])}{chevron()}</summary>
        <div class="av-faq-a">{e(f['a'])}</div></details>"""
    return f"""<section class="av-sec"><div class="av-wrap">
    <div class="av-sec-head"><span class="av-eyebrow">Common Questions</span>
      <h2 class="av-h2">Frequently Asked Questions</h2></div>
    <div class="av-faqs">{items}</div>
  </div></section>"""

def s_final(p, m):
    return f"""<section class="av-sec av-dark av-final" id="av-contact"><div class="av-wrap av-final-grid">
    <div>
      <span class="av-eyebrow av-eyebrow-green">Get Started Today</span>
      <h2 class="av-h2">{e(p['final_cta']['title'])}</h2>
      <p class="av-final-sub">{e(p['final_cta']['sub'])}</p>
      <div class="av-btns">
        <a class="av-btn av-btn-gold-black" href="{tel(CANONICAL_PHONE)}">{icon('phone_icon')} Call Now</a>
        <a class="av-btn av-btn-out-light" href="{URL_VERIFY}">{icon('guard_icon')} Verify Insurance</a>
      </div>
      <div class="av-final-trust">
        <div><span class="av-tico">{icon('guard_icon')}</span>Confidential</div>
        <div><span class="av-tico">{icon('clock_icon')}</span>24/7 Available</div>
        <div><span class="av-tico">{icon('star-icon')}</span>Free Assessment</div>
      </div>
    </div>
    <div class="av-form">
      <h3>Contact Form</h3><p class="av-form-note">All submissions are confidential.</p>
      <div class="av-field"><label>Full Name *</label><input type="text" placeholder="Your name"></div>
      <div class="av-field"><label>Phone Number *</label><input type="tel" placeholder="(555) 000-0000"></div>
      <div class="av-field"><label>Email Address</label><input type="email" placeholder="your@email.com"></div>
      <div class="av-field"><label>How can we help?</label><textarea placeholder="Tell us about your situation..."></textarea></div>
      <a class="av-btn av-btn-green" href="{URL_CONTACT}">Send Message</a>
    </div>
  </div></section>"""

def s_nearby(p, m):
    cells = "".join(f'<div class="av-near-cell">{e(t)}, PA</div>' for t in p["nearby"])
    area = "Pennsylvania" if p["county"].lower() == "statewide" else f"{p['county']} County"
    return f"""<section class="av-sec av-loc-bg av-near"><div class="av-wrap">
    <span class="av-eyebrow av-eyebrow-plain">Service Area</span>
    <h2 class="av-h2">Nearby Areas We Serve</h2>
    <p class="av-near-sub">Arkview provides treatment for residents across {e(area)} and surrounding communities.</p>
    <div class="av-near-grid">{cells}</div>
    <div class="av-near-bar">
      <div class="av-near-bar-txt">{icon('location-icon')}<span>Don't see your town listed? <a href="{URL_CONTACT}"><b>Contact us</b></a> — we may still be able to help or refer you to a trusted partner.</span></div>
      <a class="av-btn av-btn-gold" href="{tel(CANONICAL_PHONE)}">{icon('phone_icon')} Call Now</a>
    </div>
  </div></section>"""

INTRO_H2 = {
    "Mechanicsburg": "Behavioral Health and Addiction Treatment in Mechanicsburg",
    "York": "Behavioral Health and Addiction Treatment in York",
    "Pennsylvania": "Behavioral Health and Addiction Treatment Across Pennsylvania",
    "Fayetteville": "Behavioral Health and Addiction Treatment in Fayetteville",
}
IMPACT_H2 = {
    "Mechanicsburg": "Addiction and Mental Health in Mechanicsburg and Cumberland County",
    "York": "Addiction and Mental Health in York and York County",
    "Pennsylvania": "Addiction and Mental Health in Pennsylvania",
    "Fayetteville": "Addiction and Mental Health in Fayetteville and Franklin County",
}

SECTIONS_STANDARD = [s_hero, s_intro, s_levels, s_env, s_team, s_insurance,
                     s_expect, s_impact, s_faq, s_final, s_nearby]

def render_body(p, m):
    return "\n".join(fn(p, m) for fn in SECTIONS_STANDARD)

# Theme-bridge: only injected into the WordPress build. Makes the scoped block
# break out of Astra's constrained content container to true full-bleed, and
# hides the duplicate theme page title (our hero already carries the H1).
THEME_BRIDGE = (
    ".av-loc{width:100vw;max-width:100vw;margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw);}"
    ".entry-content > .av-loc{margin-top:0;}"
    "body .entry-header,body .ast-single-post .entry-title,body header.entry-header,"
    "body .page-title,body .ast-archive-description{display:none!important;}"
    ".single .entry-content,.page .entry-content{margin-block:0!important;}"
    # Hide the global Visucom smart-section top hero/breadcrumb header on these pages only
    "#section-129,#topHero{display:none!important;}"
)

def render_content(p, m):
    """Inner content posted to WordPress (style block + scoped wrapper)."""
    body = render_body(p, m)
    bridge = "" if m.standalone else THEME_BRIDGE
    return f'<style>{CSS}\n{bridge}</style>\n<div class="av-loc">\n{body}\n</div>'

def render_standalone(p):
    m = Mode(standalone=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['title_tag'])}</title></head><body style="margin:0">
{render_content(p, m)}
</body></html>"""

# ---------- Fayetteville coming-soon variant ----------
def clean_hold(s):
    return re.sub(r'\[(HOLD|PRE-LAUNCH)[^\]]*\]\s*', '', s).strip()

MEANTIME = [
    ("Mechanicsburg Campus", "Full continuum — medical detox, residential, PHP and IOP for both mental health and substance use.", "navy", "/locations/mechanicsburg-pa/"),
    ("East York Location", "Outpatient PHP and IOP close to home, with detox & residential referral to Mechanicsburg.", "slate", "/locations/york-pa/"),
    ("Virtual IOP — Statewide", "The same intensive outpatient program delivered online, anywhere in Pennsylvania.", "green", "/locations/pennsylvania/"),
]

def s_fay_hero(p, m):
    sub = e(clean_hold(p["hero_sub"]))
    trust = "".join(f'<div class="av-trust-item">{icon("guard-checkmark-icon")}<span>{e(t)}</span></div>' for t in p["trust_bar"])
    return f"""<section class="av-hero">
  <div class="av-hero-bg" style="background-image:url('{m.img(HERO_FILE)}')"></div>
  <div class="av-wrap av-hero-inner">
    <div class="av-hero-col">
      <span class="av-eyebrow av-eyebrow-green" style="margin-bottom:20px">Opening Soon</span>
      <h1 class="av-h1">{e(p['h1'])}</h1>
      <p class="av-hero-sub">{sub}</p>
      <div class="av-btns">
        <a class="av-btn av-btn-gold-black" href="{tel(CANONICAL_PHONE)}">{icon('phone_icon')} Call Now</a>
        <a class="av-btn av-btn-out-light" href="{URL_CONTACT}">Join the Interest List</a>
      </div>
    </div>
  </div>
  <div class="av-trust"><div class="av-wrap av-trust-inner">{trust}</div></div>
</section>"""

def s_fay_offer(p, m):
    note = clean_hold(p["intro"])
    cards = ""
    for nm, badge, color, desc in [
        ("Mental Health Detox", "COMING SOON", "green", "Medically supervised detox in a dedicated mental health inpatient setting, with suite-style rooms."),
        ("Residential Treatment", "COMING SOON", "green", "Primary mental health residential care designed specifically for inpatient stabilization and recovery."),
    ]:
        cards += f"""<div class="av-card"><div class="av-card-top {color}"></div>
        <div class="av-card-body"><span class="av-badge {color}">{badge}</span>
          <h3>{nm}</h3><p class="av-card-desc">{desc}</p>
          <div class="av-card-foot"><span class="av-card-dur">Details at launch</span></div></div></div>"""
    return f"""<section class="av-sec av-loc-bg"><div class="av-wrap">
    <div class="av-soon-note">⏳ Pre-launch — this facility is not yet open. Programs and details below are subject to confirmation at launch (pending environmental approval and an opening date).</div>
    <div class="av-sec-head"><span class="av-eyebrow">What We'll Offer</span>
      <h2 class="av-h2">Coming Soon — Dedicated Mental Health Inpatient Care</h2>
      <p>{e(note)}</p></div>
    <div class="av-cards" style="grid-template-columns:repeat(2,1fr);max-width:760px;margin:0 auto">{cards}</div>
  </div></section>"""

def s_fay_meantime(p, m):
    cards = ""
    for nm, desc, color, href in MEANTIME:
        cards += f"""<div class="av-card"><div class="av-card-top {color}"></div>
        <div class="av-card-body"><h3>{nm}</h3><p class="av-card-desc">{desc}</p>
          <div class="av-card-foot"><span></span><a class="av-learn" href="{href}">View Location {arrow()}</a></div></div></div>"""
    return f"""<section class="av-sec"><div class="av-wrap">
    <div class="av-sec-head"><span class="av-eyebrow av-eyebrow-plain">In the Meantime</span>
      <h2 class="av-h2">Where to Get Care Now</h2>
      <p>Until our Fayetteville doors open, care is available across the region through our existing locations and statewide Virtual IOP.</p></div>
    <div class="av-cards" style="grid-template-columns:repeat(3,1fr)">{cards}</div>
  </div></section>"""

def s_fay_final(p, m):
    return f"""<section class="av-sec av-dark av-final" id="av-contact"><div class="av-wrap av-final-grid">
    <div><span class="av-eyebrow av-eyebrow-green">Get Notified</span>
      <h2 class="av-h2">{e(p['final_cta']['title'])}</h2>
      <p class="av-final-sub">{e(p['final_cta']['sub'])} Call or leave your details and we'll reach out when we open.</p>
      <div class="av-btns">
        <a class="av-btn av-btn-gold-black" href="{tel(CANONICAL_PHONE)}">{icon('phone_icon')} Call Now</a>
        <a class="av-btn av-btn-out-light" href="{URL_CONTACT}">Contact Us</a>
      </div>
      <div class="av-final-trust">
        <div><span class="av-tico">{icon('guard_icon')}</span>Confidential</div>
        <div><span class="av-tico">{icon('clock_icon')}</span>24/7 Available</div>
        <div><span class="av-tico">{icon('star-icon')}</span>Free Assessment</div>
      </div></div>
    <div class="av-form"><h3>Join the Interest List</h3><p class="av-form-note">We'll notify you when Fayetteville opens.</p>
      <div class="av-field"><label>Full Name *</label><input type="text" placeholder="Your name"></div>
      <div class="av-field"><label>Phone Number *</label><input type="tel" placeholder="(555) 000-0000"></div>
      <div class="av-field"><label>Email Address</label><input type="email" placeholder="your@email.com"></div>
      <div class="av-field"><label>How can we help?</label><textarea placeholder="Tell us how we can help..."></textarea></div>
      <a class="av-btn av-btn-green" href="{URL_CONTACT}">Send Message</a>
    </div></div></section>"""

def render_fayetteville(p, m):
    body = "\n".join([s_fay_hero(p, m), s_fay_offer(p, m), s_fay_meantime(p, m),
                      s_insurance(p, m), s_faq(p, m), s_fay_final(p, m), s_nearby(p, m)])
    bridge = "" if m.standalone else THEME_BRIDGE
    return f'<style>{CSS}\n{bridge}</style>\n<div class="av-loc">\n{body}\n</div>'

def main():
    os.makedirs(PAGES, exist_ok=True)
    wpm = Mode(standalone=False)
    sam = Mode(standalone=True)
    index = []
    # Core locations (content.json) + Areas (areas.json) both render through the same
    # template; areas are never "hold" and never use the Fayetteville coming-soon variant.
    locations = json.load(open(os.path.join(BUILD, "content.json")))
    areas_path = os.path.join(BUILD, "areas.json")
    areas = json.load(open(areas_path)) if os.path.exists(areas_path) else []
    for p in locations + areas:
        slug = p["slug"]
        if p.get("kind") != "area" and p["key"] == "Fayetteville":
            content_wp = render_fayetteville(p, wpm)
            standalone = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
                          f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                          f'<title>{e(p["title_tag"])}</title></head><body style="margin:0">'
                          f'{render_fayetteville(p, sam)}</body></html>')
        else:
            content_wp = render_content(p, wpm)
            standalone = render_standalone(p)
        with open(os.path.join(PAGES, f"{slug}.html"), "w") as f:
            f.write(standalone)
        with open(os.path.join(PAGES, f"{slug}.content.html"), "w") as f:
            f.write(content_wp)
        index.append({"key": p["key"], "slug": slug, "kind": p.get("kind", "location"),
                      "title_tag": p["title_tag"], "meta_description": p["meta_description"],
                      "hold": p.get("kind") != "area" and p["key"] == "Fayetteville"})
        print(f"  built {p.get('kind','location')[:4]}  {slug}")
    json.dump(index, open(os.path.join(PAGES, "index.json"), "w"), indent=2)
    print(f"  total: {len(index)} pages ({len(locations)} location, {len(areas)} area)")

if __name__ == "__main__":
    main()
