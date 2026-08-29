#!/usr/bin/env python3
"""Build a rich static Blogger template catalog at build time."""
from pathlib import Path
import json,re,html,hashlib
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'generated'/'catalog.json'
def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',s or ''))).strip()
def name(p):
 s=re.sub(r'\s+Blogger\s+Templates?$','',p.stem,flags=re.I); return re.sub(r'\s+',' ',re.sub(r'[-_]+',' ',s)).strip() or 'Untitled Template'
def category(s):
 n=s.lower(); groups=[(['magazine','news','portal'],'Magazine'),(['shop','store','ecommerce','fashion'],'Shopping'),(['video','movie','film','tube'],'Video'),(['music','mp3','song'],'Music'),(['anime'],'Anime'),(['tech','app','android'],'Technology'),(['photo','gallery','portfolio'],'Portfolio'),(['blog','journal','personal'],'Blog')]
 return next((label for keys,label in groups if any(k in n for k in keys)),'Other')
def inspect(text):
 low=text.lower(); return {'widgets':len(re.findall(r'<b:widget\b',text,re.I)),'sections':len(re.findall(r'<b:section\b',text,re.I)),'has_skin':bool(re.search(r'<b:skin\b',text,re.I)),'responsive':bool(re.search(r'viewport|@media',text,re.I)),'has_menu':bool(re.search(r'(menu|navbar|navigation)',low)),'has_dark':bool(re.search(r'dark|night',low))}
items=[]
for p in ROOT.rglob('*.xml'):
 if any(x in p.parts for x in ('.git','generated')): continue
 raw=p.read_text(errors='ignore'); m=re.search(r'<title[^>]*>(.*?)</title>',raw,re.I|re.S); title=clean(m.group(1)) if m else ''
 nm=title or name(p); meta=inspect(raw)
 items.append({'id':hashlib.sha1(p.relative_to(ROOT).as_posix().encode()).hexdigest()[:12],'path':p.relative_to(ROOT).as_posix(),'name':nm,'category':category(nm),'size':p.stat().st_size,**meta})
items.sort(key=lambda x:x['name'].lower()); OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'version':2,'generated':True,'count':len(items),'categories':sorted({x['category'] for x in items}),'templates':items},ensure_ascii=False,separators=(',',':')))
print(f'Catalog v2: {len(items)} templates')
