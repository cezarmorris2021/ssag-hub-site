'use strict';

const STORAGE = {
  pipeline: 'ssag_az_web_pipeline_v2',
  settings: 'ssag_az_web_settings_v2',
  geocode: 'ssag_az_web_geocode_cache_v1'
};

const TERRITORIES = [
  ['Phoenix',33.4484,-112.0740],['Tucson',32.2226,-110.9747],['Mesa',33.4152,-111.8315],
  ['Chandler',33.3062,-111.8413],['Scottsdale',33.4942,-111.9261],['Glendale',33.5387,-112.1860],
  ['Tempe',33.4255,-111.9400],['Peoria',33.5806,-112.2374],['Surprise',33.6292,-112.3679],
  ['Goodyear',33.4353,-112.3582],['Avondale',33.4356,-112.3496],['Buckeye',33.3703,-112.5838],
  ['Casa Grande',32.8795,-111.7574],['Maricopa',33.0581,-112.0476],['Prescott',34.5400,-112.4685],
  ['Prescott Valley',34.6100,-112.3157],['Flagstaff',35.1983,-111.6513],['Yuma',32.6927,-114.6277],
  ['Lake Havasu City',34.4839,-114.3225],['Kingman',35.1894,-114.0530],['Sierra Vista',31.5455,-110.2773],
  ['Nogales',31.3404,-110.9343],['Show Low',34.2542,-110.0298],['Payson',34.2309,-111.3251]
];

const OVERPASS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter'
];

const EXCLUDED_AMENITIES = new Set([
  'school','college','university','library','police','fire_station','townhall','courthouse','community_centre',
  'place_of_worship','post_office','prison','shelter','social_facility','public_building','ranger_station'
]);

const INDUSTRY_WORDS = {
  home: ['contractor','plumber','electrician','roof','hvac','air_conditioning','landscap','handyman','carpenter','painter','construction','cleaning','locksmith','floor','tile','masonry','garden'],
  beauty: ['hair','barber','beauty','salon','spa','nail','cosmetic','massage','tattoo'],
  auto: ['car','auto','vehicle','mechanic','tyre','tire','bodyshop','car_repair','car_wash','motorcycle'],
  food: ['restaurant','cafe','coffee','fast_food','bakery','bar','pub','food','ice_cream','catering'],
  health: ['dentist','doctor','clinic','chiropr','therapy','physio','fitness','gym','optician','pharmacy','veterinary','wellness'],
  professional: ['lawyer','account','insurance','real_estate','financial','consult','tax','architect','engineer','notary','photograph'],
  retail: ['shop','store','boutique','clothes','jewelry','furniture','hardware','electronics','florist','gift','pet','convenience']
};

let liveResults = [];
let pipeline = loadJSON(STORAGE.pipeline, []);
let settings = loadJSON(STORAGE.settings, {setupPrice:799,monthlyPrice:89,callerName:'Cezar',sellerCompany:'SSAG'});
let activeAbort = null;
let activePreviewLead = null;
let toastTimer = null;

const $ = id => document.getElementById(id);

function loadJSON(key, fallback){
  try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; }
  catch { return fallback; }
}
function saveJSON(key, value){ localStorage.setItem(key, JSON.stringify(value)); }
function esc(value=''){
  return String(value).replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
}
function slug(value='business'){
  return String(value).toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,70) || 'business';
}
function money(n){ return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(Number(n)||0); }
function nowISO(){ return new Date().toISOString(); }
function toast(msg){
  const el=$('toast'); el.textContent=msg; el.classList.add('show'); clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>el.classList.remove('show'),2400);
}
function normalizePhone(v=''){ return String(v).split(';')[0].trim(); }
function phoneHref(v=''){ return 'tel:' + normalizePhone(v).replace(/[^+\d]/g,''); }
function cityOf(tags={}, fallback='Arizona'){
  return tags['addr:city'] || tags['addr:town'] || tags['addr:village'] || tags['addr:suburb'] || fallback || 'Arizona';
}
function addressOf(tags={}){
  const line=[tags['addr:housenumber'],tags['addr:street']].filter(Boolean).join(' ');
  const tail=[tags['addr:city']||tags['addr:town']||tags['addr:village'],tags['addr:state']||'AZ',tags['addr:postcode']].filter(Boolean).join(', ');
  return [line,tail].filter(Boolean).join(', ');
}
function categoryOf(tags={}){
  const pairs=[['shop',tags.shop],['craft',tags.craft],['office',tags.office],['amenity',tags.amenity],['healthcare',tags.healthcare],['tourism',tags.tourism],['leisure',tags.leisure]];
  const hit=pairs.find(([,v])=>v);
  return hit ? String(hit[1]).replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase()) : 'Local Business';
}
function isBusinessLike(tags={}){
  if(tags.shop || tags.craft || tags.office || tags.healthcare || tags.tourism) return true;
  if(tags.amenity && !EXCLUDED_AMENITIES.has(tags.amenity)) return true;
  if(tags.leisure && ['fitness_centre','sports_centre','dance','marina'].includes(tags.leisure)) return true;
  return false;
}
function industryMatch(lead, filter){
  if(filter==='all') return true;
  const hay=[lead.category, lead.rawTags?.shop, lead.rawTags?.craft, lead.rawTags?.office, lead.rawTags?.amenity, lead.rawTags?.healthcare, lead.rawTags?.leisure].filter(Boolean).join(' ').toLowerCase();
  return (INDUSTRY_WORDS[filter]||[]).some(w=>hay.includes(w));
}
function scoreLead(lead){
  let n=48;
  if(lead.phone) n+=22;
  if(lead.address) n+=10;
  if(lead.category && lead.category!=='Local Business') n+=10;
  if(lead.email) n+=5;
  if(lead.city && lead.city!=='Arizona') n+=5;
  return Math.min(100,n);
}
function keyOf(lead){ return `${lead.osmType||'x'}:${lead.osmId||''}:${(lead.phone||'').replace(/\D/g,'')}:${lead.name.toLowerCase()}`; }
function dedupe(leads){
  const map=new Map();
  for(const lead of leads){ if(!map.has(keyOf(lead))) map.set(keyOf(lead),lead); }
  return [...map.values()];
}
function elementToLead(el, territory){
  const t=el.tags||{};
  if(!t.name || !isBusinessLike(t)) return null;
  if(t.website || t['contact:website']) return null;
  const phone=normalizePhone(t.phone || t['contact:phone'] || '');
  if(!phone) return null;
  const lat=el.lat ?? el.center?.lat ?? null;
  const lon=el.lon ?? el.center?.lon ?? null;
  const lead={
    id:keyOf({osmType:el.type,osmId:el.id,phone,name:t.name}), osmType:el.type, osmId:el.id,
    name:t.name, phone, email:t.email||t['contact:email']||'', city:cityOf(t,territory), address:addressOf(t),
    category:categoryOf(t), lat, lon, websiteStatus:'Needs Verification', status:'New', previewBuilt:false,
    territory, source:'OpenStreetMap / Overpass', foundAt:nowISO(), rawTags:t
  };
  lead.score=scoreLead(lead);
  return lead;
}
function buildOverpassQuery(lat, lon, radius){
  return `[out:json][timeout:28];(\n`+
    `nwr(around:${radius},${lat},${lon})["name"]["phone"][!"website"][!"contact:website"];\n`+
    `nwr(around:${radius},${lat},${lon})["name"]["contact:phone"][!"website"][!"contact:website"];\n`+
    `);out center tags;`;
}
async function queryOverpass(lat,lon,radius,territory,signal){
  const query=buildOverpassQuery(lat,lon,radius);
  let lastError=null;
  for(const endpoint of OVERPASS){
    try{
      const res=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body:'data='+encodeURIComponent(query),signal});
      if(!res.ok) throw new Error(`Overpass ${res.status}`);
      const data=await res.json();
      return (data.elements||[]).map(el=>elementToLead(el,territory)).filter(Boolean);
    }catch(err){ if(err.name==='AbortError') throw err; lastError=err; }
  }
  throw lastError || new Error('Business-data service unavailable');
}
async function geocodeArizona(term,signal){
  const cache=loadJSON(STORAGE.geocode,{});
  const k=String(term).trim().toLowerCase();
  if(cache[k] && Date.now()-cache[k].ts < 30*86400000) return cache[k];
  const url='https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=us&addressdetails=1&q='+encodeURIComponent(`${term}, Arizona`);
  const res=await fetch(url,{headers:{'Accept':'application/json','Accept-Language':'en'},signal});
  if(!res.ok) throw new Error(`Location lookup ${res.status}`);
  const rows=await res.json();
  if(!rows.length) throw new Error('Location not found in Arizona');
  const item={lat:Number(rows[0].lat),lon:Number(rows[0].lon),label:rows[0].display_name,ts:Date.now()};
  cache[k]=item; saveJSON(STORAGE.geocode,cache); return item;
}
function setSearchState(text,type='idle'){
  const el=$('searchState'); el.textContent=text; el.className='status-pill '+type;
}
function setProgress(show,text='',pct=0,count=''){
  $('progressWrap').classList.toggle('hidden',!show); $('progressText').textContent=text; $('progressCount').textContent=count;
  $('progressBar').style.width=Math.max(0,Math.min(100,pct))+'%';
}
function toggleSearchRunning(running){
  $('searchBtn').disabled=running; $('stopBtn').classList.toggle('hidden',!running); if(!running) activeAbort=null;
}

async function runSearch(){
  const mode=$('searchMode').value, radius=Number($('radiusSelect').value), max=Number($('maxResults').value), industry=$('industryFilter').value;
  liveResults=[]; renderResults(); activeAbort=new AbortController(); toggleSearchRunning(true); setSearchState('Searching','live');
  try{
    if(mode==='statewide'){
      setProgress(true,'Starting statewide sweep…',2,'0 leads');
      const perTerritory=Math.max(3,Math.ceil(max/TERRITORIES.length)+2);
      for(let i=0;i<TERRITORIES.length;i++){
        if(activeAbort.signal.aborted) throw new DOMException('Aborted','AbortError');
        const [name,lat,lon]=TERRITORIES[i];
        setProgress(true,`Searching ${name} (${i+1}/${TERRITORIES.length})…`,Math.round((i/TERRITORIES.length)*100),`${liveResults.length} leads`);
        try{
          let batch=await queryOverpass(lat,lon,radius,name,activeAbort.signal);
          batch=batch.filter(x=>industryMatch(x,industry)).sort((a,b)=>b.score-a.score).slice(0,perTerritory);
          liveResults=dedupe([...liveResults,...batch]).sort((a,b)=>b.score-a.score).slice(0,max);
          renderResults();
        }catch(err){ if(err.name==='AbortError') throw err; console.warn(name,err); }
        await new Promise(r=>setTimeout(r,220));
      }
    }else{
      const term=$('locationInput').value.trim(); if(!term) throw new Error(mode==='zip'?'Enter an Arizona ZIP code.':'Enter an Arizona city or town.');
      setProgress(true,'Locating search area…',10,'');
      const geo=await geocodeArizona(term,activeAbort.signal);
      setProgress(true,'Searching businesses…',35,'');
      let batch=await queryOverpass(geo.lat,geo.lon,radius,term,activeAbort.signal);
      liveResults=dedupe(batch.filter(x=>industryMatch(x,industry))).sort((a,b)=>b.score-a.score).slice(0,max);
      renderResults();
    }
    setProgress(true,'Search complete',100,`${liveResults.length} leads`); setSearchState(`${liveResults.length} found`,'live');
    toast(`${liveResults.length} website opportunities found`);
  }catch(err){
    if(err.name==='AbortError'){setSearchState('Stopped','idle');setProgress(false);toast('Search stopped');}
    else{setSearchState('Search error','error');setProgress(false);toast(err.message||'Search failed');console.error(err);}
  }finally{toggleSearchRunning(false);}
}

function verificationURL(lead){
  const q=`${lead.name} ${lead.city||''} Arizona official website`;
  return 'https://www.google.com/search?q='+encodeURIComponent(q);
}
function existingLead(lead){ return pipeline.find(x=>keyOf(x)===keyOf(lead)); }
function saveLead(lead, overrides={}){
  const key=keyOf(lead), idx=pipeline.findIndex(x=>keyOf(x)===key);
  const merged={...(idx>=0?pipeline[idx]:lead),...lead,...overrides,updatedAt:nowISO()};
  if(idx>=0) pipeline[idx]=merged; else pipeline.unshift(merged);
  saveJSON(STORAGE.pipeline,pipeline); renderPipeline(); renderMetrics(); renderResults(); return merged;
}
function removeLead(key){ pipeline=pipeline.filter(x=>keyOf(x)!==key);saveJSON(STORAGE.pipeline,pipeline);renderPipeline();renderMetrics();renderResults();toast('Lead removed'); }
function setLeadStatus(key,status){ const lead=pipeline.find(x=>keyOf(x)===key); if(!lead)return; lead.status=status; lead.updatedAt=nowISO(); if(status==='Verified No Website')lead.websiteStatus='Verified No Website'; saveJSON(STORAGE.pipeline,pipeline);renderPipeline();renderMetrics();renderResults(); }

function leadCard(lead){
  const saved=existingLead(lead), current=saved||lead, verified=current.websiteStatus==='Verified No Website';
  const addr=current.address||`${current.city||current.territory}, Arizona`;
  return `<article class="lead-card">
    <div class="lead-top"><div><div class="meta"><span class="chip gold">No website listed</span>${verified?'<span class="chip green">Verified</span>':'<span class="chip red">Verify first</span>'}</div><h3 class="lead-title">${esc(current.name)}</h3></div><div class="score"><div><strong>${current.score}</strong><small>/100</small></div></div></div>
    <div class="lead-info">
      <div><span class="label">Category</span>${esc(current.category)}</div>
      <div><span class="label">Phone</span><a href="${esc(phoneHref(current.phone))}">${esc(current.phone)}</a></div>
      <div><span class="label">Location</span>${esc(addr)}</div>
      <div><span class="label">Status</span>${esc(current.status||'New')}</div>
    </div>
    <div class="card-actions">
      <a class="btn secondary small" href="${esc(verificationURL(current))}" target="_blank" rel="noopener">Verify Website</a>
      <button class="btn success small" data-act="verify" data-key="${esc(keyOf(current))}">Mark Verified</button>
      <button class="btn primary small" data-act="build" data-key="${esc(keyOf(current))}">Build Preview</button>
      <a class="btn secondary small" href="${esc(phoneHref(current.phone))}">Call ${esc(current.phone)}</a>
      <button class="btn secondary small" data-act="script" data-key="${esc(keyOf(current))}">Call Script</button>
      <button class="btn secondary small" data-act="save" data-key="${esc(keyOf(current))}">${saved?'Saved ✓':'Save Lead'}</button>
    </div>
  </article>`;
}
function renderResults(){
  const q=$('resultSearch').value.trim().toLowerCase(), sort=$('resultSort').value;
  let rows=liveResults.filter(x=>!q||[x.name,x.city,x.category,x.phone,x.address].join(' ').toLowerCase().includes(q));
  if(sort==='name') rows.sort((a,b)=>a.name.localeCompare(b.name)); else if(sort==='city') rows.sort((a,b)=>(a.city||'').localeCompare(b.city||'')); else rows.sort((a,b)=>b.score-a.score);
  $('resultsEmpty').classList.toggle('hidden',rows.length>0); $('resultsList').innerHTML=rows.map(leadCard).join('');
}
function pipelineRow(lead){
  const statuses=['New','Verify','Verified No Website','Preview Ready','Called','Interested','Follow Up','Sold','Not Fit'];
  return `<article class="pipeline-row">
    <div><div class="pipeline-name">${esc(lead.name)}</div><div class="pipeline-sub">${esc(lead.category)} • ${esc(lead.city||lead.territory||'Arizona')}</div></div>
    <div><a class="btn secondary small" href="${esc(phoneHref(lead.phone))}">☎ ${esc(lead.phone)}</a></div>
    <div><span class="chip ${lead.websiteStatus==='Verified No Website'?'green':'red'}">${esc(lead.websiteStatus||'Needs Verification')}</span></div>
    <div><select data-status-key="${esc(keyOf(lead))}">${statuses.map(s=>`<option ${lead.status===s?'selected':''}>${esc(s)}</option>`).join('')}</select></div>
    <div class="pipeline-actions">
      <button class="btn primary small" data-pipe-act="build" data-key="${esc(keyOf(lead))}">Preview</button>
      <button class="btn secondary small" data-pipe-act="script" data-key="${esc(keyOf(lead))}">Script</button>
      <a class="btn secondary small" target="_blank" rel="noopener" href="${esc(verificationURL(lead))}">Verify</a>
      <button class="btn danger small" data-pipe-act="remove" data-key="${esc(keyOf(lead))}">Remove</button>
    </div>
  </article>`;
}
function renderPipeline(){
  const q=$('pipelineSearch').value.trim().toLowerCase(), filter=$('pipelineStatusFilter').value;
  const rows=pipeline.filter(x=>(filter==='all'||x.status===filter)&&(!q||[x.name,x.city,x.category,x.phone].join(' ').toLowerCase().includes(q)));
  $('pipelineEmpty').classList.toggle('hidden',rows.length>0); $('pipelineList').innerHTML=rows.map(pipelineRow).join('');
}
function renderMetrics(){
  const count=s=>pipeline.filter(x=>x.status===s).length;
  const called=pipeline.filter(x=>['Called','Interested','Follow Up','Sold'].includes(x.status)).length;
  const interested=pipeline.filter(x=>['Interested','Follow Up','Sold'].includes(x.status)).length;
  const sold=count('Sold');
  $('metricLeads').textContent=pipeline.length; $('metricVerified').textContent=pipeline.filter(x=>x.websiteStatus==='Verified No Website').length;
  $('metricPreviews').textContent=pipeline.filter(x=>x.previewBuilt).length; $('metricCalled').textContent=called; $('metricInterested').textContent=interested; $('metricSold').textContent=sold;
  $('metricRevenue').textContent=money(sold*Number(settings.setupPrice||0)); $('metricMrr').textContent=money(sold*Number(settings.monthlyPrice||0));
}

function serviceSet(lead){
  const c=(lead.category||'').toLowerCase();
  if(/barber|hair|beauty|salon|nail|spa/.test(c)) return [['Appointments','Make it easy for local customers to call and book.'],['Services','Show your main services clearly in one place.'],['Local Contact','Mobile-first directions and contact information.']];
  if(/restaurant|cafe|food|bakery|bar|pub/.test(c)) return [['Menu & Offerings','Give customers a clear place to see what you offer.'],['Hours & Location','Help nearby customers find and contact you fast.'],['Call / Order','Turn mobile searches into direct customer action.']];
  if(/auto|car|mechanic|vehicle|tire|tyre/.test(c)) return [['Automotive Service','Present the work your shop performs.'],['Request Service','Give drivers a fast call-to-action.'],['Local Trust','Put your business details in a professional home online.']];
  if(/plumb|electric|roof|hvac|construction|contractor|landscap|clean|paint|carpenter|locksmith/.test(c)) return [['Service Requests','Turn local searches into calls and estimate requests.'],['Service Area','Show customers where you work.'],['Professional Presence','Give referrals a credible place to verify your business.']];
  if(/dent|clinic|doctor|health|chiro|therapy|fitness|veterinary/.test(c)) return [['Appointments','Make contact and appointment requests easy.'],['Services','Explain services in plain language after owner confirmation.'],['Local Information','Place location and phone details where visitors can find them quickly.']];
  return [['What You Offer','Present owner-confirmed products or services clearly.'],['Contact & Quotes','Make it easy for customers to call or request information.'],['Local Visibility','Give the business a dedicated professional destination online.']];
}
function websiteHTML(lead){
  const name=esc(lead.name), phone=esc(lead.phone), city=esc(lead.city||lead.territory||'Arizona'), cat=esc(lead.category||'Local Business'), addr=esc(lead.address||`${lead.city||lead.territory||''}, Arizona`);
  const tel=esc(phoneHref(lead.phone)); const services=serviceSet(lead);
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${name} | ${cat}</title><style>
  *{box-sizing:border-box}body{margin:0;font-family:Inter,Arial,sans-serif;background:#f7fafc;color:#112231}.notice{padding:9px 16px;text-align:center;background:#fff4cf;color:#65521d;font-size:12px}.hero{background:linear-gradient(135deg,#0b2539,#124963);color:white;padding:70px 20px}.wrap{max-width:1050px;margin:auto}.tag{font-size:12px;letter-spacing:.16em;font-weight:800;color:#8ee2ff}.hero h1{font-size:clamp(38px,8vw,72px);line-height:.95;margin:12px 0 18px;max-width:850px}.hero p{font-size:19px;color:#d5e8f1;max-width:680px;line-height:1.55}.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}.btn{display:inline-block;padding:14px 20px;border-radius:12px;text-decoration:none;font-weight:800}.primary{background:#83e7c1;color:#09231c}.secondary{border:1px solid #8ecbdf;color:white}.section{padding:60px 20px}.section h2{font-size:34px;margin:0 0 10px}.lead{color:#586e7d;max-width:700px;line-height:1.55}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:28px}.card{background:white;border:1px solid #dfe9ef;border-radius:18px;padding:24px;box-shadow:0 15px 40px rgba(11,37,57,.06)}.card h3{margin-top:0}.card p{color:#617583;line-height:1.55}.contact{background:#0b2539;color:white}.contact .lead{color:#c6dae6}.info{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:24px}.info div{padding:16px;border:1px solid #2a5067;border-radius:14px}.info span{display:block;color:#92b7ca;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px}.info a{color:white;text-decoration:none;font-weight:800}.foot{text-align:center;padding:24px;color:#788d9a;font-size:12px}@media(max-width:720px){.hero{padding:52px 18px}.section{padding:44px 18px}.grid,.info{grid-template-columns:1fr}.hero p{font-size:17px}}
  </style></head><body><div class="notice">Website concept preview — services, hours, claims and business details must be confirmed by the owner before publication.</div><header class="hero"><div class="wrap"><div class="tag">${cat.toUpperCase()} • ${city.toUpperCase()}</div><h1>${name}</h1><p>A clean, mobile-friendly home for ${name} so customers can quickly understand the business, call, and take the next step.</p><div class="actions"><a class="btn primary" href="${tel}">Call ${phone}</a><a class="btn secondary" href="#contact">Contact Business</a></div></div></header><section class="section"><div class="wrap"><h2>Built for local customers.</h2><p class="lead">This concept focuses on the information customers typically need first. Final service details and wording are confirmed with the owner before launch.</p><div class="grid">${services.map(([h,p])=>`<article class="card"><h3>${esc(h)}</h3><p>${esc(p)}</p></article>`).join('')}</div></div></section><section id="contact" class="section contact"><div class="wrap"><h2>Contact ${name}</h2><p class="lead">Make the next step simple for customers on a phone, tablet, or computer.</p><div class="info"><div><span>Phone</span><a href="${tel}">${phone}</a></div><div><span>Location</span><strong>${addr}</strong></div></div></div></section><footer class="foot">Concept website prepared for ${name}. Owner approval required before public launch.</footer></body></html>`;
}
function compactLead(lead){ return {name:lead.name,phone:lead.phone,city:lead.city,territory:lead.territory,address:lead.address,category:lead.category}; }
function encodePreview(lead){
  const json=JSON.stringify(compactLead(lead)); const bytes=new TextEncoder().encode(json); let bin=''; bytes.forEach(b=>bin+=String.fromCharCode(b)); return btoa(bin).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
function decodePreview(s){
  const padded=s.replace(/-/g,'+').replace(/_/g,'/')+'==='.slice((s.length+3)%4); const bin=atob(padded); const bytes=Uint8Array.from(bin,c=>c.charCodeAt(0)); return JSON.parse(new TextDecoder().decode(bytes));
}
function previewURL(lead){ return location.href.split('#')[0]+'#preview='+encodePreview(lead); }
function renderClientPreviewFromHash(){
  if(!location.hash.startsWith('#preview=')) return false;
  try{
    const lead=decodePreview(location.hash.slice(9)); const html=websiteHTML(lead); document.body.innerHTML=''; document.body.style.margin='0';
    const frame=document.createElement('iframe'); frame.title=`${lead.name} website preview`; frame.style.cssText='border:0;width:100vw;height:100vh;display:block;background:#fff'; frame.srcdoc=html; document.body.appendChild(frame); return true;
  }catch(err){ console.error(err); return false; }
}
function showPreview(lead){
  const saved=saveLead(lead,{previewBuilt:true,previewBuiltAt:nowISO(),status:lead.status==='Sold'?'Sold':'Preview Ready'}); activePreviewLead=saved;
  $('previewTitle').textContent=`${saved.name} — website preview`; $('previewFrame').srcdoc=websiteHTML(saved); $('previewDialog').showModal();
}
function downloadPreview(lead){
  const blob=new Blob([websiteHTML(lead)],{type:'text/html;charset=utf-8'}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`${slug(lead.name)}-website.html`; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),1200);
}
function salesScript(lead){
  const setup=money(settings.setupPrice), monthly=money(settings.monthlyPrice), caller=settings.callerName||'Cezar', company=settings.sellerCompany||'SSAG';
  return `Hi, is this the owner of ${lead.name}?\n\nMy name is ${caller} with ${company}. I was looking at ${lead.category.toLowerCase()} businesses in ${lead.city||lead.territory||'Arizona'}, and I couldn't find a dedicated website in the public listings I checked for ${lead.name}.\n\nI went ahead and built a sample homepage for the business so you can actually see it — no obligation. I can send you the preview right now.\n\nIf you like it, we can finish it, put it live, and manage it starting at ${setup} setup plus ${monthly} per month.\n\nAre you the person who handles the website or marketing?\n\nCALL: ${lead.phone}\n\nIf they already have a website: “Perfect — thanks for correcting me. I was working from a public listing that didn't show it. If you'd like, I can still show you the concept and you can compare it to what you have.”`;
}
function showScript(lead){
  const script=salesScript(lead); $('leadDialogBody').innerHTML=`<p class="eyebrow">BRIEF SALES SCRIPT</p><h2>${esc(lead.name)}</h2><div class="meta"><span class="chip">${esc(lead.category)}</span><span class="chip gold">${esc(lead.phone)}</span></div><p class="muted">Use the verification-safe wording below. It says you couldn't find a website in the public listings checked — not that the business definitely has none.</p><div class="script-box">${esc(script)}</div><div class="dialog-actions"><a class="btn primary" href="${esc(phoneHref(lead.phone))}">Call ${esc(lead.phone)}</a><button type="button" class="btn secondary" id="copyScriptBtn">Copy Script</button><button type="button" class="btn secondary" id="copyShareBtn">Copy Preview Link</button><a class="btn secondary" href="${esc(verificationURL(lead))}" target="_blank" rel="noopener">Verify Website</a></div>`;
  $('leadDialog').showModal();
  $('copyScriptBtn').onclick=()=>navigator.clipboard.writeText(script).then(()=>toast('Script copied'));
  $('copyShareBtn').onclick=()=>{ const saved=saveLead(lead,{previewBuilt:true,status:lead.status==='Sold'?'Sold':'Preview Ready'}); navigator.clipboard.writeText(previewURL(saved)).then(()=>toast('Shareable preview link copied')); };
}

function findByKey(key){ return pipeline.find(x=>keyOf(x)===key) || liveResults.find(x=>keyOf(x)===key); }
function onResultsClick(e){
  const btn=e.target.closest('[data-act]'); if(!btn)return; const lead=findByKey(btn.dataset.key); if(!lead)return;
  if(btn.dataset.act==='save'){saveLead(lead);toast('Lead saved');}
  if(btn.dataset.act==='verify'){saveLead(lead,{websiteStatus:'Verified No Website',status:lead.status==='New'?'Verified No Website':lead.status});toast('Marked verified no website');}
  if(btn.dataset.act==='build') showPreview(lead);
  if(btn.dataset.act==='script') showScript(lead);
}
function onPipelineClick(e){
  const btn=e.target.closest('[data-pipe-act]'); if(!btn)return; const lead=findByKey(btn.dataset.key); if(!lead)return;
  if(btn.dataset.pipeAct==='remove') removeLead(btn.dataset.key);
  if(btn.dataset.pipeAct==='build') showPreview(lead);
  if(btn.dataset.pipeAct==='script') showScript(lead);
}
function exportCSV(){
  const headers=['Business','Phone','Category','City','Address','Website Status','Pipeline Status','Score','Preview Built','Found At'];
  const rows=pipeline.map(x=>[x.name,x.phone,x.category,x.city,x.address,x.websiteStatus,x.status,x.score,x.previewBuilt?'Yes':'No',x.foundAt]);
  const csv=[headers,...rows].map(r=>r.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\n');
  const blob=new Blob([csv],{type:'text/csv'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`ssag-arizona-website-leads-${new Date().toISOString().slice(0,10)}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}
function backup(){
  const payload={version:2,exportedAt:nowISO(),pipeline,settings,geocodeCache:loadJSON(STORAGE.geocode,{})}; const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}); const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`ssag-arizona-opportunity-engine-backup-${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}
function restore(file){
  const r=new FileReader(); r.onload=()=>{try{const data=JSON.parse(r.result);if(!Array.isArray(data.pipeline))throw new Error('Invalid backup');pipeline=data.pipeline;if(data.settings)settings={...settings,...data.settings};saveJSON(STORAGE.pipeline,pipeline);saveJSON(STORAGE.settings,settings);if(data.geocodeCache)saveJSON(STORAGE.geocode,data.geocodeCache);applySettings();renderPipeline();renderMetrics();toast('Backup restored');}catch(err){toast('Could not restore backup');}};r.readAsText(file);
}
function saveSettings(){
  settings={setupPrice:Number($('setupPrice').value)||0,monthlyPrice:Number($('monthlyPrice').value)||0,callerName:$('callerName').value.trim()||'Cezar',sellerCompany:$('sellerCompany').value.trim()||'SSAG'};saveJSON(STORAGE.settings,settings);renderMetrics();
}
function applySettings(){ $('setupPrice').value=settings.setupPrice; $('monthlyPrice').value=settings.monthlyPrice; $('callerName').value=settings.callerName; $('sellerCompany').value=settings.sellerCompany; }
function updateModeUI(){ const custom=$('searchMode').value!=='statewide';$('locationLabel').classList.toggle('hidden',!custom);$('locationLabel').firstChild.textContent=$('searchMode').value==='zip'?'ZIP code':'City / town';$('locationInput').placeholder=$('searchMode').value==='zip'?'85701':'Tucson'; }

function init(){
  if(renderClientPreviewFromHash()) return;
  applySettings();renderResults();renderPipeline();renderMetrics();updateModeUI();
  $('searchBtn').addEventListener('click',runSearch); $('stopBtn').addEventListener('click',()=>activeAbort?.abort());
  $('clearResultsBtn').addEventListener('click',()=>{liveResults=[];renderResults();setProgress(false);setSearchState('Ready','idle');});
  $('searchMode').addEventListener('change',updateModeUI); $('resultSearch').addEventListener('input',renderResults); $('resultSort').addEventListener('change',renderResults);
  $('pipelineSearch').addEventListener('input',renderPipeline); $('pipelineStatusFilter').addEventListener('change',renderPipeline);
  $('resultsList').addEventListener('click',onResultsClick); $('pipelineList').addEventListener('click',onPipelineClick);
  $('pipelineList').addEventListener('change',e=>{const sel=e.target.closest('[data-status-key]');if(sel)setLeadStatus(sel.dataset.statusKey,sel.value);});
  ['setupPrice','monthlyPrice','callerName','sellerCompany'].forEach(id=>$(id).addEventListener('change',saveSettings));
  $('exportBtn').addEventListener('click',exportCSV); $('backupBtn').addEventListener('click',backup); $('restoreInput').addEventListener('change',e=>e.target.files[0]&&restore(e.target.files[0]));
  $('closePreviewBtn').addEventListener('click',()=>$('previewDialog').close());
  $('downloadPreviewBtn').addEventListener('click',()=>activePreviewLead&&downloadPreview(activePreviewLead));
  $('copyPreviewLinkBtn').textContent='Copy Preview Link'; $('copyPreviewLinkBtn').addEventListener('click',()=>activePreviewLead&&navigator.clipboard.writeText(previewURL(activePreviewLead)).then(()=>toast('Shareable preview link copied')));
}

document.addEventListener('DOMContentLoaded',init);
