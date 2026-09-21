(()=>{
'use strict';
const dictionary=window.DAVIANA_TRANSLATIONS||{},supported=['en','it','es','ru'];
const roots=[document,...Array.from(document.querySelectorAll('[data-site-shell]'),h=>h.shadowRoot).filter(Boolean)];
const original=new WeakMap();let language='en';
const staticLang=document.documentElement.dataset.staticLang||'';
const alternate=l=>document.querySelector('link[rel="alternate"][hreflang="'+l+'"]')?.href;
const controls=()=>roots.flatMap(r=>Array.from(r.querySelectorAll('[data-language],.language-control select')));
function translate(root,lang){
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;
 while(node=walker.nextNode()){
  if(node.parentElement?.closest('script,style,select,[data-language],.locale-notice'))continue;
  const initial=original.has(node)?original.get(node):node.nodeValue;original.set(node,initial);
  const key=initial.trim(),value=dictionary[key]?.[lang];
  node.nodeValue=value?initial.replace(key,value):initial;
 }
}
function applyLanguage(lang,{persist=true}={}){
 if(!supported.includes(lang))lang='en';
 if(staticLang){language=staticLang;try{localStorage.setItem('daviana-language',staticLang);}catch{}return;}
 language=lang;
 roots.forEach(r=>translate(r,lang));document.documentElement.lang=lang;
 controls().forEach(c=>{if(c.tagName==='SELECT')c.value=lang;else c.setAttribute('aria-pressed',String(c.dataset.language===lang));});
 const note=document.getElementById('locale-notice');
 if(note){note.hidden=lang==='en';note.textContent={it:'La navigazione è in italiano. Il contenuto di questa pagina è disponibile per ora in inglese.',es:'La navegación está en español. El contenido de esta página está disponible por ahora en inglés.',ru:'Навигация переведена на русский. Содержимое этой страницы пока доступно на английском.'}[lang]||'';}
 if(persist){try{localStorage.setItem('daviana-language',lang);}catch{}const u=new URL(location.href);if(lang==='en')u.searchParams.delete('lang');else u.searchParams.set('lang',lang);history.replaceState(null,'',u);}
}
roots.forEach(root=>{
 root.addEventListener('change',event=>{if(event.target.matches('.language-control select'))applyLanguage(event.target.value);});
 root.addEventListener('click',event=>{
  const toggle=event.target.closest('[data-language]');if(toggle){event.preventDefault();const to=toggle.dataset.language,alt=alternate(to);if(alt&&to!==(staticLang||'en')){try{localStorage.setItem('daviana-language',to);}catch{}location.href=new URL(alt).pathname;return;}if(staticLang){try{localStorage.setItem('daviana-language',to);}catch{}location.href='/'+(to==='en'?'':'?lang='+to);return;}applyLanguage(to);return;}
  const a=event.target.closest('a[href]');if(!a)return;
  const u=new URL(a.href,location.href);if(u.origin!==location.origin||a.target==='_blank'||a.hasAttribute('download'))return;
  if(language!=='en'&&u.pathname.endsWith('/')&&!/^\/(it|es|ru|fr|de)\//.test(u.pathname))u.searchParams.set('lang',language);
  const current=location.pathname.replace(/index\.html$/,'');const dest=u.pathname.replace(/index\.html$/,'');
  if(dest===current&&u.hash){const el=document.getElementById(decodeURIComponent(u.hash.slice(1)));if(el){event.preventDefault();el.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});history.replaceState(null,'',u);return;}}
  a.href=u.href;
 });
});
document.querySelectorAll('[data-site-shell="header"]').forEach(host=>{
 const r=host.shadowRoot,menu=r.querySelector('.menu'),nav=r.querySelector('.navlinks');
 const close=()=>{menu.setAttribute('aria-expanded','false');nav.classList.remove('open');};
 menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
 nav.addEventListener('click',e=>{if(e.target.closest('a'))close();});
 r.addEventListener('keydown',e=>{if(e.key==='Escape'){close();menu.focus();}});
 document.addEventListener('click',e=>{if(!e.composedPath().includes(host))close();});
 matchMedia('(min-width:901px)').addEventListener('change',close);
 window.addEventListener('orientationchange',close);
});
applyLanguage(new URL(location.href).searchParams.get('lang')||'en',{persist:false});
window.addEventListener('popstate',()=>applyLanguage(new URL(location.href).searchParams.get('lang')||'en',{persist:false}));
})();

(()=>{const frame=document.querySelector('.hero-film');if(!frame)return;const video=frame.querySelector('video'),button=frame.querySelector('.film-play'),fallback=frame.querySelector('.film-error');if(!video||!button)return;button.hidden=false;video.controls=false;button.addEventListener('click',async()=>{button.hidden=true;video.controls=true;try{if(video.ended)video.currentTime=0;video.muted=false;video.volume=1;fallback.hidden=true;await video.play();}catch{video.controls=true;fallback.hidden=false;}});video.addEventListener('ended',()=>{button.hidden=false;video.controls=false;});video.addEventListener('error',()=>{button.hidden=true;video.controls=true;fallback.hidden=false;});})();

// Product demos retain native controls when autoplay is unavailable.
(()=>{document.querySelectorAll('video[data-lazyvid]').forEach(video=>{video.muted=true;video.defaultMuted=true;video.playsInline=true;video.controls=true;const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;if(reduced){video.autoplay=false;video.removeAttribute('autoplay');video.pause();return;}const start=()=>{if(!document.hidden)video.play().catch(()=>{});};if('IntersectionObserver' in window){new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting)start();else video.pause();}),{threshold:.15}).observe(video);}else start();document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();else if(video.getBoundingClientRect().bottom>0&&video.getBoundingClientRect().top<innerHeight)start();});});})();

(()=>{const current=location.pathname.replace(/\/$/,'').replace(/\.html$/,'')||'/index';document.querySelectorAll('[data-site-shell="header"]').forEach(h=>h.shadowRoot?.querySelectorAll('.navlinks a').forEach(a=>{const path=new URL(a.href).pathname.replace(/\.html$/,'');if(path===current)a.setAttribute('aria-current','page');}));})();
