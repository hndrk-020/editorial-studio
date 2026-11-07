const steps=[
['THE EDITORIAL PROMISE','Know what this publication is for.','Define the subject, purpose and audience. Set the tone, share a reference or choose no example. The brief becomes the standard for every decision that follows.','OUTPUT / A CLEAR BRIEF'],
['CREATIVE DIRECTION','Two paths. Your point of view.','Compare two materially different directions before production. Choose one explicitly. A reusable brand sheet keeps the publication recognisable while allowing each issue its own character.','GATE / YOUR DIRECTION APPROVAL'],
['EDITORIAL PLANNING','Build an issue, not a pile of pages.','Set the issue theme, mix the stories, map the flatplan and give each piece a copy budget. Headlines, structure and voice work together to create an intentional reading order.','OUTPUT / A WORKING FLATPLAN'],
['PHOTOGRAPHY STORYTELLING','Give every photograph a reason.','Find authentic originals, record provenance and rights evidence, and choose narrative roles. Check sequencing, repetition and crops. An optional brief supports original photography.','GATE / YOUR EXACT-IMAGE APPROVAL'],
['DESIGN & EDITING','Read the words. Read the page.','Develop representative cover, feature-opening and text-heavy proofs. Inspect the design system in use, refine captions and copy, preserve evidence and read the text back in layout.','OUTPUT / INSPECTED DESIGN PROOFS'],
['WHOLE-ISSUE REVIEW','Finish with the reader in mind.','Review flow, pacing, transitions, image variety and brand consistency. Run preflight, export and audit the PDF, then visually inspect representative pages before sharing.','GATE / PDF QUALITY & VISUAL REVIEW']];
const tabs=[...document.querySelectorAll('[data-step]')];
function selectStep(index,focus=false){const data=steps[index];tabs.forEach((t,i)=>{t.setAttribute('aria-selected',String(i===index));t.tabIndex=i===index?0:-1});document.querySelector('#workflow-panel').setAttribute('aria-labelledby','tab-'+index);document.querySelector('.panel-number').textContent=String(index+1).padStart(2,'0');['step-tag','step-title','step-copy','step-gate'].forEach((id,i)=>document.getElementById(id).textContent=data[i]);if(focus)tabs[index].focus()}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectStep(i));tab.addEventListener('keydown',e=>{let next;if(e.key==='ArrowDown')next=(i+1)%tabs.length;if(e.key==='ArrowUp')next=(i+tabs.length-1)%tabs.length;if(e.key==='Home')next=0;if(e.key==='End')next=tabs.length-1;if(next!==undefined){e.preventDefault();selectStep(next,true)}})});
const installTabs=[...document.querySelectorAll('[data-install]')];
function selectInstall(tab,focus=false){installTabs.forEach(t=>{const selected=t===tab;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;document.getElementById('install-'+t.dataset.install).hidden=!selected});if(focus)tab.focus()}
installTabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectInstall(tab));tab.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();selectInstall(installTabs[e.key==='Home'?0:e.key==='End'?1:1-i],true)}})});
const quickTabs=[...document.querySelectorAll('[data-quick]')];
function selectQuick(tab,focus=false){quickTabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;document.getElementById('quick-'+t.dataset.quick).hidden=!active});document.querySelector('.quick-status').textContent='';if(focus)tab.focus()}
quickTabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectQuick(tab));tab.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();selectQuick(quickTabs[e.key==='Home'?0:e.key==='End'?quickTabs.length-1:(i+(e.key==='ArrowLeft'?-1:1)+quickTabs.length)%quickTabs.length],true)}})});
let toastTimer;document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
 const source=document.getElementById(button.dataset.copy),value=source.textContent,toast=document.getElementById('toast');
 const destination=button.dataset.destination||(button.dataset.copy.includes('command')&&!button.dataset.copy.includes('install')?'your terminal':'Codex');
 const status=button.closest('.quick-install')?.querySelector('.quick-status');
 try{await navigator.clipboard.writeText(value);toast.textContent='Copied. Paste it into '+destination+'.';if(status)status.textContent='Copied. Paste into '+destination+' to begin setup. Review permission or replacement prompts; this click has not installed anything.'}
 catch{toast.textContent='Copy unavailable. Select the prompt and copy it manually.';if(status)status.textContent=toast.textContent;const range=document.createRange();range.selectNodeContents(source);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range)}
 toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove('show'),4500);
}));

// Native controls remain available if JavaScript cannot initialize.
const heroVideo=document.getElementById('hero-video');
const heroToggle=document.getElementById('hero-toggle');
const heroFallback=document.getElementById('hero-fallback');
if(heroVideo&&heroToggle&&heroFallback){
 const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
 heroVideo.muted=true;heroVideo.controls=false;heroToggle.hidden=false;
 function updateFilmButton(){heroToggle.textContent=heroVideo.paused?'Play film':'Pause film';heroToggle.setAttribute('aria-label',heroVideo.paused?'Play hero film':'Pause hero film')}
 function respectMotion(){if(reducedMotion.matches){heroVideo.autoplay=false;heroVideo.pause();heroVideo.currentTime=0}else{heroVideo.autoplay=true;heroVideo.play().catch(updateFilmButton)}updateFilmButton()}
 heroToggle.addEventListener('click',()=>{if(heroVideo.paused)heroVideo.play().catch(updateFilmButton);else heroVideo.pause()});
 heroVideo.addEventListener('play',updateFilmButton);heroVideo.addEventListener('pause',updateFilmButton);
 function showFilmFallback(){heroVideo.hidden=true;heroFallback.hidden=false;heroToggle.hidden=true}
 heroVideo.addEventListener('error',showFilmFallback);heroVideo.querySelector('source').addEventListener('error',showFilmFallback);
 reducedMotion.addEventListener('change',respectMotion);respectMotion();
}
