#!/usr/bin/env python3
"""Build a static catalog from Blogger XML files tracked with Git LFS."""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'generated'/'catalog.json'

def name(p):
 s=p.stem
 s=re.sub(r'\s+Blogger\s+Templates?$','',s,flags=re.I)
 s=re.sub(r'[-_]+',' ',s)
 return re.sub(r'\s+',' ',s).strip() or 'Untitled Template'

def category(s):
 n=s.lower()
 for keys,label in [(['magazine','news','portal'],'Magazine'),(['shop','store','ecommerce','fashion'],'Shopping'),(['video','movie','film','tube'],'Video'),(['music','mp3','song'],'Music'),(['anime'],'Anime'),(['tech','app','android'],'Technology'),(['photo','gallery','portfolio'],'Portfolio'),(['blog','journal','personal'],'Blog')]:
  if any(k in n for k in keys): return label
 return 'Other'
items=[]
for p in ROOT.rglob('*.xml'):
 if any(x in p.parts for x in ('.git','generated')): continue
 text=p.read_text(errors='ignore') if p.stat().st_size>1000 else ''
 title=''
 if text:
  m=re.search(r'<title[^>]*>(.*?)</title>',text,re.I|re.S)
  if m: title=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',m.group(1)))).strip()
 items.append({'path':p.relative_to(ROOT).as_posix(),'name':title or name(p),'category':category(title or name(p)),'size':p.stat().st_size})
items.sort(key=lambda x:x['name'].lower())
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'generated':True,'count':len(items),'templates':items},ensure_ascii=False,indent=2))
print(f'Catalog: {len(items)} templates')
