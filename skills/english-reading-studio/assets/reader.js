'use strict';
const data=JSON.parse(document.getElementById('reading-data').textContent);
let mode='quick';
const tabs=[...document.querySelectorAll('[role=tab]')];
function currentParagraph(){
 const units=[...document.querySelectorAll(`#panel-${mode} [data-pid]`)];
 const threshold=Math.max(parseFloat(getComputedStyle(units[0]).scrollMarginTop)||0,innerWidth>760?document.querySelector('.toolbar').getBoundingClientRect().bottom+20:20)+2;
 if(units[0]?.getBoundingClientRect().top>threshold+80)return null;
 return (units.find(u=>u.getBoundingClientRect().bottom>threshold)||units.at(-1))?.dataset.pid||null;
}
function jump(pid){document.getElementById(`${mode}-${pid}`)?.scrollIntoView({block:'start'});}
function activate(next){
 if(next===mode)return;
 const pid=currentParagraph();
 mode=next;
 tabs.forEach(t=>{const active=t.dataset.mode===mode;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;});
 document.querySelectorAll('[role=tabpanel]').forEach(p=>p.hidden=p.id!==`panel-${mode}`);
 document.querySelectorAll('[data-jump]').forEach(a=>a.href=`#${mode}-${a.dataset.jump}`);
 if(pid)jump(pid);else document.getElementById(`panel-${mode}`).scrollIntoView({block:'start'});
}
tabs.forEach((t,i)=>{t.addEventListener('click',()=>activate(t.dataset.mode));t.addEventListener('keydown',event=>{
 let n;
 if(event.key==='ArrowRight')n=(i+1)%tabs.length;
 if(event.key==='ArrowLeft')n=(i+tabs.length-1)%tabs.length;
 if(event.key==='Home')n=0;if(event.key==='End')n=tabs.length-1;
 if(n!==undefined){event.preventDefault();tabs[n].focus();activate(tabs[n].dataset.mode);}
});});
document.querySelectorAll('[data-jump]').forEach(a=>a.addEventListener('click',event=>{event.preventDefault();jump(a.dataset.jump);}));
document.getElementById('toggle-translation').addEventListener('click',event=>{
 const hidden=document.body.classList.toggle('hide-translations');
 event.currentTarget.textContent=hidden?'显示译文':'隐藏译文';event.currentTarget.setAttribute('aria-pressed',String(hidden));
});
document.getElementById('font-size').addEventListener('change',event=>document.documentElement.style.setProperty('--size',event.target.value+'px'));
let noticeTimer;
function notice(message){const s=document.getElementById('status');s.textContent=message;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>s.textContent='',3500);}
const dialog=document.getElementById('copy-dialog');
document.getElementById('close-dialog').addEventListener('click',()=>dialog.close());
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{
 const index=data.paragraphs.findIndex(p=>p.id===button.dataset.copy);const p=data.paragraphs[index];
 const context=data.paragraphs.slice(Math.max(0,index-1),index+2).map(x=>`${x.id.toUpperCase()}: ${x.original}`).join('\n\n');
 const text=`文章：${data.title}\n目标段落：${p.id.toUpperCase()}\n当前模式：${tabs.find(t=>t.dataset.mode===mode).textContent}\n\n原文与相邻上下文：\n${context}\n\n我的理解：\n我卡住的地方：\n请按上下文解释，区分作者原意与补充背景，保留条件、否定与不确定性。`;
 try{if(!navigator.clipboard)throw Error('clipboard unavailable');await navigator.clipboard.writeText(text);notice('已复制。回到 AI 对话，补充你的理解和问题。');}
 catch{const field=dialog.querySelector('textarea');field.value=text;dialog.showModal();field.focus();field.select();}
}));
