#!/usr/bin/env python3
"""Build a rich static Blogger template catalog with searchable intelligence metadata."""
from pathlib import Path
import json,re,html,hashlib
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'generated'/'catalog.json'
def clean(s): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',s or ''))).strip()
def name(p):
 s=re.sub(r'\s+Blogger\s+Templates?$','',p.stem,flags=re.I); return re.sub(r'\s+',' ',re.sub(r'[-_]+',' ',s)).strip() or 'Untitled Template'
def classify(s):
 n=s.lower(); groups=[(['magazine','news','portal'],'Magazine'),(['shop','store','ecommerce','fashion','product'],'Shopping'),(['video','movie','film','tube'],'Video'),(['music','mp3','song'],'Music'),(['anime','manga'],'Anime'),(['tech','technology','app','android','software'],'Technology'),(['photo','gallery','portfolio','photography'],'Portfolio'),(['business','agency','corporate','company'],'Business'),(['recipe','food','restaurant'],'Food'),(['travel','tour','hotel'],'Travel'),(['education','school','course','university'],'Education'),(['blog','journal','personal'],'Blog')]
 return next((label for keys,label in groups if any(k in n for k in keys)),'Other')
def inspect(text,nm):
 low=text.lower(); features=[]
 rules=[('responsive',r'viewport|@media'),('dark',r'dark|night|dark-mode'),('menu',r'menu|navbar|navigation'),('slider',r'slider|carousel|swiper|slick'),('masonry',r'masonry|isotope'),('search',r'search'),('social',r'facebook|instagram|twitter|youtube|social-icons?'),('comments',r'comments?|disqus'),('pagination',r'pagination|page-nav|blog-pager'),('sticky',r'sticky|position\s*:\s*sticky'),('bootstrap',r'bootstrap'),('fontawesome',r'font[- ]?awesome|fa-[a-z]'),('google-fonts',r'fonts\.googleapis\.com|@import[^;]*google'),('woocommerce',r'woocommerce'),('rtl',r'dir\s*=\s*["\']rtl|rtl\b')]
 for key,pat in rules:
  if re.search(pat,low,re.I): features.append(key)
 style='Minimal'
 if any(x in low for x in ('gradient','glass','glassmorphism','backdrop-filter')): style='Modern'
 elif any(x in low for x in ('magazine','grid','masonry','headline')): style='Editorial'
 elif any(x in low for x in ('portfolio','gallery','photography')): style='Visual'
 elif any(x in low for x in ('shop','store','product','ecommerce')): style='Commerce'
 tech=[]
 for key,pat in [('Bootstrap','bootstrap'),('Font Awesome','font[- ]?awesome|fa-[a-z]'),('Google Fonts','fonts\.googleapis\.com'),('Swiper','swiper'),('jQuery','jquery'),('Masonry','masonry|isotope')]:
  if re.search(pat,low,re.I): tech.append(key)
 return {'widgets':len(re.findall(r'<b:widget\b',text,re.I)),'sections':len(re.findall(r'<b:section\b',text,re.I)),'has_skin':bool(re.search(r'<b:skin\b',text,re.I)),'responsive':bool(re.search(r'viewport|@media',text,re.I)),'has_menu':bool(re.search(r'(menu|navbar|navigation)',low)),'has_dark':bool(re.search(r'dark|night',low)),'features':features,'style':style,'technology':tech,'keywords':sorted(set(re.findall(r'[a-z0-9]{3,}',(nm+' '+low[:12000]).lower())))[:120]}
items=[]
for p in ROOT.rglob('*.xml'):
 if any(x in p.parts for x in ('.git','generated')): continue
 raw=p.read_text(errors='ignore'); m=re.search(r'<title[^>]*>(.*?)</title>',raw,re.I|re.S); title=clean(m.group(1)) if m else ''
 nm=title or name(p); meta=inspect(raw,nm); cat=classify(nm+' '+p.as_posix())
 items.append({'id':hashlib.sha1(p.relative_to(ROOT).as_posix().encode()).hexdigest()[:12],'path':p.relative_to(ROOT).as_posix(),'name':nm,'category':cat,'size':p.stat().st_size,**meta})
items.sort(key=lambda x:x['name'].lower()); OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'version':3,'generated':True,'count':len(items),'categories':sorted({x['category'] for x in items}),'styles':sorted({x['style'] for x in items}),'features':sorted({f for x in items for f in x['features']}),'technologies':sorted({f for x in items for f in x['technology']}),'templates':items},ensure_ascii=False,separators=(',',':')))
print(f'Catalog v3: {len(items)} templates with intelligence metadata')
