(()=>{
  const anchor=document.getElementById('currentStatePanel')||document.getElementById('healthPanel');
  if(!anchor)return;
  const panel=document.createElement('section'); panel.className='panel';panel.id='live-repo-inventory';
  panel.innerHTML='<div class="eyebrow">LIVE GITHUB INVENTORY • PUBLIC REPOSITORIES</div><h2>Latest source projects — refreshed from GitHub</h2><p class="muted">This live feed shows public source repositories, not proof that an app is deployed or earning revenue. Private repositories and Vercel-only builds are not included. The historical 389-asset baseline remains unchanged.</p><div class="toolbar"><button class="btn ice" id="repo-refresh" type="button">Refresh live inventory</button><span class="muted" id="repo-freshness" role="status">Loading current GitHub repositories…</span></div><div id="repo-metrics" class="metrics"></div><div id="repo-grid" class="grid"></div>';
  anchor.after(panel);
  const refreshBtn=document.getElementById('repo-refresh'),status=document.getElementById('repo-freshness'),metrics=document.getElementById('repo-metrics'),grid=document.getElementById('repo-grid');
  const owners=['cezarmorris2021','datatranferservice-hue'];let busy=false;
  const stamp=x=>{if(!x)return 'Unknown';const d=new Date(x);return isNaN(d.getTime())?'Unknown':d.toLocaleString();};
  function put(parent,tag,cls,label){const el=document.createElement(tag);if(cls)el.className=cls;if(label!==undefined)el.textContent=label;parent.appendChild(el);return el;}
  async function load(){
    if(busy)return;busy=true;refreshBtn.disabled=true;status.textContent='Checking GitHub now…';
    try{
      const results=await Promise.all(owners.map(async owner=>{
        const r=await fetch('https://api.github.com/users/'+encodeURIComponent(owner)+'/repos?per_page=100&sort=updated&type=public',{cache:'no-store',headers:{Accept:'application/vnd.github+json'}});
        if(!r.ok)throw Error('GitHub request '+r.status+' for '+owner);
        const x=await r.json();if(!Array.isArray(x))throw Error('Invalid inventory response for '+owner);
        return x.filter(v=>!v.private);
      }));
      const data=results.flat().sort((a,b)=>new Date(b.pushed_at||b.updated_at)-new Date(a.pushed_at||a.updated_at));
      metrics.replaceChildren();grid.replaceChildren();
      const metric=put(metrics,'div','metric');put(metric,'strong','',String(data.length));put(metric,'span','','Visible public repositories');
      const deployed=put(metrics,'div','metric');put(deployed,'strong','',String(data.filter(x=>x.has_pages).length));put(deployed,'span','','GitHub Pages configured (not verified live)');
      for(const repo of data){
        const card=put(grid,'div','card');put(card,'span','badge',repo.archived?'ARCHIVED SOURCE':'SOURCE REPOSITORY');put(card,'h3','',repo.name);
        put(card,'p','',repo.description||'No repository description supplied.');
        put(card,'p','',repo.owner.login+' • Last code push: '+stamp(repo.pushed_at));
        const a=put(card,'a','btn','View source');a.href=repo.html_url;a.target='_blank';a.rel='noopener noreferrer';
        if(repo.homepage&&/^https:\/\//i.test(repo.homepage)){const h=put(card,'a','btn ice','Website listed by repo');h.href=repo.homepage;h.target='_blank';h.rel='noopener noreferrer';}
      }
      const now=new Date();status.textContent='Last fetched: '+now.toLocaleString()+' • Live GitHub response • '+data.length+' repositories';
    }catch(e){status.textContent='Live inventory unavailable: '+e.message+'. Last verified data cannot be assumed current.';if(!grid.children.length)put(grid,'p','muted','GitHub inventory failed to load. Use the refresh button later.');}
    finally{busy=false;refreshBtn.disabled=false;}
  }
  refreshBtn.addEventListener('click',load);load();
  setInterval(()=>{if(!document.hidden)load();},300000);
})();