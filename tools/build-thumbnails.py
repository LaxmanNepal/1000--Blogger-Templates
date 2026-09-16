#!/usr/bin/env python3
"""Render and quality-check a visual snapshot for every Blogger XML template."""
from pathlib import Path
import asyncio, html, json, re, time
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'generated'/'catalog.json'
OUT=ROOT/'generated'/'thumbnails'
REPORT=ROOT/'generated'/'snapshot-report.json'
OUT.mkdir(parents=True,exist_ok=True)


def esc(s): return html.escape(str(s or ''))


def renderable(xml,name):
    m=re.search(r'<b:skin\b[^>]*>([\s\S]*?)</b:skin>',xml,re.I)
    skin=re.sub(r'<!\[CDATA\[|\]\]>','',m.group(1) if m else '')
    m=re.search(r'<body\b[^>]*>([\s\S]*?)</body>',xml,re.I)
    body=m.group(1) if m else ''
    body=re.sub(r'<script\b[\s\S]*?</script>','',body,flags=re.I)
    body=re.sub(r'<b:widget\b[^>]*>[\s\S]*?</b:widget>','<section class="widget-fallback"><h3>Sample Widget</h3><p>Preview content</p></section>',body,flags=re.I)
    body=re.sub(r'<b:[^>]+/?>|</b:[^>]+>','',body,flags=re.I)
    body=re.sub(r'<data:[^>]+/?>|</data:[^>]+>','',body,flags=re.I)
    if not body.strip():
        body=f'<main class="fallback"><header><strong>{esc(name)}</strong><nav>Home &nbsp; Categories &nbsp; About</nav></header><section><h1>{esc(name)}</h1><p>Sample Blogger template preview</p></section><div class="cols"><article><h2>Featured Post</h2><p>Sample article content and template layout.</p></article><aside><h3>Sidebar</h3><p>Recent posts · Labels · Archive</p></aside></div></main>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(name)}</title><style>*{{box-sizing:border-box}}html,body{{margin:0;padding:0;min-height:100%;background:#fff}}body{{font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#202124;overflow-x:hidden}}img{{max-width:100%;height:auto}}a{{color:inherit}}.widget-fallback{{margin:18px;padding:18px;border:1px solid #e5e7eb;border-radius:12px;background:#fff}}.fallback{{padding:0 28px}}.fallback header{{display:flex;justify-content:space-between;padding:22px 0;border-bottom:1px solid #eee}}.fallback section{{padding:40px 0;background:#f4f6f8}}.fallback .cols{{display:grid;grid-template-columns:2fr 1fr;gap:22px;margin-top:22px}}.fallback article,.fallback aside{{padding:24px;border:1px solid #eee;border-radius:14px}}{skin}</style></head><body>{body}</body></html>'''


def fallback_svg(item,reason):
    name=esc(item['name'][:48])
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500"><rect width="800" height="500" fill="#f3f4f6"/><rect x="30" y="30" width="740" height="440" rx="22" fill="#fff"/><rect x="30" y="30" width="740" height="70" rx="22" fill="#111827"/><text x="55" y="165" font-family="Arial" font-size="26" font-weight="700" fill="#111827">{name}</text><text x="55" y="205" font-family="Arial" font-size="16" fill="#667085">Snapshot unavailable — open live preview</text><text x="55" y="240" font-family="Arial" font-size="12" fill="#98a2b3">{esc(reason[:90])}</text></svg>'


async def render_once(browser,item):
    out=OUT/f"{item['id']}.jpg"
    page=None
    try:
        xml=(ROOT/item['path']).read_text(errors='ignore')
        page=await browser.new_page(viewport={'width':800,'height':500},device_scale_factor=1)
        await page.set_content(renderable(xml,item['name']),wait_until='domcontentloaded',timeout=15000)
        await page.evaluate('document.fonts && document.fonts.ready')
        await page.wait_for_timeout(450)
        await page.screenshot(path=str(out),type='jpeg',quality=82,full_page=False)
        size=out.stat().st_size if out.exists() else 0
        if size < 5000:
            raise RuntimeError(f'snapshot too small ({size} bytes)')
        return True,None,size
    except Exception as e:
        return False,str(e),0
    finally:
        if page:
            await page.close()


async def one(browser,item,sem):
    async with sem:
        started=time.time(); attempts=[]
        for attempt in range(1,4):
            ok,error,size=await render_once(browser,item)
            attempts.append({'attempt':attempt,'ok':ok,'error':error,'bytes':size})
            if ok:
                return {'id':item['id'],'path':item['path'],'name':item['name'],'status':'ok','attempts':attempts,'bytes':size,'seconds':round(time.time()-started,2)}
            await asyncio.sleep(0.35*attempt)
        reason=attempts[-1]['error'] or 'render failed'
        (OUT/f"{item['id']}.jpg").unlink(missing_ok=True)
        (OUT/f"{item['id']}.svg").write_text(fallback_svg(item,reason))
        return {'id':item['id'],'path':item['path'],'name':item['name'],'status':'fallback','attempts':attempts,'bytes':0,'seconds':round(time.time()-started,2)}


async def main():
    items=json.loads(CAT.read_text()).get('templates',[])
    for p in OUT.glob('*'):
        if p.suffix.lower() in {'.jpg','.svg'}: p.unlink()
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        sem=asyncio.Semaphore(4)
        results=await asyncio.gather(*(one(browser,x,sem) for x in items))
        await browser.close()
    report={'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'total':len(results),'real_snapshots':sum(r['status']=='ok' for r in results),'fallback_snapshots':sum(r['status']=='fallback' for r in results),'results':results}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f"Generated {report['real_snapshots']} real snapshots, {report['fallback_snapshots']} fallbacks, {report['total']} total")

if __name__=='__main__': asyncio.run(main())
