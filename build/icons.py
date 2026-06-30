#!/usr/bin/env python3
"""Read SVG icon files and inline them, normalized to currentColor so they
inherit the surrounding text color. Width/height stripped for CSS sizing."""
import os, re

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

_cache = {}

def icon(name, cls="av-ico"):
    """Return inline <svg> for assets/<name>.svg with stroke/fill -> currentColor."""
    if name not in _cache:
        path = os.path.join(ASSETS, f"{name}.svg")
        with open(path) as f:
            svg = f.read()
        _cache[name] = svg
    svg = _cache[name]
    # strip xml width/height attrs on the root svg so CSS controls size
    svg = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1', svg, count=1)
    svg = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1', svg, count=1)
    # normalize colors to currentColor (keep fill="none")
    svg = re.sub(r'stroke="(?!none)[^"]*"', 'stroke="currentColor"', svg)
    svg = re.sub(r'fill="(?!none)[^"]*"', 'fill="currentColor"', svg)
    # add class to root svg
    svg = re.sub(r'<svg ', f'<svg class="{cls}" ', svg, count=1)
    return svg.strip()

# inline arrow (not in asset set)
def arrow(cls="av-ico"):
    return (f'<svg class="{cls}" viewBox="0 0 16 16" fill="none" '
            'xmlns="http://www.w3.org/2000/svg"><path d="M3.5 8h9m0 0L9 4.5M12.5 8 9 11.5" '
            'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            'stroke-linejoin="round"/></svg>')

def chevron(cls="av-ico"):
    return (f'<svg class="{cls}" viewBox="0 0 16 16" fill="none" '
            'xmlns="http://www.w3.org/2000/svg"><path d="M4 6l4 4 4-4" '
            'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" '
            'stroke-linejoin="round"/></svg>')
