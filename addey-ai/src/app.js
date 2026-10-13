const D=await (await fetch("src/data.json")).json(),IMG="src/addey.jpg";
const $=id=>document.getElementById(id),esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>s.toLowerCase().trim(),cap=s=>s.charAt(0).toUpperCase()+s.slice(1);
function theme(t){document.documentElement.dataset.theme=t;try{localStorage.setItem("addey-theme",t)}catch(e){}}
let t0=null;try{t0=localStorage.getItem("addey-theme")}catch(e){}
theme(t0||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"));
document.querySelectorAll(".th").forEach(b=>b.onclick=()=>theme(document.documentElement.dataset.theme=="dark"?"light":"dark"));
const W={"very common":3,"common":2,"less common":1.5,"rare":1},names=[...new Set(D.s.map(x=>norm(x.n)))];
$("kb").innerHTML=`🦠 ${D.d.length} Diseases<br>🌿 ${D.p.length}+ Plants<br>📚 Trusted Sources<br>🇪🇹 Ethiopian Focus`;
let hist=[],saved=new Set();try{saved=new Set(JSON.parse(localStorage.getItem("addey-saved")||"[]"))}catch(e){}
const bot=h=>{$("msgs").insertAdjacentHTML("beforeend",`<div class="bot"><img class="pf" src="${IMG}" alt=""><div class="bub">${h}</div></div>`);$("msgs").scrollTop=1e9};
const me=t=>{$("msgs").insertAdjacentHTML("beforeend",`<div class="me">${esc(t)}</div>`)};
function openChat(){$("welcome").hidden=true;$("chat").hidden=false;if(!$("msgs").children.length)fresh();$("q").focus()}
function fresh(){$("msgs").innerHTML="";bot(`<b>Hello, I am Addey.</b><p>Tell me your symptoms and I will share what is documented about related conditions and Ethiopian traditional plants. Try an example:</p><div class="ex">${["I have fever, chills and headache","persistent cough and night sweats","watery stool and vomiting","abdominal pain and weight loss"].map(x=>`<button data-q="${esc(x)}">${esc(x)}</button>`).join("")}</div>`)}
$("ty").onclick=openChat;
$("sp").onclick=()=>{openChat();listen()};$("mic").onclick=listen;
function listen(){const R=window.SpeechRecognition||window.webkitSpeechRecognition;if(!R){bot("<p>Voice input is not supported in this browser. Please type your symptoms.</p>");return}
 try{const r=new R();r.lang="en-US";r.onresult=e=>{$("q").value=e.results[0][0].transcript;send()};r.onerror=()=>bot("<p>I could not hear you. Please try again or type your symptoms.</p>");r.start()}catch(e){bot("<p>Voice input is unavailable here. Please type your symptoms.</p>")}}
function analyze(text){const t=norm(text);
 const hit=names.filter(n=>t.includes(n)||(n.includes(" ")&&n.split(" ").filter(w=>w.length>3).length&&n.split(" ").filter(w=>w.length>3).every(w=>t.includes(w))));
 const rows=D.d.map(d=>{const ss=D.s.filter(x=>x.d==d.id),tot=ss.reduce((a,x)=>a+(W[norm(x.c)]||1),0),h=ss.filter(x=>hit.includes(norm(x.n)));return{d,h,p:Math.round(100*h.reduce((a,x)=>a+(W[norm(x.c)]||1),0)/tot)}}).filter(r=>r.h.length).sort((a,b)=>b.p-a.p);
 return{hit,rows}}
function send(v){const text=(v??$("q").value).trim();if(!text)return;$("q").value="";me(text);hist.unshift(text);
 const{hit,rows}=analyze(text);
 if(!rows.length){bot("<p>I could not match those words to the symptoms I know. Try describing them differently, for example fever, cough, diarrhea, or abdominal pain.</p>");return}
 const r=rows[0],close=rows.length>1&&r.p-rows[1].p<15,ps=D.p.filter(p=>p.d==r.d.id);
 bot(`<p>I analyzed your symptoms: ${hit.map(cap).join(", ")}.</p>
 ${close?`<p><b>These symptoms overlap several conditions</b>, so I am not giving a single answer. Others in the dataset: ${rows.slice(1,3).map(x=>esc(x.d.name)+" ("+x.p+"%)").join(", ")}.</p>`:""}
 <div class="cond"><span>✓ Possible condition: ${esc(r.d.name)}</span><span class="pill">Symptom match: ${r.p}%</span></div>
 <b>About ${esc(r.d.name)}</b><p>${esc(r.d.desc)}</p><p class="mut" style="color:var(--mut)">${esc(r.d.why)}</p>
 <b>Traditional medicinal plants</b><div class="plants">${ps.map(p=>`<button class="pl" data-p="${p.id}"><i>🌿</i>${esc(p.name)}<small>${esc(p.sci.split(" ").slice(0,2).join(" "))}</small></button>`).join("")}</div><div class="pdet"></div>
 <div class="note">🛡 <b>Important:</b> This AI provides educational information, not a medical diagnosis. Traditional use is not proof of safety or effectiveness. Please consult a healthcare professional${r.d.lvl=="High"?", and seek urgent care if symptoms are severe or worsening":""}.</div>
 <p style="font-size:.78rem;color:var(--mut)">Sources: ${(D.r[r.d.id]||[]).map(x=>`<a href="${esc(x[1])}" target="_blank" rel="noopener" style="color:var(--g)">${esc(x[0])}</a>`).join(" · ")}</p>`)}
$("go").onclick=()=>send();$("q").onkeydown=e=>{if(e.key=="Enter")send()};
$("msgs").onclick=e=>{const el=e.target.closest("button");if(!el)return;
 if(el.dataset.q)return send(el.dataset.q);
 if(el.dataset.p){const p=D.p.find(x=>x.id==el.dataset.p),box=el.closest(".bub").querySelector(".pdet");
  box.innerHTML=`<div class="det"><b>${esc(p.name)}</b> <i>(${esc(p.sci)})</i>${p.loc?`<br>Local name: ${esc(p.loc)}`:""}<br><b>Traditional use:</b> ${esc(p.use)}<br><b>Part &amp; preparation:</b> ${esc(p.part)}: ${esc(p.prep)}<br><b>Regions:</b> ${esc(p.reg)}<br><b>Evidence:</b> ${esc(p.ev)}<br><span style="color:var(--red)">${esc(p.warn)}</span>${p.ref?`<br><a href="${esc(p.ref[1])}" target="_blank" rel="noopener" style="color:var(--g)">${esc(p.ref[0])}</a>`:""}<br><button class="sv" data-s="${p.id}">${saved.has(p.id)?"Saved ✓":"Save plant"}</button></div>`}
 if(el.dataset.s){saved.has(el.dataset.s)?saved.delete(el.dataset.s):saved.add(el.dataset.s);el.textContent=saved.has(el.dataset.s)?"Saved ✓":"Save plant";try{localStorage.setItem("addey-saved",JSON.stringify([...saved]))}catch(e){}}}
$("mb").onclick=()=>$("sb").classList.toggle("open");
$("sb").onclick=e=>{const a=e.target.dataset.a;if(!a)return;document.querySelectorAll("#sb .nb").forEach(b=>b.classList.toggle("on",b==e.target));$("sb").classList.remove("open");
 if(a=="new")fresh();
 if(a=="hist")bot(hist.length?`<b>This session</b><div class="ex">${hist.map(x=>`<button data-q="${esc(x)}">${esc(x)}</button>`).join("")}</div>`:"<p>No searches yet in this session.</p>");
 if(a=="saved")bot(saved.size?`<b>Saved plants</b><div class="plants">${[...saved].map(id=>D.p.find(p=>p.id==id)).filter(Boolean).map(p=>`<button class="pl" data-p="${p.id}"><i>🌿</i>${esc(p.name)}</button>`).join("")}</div><div class="pdet"></div>`:"<p>No saved plants yet. Open a plant card and tap Save plant.</p>");
 if(a=="about")bot("<p>Addey AI organizes disease, symptom, plant and reference data about Ethiopian indigenous medicine into one educational assistant. It retrieves what is in its datasets and does not diagnose. It is a prototype and has not been clinically validated.</p>");
 if(a=="set"){theme(document.documentElement.dataset.theme=="dark"?"light":"dark");bot("<p>Theme switched. You can also use the sun and moon button at the top.</p>")}};
