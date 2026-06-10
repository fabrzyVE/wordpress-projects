#!/usr/bin/env python3
"""Inline calculator-page.css + .js into the markup, producing two outputs:

  dist/calculator-page.combined.html  -> full standalone page (for preview / Custom HTML)
  dist/calculator-page.wp.html        -> body-only block (<style> + markup + <script>),
                                          ready to paste into an Elementor HTML widget
                                          or a WordPress Custom HTML block / LPagery template.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
os.makedirs(DIST, exist_ok=True)

html = open(os.path.join(HERE, "calculator-page.html")).read()
css  = open(os.path.join(HERE, "calculator-page.css")).read()
js   = open(os.path.join(HERE, "calculator-page.js")).read()

# Pull the .tl-calc markup block out of the standalone preview file.
m = re.search(r'(<div class="tl-calc">.*?</div><!-- /\.tl-calc -->)', html, re.S)
markup = m.group(1)

fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">')

block = (fonts + "\n<style>\n" + css + "\n</style>\n\n" + markup +
         "\n\n<script>\n" + js + "\n</script>\n")

with open(os.path.join(DIST, "calculator-page.wp.html"), "w") as f:
    f.write(block)

standalone = (
    "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<title>Trueline Calculator Page</title>\n" + fonts + "\n<style>\n" + css +
    "\n</style>\n</head>\n<body>\n" + markup + "\n<script>\n" + js + "\n</script>\n</body>\n</html>\n"
)
with open(os.path.join(DIST, "calculator-page.combined.html"), "w") as f:
    f.write(standalone)

print("Wrote dist/calculator-page.wp.html and dist/calculator-page.combined.html")
