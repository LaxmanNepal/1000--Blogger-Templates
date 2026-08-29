const REPO='LaxmanNepal/1000--Blogger-Templates';
const BRANCH='main';
const TREE_URL=`https://api.github.com/repos/${REPO}/git/trees/${BRANCH}?recursive=1`;
const MEDIA_BASE=`https://media.githubusercontent.com/media/${REPO}/${BRANCH}/`;
const RAW_BASE=`https://raw.githubusercontent.com/${REPO}/${BRANCH}/`;

const state={templates:[],filtered:[],page:1,pageSize:24,sort:'az',search:'',current:null};
const $=s=>document.querySelector(s);
const grid=$('#grid'), status=$('#status'), modal=$('#modal'), frame=$('#previewFrame'), device=$('#device');

function cleanName(path){return path.split('/').pop().replace(/\.xml$/i,'').replace(/\s+Blogger\s+Templates?$/i,'').replace(/\s+Blogger\s+Template$/i,'').replace(/[-_]+/g,' ').replace(/\s+/g,' ').trim()||'Untitled Template'}
function mediaUrl(path){return MEDIA_BASE+path.split('/').map(encodeURIComponent).join('/')}
function rawUrl(path){return RAW_BASE+path.split('/').map(encodeURIComponent).join('/')}
function escapeHtml(s){return s.replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function category(name){const n=name.toLowerCase();if(/magazine|news|portal/.test(n))return 'Magazine';if(/shop|store|ecommerce|fashion/.test(n))return 'Shopping';if(/video|movie|film|tube/.test(n))return 'Video';if(/music|mp3|song/.test(n))return 'Music';if(/anime/.test(n))return 'Anime';if(/tech|app|android/.test(n))return 'Technology';if(/photo|gallery|portfolio/.test(n))return 'Portfolio';if(/personal|blog|journal/.test(n))return 'Blog';return 'Other'}

async function loadLibrary(){
  try{
    const r=await fetch(TREE_URL,{headers:{Accept:'application/vnd.github+json'}}); if(!r.ok)throw new Error(`GitHub returned ${r.status}`);
    const data=await r.json();
    state.templates=(data.tree||[]).filter(x=>x.type==='blob'&&/\.xml$/i.test(x.path)).map(x=>({path:x.path,name:cleanName(x.path),category:category(cleanName(x.path)),sha:x.sha,size:x.size||0}));
    state.templates.sort((a,b)=>a.name.localeCompare(b.name));
    $('#templateCount').textContent=state.templates.length.toLocaleString();
    $('#categoryCount').textContent=new Set(state.templates.map(x=>x.category)).size;
    applyFilters();
  }catch(e){status.textContent='Could not load the template library. Please refresh or open the repository directly.';console.error(e)}
}

function applyFilters(){
  const q=state.search.toLowerCase().trim();
  state.filtered=state.templates.filter(t=>!q||`${t.name} ${t.category}`.toLowerCase().includes(q));
  state.filtered.sort((a,b)=>state.sort==='az'?a.name.localeCompare(b.name):b.name.localeCompare(a.name));
  const pages=Math.max(1,Math.ceil(state.filtered.length/state.pageSize)); if(state.page>pages)state.page=pages;
  renderGrid();renderPagination();
}

function renderGrid(){
  const start=(state.page-1)*state.pageSize, items=state.filtered.slice(start,start+state.pageSize);
  status.textContent=state.filtered.length?`Showing ${start+1}–${Math.min(start+items.length,state.filtered.length)} of ${state.filtered.length.toLocaleString()} templates`:'No templates match your search.';
  grid.innerHTML=items.map((t,i)=>`<article class="card" data-path="${escapeHtml(t.path)}"><div class="thumb"><div class="thumb-loading">Loading preview…</div><iframe title="${escapeHtml(t.name)} preview" data-preview-path="${escapeHtml(t.path)}" loading="lazy" sandbox="allow-forms allow-popups"></iframe></div><div class="card-body"><div class="card-title" title="${escapeHtml(t.name)}">${escapeHtml(t.name)}</div><div class="card-meta">${escapeHtml(t.category)} · Blogger XML</div><div class="preview-link">Open live preview →</div></div></article>`).join('');
  grid.querySelectorAll('.card').forEach(c=>c.addEventListener('click',()=>openPreview(c.dataset.path)));
  lazyPreviewFrames();
}

function renderPagination(){
  const pages=Math.max(1,Math.ceil(state.filtered.length/state.pageSize));
  if(pages<=1){$('#pagination').innerHTML='';return}
  const nums=[];const add=n=>{if(n>=1&&n<=pages&&!nums.includes(n))nums.push(n)};add(1);add(pages);for(let n=state.page-2;n<=state.page+2;n++)add(n);nums.sort((a,b)=>a-b);
  let html=`<button class="page-btn" ${state.page===1?'disabled':''} data-page="${state.page-1}">‹</button>`;let prev=0;
  nums.forEach(n=>{if(prev&&n>prev+1)html+='<span class="page-btn" style="pointer-events:none">…</span>';html+=`<button class="page-btn ${n===state.page?'active':''}" data-page="${n}">${n}</button>`;prev=n});
  html+=`<button class="page-btn" ${state.page===pages?'disabled':''} data-page="${state.page+1}">›</button>`;$('#pagination').innerHTML=html;
  $('#pagination').querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>{const p=Number(b.dataset.page);if(p>=1&&p<=pages){state.page=p;renderGrid();renderPagination();window.scrollTo({top:300,behavior:'smooth'})}}));
}

function lazyPreviewFrames(){
  const frames=[...grid.querySelectorAll('iframe[data-preview-path]')];
  const load=f=>{if(f.dataset.loaded)return;f.dataset.loaded='1';loadTemplate(f.dataset.previewPath).then(xml=>{f.srcdoc=buildPreview(xml,f.dataset.previewPath,true);const l=f.parentElement.querySelector('.thumb-loading');if(l)l.remove()}).catch(()=>{const l=f.parentElement.querySelector('.thumb-loading');if(l)l.textContent='Preview unavailable'})};
  if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){load(e.target);io.unobserve(e.target)}}),{rootMargin:'500px'});frames.forEach(f=>io.observe(f))}else frames.slice(0,8).forEach(load);
}

async function loadTemplate(path){
  const r=await fetch(mediaUrl(path));if(!r.ok)throw new Error(`Template fetch failed: ${r.status}`);return await r.text();
}

function extractSkin(xml){
  const m=xml.match(/<b:skin\b[^>]*>([\s\S]*?)<\/b:skin>/i);return m?m[1].replace(/^\s*<!\[CDATA\[/,'').replace(/\]\]>\s*$/,''):'';
}
function extractBody(xml){
  const m=xml.match(/<body\b[^>]*>([\s\S]*?)<\/body>/i);return m?m[1]:xml.replace(/^[\s\S]*?<body\b[^>]*>/i,'').replace(/<\/body>[\s\S]*$/i,'')}
function sampleWidget(type,id){
  const posts=`<article class="post hentry"><h2 class="post-title entry-title"><a href="#">Welcome to Your New Blog</a></h2><div class="post-meta">August 30, 2026 · Admin</div><p class="post-body entry-content">This is sample Blogger content used only for the template preview. Add your own posts, images, labels and widgets in Blogger.</p><a class="read-more" href="#">Read more</a></article><article class="post hentry"><h2 class="post-title entry-title"><a href="#">A Clean, Responsive Blogger Layout</a></h2><div class="post-meta">August 29, 2026 · Admin</div><p class="post-body entry-content">Preview the typography, spacing, navigation, sidebar and responsive behavior before downloading the XML.</p></article>`;
  if(/blog/i.test(type||id||''))return `<div class="blog-posts sample-blog">${posts}</div>`;
  return `<div class="widget sample-widget"><h2 class="title">Popular Posts</h2><ul><li><a href="#">Welcome to Your New Blog</a></li><li><a href="#">Latest Blogger Tips</a></li><li><a href="#">Responsive Design</a></li></ul></div>`;
}
function normalizeTemplate(xml){
  let body=extractBody(xml);
  body=body.replace(/<script\b[\s\S]*?<\/script>/gi,'');
  body=body.replace(/<noscript\b[\s\S]*?<\/noscript>/gi,'');
  body=body.replace(/<b:widget\b([^>]*)>([\s\S]*?)<\/b:widget>/gi,(m,a)=>{const typ=(a.match(/type=['"]([^'"]+)/i)||[])[1]||'';const id=(a.match(/id=['"]([^'"]+)/i)||[])[1]||'';return sampleWidget(typ,id)});
  body=body.replace(/<b:widget\b[^>]*\/>/gi,()=>sampleWidget('',''));
  body=body.replace(/<b:(?:section|includable|loop|if|else|switch|case|default)\b[^>]*>/gi,'<div>').replace(/<\/b:(?:section|includable|loop|if|else|switch|case|default)>/gi,'</div>');
  body=body.replace(/<b:(?:include|eval|message|comment)\b[^>]*\/>/gi,'');
  body=body.replace(/<b:[^>]+\/>/gi,'');
  body=body.replace(/<data:blog\.title\s*\/?>(?:<\/data:blog\.title>)?/gi,'My Blogger Site');
  body=body.replace(/<data:blog\.pageTitle\s*\/?>(?:<\/data:blog\.pageTitle>)?/gi,'My Blogger Site');
  body=body.replace(/<data:[^>]+\s*\/?>(?:<\/data:[^>]+>)?/gi,'');
  body=body.replace(/\$\([^)]*\)/g,'#777');
  if(body.replace(/<[^>]*>/g,'').trim().length<30)body+=`<main class="sample-fallback"><div class="sample-blog">${sampleWidget('Blog','Blog1')}</div></main>`;
  return body;
}
function buildPreview(xml,path,thumb=false){
  const skin=extractSkin(xml).replace(/<style[^>]*>|<\/style>/gi,'');
  const body=normalizeTemplate(xml);
  const title=cleanName(path);
  const safeSkin=skin.replace(/@import\s+url\([^)]*\);?/gi,'');
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(title)}</title><style>html,body{margin:0;padding:0}body{min-height:100vh}img{max-width:100%}iframe{max-width:100%}${safeSkin}</style></head><body>${body}<div id="preview-badge" style="position:fixed;right:10px;bottom:10px;z-index:2147483647;font:11px Arial,sans-serif;background:#111;color:#fff;padding:6px 8px;border-radius:6px;opacity:.65">Template preview</div></body></html>`;
}

async function openPreview(path){
  state.current=path;$('#previewTitle').textContent=cleanName(path);$('#downloadBtn').href=mediaUrl(path);$('#downloadBtn').setAttribute('download',path.split('/').pop());$('#sourceBtn').href=rawUrl(path);modal.hidden=false;document.body.style.overflow='hidden';device.classList.remove('mobile');device.classList.add('desktop');$('#desktopBtn').classList.add('active');$('#mobileBtn').classList.remove('active');frame.srcdoc='<html><body style="font:14px Arial;padding:30px">Loading preview…</body></html>';
  try{const xml=await loadTemplate(path);frame.srcdoc=buildPreview(xml,path,false)}catch(e){frame.srcdoc='<html><body style="font:14px Arial;padding:30px">This template could not be previewed. The original XML is still available from the Download button.</body></html>';console.error(e)}
}
function closeModal(){modal.hidden=true;document.body.style.overflow='';frame.srcdoc=''}

$('#search').addEventListener('input',e=>{state.search=e.target.value;state.page=1;applyFilters()});$('#sort').addEventListener('change',e=>{state.sort=e.target.value;state.page=1;applyFilters()});$('#pageSize').addEventListener('change',e=>{state.pageSize=Number(e.target.value);state.page=1;applyFilters()});
$('#desktopBtn').addEventListener('click',()=>{device.classList.remove('mobile');device.classList.add('desktop');$('#desktopBtn').classList.add('active');$('#mobileBtn').classList.remove('active')});$('#mobileBtn').addEventListener('click',()=>{device.classList.remove('desktop');device.classList.add('mobile');$('#mobileBtn').classList.add('active');$('#desktopBtn').classList.remove('active')});
document.addEventListener('click',e=>{if(e.target.matches('[data-close]'))closeModal()});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!modal.hidden)closeModal()});
loadLibrary();
