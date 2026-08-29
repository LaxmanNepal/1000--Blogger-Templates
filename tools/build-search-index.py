#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'generated'/'catalog.json'
OUT=ROOT/'generated'/'search-index.json'
data=json.loads(CAT.read_text(encoding='utf-8'))
items=[]
for t in data.get('templates',[]):
    text=' '.join(str(t.get(k,'')) for k in ('name','category','path')).lower()
    tokens=sorted(set(re.findall(r'[a-z0-9]{2,}',text)))
    items.append({'id':t['id'],'tokens':tokens})
OUT.write_text(json.dumps({'version':1,'count':len(items),'items':items},separators=(',',':')),encoding='utf-8')
print(f'Search index: {len(items)} templates')
