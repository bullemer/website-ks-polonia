const data = await fetch('./room.json').then(r=>r.json());
const budget = await fetch('./budget.json').then(r=>r.json());
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let mode='daily', redraw3D=()=>{}, loungeTone='wine';
const loungeFinishes={wine:{seat:'#743744',back:'#60303a'},cognac:{seat:'#9d6945',back:'#835437'}};
const euro=n=>new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(n);
const modes={daily:['01 / VEREINSALLTAG','Ein Clubzimmer mit Charakter.','12 Tischplätze, vier Loungesessel und vier Barhocker: 20 soziale Sitzplätze plus zwei Arbeitsplätze. Die feste Küche versorgt den L-Tresen mit Stauraum und Bediengang.'],match:['02 / SPORTABEND','Die Wand wird zur Tribüne.','24 Stühle zum TV. Tische auf Wagen, Sessel an der Rückwand geparkt, Hocker gestapelt. L-Tresen mit Bediengang bleibt stehen. Blickwinkel und mögliche Stützenschatten vor Ort mit Sitzprobe prüfen.'],party:['03 / FEIER','Die Küche versorgt den L-Tresen.','L-Tresen mit Stauraum und Personalzugang, vier Stehtische, zwölf Stühle und vier Loungesessel. Ziel: 60–80 Gäste gemischt stehend/sitzend; zulässige Belegung noch offen.']};
function furniture(m){
 const a=[];const add=(type,name,x,z,w,d,h=.75)=>a.push({type,name,x,z,w,d,h});
 add('kitchen','Küche / Ausgabe',4.03,13.05,.64,3.6,.9325);
 add('fridge','Getränke untergebaut',4.03,12.15,.58,.58,.84);add('fridge','Lebensmittel untergebaut',4.03,12.75,.58,.58,.84);
 add('drinkfridge','Getränke 1',.425,12.0,.65,.6,1.85);add('drinkfridge','Getränke 2',.425,13.1,.65,.6,1.85);
 add('desk','Arbeiten 1',1.5,3,1.6,.7);add('desk','Arbeiten 2',1.5,4.4,1.6,.7);
 {add('officechair','Büro',1.5,3.7,.55,.55,.95);add('officechair','Büro',1.5,5.1,.55,.55,.95)}
 add('gymstore','Sportlager niedrig',10.82,1.5,.55,1.05,.8);
 if(m!=='party'){add('bench','Klappbank',9.83,2.8,.55,1.3,.48);add('weights','Leichte Hanteln',10.65,3.95,.65,.5,.65)}
 if(m==='party')add('foldedgear','Bank / Matten gesichert',9.8,1.5,.55,.4,1.3);
 add('cabinet','Vereinslager',2.1,.48,1.3,.62,1.9);
 if(m!=='party')add('cabinet','Stehtische gefaltet',3.9,.48,1.8,.55,1.4);
 // L counter stays offset from the wall in all modes; corner return includes staff access.
 for(const x of[5.4,6.6,7.8])add('bar','Tresen / Stauraum',x,9.475,1.2,.75,.9325);
 add('barcorner','Tresenecke',4.255,9.475,1.09,.75,.9325);add('bargate','Personalzugang',4.03,10.55,.64,1.4,.9325);
 if(m==='daily')for(const x of[5.4,6.2,7,7.8])add('stool','Barhocker',x,8.85,.44,.44,.62);
 else add('cart','Hocker gestapelt',7.55,.55,.6,.8,1.1);
 if(m==='match'){
  for(const x of[4,5.1,6.2,7.3])add('lounge','Sessel geparkt',x,2,.78,.8,.85);
  add('coffee','Couchtisch geparkt',8.2,1.35,.9,.65,.42);
 }else{
  for(const x of[5.2,6.6])for(const z of[2.3,4.3])add('lounge','Clubsessel',x,z,.78,.8,.85);
  add('coffee','Clubtisch',5.9,3.3,.9,.65,.42);
 }
 if(m==='daily')for(const x of[3.50,6.685,8.75]){add('table','Vereinstisch',x,5.95,1.8,.8);for(const dx of[-.45,.45])for(const dz of[-.7,.7])add('chair','Stuhl',x+dx,5.95+dz,.45,.45,.8)}
 if(m==='match')for(const z of[4.65,6.1,7.1])for(const x of[2.75,3.4,5.3,5.95,6.6,8.2,8.85,9.5])add('chair','TV-Platz',x,z,.45,.45,.8);
 if(m==='party'){
  for(const[x,z]of[[3.2,3.4],[8,3],[3.2,5.2],[8.8,5.2]])add('standing','Stehtisch',x,z,.75,.75,1.1);
  for(const x of[2.7,5.8,8.8])for(const dx of[-.4,.4])for(const z of[6.1,7.1])add('chair','Sitzinsel',x+dx,z,.45,.45,.8);
 }
 add('cart',m==='daily'?'3 Tische auf Wagen':'6 Tische auf Wagen',6,.55,1.9,.75,1.2);
 if(m!=='match')add('cart','12 Stühle gestapelt',m==='party'?3.9:7.55,m==='party'?.55:1.3,1.1,.9,1.5);
 return a;
}
const zones=[['GYM OPTIONAL',8.65,1.1,2.5,3.2,'#d2d7c5'],['CLUBLOUNGE',4.65,1.7,2.5,3.15,'#e5d9c6']];
// Keep routes in front of the bar and continue to both doors; rear bar space is operational.
const escapeRects=[[.8,7.4,10.75,1.2],[1.45,8.6,1.2,5.4],[1.15,14,1.2,1.54],[10.35,6,1.2,5.1]];
function svgPlan(electrical=false,lightingOnly=false){
 const W=data.width,D=data.depth,A=data.alcoveWidth,B=data.alcoveDepth;
 const rect=(x,z,w,d,fill,stroke='none',extra='')=>`<rect x="${x}" y="${z}" width="${w}" height="${d}" fill="${fill}" stroke="${stroke}" stroke-width=".035" ${extra}/>`;
 const label=(x,z,t,size=.2,fill='#34473e',anchor='middle')=>`<text x="${x}" y="${z}" font-family="Arial,sans-serif" font-size="${size}" fill="${fill}" text-anchor="${anchor}">${t}</text>`;
 let s=`<svg viewBox="-1.1 -1.3 14.2 18.3" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${electrical?'Elektro-Bedarfsplan':'Möblierungsplan'}"><defs><pattern id="hatch${electrical}" width=".18" height=".18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line y2=".18" stroke="#b8d3c2" stroke-width=".045"/></pattern></defs>`;
 s+=`<path d="M0 0H${W}V${D}H${A}V${D+B}H0Z" fill="#f8f6ef" stroke="#37453e" stroke-width=".1"/>`;
 zones.forEach(([n,x,z,w,d,c])=>{s+=rect(x,z,w,d,c);if(!electrical)s+=label(x+w/2,z+.32,n,.16)});
 escapeRects.forEach(([x,z,w,d])=>s+=rect(x,z,w,d,`url(#hatch${electrical})`));
 s+=label(6,8.08,'FREIHALTEN · VORLÄUFIG 1,20 m',.19,'#438168');
 // Erase wall at two provisional exit openings.
 s+=rect(10.35,10.99,1.2,.23,'#f8f6ef')+rect(1.05,15.43,1.4,.23,'#f8f6ef');
 s+=`<path d="M10.35 11.1v-1.2m0 0a1.2 1.2 0 0 1 1.2 1.2M1.05 15.54v1.2m0 0a1.2 1.2 0 0 0 1.2-1.2" stroke="#438168" fill="none" stroke-width=".035" stroke-dasharray=".1 .08"/>`;
 s+=label(10.95,11.55,'TREPPE',.18)+label(1.8,16.65,'HAUPTEINGANG · AUSSENTREPPE',.18);
 s+=rect(4.56,11.45,6.7,3.65,'#ecece6','#c4c8bf');s+=label(7.85,13.4,'TREPPE / LUFTRAUM',.24)+label(7.85,13.8,'NICHT MÖBLIERBAR',.17);
 for(const z of[.65,3.65,6.65,9.65]){s+=rect(-.08,z,.16,2.15,'#a9c2c7');s+=rect(.13,z,.15,2,'#dbd6ca')}
 s+=rect(8.1,-.08,2.1,.16,'#a9c2c7');for(const w of data.hallWindows)s+=rect(11.47,w.center-w.width/2,.16,w.width,'#a9c2c7');
 for(const[x,z]of data.columns)s+=rect(x-.12,z-.12,.24,.24,'#a97e51','#644b30');
 s+=rect(.25,.25,1.05,.75,'#d6d4cc','#aaa')+label(.78,.68,'Schacht?',.16);
 s+=rect(6.16,10.94,1.88,.12,'#ab293d')+label(7.1,10.85,'85″ TV',.18);
 for(const f of furniture(mode)){
  const c=({kitchen:'#a9855d',fridge:'#c3c5bd',desk:'#b18c62',gymstore:'#494344',cabinet:'#494344',cart:'#b9b7af',weights:'#333c37',bench:'#4d5751',table:'#b18c62',chair:'#e2dace',officechair:'#716b65',standing:'#ba976c',bar:'#ad3945',barcorner:'#ad3945',bargate:'#e7b76c',drinkfridge:'#b7c9ce',foldedgear:'#494344',stool:'#d0a477',lounge:loungeFinishes[loungeTone].seat,coffee:'#b99168'})[f.type];
  s+=rect(f.x-f.w/2,f.z-f.d/2,f.w,f.d,c,'#747a6d','rx=".04"');
  if(!electrical && f.type==='kitchen')s+=`<text x="4.1" y="13.2" transform="rotate(-90 4.1 13.2)" font-size=".19" font-family="Arial" text-anchor="middle">KÜCHE / AUSGABE · 3,60 m</text>`;
  if(!electrical && !['chair','officechair','weights','bench','kitchen','fridge','stool','lounge','bargate','barcorner','drinkfridge'].includes(f.type))s+=label(f.x,f.z+.07,f.name,.15,f.type==='cabinet'||f.type==='gymstore'?'#fff':'#25332b');
 }
 const nc=data.network.cabinet, ap=data.network.ap, reserve=data.network.apReserve;
 s+=rect(nc.x-nc.width/2,nc.z-nc.depth/2,nc.width,nc.depth,'#347d83','#20555b')+label(nc.x,.82,'N01 · Wandschrank',.16,'#20555b');
 s+=`<circle cx="${ap.x}" cy="${ap.z}" r=".17" fill="#347d83"/>`+label(ap.x,ap.z-.28,'AP1 · WLAN',.16,'#20555b');
 if(electrical&&!lightingOnly){
  s+=`<path d="M2.1 .3H.4V10.6H7.1V11.02M.4 3.21H.08M.4 3.39H.08M2.1 .3H5.6V5M5.6 .3H8.8V8" stroke="#237a88" stroke-width=".04" stroke-dasharray=".12 .08" fill="none"/>`;
  s+=`<circle cx="${reserve.x}" cy="${reserve.z}" r=".15" fill="none" stroke="#237a88" stroke-width=".03"/>`+label(reserve.x+.3,reserve.z-.2,'AP2 Reserve',.16,'#20555b');
  s+=label(7.1,10.35,'2 × LAN TV',.16,'#20555b');
 }
 s+=label(10.65,7.5,'HALLE →',.18,'#4d7982');
 s+=label(6.7,10.55,'BEDIENBEREICH · ca. 1,25 m',.16,'#ab653c');
 s+=label(4.03,10.5,'KLAPPE',.13,'#824e17');
 s+=label(.425,12.08,'K1',.16)+label(.425,13.18,'K2',.16);
 s+=rect(.8,11.55,.6,2.05,'#f1e6d0')+label(1.1,13.8,'Bedienen',.13,'#824e17');
 for(const z of[12,13.1])s+=`<path d="M.75 ${z-.3}h.6M1.35 ${z-.3}a.6 .6 0 0 1 -.6 .6" fill="none" stroke="#b28249" stroke-width=".025" stroke-dasharray=".07 .06"/>`;
 s+=label(2.95,14.6,'ABHOLEN',.17)+label(2.8,11.8,'ZUBEREITEN',.17);
 if(electrical){
  s+=`<path d="M.4 1.65V.16H11.35V10.6M.4 1.65V10.6H10.1M4.25 10.6V14.8" stroke="#bd8d39" stroke-width=".035" stroke-dasharray=".12 .1" fill="none"/>`;
  for(const p of (lightingOnly?[]:data.sockets)){
   let x=p.x,z=p.z;
   if(['E21','E22'].includes(p.id))z-=.5;
   if(p.id==='E08'){x=-.35;z=3.0;}if(p.id==='E09'){x=.65;z=3.55;}
   if(p.id==='E10')x-=.45;if(p.id==='E11')x+=.45;
   if(['E04','E06','E07'].includes(p.id))x-=1.1;if(p.id==='E05')x-=1.7;
   s+=`<path d="M${p.x} ${p.z}L${x} ${z}" stroke="#9c5360" stroke-width=".018"/><circle cx="${x}" cy="${z}" r=".16" fill="#af2d3d"/>`+label(x,z+.05,p.id.slice(1),.14,'#fff');
   s+=rect(x-.34,z+.18,.68,.18,'#fffdf5')+label(x,z+.32,`${p.count}× · ${Math.round(p.height*100)} cm`,.125,'#8c2a3d');
  }
  for(const l of data.lights){
   s+=l.type==='linear'?rect(l.x-.6,l.z-.08,1.2,.16,'#e3b344','#a9812c'):l.type==='kitchenlight'?rect(l.x-.06,l.z-.55,.12,1.1,'#e3b344','#a9812c'):`<circle cx="${l.x}" cy="${l.z}" r=".13" fill="#e3b344" stroke="#a9812c" stroke-width=".025"/>`;
   if(lightingOnly)s+=label(l.x,l.z-.2,l.group,.16,'#885d0f');
  }
  for(const sw of data.switches)s+=rect(sw.x-.08,sw.z-.08,.16,.16,'#367a98')+label(sw.x-.22,sw.z-.22,sw.id+' · '+Math.round(sw.height*100)+' cm',.15,'#20536b');
  s+=lightingOnly?label(6.5,1.25,'GELB: LEUCHTEN · HÖHEN SIEHE LISTE',.15,'#885d0f'):label(6.5,1.25,'BLAU GESTRICHELT: DATEN · SCHEMATISCH',.15,'#237a88');
  for(const x of[4.532,7.717])s+=`<path d="M${x} .25V5.6" stroke="#bd8d39" stroke-width=".025" stroke-dasharray=".1 .1" fill="none"/>`;
 }
 s+=`<path d="M0 -.55H11.55M0 -.7V-.4M11.55 -.7V-.4M12.1 0V11.1M11.95 0H12.25M11.95 11.1H12.25" stroke="#858f82" stroke-width=".025"/>`;
 s+=label(5.7,-.7,'11,550 m · Breitenkette im Plan',.25)+`<text x="12.45" y="6" font-size=".22" font-family="Arial" transform="rotate(90 12.45 6)">ca. 11,10 m · Annahme</text>`;
 s+=label(.15,-.15,'0 / 0',.17)+label(6,16,'KONZEPT · ALLE POSITIONEN VOR ORT PRÜFEN',.18);
 s+=rect(8.5,15.3,1,.08,'#34473e')+rect(9.5,15.3,1,.08,'#a6afa2')+label(8.5,15.65,'0',.18)+label(10.5,15.65,'2 m',.18);
 return s+'</svg>';
}
function refresh(){const[badge,title,copy]=modes[mode];$('#mode-tag').textContent=badge;$('#mode-title').textContent=title;$('#mode-copy').textContent=copy;$$('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',b.dataset.mode===mode)});$('#floorplan').innerHTML=svgPlan();$('#electric-plan').innerHTML=svgPlan(true);$('#lighting-plan').innerHTML=svgPlan(true,true);redraw3D()}
$('#lounge-tone').onchange=e=>{loungeTone=e.target.value;$('.palette-chair').style.background=loungeFinishes[loungeTone].seat;refresh()};
$$('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;refresh()});
$$('[data-tab]').forEach(b=>b.onclick=()=>{$$('[data-tab]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',x===b)});$$('.panel').forEach(x=>x.classList.toggle('active',x.id===b.dataset.tab));window.dispatchEvent(new Event('resize'))});
$$('.print').forEach(b=>b.onclick=()=>window.print());
$('#socket-rows').innerHTML=data.sockets.map(p=>`<tr><td>${p.id} · ${p.name}</td><td>${p.x.toFixed(2)} / ${p.z.toFixed(2)}</td><td>${p.height.toFixed(2)}</td><td>${p.count}</td><td>${p.circuit}<small>${p.note}</small></td></tr>`).join('')+`<tr><td>Summe</td><td colspan="4">${data.sockets.reduce((s,p)=>s+p.count,0)} Einzelsteckplätze an ${data.sockets.length} Positionen; Netzwerk, Schalter und Leuchten zusätzlich.</td></tr>`;
$('#budget-rows').innerHTML=budget.map(([name,phase,q,lo,hi,note])=>`<tr><td>${name}</td><td>${phase}</td><td>${q}</td><td>${euro(q*lo)}–${euro(q*hi)}</td><td>${note}</td></tr>`).join('');
const low=budget.reduce((s,r)=>s+r[2]*r[3],0),high=budget.reduce((s,r)=>s+r[2]*r[4],0);
$('#subtotal').textContent=`${euro(low)}–${euro(high)}`;$('#total').textContent=`${euro(low*1.2)}–${euro(high*1.2)}`;
function costs(){const d=Math.max(0,Number($('#donation').value)||0);$('#net').textContent=`Rest inkl. Reserve: ${euro(Math.max(0,low*1.2-d))}–${euro(Math.max(0,high*1.2-d))}`};$('#donation').oninput=costs;costs();
$('#photos').innerHTML=['183102','183104','183109','183113','183118','183120','183136','183138'].map(id=>`<a href="assets/20261005_${id}.jpg" target="_blank"><img loading="lazy" src="assets/20261005_${id}.jpg" alt="Bestandsfoto Clubraum ${id}"><span>Bestand · ${id}</span></a>`).join('');
refresh();
try{
 const THREE=await import('three');const{OrbitControls}=await import('./vendor/OrbitControls.js');const{GLTFExporter}=await import('./vendor/GLTFExporter.js');
 const view=$('#viewport'),scene=new THREE.Scene();scene.background=new THREE.Color('#e7e8df');
 const camera=new THREE.PerspectiveCamera(42,1,.1,150);const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;view.appendChild(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=4;controls.maxDistance=42;controls.maxPolarAngle=Math.PI/2-.02;
 function reset(){controls.minDistance=4;const k=view.clientWidth/view.clientHeight>1.3?.74:1;camera.position.set(5.5+15.5*k,.5+20.5*k,6.6-23.6*k);controls.target.set(5.5,.5,6.6);controls.update()}reset();$('#reset').onclick=reset;$('#bar-view').onclick=()=>{camera.position.set(6.5,5.4,3.7);controls.target.set(7.1,1.1,10.2);controls.update()};$('#lounge-view').onclick=()=>{camera.position.set(3,3.4,5.4);controls.target.set(5.9,.45,3.3);controls.update()};$('#network-view').onclick=()=>{controls.minDistance=.8;camera.position.set(4.2,3.3,3.6);controls.target.set(2.1,2.35,.3);controls.update()};$('#kitchen-view').onclick=()=>{camera.position.set(-1,5.8,18.5);controls.target.set(2.25,.9,13.3);controls.update()};
 scene.add(new THREE.HemisphereLight(0xffffff,0x8b8b73,2.5));const sun=new THREE.DirectionalLight(0xfff1d9,3);sun.position.set(5,18,-8);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-20,right:20,top:20,bottom:-20,far:65});sun.shadow.bias=-.0005;scene.add(sun);scene.add(sun.target);sun.target.position.set(5,0,6);
 const model=new THREE.Group();model.name='Polonia_concept_metres_unverified';model.userData={status:'Concept only; survey required',units:'metres',sourceArea:147.79};scene.add(model);
 const base=new THREE.Group(),furn=new THREE.Group(),roof=new THREE.Group(),electrical=new THREE.Group(),routes=new THREE.Group();model.add(base,furn,roof,electrical,routes);const lights=new THREE.Group();lights.name='Industrial lighting concept';model.add(lights);roof.visible=false;electrical.visible=true;
 const mats={};const logoTexture=await new THREE.TextureLoader().loadAsync('./assets/original-logo.png');logoTexture.colorSpace=THREE.SRGBColorSpace;mats.officialLogo=new THREE.MeshBasicMaterial({map:logoTexture,side:THREE.DoubleSide});let storageOpen=false;
 function badge(g,x,y,z,w,rot=0){const h=w*logoTexture.image.height/logoTexture.image.width;const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),mats.officialLogo);m.position.set(x,y,z);m.rotation.y=rot;m.name='Original KS Polonia logo';g.add(m);return m}
 function mat(c){return mats[c]??=(new THREE.MeshStandardMaterial({color:c,roughness:.85}))}
 function box(g,n,x,y,z,w,h,d,c){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat(c));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;m.name=n;g.add(m);return m}
 function cyl(g,n,x,y,z,r,h,c){const m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,32),mat(c));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;m.name=n;g.add(m);return m}
 function sign(g,text,x,y,z,w,h,ry=0,bg='#ae2c3d',fg='#fff7e7'){
  const c=document.createElement('canvas');c.width=1024;c.height=256;const ctx=c.getContext('2d');ctx.fillStyle=bg;ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle=fg;ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='bold 60px Arial';ctx.fillText(text,512,128,950);const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:tex,side:THREE.DoubleSide}));m.position.set(x,y,z);m.rotation.y=ry;m.name=text;g.add(m);return m;
 }
 box(base,'Main floor',5.775,-.13,5.55,11.55,.26,11.1,'#b9b8ae');box(base,'Entrance alcove',2.2,-.13,13.32,4.4,.26,4.44,'#b9b8ae');
 box(base,'Gym optional 8m2',9.9,.02,2.7,2.5,.04,3.2,'#4b4847');
 // Cutaway shell: low walls are intentional; openings are schematic.
 box(base,'Back cutaway wall',5.775,.32,-.12,11.79,.64,.24,'#c7c5b8');box(base,'East cutaway wall',11.67,.32,5.55,.24,.64,11.1,'#c7c5b8');
 for(const z of[.3,3.3,6.3,9.3,11.1])box(base,'Window pier',-.12,1.6,z,.24,3.2,.42,'#c7c5b8');
 box(base,'West sill wall',-.12,.43,5.55,.24,.86,11.1,'#c7c5b8');box(base,'West lintel',-.12,3.3,5.55,.24,.25,11.1,'#c7c5b8');
 const glass=new THREE.MeshStandardMaterial({color:'#aac6c7',transparent:true,opacity:.22,roughness:.2,side:THREE.DoubleSide});mats.sharedGlass=glass;
 for(const z of[1.65,4.65,7.65,10.3]){const len=z===10.3?1.1:2.35;const m=new THREE.Mesh(new THREE.BoxGeometry(.04,2.1,len),glass);m.position.set(-.12,1.95,z);base.add(m);for(const zz of[z-len/2,z,z+len/2])box(base,'Window frame',-.1,1.95,zz,.12,2.15,.045,'#edece2');box(base,'Radiator',.13,.53,z,.18,.58,len*.85,'#e8e7dd')}
 for(const w of data.hallWindows){const z=w.center;
  const m=new THREE.Mesh(new THREE.BoxGeometry(.04,w.height,w.width),glass);m.position.set(11.66,w.sill+w.height/2,z);m.name='Interior viewing window into sports hall';base.add(m);
  for(const zz of[z-w.width/2,z,z+w.width/2])box(base,'Hall window frame',11.65,1.95,zz,.1,2.1,.045,'#e8e7dd');
  for(const y of[.9,3])box(base,'Hall window horizontal',11.65,y,z,.1,.045,2.24,'#e8e7dd');
 }
 sign(base,'SPORTHALLE',11.67,3.23,data.hallWindows[0].center,1.9,.25,-Math.PI/2,'#56796c');
 // Back window / radiator shown as outlines above the cutaway.
 for(const x of[8.1,9.15,10.2])box(base,'Back window frame',x,1.9,-.1,.04,2.05,.08,'#e8e7dd');for(const y of[.9,2.92])box(base,'Back window horizontal',9.15,y,-.1,2.14,.04,.08,'#e8e7dd');box(base,'Back radiator',9.15,.5,.12,2,.55,.18,'#e8e7dd');
 box(base,'Shaft position provisional',.78,1.6,.55,1.05,3.2,.75,'#deded3');
 box(base,'TV wall',7.375,1.7,11.22,5.95,3.4,.24,'#9b9d91');box(base,'Entrance niche right wall',4.52,.7,13.32,.24,1.4,4.44,'#c7c5b8');box(base,'Entrance niche left wall',-.12,.55,13.32,.24,1.1,4.44,'#c7c5b8');
 box(base,'South wall left',.525,.6,15.66,1.05,1.2,.24,'#c7c5b8');box(base,'South wall right',3.425,.6,15.66,1.95,1.2,.24,'#c7c5b8');
 for(const[x,z]of data.columns){box(base,'Timber column 240mm',x,2.05,z,.24,4.1,.24,'#bd925e');box(base,'Column foot',x,.08,z,.26,.16,.26,'#71776e')}
 box(base,'Club red feature',7.1,1.7,11.075,4.6,2.5,.03,'#a82d3e');
 box(base,'TV 85 inch approx',7.1,1.8,11.01,1.91,1.09,.08,'#172523');sign(base,'POLONIA  •  MATCHDAY',7.1,1.8,10.96,1.84,1.02,Math.PI,'#3b292f');box(base,'Soundbar',7.1,1.14,10.98,1,.08,.08,'#222b29');badge(base,5.48,2.2,11.04,.83,Math.PI);
 sign(base,'AUSGANG',10.95,2.4,11.12,.75,.25,Math.PI,'#337b50');sign(base,'EINGANG / AUSGANG',1.75,2.4,15.6,.75,.25,Math.PI,'#337b50');
 // Dedicated wall cabinet above club storage; Wi-Fi radio is outside the cabinet.
 const nc=data.network.cabinet, ap=data.network.ap;
 box(base,'N01 ventilated lockable network cabinet',nc.x,nc.bottom+nc.height/2,nc.z,nc.width,nc.height,nc.depth,'#393739');
 box(base,'N01 inset front',nc.x,2.4,.534,.53,.51,.018,'#625b5c');
 for(const y of[2.2,2.25,2.55,2.6])box(base,'Cabinet ventilation',nc.x,y,.55,.43,.016,.01,'#253234');
 box(base,'Cabinet lock',2.34,2.4,.558,.024,.06,.015,'#d9d5bd');
 sign(base,'N01 · ROUTER / LAN',nc.x,2.4,.561,.47,.095,0,'#263b40');
 cyl(base,'AP1 members WiFi / PoE',ap.x,ap.height,ap.z,.16,.055,'#f5f3e9');
 cyl(base,'AP1 status',ap.x,ap.height-.03,ap.z,.035,.006,'#6cc9ba');
 box(base,'AP1 mounting drop provisional',ap.x,3.74,ap.z,.025,.63,.025,'#9caaa2');
 // Roof simplified as an optional structural layer; actual pitch unknown.
 box(roof,'Main timber beam assumed elevation',5.775,4.03,5.6,11.55,.45,.24,'#b78b57');
 for(const x of[1.5,3.5,5.5,7.5,9.5])box(roof,'Secondary timber assumed',x,4.43,5.55,.15,.26,11.1,'#c59b67');
 for(let x=.3;x<11.5;x+=.3)box(roof,'Metal roof schematic',x,4.75,5.55,.065,.04,11.1,'#afb5ad');
 for(const l of data.lights){
  const y=l.height;
  if(['linear','kitchenlight'].includes(l.type)){
   const w=l.type==='linear'?1.2:.12,d=l.type==='linear'?.12:1.1;
   box(lights,l.group+' black housing',l.x,y,l.z,w,.09,d,'#26302d');box(lights,l.group+' diffuser',l.x,y-.05,l.z,w-.02,.012,d-.02,'#fff0c8');
   for(const delta of[-.4,.4])box(lights,l.group+' suspension',l.x+(l.type==='linear'?delta:0),(y+3.9)/2,l.z+(l.type==='linear'?0:delta),.015,3.9-y,.015,'#3d4440');
  }else if(l.type==='pendant'){
   const shade=new THREE.Mesh(new THREE.CylinderGeometry(.065,.16,.2,32),mat('#29322e'));shade.position.set(l.x,y+.1,l.z);shade.name='L3 industrial shade';lights.add(shade);
   cyl(lights,'L3 recessed diffuser',l.x,y+.01,l.z,.14,.018,'#fff0c8');box(lights,'L3 pendant cable',l.x,(y+4)/2,l.z,.015,4-y,.015,'#3d4440');
  }else if(l.type==='desk'){
   cyl(lights,'L2A task light base',l.x,.80,l.z,.09,.03,'#323d37');box(lights,'L2A adjustable stem',l.x,1.06,l.z,.018,.53,.018,'#323d37');box(lights,'L2A shielded head',l.x-.1,y,l.z,.3,.035,.1,'#323d37');
  }else {box(lights,l.group+' wall fixture',l.x,y,l.z,.18,.2,.16,'#303a34');box(lights,l.group+' diffuser',l.x,y-.11,l.z,.14,.02,.12,'#fff0c8');}
 }
 for(const [x,z] of data.columns){
  box(base,'Column protected surface conduit',x,2.42,z-.145,.04,3.06,.04,'#343c38');
  for(const dx of[-.155,.155]){box(base,'Column twin socket black',x+dx,.85,z,.07,.18,.15,'#303935');for(const yy of[.81,.89]){const disc=cyl(base,'Socket face',x+dx*1.23,yy,z,.025,.008,'#a1aaa3');disc.rotation.z=Math.PI/2;}}
 }
 function wallRotation(p){return p.x<.3?Math.PI/2:p.x>11?-Math.PI/2:(p.x>4.2&&p.x<4.4&&p.z>11.1)?-Math.PI/2:p.z>10.9?Math.PI:0;}
 for(const sw of data.switches){const g=new THREE.Group();g.position.set(sw.x,sw.height,sw.z);g.rotation.y=wallRotation(sw);base.add(g);box(g,sw.id+' '+sw.name,0,0,0,.085,.085,.055,'#303935');box(g,'Switch rocker',0,0,.031,.055,.055,.012,'#65726a');sign(electrical,sw.id+' · 105 cm',sw.x,sw.height+.15,sw.z,.4,.09,wallRotation(sw),'#275e70');}


 for(const[x,z,w,d]of escapeRects){const m=box(routes,'Provisional clear route',x+w/2,.013,z+d/2,w,.025,d,'#76a286');m.material=new THREE.MeshStandardMaterial({color:'#6caa87',transparent:true,opacity:.3,roughness:1});m.castShadow=false}
 for(const p of data.sockets){
  const rot=wallRotation(p);
  if(!['E21','E22'].includes(p.id)){
   const g=new THREE.Group();g.position.set(p.x,p.height,p.z);g.rotation.y=rot;g.name=p.id+' '+p.name;base.add(g);
   const cols=Math.min(p.count,2),rows=Math.ceil(p.count/cols);
   box(g,'Graphite surface socket housing',0,0,0,cols*.075+.018,rows*.075+.018,.06,'#303935');
   for(let i=0;i<p.count;i++){const xx=(i%cols-(cols-1)/2)*.075,yy=(Math.floor(i/cols)-(rows-1)/2)*.075;const face=cyl(g,'Socket face',xx,yy,.035,.025,.008,'#c0c6bc');face.rotation.x=Math.PI/2;for(const dx of[-.01,.01])box(g,'Socket opening',xx+dx,yy,.041,.006,.009,.006,'#27352e');}
  }
  sign(electrical,p.id+' · '+Math.round(p.height*100)+' cm',p.x,p.height+.18,p.z,.44,.095,rot,'#a23243');
 }

 function chair(g,f,office=false){const c=office?'#716b65':'#e2dace';box(g,f.name,f.x,.44,f.z,f.w,.07,f.d,c);const face=(mode==='daily'&&f.type==='chair'&&[6.65].some(z=>Math.abs(z-f.z)<.01))?1:-1;box(g,'Chair back',f.x,.68,f.z+face*.19,f.w,.35,.045,c);for(const dx of[-.17,.17])for(const dz of[-.17,.17])box(g,'Chair leg',f.x+dx,.22,f.z+dz,.035,.42,.035,'#39423b')}
 function table(g,f){box(g,f.name,f.x,f.h,f.z,f.w,.055,f.d,f.type==='desk'?'#b18c62':'#b18c62');for(const dx of[-f.w/2+.12,f.w/2-.12])for(const dz of[-f.d/2+.1,f.d/2-.1])box(g,'Table leg',f.x+dx,f.h/2,f.z+dz,.045,f.h,.045,'#323b35')}
 function clearGroup(g){const geos=new Set(),customMats=new Set();g.traverse(o=>{if(o.geometry)geos.add(o.geometry);if(o.material&&!Object.values(mats).includes(o.material))customMats.add(o.material)});g.clear();geos.forEach(v=>v.dispose());customMats.forEach(v=>{v.map?.dispose();v.dispose()})}
 redraw3D=()=>{
  clearGroup(furn);
  for(const f of furniture(mode)){
   if(['table','desk','coffee'].includes(f.type)){table(furn,f);if(f.type==='desk'&&mode!=='party'){box(furn,'Laptop',f.x,.79,f.z,.4,.03,.28,'#3a433e');box(furn,'Laptop display',f.x,.96,f.z-.12,.4,.3,.025,'#24352f')}}
   else if(['chair','officechair'].includes(f.type))chair(furn,f,f.type==='officechair');
   else if(['bar','barcorner'].includes(f.type)){
    const w=f.w,d=f.d;
    box(furn,'Tresenfront',f.x,.455,f.z-d/2+.29,w-.04,.83,.08,'#363235');
    for(const dx of[-w/2+.04,w/2-.04])box(furn,'Schrankseite',f.x+dx,.455,f.z+.125,.08,.83,d-.31,'#363235');
    box(furn,'Arbeitsplatte',f.x,.91,f.z,w,.045,d,'#b18c62');
    for(const y of[.14,.43,.7])box(furn,'Verstellbarer Fachboden',f.x,y,f.z+.125,w-.16,.035,d-.37,'#c7b694');
    if(storageOpen){
     for(let i=0;i<4;i++)cyl(furn,'Tellerstapel',f.x-w*.22,.735+i*.025,f.z+.125,.12,.022,'#f6f2dd');
     for(const dx of[0,w*.23])for(const dz of[-.06,.08])cyl(furn,'Tassen / Gläser',f.x+dx,.5,f.z+.125+dz,.047,.1,'#e2dfce');
     box(furn,'Besteckbox',f.x,.2,f.z+.125,w*.65,.07,.18,'#a58056');
    }else{
     for(const dx of[-w*.22,w*.22]){box(furn,'Schiebetür Personal-Seite',f.x+dx,.5,f.z+d/2-.02,w*.43,.77,.035,'#494344');box(furn,'Griff',f.x+dx,.58,f.z+d/2+.008,.12,.025,.02,'#b9bba6')}
    }
    if(f.type==='bar'&&Math.abs(f.x-6.6)<.01)badge(furn,f.x,.57,f.z-d/2+.248,.4,Math.PI);
   }
   else if(f.type==='bargate'){
    // Hinged counter flap: raised for access, closed to show the L-shaped worktop.
    if(storageOpen)box(furn,'Gesicherte hochgeklappte Thekenklappe',f.x,1.61,9.8725,.64,1.4,.045,'#b18c62');
    else box(furn,'Hochklappbarer Personalzugang',f.x,.91,f.z,f.w,.045,f.d,'#b18c62');
   }
   else if(f.type==='drinkfridge'){
    box(furn,'Getraenkekuehlschrank',f.x,.925,f.z,f.w,1.85,f.d,'#393739');
    const doorX=f.x+f.w/2+.01;
    const door=box(furn,'Glastuer',doorX,.99,f.z,.025,1.57,f.d-.08,'#afc7bd');door.material=glass;
    for(const z of[f.z-f.d/2+.025,f.z+f.d/2-.025])box(furn,'Tuerrahmen',doorX,.99,z,.035,1.64,.04,'#adb6a5');
    box(furn,'Kuehlschrankgriff',doorX+.03,1.1,f.z+.2,.04,.3,.035,'#d1d4c6');
    for(const y of[.35,.7,1.05,1.4]){box(furn,'Flaschenboden',f.x,y,f.z,.53,.025,.5,'#bbc8b7');for(const z of[f.z-.15,f.z,f.z+.15])cyl(furn,'Getraenkeflasche',f.x+.2,y+.12,z,.042,.22,'#75945f')}
    sign(furn,'GETRÄNKE',doorX+.02,1.78,f.z,.52,.12,Math.PI/2,'#393739');
   }
   else if(f.type==='stool'){cyl(furn,'Bar stool seat',f.x,.62,f.z,.22,.07,'#b18c62');for(const dx of[-.14,.14])for(const dz of[-.14,.14])box(furn,'Stool leg',f.x+dx,.30,f.z+dz,.035,.58,.035,'#363235')}
   else if(f.type==='lounge'){
    box(furn,f.name,f.x,.34,f.z,.74,.22,.76,loungeFinishes[loungeTone].seat);
    const back=f.z<4?-.32:.32;
    box(furn,'Lounge back',f.x,.65,f.z+back,.74,.48,.13,loungeFinishes[loungeTone].seat);
    for(const dx of[-.34,.34])box(furn,'Lounge arm',f.x+dx,.5,f.z,.1,.25,.72,loungeFinishes[loungeTone].back);
    for(const dx of[-.28,.28])for(const dz of[-.28,.28])box(furn,'Lounge leg',f.x+dx,.1,f.z+dz,.04,.2,.04,'#38463c');
   }
   else if(f.type==='standing'){cyl(furn,'Standing tabletop',f.x,1.1,f.z,.375,.06,'#b18c62');cyl(furn,'Standing leg',f.x,.55,f.z,.045,1.1,'#303d36');cyl(furn,'Standing base',f.x,.04,f.z,.29,.05,'#303d36')}
   else if(f.type==='kitchen'){
    for(let i=0;i<6;i++){const z=11.55+i*.6;if(![1,2].includes(i)){box(furn,'Kitchen module',4.03,.44,z,.6,.85,.58,'#393739');box(furn,'Handle',3.71,.75,z,.025,.025,.2,'#b4b5a5')}}
    box(furn,'Kitchen worktop',f.x,.91,f.z,f.w,.045,f.d,'#b18c62');box(furn,'Sink',4.03,.94,13.35,.4,.025,.47,'#b5beb5');cyl(furn,'Tap',4.23,1.07,13.35,.025,.28,'#858e86');box(furn,'Coffee maker',4.02,1.1,11.55,.28,.34,.27,'#242e29');box(furn,'Microwave',4.04,1.4,12.72,.38,.3,.45,'#252f29');box(furn,'Microwave shelf',4.04,1.23,12.72,.4,.04,.55,'#b18c62');
    sign(furn,'KAFFEE · CLUBKÜCHE',4.3,1.95,12.65,2,.28,-Math.PI/2,'#ae2c3d');
    sign(furn,'AUSGABE',3.68,.7,14.55,.48,.18,-Math.PI/2,'#ae2c3d');
   }else if(f.type==='fridge'){box(furn,f.name,f.x,f.h/2,f.z,f.w,f.h,f.d,'#b8c0b7');box(furn,'Undercounter fridge door',f.x-f.w/2-.01,.43,f.z,.035,.76,.54,'#575253');box(furn,'Fridge handle',f.x-f.w/2-.04,.65,f.z+.18,.03,.16,.026,'#dae0d7')}
   else if(f.type==='bench'){box(furn,'Bench pad',f.x,.48,f.z,.5,.1,1.3,'#2b3931');for(const z of[f.z-.48,f.z+.48])box(furn,'Bench support',f.x,.22,z,.45,.44,.07,'#7b857b')}
   else if(f.type==='weights'){box(furn,'Weight shelf',f.x,.35,f.z,f.w,.07,f.d,'#313d33');for(const x of[f.x-.18,f.x+.18]){cyl(furn,'Dumbbell',x,.46,f.z,.085,.17,'#252e29')}}
   else{box(furn,f.name,f.x,f.h/2,f.z,f.w,f.h,f.d,f.type==='cart'?'#acb2a4':'#393739');if(f.type==='gymstore')sign(furn,mode==='party'?'GYM · ZU':'GYM',f.x,.5,f.z+f.d/2+.01,.5,.15,0,'#393739');}
  }
  model.userData.layout=mode;model.userData.loungeFinish=loungeTone;window.poloniaReady=true;
 };
 $('#storage').onchange=e=>{storageOpen=e.target.checked;redraw3D();if(storageOpen){controls.minDistance=.8;camera.position.set(8.4,1.3,10.85);controls.target.set(6.0,.48,9.6);controls.update()}else reset()};
 $('#lights').onchange=e=>{lights.visible=e.target.checked};
 $('#roof').onchange=e=>roof.visible=e.target.checked;$('#electrical').onchange=e=>electrical.visible=e.target.checked;$('#routes').onchange=e=>routes.visible=e.target.checked;
 async function exportModel(){const group=model.clone(true);group.children[2].visible=true;group.children[3].visible=false;group.children[4].visible=false;const result=await new GLTFExporter().parseAsync(group,{binary:true,onlyVisible:true});return result}
 window.exportPolonia=exportModel;
 $('#export').onclick=async()=>{const b=$('#export');b.disabled=true;b.textContent='Export läuft…';try{const result=await exportModel();const url=URL.createObjectURL(new Blob([result],{type:'model/gltf-binary'}));const a=document.createElement('a');a.href=url;a.download=`polonia-${mode}-concept.glb`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}catch(e){console.error(e);alert('Export fehlgeschlagen. Bitte Grundriss und Modelldaten verwenden.')}finally{b.disabled=false;b.textContent='3D-Modell (.glb)'}};
 function resize(){const w=view.clientWidth,h=view.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}window.addEventListener('resize',resize);new ResizeObserver(resize).observe(view);resize();refresh();
 renderer.setAnimationLoop(()=>{if($('#model').classList.contains('active')&&!document.hidden){controls.update();renderer.render(scene,camera)}});
 window.polonia={lights,data,furniture,escapeRects,svgPlan,model,scene,camera,renderer,controls,setMode:m=>{mode=m;refresh()}};
}catch(e){console.error(e);$('#model-error').hidden=false;$('#export').disabled=true;}
