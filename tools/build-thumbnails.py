#!/usr/bin/env python3
"""Generate tiny same-origin SVG preview cards at build time.
These are intentionally lightweight placeholders; real XML is only loaded on demand."""
from pathlib import Path
import json, html, re
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'generated'/'catalog.json'; OUT=ROOT/'generated'/'thumbnails'; OUT.mkdir(parents=True,exist_ok=True)
data=json.loads(CAT.read_text())
for t in data.get('templates',[]):
    slug=t['id']; title=html.escape(t['name'][:42]); cat=html.escape(t['category'])
    widgets=t.get('widgets',0); sections=t.get('sections',0)
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#eef4ff"/><stop offset="1" stop-color="#e9e7ff"/></linearGradient></defs><rect width="800" height="500" fill="url(#g)"/><rect x="35" y="30" width="730" height="440" rx="24" fill="#fff" opacity=".88"/><rect x="35" y="30" width="730" height="72" rx="24" fill="#111827"/><circle cx="72" cy="66" r="8" fill="#fff" opacity=".9"/><rect x="100" y="56" width="170" height="18" rx="9" fill="#fff" opacity=".8"/><rect x="55" y="130" width="440" height="180" rx="16" fill="#dbe5f4"/><rect x="525" y="130" width="215" height="180" rx="16" fill="#edf1f7"/><rect x="55" y="330" width="685" height="14" rx="7" fill="#d8dee9"/><rect x="55" y="358" width="520" height="12" rx="6" fill="#e2e7ef"/><text x="55" y="415" font-family="Arial,sans-serif" font-size="22" font-weight="700" fill="#111827">{title}</text><text x="55" y="444" font-family="Arial,sans-serif" font-size="14" fill="#667085">{cat} · {widgets} widgets · {sections} sections</text></svg>'''
    (OUT/f'{slug}.svg').write_text(svg)
print(f'Generated {len(data.get("templates",[]))} lightweight thumbnails')
