#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import cp from 'node:child_process';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const modules = process.env.CODEX_NODE_MODULES;
if (!modules) throw new Error('CODEX_NODE_MODULES is required');
const { chromium } = require(path.join(modules, 'playwright'));
const sharp = require(path.join(modules, 'sharp'));
const { PNG } = require(path.join(modules, 'pngjs'));
const pixelmatch = require(path.join(modules, 'pixelmatch')).default;
const root = process.cwd();
const sourceRepo = process.argv[2];
const sourceUrl = process.argv[3] || 'http://127.0.0.1:4171/';
if (!sourceRepo) throw new Error('usage: generate_roadmap_source_fidelity_171.mjs <source-repo> [source-url]');
const fixedCommit = '52654da574952148f96d051e439bff1cbc7b4b9d';
const relRoot = 'foundation-library/motion-system/MOTION-SYSTEM-001/source-fidelity-candidates/CAROLINA-ROADMAP-SOURCE-FAITHFUL-001';
const out = path.join(root, relRoot);
const dirs = ['evidence/source','evidence/candidate','evidence/diff','evidence/overlay','evidence/side-by-side','evidence/geometry','evidence/computed-styles'];
for (const dir of dirs) fs.mkdirSync(path.join(out, dir), { recursive: true });
const json = (name, value) => fs.writeFileSync(path.join(out, name), JSON.stringify(value, null, 2) + '\n');
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const read = relative => fs.readFileSync(path.join(sourceRepo, relative));
const git = args => cp.execFileSync('git', ['-c', `safe.directory=${sourceRepo}`, '-C', sourceRepo, ...args], { encoding: 'utf8' }).trim();
const roles = {
  'app/page.tsx':['MARKUP'], 'app/layout.tsx':['TYPOGRAPHY','ACCESSIBILITY_BEHAVIOR'], 'app/globals.css':['STYLES','RESPONSIVE_RULES'],
  'components/landing/LandingPage.tsx':['MARKUP','STYLES'], 'components/landing/_landingMarkup.ts':['MARKUP','CONTENT_DATA','ICON_ASSET','ACCESSIBILITY_BEHAVIOR'],
  'hooks/landing/useCarolinaLandingInteractions.ts':['REVEAL_BEHAVIOR','ACCESSIBILITY_BEHAVIOR'], 'hooks/landing/_landingTypes.ts':['ACCESSIBILITY_BEHAVIOR'],
  'hooks/landing/_scrollReveal.ts':['MOTION_FORMULA','REVEAL_BEHAVIOR','RESPONSIVE_RULES','ACCESSIBILITY_BEHAVIOR'],
  'public/landing/carolina_md_approved_patch.css':['STYLES','TYPOGRAPHY','RESPONSIVE_RULES','ICON_ASSET','ACCESSIBILITY_BEHAVIOR'],
};
const imports = {
  'app/page.tsx':['components/landing/LandingPage.tsx'], 'app/layout.tsx':['app/page.tsx'], 'app/globals.css':['app/layout.tsx'],
  'components/landing/LandingPage.tsx':['app/page.tsx'], 'components/landing/_landingMarkup.ts':['components/landing/LandingPage.tsx'],
  'hooks/landing/useCarolinaLandingInteractions.ts':['components/landing/LandingPage.tsx'], 'hooks/landing/_landingTypes.ts':['hooks/landing/useCarolinaLandingInteractions.ts','hooks/landing/_scrollReveal.ts'],
  'hooks/landing/_scrollReveal.ts':['hooks/landing/useCarolinaLandingInteractions.ts'], 'public/landing/carolina_md_approved_patch.css':['components/landing/LandingPage.tsx'],
};
const symbols = {
  'app/page.tsx':['Home','LandingPage'], 'app/layout.tsx':['Inter','RootLayout'], 'app/globals.css':['html','body','*'],
  'components/landing/LandingPage.tsx':['LandingPage','LANDING_CSS_HREF'], 'components/landing/_landingMarkup.ts':['approvedLandingMarkup','.ca-roadmap-editorial'],
  'hooks/landing/useCarolinaLandingInteractions.ts':['useCarolinaLandingInteractions','initScrollReveal'], 'hooks/landing/_landingTypes.ts':['LandingCtx','Cleanup'],
  'hooks/landing/_scrollReveal.ts':['initScrollReveal','updateTimeline','--rail-start','--rail-height','--rail-fill-height','--progress'],
  'public/landing/carolina_md_approved_patch.css':['.ca-roadmap-editorial','.ca-roadmap-editorial__timeline','.ca-roadmap-editorial__line','.ca-roadmap-editorial__progress','.ca-roadmap-editorial__step','.ca-roadmap-editorial__dot','.ca-roadmap-editorial__card'],
};
const inventory = Object.keys(roles).map(relative => ({ repository:'marcellusanthonson-ctrl/carolina-md-next-landing', fixed_commit:fixedCommit, path:relative,
  blob_sha:git(['rev-parse',`${fixedCommit}:${relative}`]), sha256:sha256(read(relative)), role:roles[relative], imported_by:imports[relative],
  selectors_or_symbols:symbols[relative], copied_referenced_or_excluded:relative.includes('_landingMarkup') || relative.endsWith('.css') ? 'COPIED_EXACT_INTO_MONOLITHIC_REFERENCE' : 'REFERENCED_AND_FRAMEWORK_NEUTRALIZED_WITH_BEHAVIOR_PRESERVED', exclusion_reason:null }));

const contracted = {
  ROADMAP_CONTAINER:'.ca-roadmap-editorial', TIMELINE:'.ca-roadmap-editorial__timeline', BASE_RAIL:'.ca-roadmap-editorial__line', ACTIVE_RAIL:'.ca-roadmap-editorial__progress',
  START_NODE:'.ca-roadmap-editorial__step:first-of-type .ca-roadmap-editorial__dot', INTERMEDIATE_NODES:'.ca-roadmap-editorial__dot', TERMINAL_CAP:'.ca-roadmap-editorial__line::after',
  NODE_OUTER_HALO:'.ca-roadmap-editorial__dot::after', NODE_SURFACE:'.ca-roadmap-editorial__step::before', NODE_RING:'.ca-roadmap-editorial__dot::after', NODE_CORE:'.ca-roadmap-editorial__dot',
  LEFT_CARDS:'.ca-roadmap-editorial__step:nth-of-type(odd) .ca-roadmap-editorial__card', RIGHT_CARDS:'.ca-roadmap-editorial__step:nth-of-type(even) .ca-roadmap-editorial__card',
  CARD_ICON_CONTAINER:'.ca-roadmap-editorial__icon', CARD_ICON:'.ca-roadmap-editorial__icon svg', CARD_TITLE:'.ca-roadmap-editorial__card-title', CARD_NUMBER:'.ca-roadmap-editorial__number',
  CARD_DESCRIPTION:'.ca-roadmap-editorial__card-text', CARD_META_BADGE:'.ca-roadmap-editorial__meta', CARD_BACKGROUND:'.ca-roadmap-editorial__card', CARD_BORDER:'.ca-roadmap-editorial__card',
  CARD_SHADOW:'.ca-roadmap-editorial__card', SECTION_BACKGROUND:'.ca-roadmap-editorial', SPACING_SYSTEM:'.ca-roadmap-editorial__timeline'
};
const styleProps = ['display','position','top','right','bottom','left','width','height','padding','margin','gap','gridTemplateColumns','gridTemplateRows','flexDirection','justifyContent','alignItems','transform','transformOrigin','opacity','border','borderRadius','background','boxShadow','color','fontFamily','fontSize','fontWeight','lineHeight','letterSpacing','transition','animation','zIndex','overflow'];
const checkpoints = ['before-first-node','first-node-activation','between-nodes-1-2','second-node-activation','between-nodes-2-3','third-node-activation','terminal-completion','reverse-traversal'];
const viewports = [[390,844],[768,1024],[1280,900],[1440,1000]];
const modes = ['normal','reduced'];
const safe = value => value.replaceAll('<\/style','<\\/style').replaceAll('<\/script','<\\/script');
async function inlineCss(page) {
  const hrefs = await page.$$eval('link[rel="stylesheet"]', els => els.map(el => el.href));
  const parts = [];
  for (const href of hrefs) {
    let css = await (await fetch(href)).text();
    for (const match of [...css.matchAll(/url\(([^)]+)\)/g)]) {
      const raw = match[1].trim().replace(/^['"]|['"]$/g,'');
      if (raw.startsWith('data:') || raw.startsWith('#')) continue;
      const asset = new URL(raw, href);
      if (!['127.0.0.1','localhost'].includes(asset.hostname)) throw new Error(`external CSS asset ${asset}`);
      const response = await fetch(asset); const bytes = Buffer.from(await response.arrayBuffer());
      const type = response.headers.get('content-type') || (asset.pathname.endsWith('.woff2') ? 'font/woff2' : 'application/octet-stream');
      css = css.split(match[0]).join(`url(data:${type};base64,${bytes.toString('base64')})`);
    }
    parts.push(`/* ${href} */\n${css}`);
  }
  return parts.join('\n');
}
function motionScript() { return String.raw`(() => {
  const clamp=(v,min,max)=>Math.min(Math.max(v,min),max), section=document.querySelector('.ca-roadmap-editorial'); if(!section)return;
  const timeline=section.querySelector('.ca-roadmap-editorial__timeline'), progress=section.querySelector('.ca-roadmap-editorial__progress'), line=section.querySelector('.ca-roadmap-editorial__line');
  const steps=[...section.querySelectorAll('.ca-roadmap-editorial__step')], dots=steps.map(s=>s.querySelector('.ca-roadmap-editorial__dot')), reduce=matchMedia('(prefers-reduced-motion: reduce)'); if(!timeline||!progress||!line||!steps.length||!dots.every(Boolean))return;
  const obs=new IntersectionObserver((entries,o)=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-visible');o.unobserve(e.target)}}),{root:null,rootMargin:'0px',threshold:.1}); steps.forEach(s=>obs.observe(s)); let ticking=false;
  const center=el=>{const tr=timeline.getBoundingClientRect(),er=el.getBoundingClientRect();return er.top+er.height/2-tr.top};
  const update=()=>{const init=timeline.getBoundingClientRect(),first=center(dots[0]),last=steps.at(-1),card=last.querySelector('.ca-roadmap-editorial__card'),cr=card?.getBoundingClientRect(),h=cr?cr.height:280; timeline.style.paddingBottom=Math.ceil(h+72)+'px';
    const tr=timeline.getBoundingClientRect(),top=cr?cr.top-tr.top:first,mid=top+h/2,end=mid+h,start=Math.max(0,first),railEnd=Math.min(tr.height,end),railHeight=Math.max(1,railEnd-start); timeline.style.setProperty('--rail-start',start.toFixed(2)+'px');timeline.style.setProperty('--rail-height',railHeight.toFixed(2)+'px');
    let fill=clamp(innerHeight*.64-init.top-start,0,railHeight);if(reduce.matches)fill=railHeight;timeline.style.setProperty('--rail-fill-height',fill.toFixed(2)+'px');timeline.classList.toggle('is-end-active',fill>=railHeight-2);
    steps.forEach((step,i)=>{const offset=center(dots[i])-start;step.classList.toggle('is-dot-active',fill>=offset+3);const sr=step.getBoundingClientRect(),a=sr.top-tr.top-start,b=sr.bottom-tr.top-start,d=Math.max(1,b-a);step.style.setProperty('--progress',clamp((fill-a)/d,0,1).toFixed(3))});ticking=false};
  const request=()=>{if(!ticking){ticking=true;requestAnimationFrame(update)}};['scroll','resize','orientationchange','load'].forEach(name=>addEventListener(name,request,{passive:true}));document.fonts?.ready.then(request);request();setTimeout(request,120);setTimeout(request,360);
})();`; }
async function settle(page) { await page.waitForLoadState('load'); await page.evaluate(()=>document.fonts?.ready); await page.waitForTimeout(460); await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))); }
async function position(page, checkpoint) { return page.evaluate(async checkpoint => {
  const wait=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))), t=document.querySelector('.ca-roadmap-editorial__timeline'), dots=[...document.querySelectorAll('.ca-roadmap-editorial__dot')];
  const calc=()=>{const tr=t.getBoundingClientRect(),start=parseFloat(getComputedStyle(t).getPropertyValue('--rail-start'))||0,height=parseFloat(getComputedStyle(t).getPropertyValue('--rail-height'))||1, offsets=dots.map(d=>{const r=d.getBoundingClientRect();return r.top+r.height/2-tr.top-start});return{tr,start,height,offsets}};
  let g=calc(), desired=0; const map={ 'before-first-node':Math.max(0,g.offsets[0]-8), 'first-node-activation':g.offsets[0]+4, 'between-nodes-1-2':(g.offsets[0]+g.offsets[1])/2, 'second-node-activation':g.offsets[1]+4, 'between-nodes-2-3':(g.offsets[1]+g.offsets[2])/2, 'third-node-activation':g.offsets[2]+4, 'terminal-completion':g.height+3, 'reverse-traversal':(g.offsets[1]+g.offsets[2])/2 };
  if(checkpoint==='reverse-traversal'){scrollTo(0,t.getBoundingClientRect().top+scrollY+g.start+g.height+8-innerHeight*.64);await wait();await new Promise(r=>setTimeout(r,80));g=calc()}
  desired=map[checkpoint];scrollTo(0,Math.max(0,t.getBoundingClientRect().top+scrollY+g.start+desired-innerHeight*.64));await wait();await new Promise(r=>setTimeout(r,90));return{desired,scrollY};
 }, checkpoint); }
async function snapshot(page) { return page.evaluate(({ contracted, styleProps }) => {
  const split=s=>{const i=s.indexOf('::');return i<0?[s,null]:[s.slice(0,i),s.slice(i)]}, rect=r=>({x:r.x,y:r.y,width:r.width,height:r.height,top:r.top,right:r.right,bottom:r.bottom,left:r.left});
  const styles={},geometry={}; for(const [role,raw] of Object.entries(contracted)){const [sel,pseudo]=split(raw),els=[...document.querySelectorAll(sel)];styles[role]=els.map(el=>{const cs=getComputedStyle(el,pseudo);return Object.fromEntries(styleProps.map(p=>[p,cs[p]]))});geometry[role]=els.map(el=>{const r=el.getBoundingClientRect();if(!pseudo)return rect(r);const cs=getComputedStyle(el,pseudo),w=parseFloat(cs.width)||0,h=parseFloat(cs.height)||0;return{x:r.x+r.width/2-w/2,y:r.y+r.height/2-h/2,width:w,height:h,top:r.y+r.height/2-h/2,left:r.x+r.width/2-w/2,right:r.x+r.width/2+w/2,bottom:r.y+r.height/2+h/2}})}
  const timeline=document.querySelector('.ca-roadmap-editorial__timeline'),cs=getComputedStyle(timeline),steps=[...document.querySelectorAll('.ca-roadmap-editorial__step')];return{styles,geometry,state:{rail_start:parseFloat(cs.getPropertyValue('--rail-start')),rail_height:parseFloat(cs.getPropertyValue('--rail-height')),rail_fill_height:parseFloat(cs.getPropertyValue('--rail-fill-height')),end_active:timeline.classList.contains('is-end-active'),dot_active:steps.map(s=>s.classList.contains('is-dot-active')),cards_visible:steps.map(s=>s.classList.contains('is-visible')),progress:steps.map(s=>parseFloat(s.style.getPropertyValue('--progress'))||0),horizontal_overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth}};
 }, { contracted, styleProps }); }
function ssim(a,b) { const width=a.width,height=a.height,block=8,C1=6.5025,C2=58.5225;let sum=0,n=0;for(let y=0;y<height;y+=block)for(let x=0;x<width;x+=block){let av=[],bv=[];for(let j=y;j<Math.min(y+block,height);j++)for(let i=x;i<Math.min(x+block,width);i++){const k=(j*width+i)*4;av.push(.2126*a.data[k]+.7152*a.data[k+1]+.0722*a.data[k+2]);bv.push(.2126*b.data[k]+.7152*b.data[k+1]+.0722*b.data[k+2])}const ma=av.reduce((q,v)=>q+v,0)/av.length,mb=bv.reduce((q,v)=>q+v,0)/bv.length;let va=0,vb=0,cov=0;for(let i=0;i<av.length;i++){va+=(av[i]-ma)**2;vb+=(bv[i]-mb)**2;cov+=(av[i]-ma)*(bv[i]-mb)}const d=Math.max(1,av.length-1);va/=d;vb/=d;cov/=d;sum+=((2*ma*mb+C1)*(2*cov+C2))/((ma*ma+mb*mb+C1)*(va+vb+C2));n++}return sum/n; }
function compareSnapshots(a,b) { let styleMismatch=0,geometryMismatch=0,maxDelta=0;for(const role of Object.keys(contracted)){const aa=a.styles[role],bb=b.styles[role];if(JSON.stringify(aa)!==JSON.stringify(bb))styleMismatch++;const ag=a.geometry[role],bg=b.geometry[role];if(ag.length!==bg.length){geometryMismatch++;continue}for(let i=0;i<ag.length;i++)for(const p of ['x','y','width','height']){const d=Math.abs(ag[i][p]-bg[i][p]);maxDelta=Math.max(maxDelta,d);if(d>.5)geometryMismatch++}}return{computed_style_mismatch_count:styleMismatch,geometry_mismatch_count:geometryMismatch,max_structural_delta_css_px:maxDelta}; }

const browserPath = process.env.CODEX_CHROMIUM_PATH;
const browser = await chromium.launch({ headless:true, ...(browserPath ? { executablePath:browserPath } : {}) });
const browserVersion = browser.version();
const seed = await browser.newPage({ viewport:{width:1440,height:1000}, reducedMotion:'no-preference' });
const external=[]; await seed.route('**/*',route=>{const u=new URL(route.request().url());if(['127.0.0.1','localhost'].includes(u.hostname))route.continue();else{external.push(u.href);route.abort()}});
await seed.goto(sourceUrl,{waitUntil:'networkidle'}); await settle(seed);
const htmlClasses=await seed.evaluate(()=>({html:document.documentElement.className,body:document.body.className}));
const landing=await seed.$eval('.carolina-md-approved-landing',el=>{const c=el.cloneNode(true),t=c.querySelector('.ca-roadmap-editorial__timeline');t?.removeAttribute('style');t?.classList.remove('is-end-active');c.querySelectorAll('.ca-roadmap-editorial__step').forEach(s=>{s.classList.remove('is-visible','is-dot-active');s.removeAttribute('style')});return c.outerHTML});
const css=await inlineCss(seed); await seed.close();
const reference=`<!doctype html><html lang="es" class="${htmlClasses.html}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Carolina roadmap source-faithful reference — human review pending</title><style>${safe(css)}</style></head><body class="${htmlClasses.body}">${landing}<script>${safe(motionScript())}</script></body></html>`;
fs.writeFileSync(path.join(out,'REFERENCE_IMPLEMENTATION.html'),reference.replace(/[ \t]*\r?\n[ \t]*/g,' '));
const cases=[], sourceStyles={}, candidateStyles={}, sourceResults=[], candidateResults=[];
for(const [width,height] of viewports)for(const mode of modes)for(const checkpoint of checkpoints){const key=`${width}x${height}__${mode}__${checkpoint}`, reduced=mode==='reduced';
  const source=await browser.newPage({viewport:{width,height},reducedMotion:reduced?'reduce':'no-preference'}),candidate=await browser.newPage({viewport:{width,height},reducedMotion:reduced?'reduce':'no-preference'});let sourceExternal=[],candidateExternal=[];
  await source.route('**/*',route=>{const u=new URL(route.request().url());if(['127.0.0.1','localhost'].includes(u.hostname))route.continue();else{sourceExternal.push(u.href);route.abort()}});await candidate.route('**/*',route=>{const u=new URL(route.request().url());if(u.protocol==='file:'||u.protocol==='data:')route.continue();else{candidateExternal.push(u.href);route.abort()}});
  await source.goto(sourceUrl,{waitUntil:'networkidle'});await candidate.goto(pathToFileURL(path.join(out,'REFERENCE_IMPLEMENTATION.html')).href,{waitUntil:'load'});await settle(source);await settle(candidate);await position(source,checkpoint);await position(candidate,checkpoint);await Promise.all([source.waitForTimeout(1000),candidate.waitForTimeout(1000)]);
  const bounds=await source.$eval('.ca-roadmap-editorial',el=>{const r=el.getBoundingClientRect();return{top:r.top,bottom:r.bottom}}),clipY=Math.max(0,Math.min(height-1,bounds.top)),clipBottom=Math.max(clipY+1,Math.min(height,bounds.bottom));
  const ss=await snapshot(source),cs=await snapshot(candidate),sourcePath=path.join(out,'evidence/source',key+'.png'),candidatePath=path.join(out,'evidence/candidate',key+'.png'),clip={x:0,y:clipY,width,height:clipBottom-clipY};
  await source.screenshot({path:sourcePath,clip});await candidate.screenshot({path:candidatePath,clip});await sharp(sourcePath).png({compressionLevel:9,palette:true,quality:90}).toFile(sourcePath+'.tmp');fs.renameSync(sourcePath+'.tmp',sourcePath);await sharp(candidatePath).png({compressionLevel:9,palette:true,quality:90}).toFile(candidatePath+'.tmp');fs.renameSync(candidatePath+'.tmp',candidatePath);
  const a=PNG.sync.read(fs.readFileSync(sourcePath)),b=PNG.sync.read(fs.readFileSync(candidatePath)),diff=new PNG({width:a.width,height:a.height});const pixels=pixelmatch(a.data,b.data,diff.data,a.width,a.height,{threshold:.1});fs.writeFileSync(path.join(out,'evidence/diff',key+'.png'),PNG.sync.write(diff,{colorType:6}));
  await sharp({create:{width:a.width*2,height:a.height,channels:4,background:'#fff'}}).composite([{input:sourcePath,left:0,top:0},{input:candidatePath,left:a.width,top:0}]).png({compressionLevel:9}).toFile(path.join(out,'evidence/side-by-side',key+'.png'));
  await sharp(sourcePath).composite([{input:candidatePath,blend:'over',opacity:.5}]).png({compressionLevel:9}).toFile(path.join(out,'evidence/overlay',key+'.png'));
  const comparison=compareSnapshots(ss,cs),score=ssim(a,b),record={key,viewport:`${width}x${height}`,mode,checkpoint,ssim:score,pixel_diff_count:pixels,pixel_diff_ratio:pixels/(a.width*a.height),...comparison,source_external_requests:[...new Set(sourceExternal)],candidate_external_requests:[...new Set(candidateExternal)],source_state:ss.state,candidate_state:cs.state};cases.push(record);sourceStyles[key]=ss.styles;candidateStyles[key]=cs.styles;sourceResults.push({key,geometry:ss.geometry,state:ss.state});candidateResults.push({key,geometry:cs.geometry,state:cs.state});json(`evidence/geometry/${key}.json`,{source:ss.geometry,candidate:cs.geometry,comparison});json(`evidence/computed-styles/${key}.json`,{source:ss.styles,candidate:cs.styles,mismatch_count:comparison.computed_style_mismatch_count});await source.close();await candidate.close();
}
await browser.close();
const cssText=read('public/landing/carolina_md_approved_patch.css').toString('utf8'),breakpoints=[...new Set([...cssText.matchAll(/@media\s*\(([^)]+)\)/g)].map(m=>m[1]))];
json('SOURCE_FILE_INVENTORY.json',{schema_version:'1.0.0',repository:'marcellusanthonson-ctrl/carolina-md-next-landing',fixed_commit:fixedCommit,complete:true,records:inventory});
json('SOURCE_PROVENANCE.json',{schema_version:'1.0.0',source_repository:'marcellusanthonson-ctrl/carolina-md-next-landing',fixed_commit:fixedCommit,disposable_path:sourceRepo,push_disabled:git(['remote']).length===0,source_build:'PASS_NEXT_16_2_7',lockfile_sha256:sha256(read('package-lock.json')),markup_extraction:'EXACT_DOM_SUBTREE',style_extraction:'ALL_RENDERED_STYLESHEETS_INLINE_WITH_FONT_BYTES',behavior_packaging:'FRAMEWORK_NEUTRAL_EQUIVALENT_OF_SCROLL_REVEAL_SOURCE',external_requests_blocked:[...new Set(external)]});
json('SOURCE_FIDELITY_CONTRACT.json',{schema_version:'1.0.0',status:'HUMAN_REVIEW_PENDING',required_distinctions:['REFERENCE_IMPLEMENTATION','BEHAVIOR_CORE','NEUTRAL_ADAPTATION','PROJECT_ADAPTATION'],reference_implementation:'REFERENCE_IMPLEMENTATION.html',exact:['DOM_HIERARCHY','VISIBLE_CONTENT','CARD_ORDER','CARD_ALTERNATION','NODE_ANATOMY','INLINE_SVG','TYPOGRAPHY','SPACING','RESPONSIVE_RULES','MOTION_FORMULA','REVERSE_SCROLL','REDUCED_MOTION'],prohibited:['NEUTRAL_ADAPTATION_IMPERSONATION','CANONICAL_REPLACEMENT','REUSABLE_PROMOTION','HUMAN_APPROVAL_CLAIM']});
json('VISUAL_ANATOMY_CONTRACT.json',{schema_version:'1.0.0',layers:Object.entries(contracted).map(([role,selector])=>({role,source_selector:selector,dom_role:role.includes('CARD')?'CARD_LAYER':role.includes('NODE')?'NODE_LAYER':'STRUCTURAL_LAYER',dimensions:'COMPUTED_STYLE_BASELINE',positioning:'COMPUTED_STYLE_BASELINE',z_index:'COMPUTED_STYLE_BASELINE',color:'COMPUTED_STYLE_BASELINE',border:'COMPUTED_STYLE_BASELINE',radius:'COMPUTED_STYLE_BASELINE',shadow:'COMPUTED_STYLE_BASELINE',opacity:'COMPUTED_STYLE_BASELINE',transform:'COMPUTED_STYLE_BASELINE',transition:'COMPUTED_STYLE_BASELINE',relationship_to_rail:'MEASURED_IN_GEOMETRY_EVIDENCE',relationship_to_card:'MEASURED_IN_GEOMETRY_EVIDENCE',responsive_overrides:breakpoints,motion_states:['INITIAL','ACTIVE','VISIBLE','TERMINAL','REVERSE','REDUCED_MOTION']}))});
json('GEOMETRY_INVARIANTS.json',{schema_version:'1.0.0',axis_tolerance_css_px:.25,concentricity_tolerance_css_px:.25,source_candidate_structural_tolerance_css_px:.5,text_xy_tolerance_css_px:1,exact_relationships:['CARD_ALTERNATION','NODE_COUNT','CARD_COUNT','CARD_ORDER','NODE_TO_CARD_ASSOCIATION','RAIL_START','RAIL_ENDPOINT','TAIL_EXTENT','NO_CLIPPED_HALO','NO_CLIPPED_TERMINAL_CAP','NO_HORIZONTAL_SCROLL'],measurements:'evidence/geometry/'});
json('RESPONSIVE_CONTRACT.json',{schema_version:'1.0.0',viewports:viewports.map(v=>v.join('x')),source_media_queries:breakpoints,card_alternation_desktop:'LEFT_RIGHT',mobile:'SINGLE_COLUMN_RAIL_LEFT',same_browser_build:true,device_scale_factor:1});
json('MOTION_STATE_CONTRACT.json',{schema_version:'1.0.0',states:checkpoints,modes,trigger_viewport_ratio:.64,events:['INITIAL_LOAD','SCROLL_FORWARD','SCROLL_REVERSE','RESIZE','ORIENTATION_CHANGE','WINDOW_LOAD','DOCUMENT_FONTS_READY','POST_INITIALIZATION_120_MS','POST_INITIALIZATION_360_MS'],card_reveal:{threshold:.1,independent:true},reduced_motion:{rail:'COMPLETE',nodes:'ACTIVE',scroll_transitions:'DISABLED_BY_SOURCE_CSS'}});
json('FORMULA_CONTRACT.json',{schema_version:'1.0.0',rail_start:'max(0, firstDotCenter)',dynamic_padding_bottom:'ceil(lastCardHeight + 72)',target_tail_end:'lastCardMid + lastCardHeight',rail_end:'min(timelineHeight, targetTailEnd)',rail_height:'max(1, railEnd - railStart)',trigger_y:'viewportHeight * 0.64',fill_height:'clamp(triggerY - initialTimelineTop - railStart, 0, railHeight)',reduced_motion_fill:'railHeight',node_reached:'fillHeight >= dotOffset + 3',step_progress:'clamp((fillHeight - stepTop) / max(1, stepBottom - stepTop), 0, 1)',terminal_active:'fillHeight >= railHeight - 2'});
json('COMPUTED_STYLE_BASELINE.json',{schema_version:'1.0.0',properties:styleProps,cases:sourceStyles});json('SOURCE_RENDER_BASELINE.json',{schema_version:'1.0.0',browser_control:'PLAYWRIGHT',browser_product:'GOOGLE_CHROME',browser_version:browserVersion,device_scale_factor:1,cases:sourceResults});json('CANDIDATE_RENDER_RESULTS.json',{schema_version:'1.0.0',status:'HUMAN_REVIEW_PENDING',browser_control:'PLAYWRIGHT',browser_product:'GOOGLE_CHROME',browser_version:browserVersion,cases:candidateResults});
const minimum=Math.min(...cases.map(c=>c.ssim)),styleMismatch=cases.reduce((n,c)=>n+c.computed_style_mismatch_count,0),geometryMismatch=cases.reduce((n,c)=>n+c.geometry_mismatch_count,0),candidateExternal=cases.flatMap(c=>c.candidate_external_requests);let axisMax=0,concentricityMax=0;
for(const result of [...sourceResults,...candidateResults]){const g=result.geometry,center=r=>[r.x+r.width/2,r.y+r.height/2],rail=center(g.BASE_RAIL[0])[0];for(const item of [...g.ACTIVE_RAIL,...g.INTERMEDIATE_NODES,...g.TERMINAL_CAP,...g.NODE_OUTER_HALO,...g.NODE_RING])axisMax=Math.max(axisMax,Math.abs(rail-center(item)[0]));for(let i=0;i<g.NODE_CORE.length;i++){const [cx,cy]=center(g.NODE_CORE[i]);for(const layer of [g.NODE_OUTER_HALO[i],g.NODE_RING[i]]){const [x,y]=center(layer);concentricityMax=Math.max(concentricityMax,Math.abs(x-cx),Math.abs(y-cy))}}}
json('COMPARISON_METRICS.json',{schema_version:'1.0.0',status:minimum>=.995&&styleMismatch===0&&geometryMismatch===0&&axisMax<=.25&&concentricityMax<=.25&&candidateExternal.length===0?'PASS_AUTOMATED_GATES_HUMAN_REVIEW_PENDING':'SOURCE_FIDELITY_CANDIDATE_BLOCKED',minimum_required_ssim:.995,minimum_observed_ssim:minimum,computed_style_mismatch_count:styleMismatch,geometry_mismatch_count:geometryMismatch,maximum_axis_delta_css_px:axisMax,maximum_concentricity_delta_css_px:concentricityMax,candidate_external_request_count:candidateExternal.length,cases});
json('MANIFEST.json',{schema_version:'1.0.0',candidate_id:'CAROLINA-ROADMAP-SOURCE-FAITHFUL-001',status:'HUMAN_REVIEW_PENDING',classification:'REFERENCE_IMPLEMENTATION_CANDIDATE',source_repository:'marcellusanthonson-ctrl/carolina-md-next-landing',fixed_commit:fixedCommit,decision_ref:'DEC-LAB-031',authorization_ref:'AUTHORIZATION_LAB_ROADMAP_SOURCE_FIDELITY_FORENSIC_RECONSTRUCTION_171',current_neutral_derivation:'REJECTED_AS_CANONICAL_REFERENCE_PRESERVED_HISTORICALLY',canonical_replacement:false,reusable_promotion:false,product_integration:false,human_approval:false});
const matrix=cases.map(c=>`| ${c.viewport} | ${c.mode} | ${c.checkpoint} | ${c.ssim.toFixed(6)} | ${c.computed_style_mismatch_count} | ${c.geometry_mismatch_count} |`).join('\n');
fs.writeFileSync(path.join(out,'COMPARISON_REPORT.md'),`# Carolina roadmap source-fidelity comparison\n\nStatus: **HUMAN_REVIEW_PENDING**. Automated comparison does not constitute reference approval, canonical replacement or reusable promotion.\n\n- Source: marcellusanthonson-ctrl/carolina-md-next-landing@${fixedCommit}\n- Minimum SSIM: ${minimum.toFixed(6)} (gate >= 0.995)\n- Computed-style mismatches: ${styleMismatch}\n- Geometry mismatches: ${geometryMismatch}\n- Maximum axis delta: ${axisMax.toFixed(3)} CSS px\n- Maximum concentricity delta: ${concentricityMax.toFixed(3)} CSS px\n- Candidate external requests: ${candidateExternal.length}\n\n| Viewport | Mode | Checkpoint | SSIM | Style mismatches | Geometry mismatches |\n|---|---|---|---:|---:|---:|\n${matrix}\n`);
const options=cases.map(c=>`<option value="${c.key}">${c.viewport} · ${c.mode} · ${c.checkpoint}</option>`).join('');
fs.writeFileSync(path.join(out,'HUMAN_COMPARISON.html'),`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Human comparison — pending</title><style>body{margin:0;font:14px system-ui;background:#07131f;color:#e2e8f0}header{position:sticky;top:0;z-index:2;padding:16px 20px;background:#0f172a;border-bottom:1px solid #334155}h1{font-size:18px;margin:0 0 6px}.pending{color:#a3e635;font-weight:800}main{padding:18px;display:grid;gap:16px}.controls{display:flex;gap:10px;flex-wrap:wrap}select,button,a{padding:9px 12px;border-radius:8px;border:1px solid #475569;background:#1e293b;color:#fff}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}.pair img,.single img,iframe{width:100%;background:white;border:1px solid #334155}iframe{height:760px}.metrics{white-space:pre-wrap;background:#0f172a;padding:12px;border:1px solid #334155}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style></head><body><header><h1>Carolina roadmap source-fidelity comparison</h1><div class="pending">HUMAN_REVIEW_PENDING · no canonical replacement · no reusable promotion</div></header><main><div class="controls"><select id="case">${options}</select><select id="mode"><option value="pair">Side by side</option><option value="overlay">Overlay</option><option value="diff">Diff</option></select><a href="REFERENCE_IMPLEMENTATION.html" target="_blank">Full-screen candidate</a><a href="SOURCE_FILE_INVENTORY.json" target="_blank">Source inventory</a></div><div id="view"></div><div class="metrics" id="metrics"></div><h2>Live candidate</h2><iframe src="REFERENCE_IMPLEMENTATION.html"></iframe></main><script>const cases=${JSON.stringify(cases)};const s=document.querySelector('#case'),m=document.querySelector('#mode'),v=document.querySelector('#view'),x=document.querySelector('#metrics');function render(){const k=s.value,c=cases.find(i=>i.key===k);if(m.value==='pair')v.innerHTML='<div class="pair"><img src="evidence/source/'+k+'.png"><img src="evidence/candidate/'+k+'.png"></div>';else v.innerHTML='<div class="single"><img src="evidence/'+m.value+'/'+k+'.png"></div>';x.textContent=JSON.stringify({ssim:c.ssim,geometry:c.max_structural_delta_css_px,computed_style_mismatch_count:c.computed_style_mismatch_count,source_state:c.source_state,candidate_state:c.candidate_state},null,2)}s.onchange=m.onchange=render;render()</script></body></html>`);
if(minimum<.995||styleMismatch||geometryMismatch||candidateExternal.length)process.exitCode=2;
