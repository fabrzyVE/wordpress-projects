#!/usr/bin/env python3
"""Scoped design-system CSS for the Arkview location page. Everything is
prefixed with `.av-loc` so it is self-contained inside one WordPress page and
neutralizes Astra/global theme style-bleed."""

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

/* ---- scope + reset ---- */
.av-loc, .av-loc *, .av-loc *::before, .av-loc *::after { box-sizing: border-box; }
.av-loc {
  --navy:#0F1D3B; --navy2:#16264a; --navy-card:#1b294780; --gold:#EAB308;
  --green:#74D59B; --green-deep:#5bbf86; --ink:#0B1937; --body:#566173;
  --muted:#67768E; --bg:#F7F8F8; --line:#E7EAF0; --line2:#eceef3;
  font-family:'Inter',system-ui,-apple-system,sans-serif; color:var(--body);
  font-size:16px; line-height:1.62; -webkit-font-smoothing:antialiased;
  background:#fff; overflow-x:clip;
}
.av-loc h1,.av-loc h2,.av-loc h3,.av-loc h4 {
  font-family:'Poppins',sans-serif; color:var(--ink); margin:0; line-height:1.16; font-weight:700;
}
.av-loc p { margin:0; }
.av-loc a { color:inherit; text-decoration:none; }
.av-loc img { max-width:100%; display:block; }
/* NOTE: do NOT set background/border here — `.av-loc button` (0,1,1) would beat
   the `.av-btn-*` fill classes (0,1,0) and wipe the Send Message button fill. */
.av-loc button { font-family:inherit; cursor:pointer; }
.av-loc ul { margin:0; padding:0; list-style:none; }
.av-ico { width:1em; height:1em; flex:none; }

.av-wrap { max-width:1200px; margin:0 auto; padding:0 28px; }
.av-sec { padding:96px 0; }
.av-sec-tight { padding:64px 0; }
.av-dark.av-sec { padding:104px 0; }   /* admissions / final CTA — extra top/bottom */

/* ---- typography helpers ---- */
.av-h1 { font-size:clamp(34px,4.6vw,56px); letter-spacing:-.01em; }
.av-h2 { font-size:clamp(28px,3.4vw,42px); letter-spacing:-.01em; }
.av-h3 { font-size:20px; font-weight:600; }
.av-lead { font-size:17px; line-height:1.7; }
.av-center { text-align:center; }
.av-sec-head { max-width:760px; margin:0 auto 52px; text-align:center; }
.av-sec-head .av-h2 { margin:18px 0 14px; }
.av-sec-head p { color:var(--body); font-size:17px; }

/* ---- eyebrow pill ---- */
.av-eyebrow {
  display:inline-block; font-family:'Poppins'; font-weight:600; font-size:12px;
  letter-spacing:.09em; text-transform:uppercase; color:#46546f;
  background:#fff; border:1px solid var(--line); border-radius:9px; padding:8px 15px;
}
.av-eyebrow-plain { background:#f1f3f7; border-color:transparent; }
.av-eyebrow-green { color:#3a9e6e; background:rgba(116,213,155,.13); border:1px solid rgba(116,213,155,.3); }

/* ---- buttons (theme-proof: .av-loc-prefixed to beat Astra link styles) ---- */
.av-loc a { text-decoration:none!important; }
.av-btns { display:flex; flex-wrap:wrap; gap:14px; margin-top:6px; }
.av-loc .av-btn {
  display:inline-flex; align-items:center; gap:9px; font-family:'Poppins';
  font-weight:600; font-size:15px; line-height:1; padding:16px 27px; border-radius:11px;
  border:1.5px solid transparent; cursor:pointer; white-space:nowrap; text-decoration:none!important;
  transition:background .18s ease, color .18s ease, border-color .18s ease, filter .18s ease;
}
.av-loc .av-btn .av-ico { width:17px; height:17px; }
/* gold = Call Now (navy text/icon); -black / -white variants per section */
.av-loc .av-btn-gold { background:var(--gold); color:var(--navy); }
.av-loc .av-btn-gold:hover { background:#d9a608; }
.av-loc .av-btn-gold-black { background:var(--gold); color:#111; }
.av-loc .av-btn-gold-black:hover { background:#d9a608; }
.av-loc .av-btn-gold-white { background:var(--gold); color:#fff; }
.av-loc .av-btn-gold-white:hover { background:#d9a608; }
/* navy = Verify (white text) -> hover white bg / navy text */
.av-loc .av-btn-navy { background:var(--navy); color:#fff; border-color:var(--navy); }
.av-loc .av-btn-navy:hover { background:#fff; color:var(--navy); border-color:var(--navy); }
/* hero Verify Insurance override (client request): solid white bg, navy text, no hover effect */
.av-loc .av-hero .av-btn-navy,
.av-loc .av-hero .av-btn-navy:hover { background:#fff; color:var(--navy); border-color:#fff; }
/* navy2 (#1C356C) = Verify on admissions -> hover white bg / black text */
.av-loc .av-btn-navy2 { background:#1C356C; color:#fff; border-color:#1C356C; }
.av-loc .av-btn-navy2:hover { background:#fff; color:#111; border-color:#fff; }
/* green = Verify on coverage (black text, bg unchanged) */
.av-loc .av-btn-green { background:var(--green); color:#0d2a1c; }
.av-loc .av-btn-green:hover { filter:brightness(.96); }
.av-loc .av-btn-green-black { background:var(--green); color:#111; }
.av-loc .av-btn-green-black:hover { filter:brightness(.96); }
/* outline on light = Contact Form -> hover navy bg / white text */
.av-loc .av-btn-out { background:transparent; border-color:#cbd2df; color:var(--navy); }
.av-loc .av-btn-out:hover { background:var(--navy); color:#fff; border-color:var(--navy); }
/* white = Contact Form on dark (navy text) */
.av-loc .av-btn-white { background:#fff; color:var(--navy); border-color:#fff; }
.av-loc .av-btn-white:hover { background:#e9edf4; color:var(--navy); }
/* outline-light = Contact Form on hero/dark -> hover white bg / navy text */
.av-loc .av-btn-out-light { background:transparent; border-color:rgba(255,255,255,.34); color:#fff; }
.av-loc .av-btn-out-light:hover { background:#fff; color:var(--navy); border-color:#fff; }

/* ===== 1. HERO ===== */
.av-hero { position:relative; background:var(--navy); color:#fff; overflow:hidden;
  min-height:720px; display:flex; flex-direction:column; }
.av-hero-bg { position:absolute; inset:0; background-size:cover; background-position:center center;
  background-repeat:no-repeat; }
.av-hero-bg::after { content:""; position:absolute; inset:0;
  background:linear-gradient(105deg, #0c1830 0%, rgba(12,24,48,.9) 40%, rgba(12,24,48,.5) 72%, rgba(12,24,48,.28) 100%); }
/* .av-hero-inner is the 1200 wrap; content lives in av-hero-col (left-aligned, not centered).
   Extra top padding clears the site navbar. */
/* width:100% is required — without it this flex item (margin:0 auto from .av-wrap)
   shrink-wraps to the 680px col and self-centers, pushing the hero text to the
   middle. width:100% makes it fill the 1200 wrap so the col left-aligns. */
.av-hero-inner { position:relative; padding:200px 28px 130px; flex:1; width:100%;
  display:flex; flex-direction:column; justify-content:center; align-items:flex-start; }
.av-hero-col { max-width:680px; display:flex; flex-direction:column; align-items:flex-start; text-align:left; }
.av-hero .av-h1 { color:#fff; margin-bottom:30px; }
.av-hero-sub { color:#c7cedd; font-size:18px; line-height:1.75; margin:0 0 42px; max-width:600px; }
.av-trust { position:relative; border-top:1px solid rgba(255,255,255,.1); background:rgba(6,14,30,.55); }
.av-trust-inner { display:flex; flex-wrap:wrap; justify-content:center; gap:14px 56px; padding:22px 0; }
.av-trust-item { display:flex; align-items:center; gap:10px; color:#cdd4e2; font-size:14.5px; font-weight:500; }
.av-trust-item .av-ico { width:18px; height:18px; color:var(--green); }

/* ===== 2. INTRO + STAT CARDS ===== */
.av-intro-grid { display:grid; grid-template-columns:1.15fr .85fr; gap:64px; align-items:center; }
.av-intro .av-h2 { margin:18px 0 22px; }
.av-intro-body p { margin-bottom:16px; color:var(--body); }
.av-intro .av-btns { margin-top:30px; }
.av-stats { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
.av-stat { background:#fff; border:1px solid var(--line); border-radius:16px; padding:26px 24px; text-align:center;
  box-shadow:0 1px 2px rgba(16,29,59,.04); }
.av-stat-big { font-family:'Poppins'; font-weight:700; font-size:26px; color:var(--navy); line-height:1.15; }
.av-stat-label { font-size:13.5px; color:var(--muted); margin-top:8px; line-height:1.45; }

/* ===== 3. LEVELS OF CARE ===== */
.av-loc-bg { background:var(--bg); }
.av-cards { display:grid; grid-template-columns:repeat(4,1fr); gap:22px; }
.av-card { background:#fff; border:1px solid var(--line); border-radius:14px; overflow:hidden;
  display:flex; flex-direction:column; box-shadow:0 1px 2px rgba(16,29,59,.04); }
.av-card-top { height:6px; }
.av-card-top.navy { background:var(--navy); }
.av-card-top.slate { background:#7c89a3; }
.av-card-top.green { background:var(--green); }
.av-card-body { padding:24px 22px 22px; display:flex; flex-direction:column; flex:1; }
/* category badge spans the full card width (revision: extend to container width) */
.av-badge { align-self:stretch; display:block; width:100%; font-family:'Poppins'; font-weight:600;
  font-size:11px; letter-spacing:.07em; text-transform:uppercase; padding:7px 12px; border-radius:6px;
  color:#fff; margin-bottom:16px; text-align:left; }
.av-badge.navy { background:var(--navy); }
.av-badge.slate { background:#7c89a3; }
.av-badge.green { background:var(--green); color:#0d2a1c; }
.av-card h3 { font-size:18px; font-weight:600; margin-bottom:11px; }
.av-card-desc { font-size:14px; color:var(--body); line-height:1.6; flex:1; }
/* wrap when a referral card's duration label is long (e.g. "At Mechanicsburg") so
   Learn More drops to its own line cleanly instead of wrapping mid-text. */
.av-card-foot { display:flex; align-items:center; justify-content:space-between; gap:8px 14px; flex-wrap:wrap; margin-top:20px; }
.av-card-dur { font-family:'Poppins'; font-weight:600; font-size:13.5px; color:var(--ink); }
.av-learn { display:inline-flex; align-items:center; gap:6px; font-size:13.5px; font-weight:700; color:#5b7088; white-space:nowrap; }
.av-learn .av-ico { width:14px; height:14px; }
.av-loc-cta { display:flex; justify-content:center; margin-top:46px; }

/* ===== 4. ENVIRONMENT ===== */
.av-env-head { display:flex; justify-content:space-between; align-items:flex-end; gap:40px; margin-bottom:34px; }
.av-env-head .av-h2 { margin-top:16px; }
.av-env-head p { color:var(--body); max-width:360px; font-size:15.5px; }
/* big image (70%) spans the two top rows; right column (30%) holds two stacked
   images at the same total height; bottom row = two side-by-side under the big
   (bottom-right stays empty, per design). */
.av-env-grid { display:grid; grid-template-columns:35fr 35fr 30fr; grid-template-rows:1fr 1fr 1.5fr;
  gap:16px; height:600px; }
.av-tile { position:relative; border-radius:14px; overflow:hidden; background:#dfe3ea; }
.av-tile img { width:100%; height:100%; object-fit:cover; }
.av-tile::after { content:""; position:absolute; inset:0; background:linear-gradient(to top, rgba(8,16,33,.6), transparent 52%); }
.av-tile-label { position:absolute; left:16px; bottom:14px; z-index:2; color:#fff; font-family:'Poppins';
  font-weight:600; font-size:14px; }
/* design layout: big left image (70%, top) over two side-by-side (bottom),
   plus a right column (30%) of two vertically-stacked images.
   content order is [Welcoming, Group, Common, Admissions, Individual]. */
.av-tile-1 { grid-column:1 / 3; grid-row:1 / 3; } /* Welcoming — big top-left, 70%, 2 rows tall */
.av-tile-2 { grid-column:3; grid-row:1; }        /* Group — right column, top of stack */
.av-tile-3 { grid-column:3; grid-row:2; }        /* Common — right column, bottom of stack */
.av-tile-4 { grid-column:1; grid-row:3; }        /* Admissions — bottom-left, under big */
.av-tile-5 { grid-column:2; grid-row:3; }        /* Individual — bottom-mid, under big */

/* ===== 5. TEAM (image background + blue overlay, like the hero) ===== */
.av-team-sec { position:relative; background:var(--navy); color:#fff; overflow:hidden; }
.av-team-bg { position:absolute; inset:0; background-size:cover; background-position:center center;
  background-repeat:no-repeat; }
.av-team-bg::after { content:""; position:absolute; inset:0;
  background:linear-gradient(110deg, rgba(10,22,44,.94) 0%, rgba(12,24,48,.86) 45%, rgba(12,24,48,.66) 100%); }
.av-team-sec > .av-wrap { position:relative; z-index:1; }
.av-team-sec .av-h2 { color:#fff!important; }
.av-team-head { display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:38px; gap:24px; }
.av-team-head .av-h2 { margin-top:16px; }
.av-loc .av-viewstaff { display:inline-flex; align-items:center; gap:7px; font-family:'Poppins'; font-weight:600;
  font-size:14px; }
.av-team-sec .av-viewstaff { color:#fff!important; }
/* Staff cards: faithful reproduction of the live /about/staff card design + hover
   (those rules are page-inline on /about/staff, not in a global stylesheet, so we
   reproduce them scoped here — self-contained, works in drafts). 5 cards lay out
   3-then-2. Avatar is a circle overlapping the top of a navy-bordered card; on hover
   the card darkens, text turns white, it scales up, and the photo goes sepia. */
/* layout: 3 cards on row 1, the rest centered on row 2 (flex-wrap + justify-center);
   standardized card width, and align-items:stretch equalizes height within a row. */
.av-staff-row { display:flex; flex-wrap:wrap; justify-content:center; align-items:stretch;
  gap:120px 40px; padding-top:110px; }
.av-staff-row .staffInner { display:flex; width:350px; max-width:100%; }
.av-staff-row .vc_column-inner {
  position:relative; background:#fff; text-align:center; line-height:1.5;
  padding:80px 24px 28px; border-radius:15px; border:10px solid #212f4a;
  width:100%; min-height:250px; margin:0; transition:all .3s ease; }
.av-staff-row .vc_column-inner:hover {
  background:#1e1e1e; color:#fff; transform:scale(1.05); box-shadow:0 20px 30px -25px #ddd; }
.av-staff-row .vc_column-inner h3 { font-size:21px!important; margin:0 0 5px!important; }
.av-staff-row .vc_column-inner h5 { font-size:15px; color:#8ca8de; margin:0; }
.av-staff-row .vc_column-inner:hover h3,
.av-staff-row .vc_column-inner:hover h5 { color:#fff!important; }
.av-staff-row .ult-modal-input-wrapper { margin-bottom:100px; }
.av-staff-row .ult-modal-input-wrapper img.ult-modal-img {
  position:absolute; top:-100px; left:50%; transform:translate(-50%,0);
  width:200px; height:200px; border-radius:50%; border:10px solid #1f2d47;
  object-fit:cover; object-position:center top; cursor:default; }
.av-staff-row .vc_column-inner:hover .ult-modal-input-wrapper img.ult-modal-img { border:10px inset #1f2d47; }
.av-staff-row .vc_column-inner:hover .ult-modal-input-wrapper img.ult-modal-img:hover { filter:sepia(1); }

/* ===== 6. INSURANCE ===== */
.av-coverage .av-sec-head { margin-bottom:64px; }   /* more spacing between subsections */
.av-ins-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:16px; margin-bottom:52px; }
.av-ins-cell { background:#fafbfc; border:1px solid var(--line); border-radius:12px; min-height:74px;
  display:flex; align-items:center; justify-content:center; text-align:center; padding:14px;
  font-family:'Poppins'; font-weight:600; font-size:14px; color:var(--navy); }
.av-ins-bar { background:#f6f8fa; border:1px solid var(--line); border-radius:16px; padding:26px 30px;
  display:flex; align-items:center; justify-content:space-between; gap:24px; flex-wrap:wrap; }
.av-ins-bar h3 { font-size:20px; font-weight:600; margin-bottom:4px; }
.av-ins-bar p { font-size:14.5px; color:var(--body); }

/* ===== 7. WHAT TO EXPECT ===== */
.av-dark { background:var(--navy); color:#fff; }
.av-dark .av-h2 { color:#fff!important; }
.av-dark .av-sec-head p { color:#aab3c6; }
.av-steps { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; }
.av-step { background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.09); border-radius:16px;
  padding:28px 26px; position:relative; }
/* icon + number sit together, left-aligned */
.av-step-top { display:flex; align-items:center; justify-content:flex-start; gap:14px; margin-bottom:18px; }
/* icon tile = solid brand green; icon glyph navy */
.av-step-ico { width:46px; height:46px; border-radius:11px; background:#75D69C;
  display:flex; align-items:center; justify-content:center; color:var(--navy); }
.av-step-ico .av-ico { width:22px; height:22px; }
.av-step-num { font-family:'Poppins'; font-weight:700; font-size:34px; color:rgba(255,255,255,.18); }
/* smaller title so it doesn't wrap */
.av-step h3 { color:#fff!important; font-size:16px; font-weight:600; margin-bottom:10px; }
.av-step p { color:#aab3c6; font-size:14px; line-height:1.6; }
.av-dark .av-loc-cta { margin-top:48px; }

/* ===== 8. LOCAL IMPACT ===== */
.av-impact { border-bottom:1px solid var(--line); }   /* single horizontal divider (no extra gray span) */
.av-impact-grid { display:grid; grid-template-columns:1.05fr .95fr; gap:64px; align-items:start; }
.av-impact .av-h2 { margin:16px 0 22px; }
.av-impact-body p { margin-bottom:15px; color:var(--body); font-size:15.5px; }
.av-bars { display:flex; flex-direction:column; gap:24px; }
.av-bar-top { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:9px; }
.av-bar-name { font-family:'Poppins'; font-weight:600; font-size:15px; color:var(--ink); }
.av-bar-pct { font-family:'Poppins'; font-weight:600; font-size:15px; color:var(--ink); }
.av-bar-track { height:9px; background:#eaedf2; border-radius:6px; overflow:hidden; }
.av-bar-fill { height:100%; background:var(--green); border-radius:6px; }
.av-bar-sub { font-size:12.5px; color:var(--muted); margin-top:7px; }
.av-impact-src { font-size:12px; color:#9aa3b2; margin-top:26px; }

/* ===== 9. FAQ ===== */
.av-faqs { max-width:920px; margin:0 auto; display:flex; flex-direction:column; gap:14px; }
.av-faq { border:1px solid var(--line); border-radius:13px; background:#fff; overflow:hidden; }
.av-faq summary { list-style:none; cursor:pointer; padding:21px 24px; display:flex; align-items:center;
  justify-content:space-between; gap:20px; font-family:'Poppins'; font-weight:600; font-size:16px; color:var(--ink); }
.av-faq summary::-webkit-details-marker { display:none; }
.av-faq summary .av-ico { width:18px; height:18px; color:#8a93a6; transition:transform .2s ease; flex:none; }
.av-faq[open] summary .av-ico { transform:rotate(180deg); }
.av-faq-a { padding:0 24px 22px; color:var(--body); font-size:15px; line-height:1.65; }

/* ===== 10. FINAL CTA ===== */
.av-final-grid { display:grid; grid-template-columns:1fr 1fr; gap:62px; align-items:center; }
.av-final .av-eyebrow { margin-bottom:26px; }
.av-final .av-h2 { color:#fff!important; margin:0 0 24px; }
.av-final-sub { color:#aab3c6; font-size:17px; line-height:1.65; margin-bottom:40px; max-width:440px; }
.av-final .av-btns { margin-bottom:52px; }
.av-final-trust { display:flex; justify-content:space-between; gap:24px; border-top:1px solid rgba(255,255,255,.1); padding-top:30px; }
.av-final-trust div { display:flex; flex-direction:column; align-items:center; gap:9px; color:#aab3c6; font-size:12.5px; flex:1; }
.av-final-trust .av-tico { width:42px; height:42px; border-radius:10px; border:1px solid rgba(255,255,255,.14);
  display:flex; align-items:center; justify-content:center; color:var(--green); }
.av-final-trust .av-tico .av-ico { width:19px; height:19px; }
.av-form { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.1); border-radius:18px; padding:32px; }
.av-form h3 { color:#fff!important; font-size:21px; font-weight:600; margin-bottom:4px; }
.av-form-note { color:#8e98ac; font-size:13px; margin-bottom:22px; }
.av-field { margin-bottom:17px; }
.av-field label { display:block; color:#cdd4e2; font-size:13px; font-weight:600; margin-bottom:8px; font-family:'Poppins'; }
.av-field input, .av-field textarea { width:100%; background:#eef1f6; border:1px solid transparent; border-radius:10px;
  padding:13px 15px; font-family:inherit; font-size:14.5px; color:#1a2640; }
.av-field textarea { min-height:104px; resize:vertical; }
.av-field input::placeholder, .av-field textarea::placeholder { color:#9aa3b2; }
.av-form .av-btn-green { width:100%; justify-content:center; margin-top:6px; }

/* ===== 11. NEARBY AREAS ===== */
.av-near .av-h2 { margin:16px 0 12px; }
.av-near-sub { color:var(--body); font-size:16px; margin-bottom:32px; }
.av-near-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:14px; margin-bottom:26px; }
.av-near-cell { background:#fff; border:1px solid var(--line); border-radius:11px; padding:15px 10px;
  text-align:center; font-family:'Poppins'; font-weight:600; font-size:14px; color:var(--navy); }
.av-near-bar { background:#fff; border:1px solid var(--line); border-radius:14px; padding:20px 26px;
  display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap; }
.av-near-bar-txt { display:flex; align-items:center; gap:11px; color:var(--body); font-size:15px; }
.av-near-bar-txt .av-ico { width:18px; height:18px; color:var(--green); }
.av-near-bar-txt b { color:var(--ink); font-weight:600; }

/* ---- coming soon (Fayetteville) ---- */
.av-soon-note { background:#fff7e6; border:1px solid #f3d98a; color:#8a6d1d; border-radius:12px;
  padding:16px 20px; font-size:14.5px; margin-bottom:30px; font-weight:500; }

/* ===== responsive ===== */
@media (max-width:1024px){
  .av-cards{grid-template-columns:repeat(2,1fr);}
  .av-ins-grid{grid-template-columns:repeat(4,1fr);}
  .av-near-grid{grid-template-columns:repeat(4,1fr);}
  .av-env-grid{grid-template-columns:1fr 1fr; height:auto; grid-template-rows:none;}
  .av-tile-1,.av-tile-2,.av-tile-3,.av-tile-4,.av-tile-5{grid-column:auto; grid-row:auto; height:230px;}
  .av-tile-1{grid-column:1 / span 2; height:320px;}
}
@media (max-width:860px){
  .av-sec,.av-dark.av-sec{padding:64px 0;}
  .av-intro-grid,.av-impact-grid,.av-final-grid{grid-template-columns:1fr; gap:40px;}
  .av-team-grid,.av-steps{grid-template-columns:1fr;}
  .av-env-head,.av-team-head{flex-direction:column; align-items:flex-start; gap:14px;}
  .av-hero{min-height:0;}
  .av-hero-inner{padding:96px 0 72px;}
  .av-final-trust{flex-wrap:wrap; gap:18px;}
}
@media (max-width:560px){
  .av-cards,.av-stats,.av-ins-grid,.av-near-grid,.av-env-grid{grid-template-columns:1fr;}
  .av-tile-1{grid-column:auto;}
}
"""
