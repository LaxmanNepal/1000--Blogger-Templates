#!/usr/bin/env python3
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir()
for name in ('index.html','styles.css','app-fast.js','sw.js','404.html','manifest.webmanifest','robots.txt'):
    src=ROOT/name
    if src.exists(): shutil.copy2(src,DIST/name)
for name in ('catalog.json','search-index.json','snapshot-report.json'):
    src=ROOT/'generated'/name
    if src.exists(): shutil.copy2(src,DIST/name)
thumbs=ROOT/'generated'/'thumbnails'
if thumbs.exists(): shutil.copytree(thumbs,DIST/'generated'/'thumbnails')
print('Prepared static Pages site:', DIST)
