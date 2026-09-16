window.SSAGAssetIntel = (() => {
  const exact = {
    'SSAG — Strategic Systems Advisory Group': ['Umbrella operating ecosystem that packages business models, SOPs, acquisition, automation, dashboards, AI support and recurring services into reusable infrastructure.','License/setup fees, retainers, support subscriptions, royalties where legally structured, and cross-sold services.','Operating ecosystem','Consolidate live data from every production system into one owner view.'],
    'Sentinel Zero LLC': ['Cybersecurity advisory business for risk reviews, remediation planning, ongoing oversight and insurance-readiness workflows.','Assessment/advisory onboarding, monthly retainers, remediation support and referral-channel revenue.','Revenue lane','Keep acquisition, proposal, payment and service delivery connected to one CRM record.'],
    'Employee Call Dispatch Platform': ['Lets employees mark themselves on duty, distributes incoming calls across available staff and gives the owner visibility into availability, appointments and routing.','Monthly software/service fee, setup fee, or licensing to service businesses with distributed staff.','Operating system','Verify live telephony, database persistence, authentication and after-hours behavior end to end.'],
    'QuoteForge Local': ['Creates professional service quotes from a phone, calculates totals and produces customer-ready estimates.','Paid branded setup, white-label setup and recurring support.','Revenue-ready','Drive local service-business prospects into the paid setup offer.'],
    'Retail Arbitrage Business / Retail Arbitrage Command Center': ['Finds discounted or clearance products and evaluates resale opportunities so an operator can prioritize profitable inventory.','Resale profit, membership/access fees, affiliate revenue where lawful, or operator licensing.','Operating tool','Connect reliable local inventory/pricing feeds and track actual sell-through/margin.'],
    'Coupon Optimization System': ['Organizes legitimate coupons, discounts and deal combinations to lower purchase cost.','Affiliate revenue, premium access, lead generation or savings-subscription model.','Operating concept/tool','Add reliable offer feeds and validate expiration/stacking rules automatically.'],
    'AI Receptionist Business': ['Automates call answering, intake, FAQ handling, routing and appointment-oriented front-desk tasks.','Setup fee plus monthly recurring service per business/location.','Revenue lane','Complete carrier/telephony integration and package a standardized onboarding flow.'],
    'AI Calling Service': ['Provides AI-assisted outbound or inbound calling, qualification, appointment setting and follow-up where legally and technically supported.','Usage/setup fees and recurring communication-service subscriptions.','Revenue lane','Finish live calling integration, consent/compliance controls and measurable call-result reporting.'],
    'SSAG Marketplace': ['Presents turnkey businesses, operator opportunities, pricing, licensing information and application/request flows.','License/setup fees, support subscriptions, marketplace fees and lawful royalties.','Monetization platform','Only publish businesses with verified delivery, economics, support capacity and legal review.'],
    'Fintech / Payments / Wallet Business': ['Future embedded-payments layer for merchant checkout, subscriptions, reporting, wallet/card experiences and transaction services through compliant partners.','Platform subscription, transaction margin/revenue share and cross-sell retention.','Future regulated lane','Start with licensed payment rails and real merchant volume before proprietary money-transmission or token issuance.'],
    'SSAG Digital Currency / Token Concept': ['Future ecosystem payment/rewards concept intended to support transactions and loyalty once the payment layer has real usage.','Potential transaction economics and ecosystem retention only after compliant structure exists.','Future regulated lane','Do not issue first; establish payment volume, legal structure, reserves/compliance and licensed partners first.']
  };

  function capability(x){
    if (exact[x.name]) return exact[x.name];
    const n=x.name.toLowerCase(), c=x.category.toLowerCase();
    if(/^(exe|ops|sal|mkt|csm|dlv|qcr|fin|tec|ppl|kdi|plm)-\d{3}\b/i.test(x.name)) { const a=x.name.includes('—')?x.name.split('—').slice(1).join('—').trim():x.name; return [`Step-by-step controlled procedure for ${a.toLowerCase()}, including who performs it, required handoffs and proof of completion.`,`Reduces rework, missed steps and dependence on the founder.`,`Controlled SOP`,`Attach the form/system used to execute it and a measurable completion/quality check.`]; }
    if(c.includes('position manuals')) return [`Defines the ${x.name.replace(' — Position Manual','')} role: responsibilities, authority, workflows, handoffs and performance expectations.`,`Reduces training time, mistakes and management overhead; supports faster scaling.`,`Controlled operating document`,`Link this role to its starter kit, SOPs, KPIs and current seat owner.`];
    if(c.includes('starter')) return [`Onboards and certifies the ${x.name.replace(' — Starter & Certification Kit','')} role with training steps, checklists and authorization criteria.`,`Cuts onboarding time and lowers execution errors when adding staff.`,`Controlled training asset`,`Attach proof-of-training, required systems access and release criteria.`];
    if(c.includes('workstation')) return [`Department binder consolidating procedures, controls, responsibilities and handoffs for ${x.name.replace(' — Department Workstation Binder','')}.`,`Protects continuity and allows departments to operate consistently without relying on memory.`,`Controlled operating binder`,`Keep the binder linked to current SOP versions, forms, KPIs and department owner.`];
    if(c.includes('sops')) { const a=x.name.includes('—')?x.name.split('—').slice(1).join('—').trim():x.name; return [`Step-by-step controlled procedure for ${a.toLowerCase()}, including who performs it, required handoffs and proof of completion.`,`Reduces rework, missed steps and dependence on the founder.`,`Controlled SOP`,`Attach the form/system used to execute it and a measurable completion/quality check.`]; }
    if(c.includes('forms')) { const a=x.name.includes('—')?x.name.split('—').slice(1).join('—').trim():x.name; return [`Controlled record used to document ${a.toLowerCase()} consistently.`,`Creates auditability, reduces disputes and makes operations measurable.`,`Controlled form`,`Connect this form to the SOP that requires it and the storage/retention location.`]; }
    if(c.includes('vercel')) return [`Deployed web application/version supporting ${x.name.replaceAll('_',' ')}.`,`Can support direct sales, lead capture, operations, customer delivery or internal efficiency depending on the app.`,`Deployed project`,`Confirm production route, user flow, data persistence, monetization path and current source owner.`];
    if(c.includes('github')) return [`Source-code repository preserving and controlling the codebase for ${x.name}.`,`Protects ownership, allows maintenance/deployment and increases transferable asset value.`,`Source asset`,`Map the repository to its live deployment, current branch, dependencies and operating owner.`];
    if(c.includes('top-level')){
      if(n.includes('revenue')||n.includes('funnel')) return ['Financial/funnel control system for tracking stages, conversion, cash collection and operating performance.','Improves conversion discipline and shows which revenue activities deserve more resources.','Management control','Feed it actual CRM/payment results instead of estimates.'];
      if(n.includes('command center')) return ['Owner/management workbook for tracking activation, execution, status and priorities.','Saves management time and prevents work from becoming disconnected.','Management control','Connect live system metrics and assign owners/dates to every open item.'];
      if(n.includes('manual')) return ['Controlled manual defining how a role, department or function is intended to operate.','Reduces founder dependence and makes training/replication easier.','Controlled document','Tie each section to current SOPs, systems and accountable owners.'];
      return ['Controlled enterprise document used to standardize, govern or operate part of the SSAG ecosystem.','Improves repeatability, transferability, quality control and enterprise value.','Controlled document','Keep version, owner, related systems and evidence of use attached to the record.'];
    }
    if(c.includes('standalone')){
      if(n.includes('website')) return [`Public-facing website for ${x.name.replace(' Website','')}, used to present the brand, offer and customer contact path.`,`Can generate leads or direct sales when paired with traffic, a clear offer and follow-up.`,`Customer-facing asset`,`Verify the live URL, conversion path, analytics, lead destination and follow-up automation.`];
      if(n.includes('portal')) return ['Purpose-built portal that gives a defined user group access to tools, records or workflows.','Can reduce service labor, improve retention and support recurring subscriptions.','Portal/system','Verify authentication, permissions, data persistence and the customer/employee workflow end to end.'];
      if(n.includes('dashboard')) return ['Dashboard that centralizes status, metrics, actions and links for an owner or operating team.','Saves management time and exposes bottlenecks that affect revenue.','Management system','Replace static numbers with live connected data wherever feasible.'];
      if(n.includes('crm')||n.includes('pipeline')) return ['CRM/pipeline structure for tracking leads, stages, ownership, follow-up and sales outcomes.','Directly protects revenue by preventing leads and follow-ups from being lost.','Revenue operations system','Make it the single source of truth and connect forms, calling, proposals and payments.'];
      if(n.includes('calling')) return ['Calling system covering lead queues, scripts, qualification, call status and follow-up.','Creates appointments and client opportunities from outbound/inbound calling activity.','Revenue operations system','Verify telephony, legal/compliance controls, call logging and CRM handoff.'];
      if(n.includes('arbitrage')) return ['Product-sourcing tool for identifying items that may be acquired locally and resold at a higher price.','Produces resale margin when sourcing, fees and sell-through are favorable.','Commerce tool','Use live inventory, completed-sale data and true net-margin calculations before buying.'];
      if(n.includes('legacy')||n.includes('continuity')) return ['Continuity system for organizing critical records, successor instructions and emergency operating information.','Can be sold as a service and also protects the value of the owner’s businesses.','Continuity asset','Add recurring review dates, accountable successors and secure document-storage references.'];
      return [`Recovered operating asset supporting ${x.name.toLowerCase()} within the ecosystem.`,`Value comes from direct revenue, operational savings, risk reduction or reusable intellectual property depending on how it is activated.`,`Recovered asset`,`Verify current source, live status, owner, revenue role and next dependency before calling it complete.`];
    }
    if(c.includes('businesses')) return [`Business or division model for ${x.name}; intended to package an offer, acquisition method, delivery workflow and recurring economics.`,`Potential revenue comes from its specific service/product, recurring support and cross-sell into the SSAG ecosystem.`,`Business model / venture`,`Confirm offer, pricing, customer, acquisition channel, delivery capacity and payment path before active scale.`];
    return [`Recovered SSAG asset supporting ${x.name.toLowerCase()}.`,`Its business value is revenue generation, cost/time savings, risk reduction or reusable IP.`,`Recovered asset`,`Verify source, owner, live status, dependencies and monetization role.`];
  }

  return { capability };
})();

// Owner Control Audit: inserted automatically so the command center surfaces what the owner should have been told without requiring a separate request.
window.addEventListener('DOMContentLoaded', () => {
  const why = document.querySelector('.panel.why');
  if (!why) return;
  const panel = document.createElement('section');
  panel.className = 'panel';
  panel.id = 'owner-control-audit';
  panel.innerHTML = `
    <div class="eyebrow">OWNER CONTROL AUDIT • ADDED AUTOMATICALLY</div>
    <h2>What was missing from the command center</h2>
    <p class="muted">These are not new business ideas. They are control layers the ecosystem needs so the owner can tell what is live, what is exposed, what makes money, what is duplicated and what is blocking scale.</p>
    <div class="grid">
      <div class="card offer"><span class="badge warn">CRITICAL</span><h3>Private Owner Access</h3><p>The current Master Dashboard is served from public GitHub Pages. Owner-only inventory, gaps and infrastructure clues should be behind authenticated access rather than treated like a public marketing page.</p><div class="next"><b>Action:</b> Move owner intelligence to an authenticated owner portal; keep only public-safe summaries on the public hub.</div></div>
      <div class="card offer"><span class="badge warn">DRIFT</span><h3>Historical vs Current Inventory</h3><p>The 389-item audit is a historical baseline. Current platform state has continued changing, including newer deployments. The baseline must remain frozen while a separate current-state layer tracks additions.</p><div class="next"><b>Action:</b> Preserve 389 as the audited baseline and maintain a dated current inventory above it.</div></div>
      <div class="card offer"><span class="badge warn">SOURCE CONTROL</span><h3>Deployment → Source Mapping</h3><p>The connected Vercel account currently shows 16 projects, but only 2 show a Git repository linked in Vercel. A working URL is not enough; every production deployment needs a canonical source owner.</p><div class="next"><b>Action:</b> Map every Vercel project to one canonical repo/branch and retire orphaned or superseded versions.</div></div>
      <div class="card offer"><span class="badge warn">HEALTH</span><h3>Service Health Monitoring</h3><p>The connected Render account shows 5 web services and none currently has a health-check path configured at the platform level. The CallFlow/outbound/chess code already contains health endpoints, so the monitoring layer is the missing piece.</p><div class="next"><b>Action:</b> Configure Render health checks and surface pass/fail/last-checked status in this owner dashboard.</div></div>
      <div class="card offer"><span class="badge warn">PAYMENTS</span><h3>Live Checkout Readiness</h3><p>The connected Stripe account available here is sandbox/test mode. The make-good products can collect order/invoice requests, but they are not yet instant live-card checkout products.</p><div class="next"><b>Action:</b> Connect/authorize the intended live Stripe account, then replace invoice-request friction with checkout/payment links where appropriate.</div></div>
      <div class="card offer"><span class="badge warn">DATA</span><h3>Universal Lead / CRM Spine</h3><p>Several tools still keep data locally or inside their own workflow. The Arizona Website Opportunity Engine, calling systems, forms, proposals and payments need one shared lead/customer identity.</p><div class="next"><b>Action:</b> Make one CRM/customer ID the spine so lead → call → proposal → payment → onboarding → support is one record.</div></div>
      <div class="card offer"><span class="badge warn">VERSIONING</span><h3>Canonical Version Control</h3><p>Multiple fixed versions, old deployments and duplicate repositories exist. The owner needs one ACTIVE version, one source repo and an explicit RETIRED/HISTORICAL label for older copies.</p><div class="next"><b>Action:</b> Add canonical/retired flags and stop presenting historical copies as equivalent choices.</div></div>
      <div class="card offer"><span class="badge warn">ACTUALS</span><h3>Actual Revenue Telemetry</h3><p>The dashboard explains revenue capability, but it does not yet pull actual collected cash, MRR, pipeline value, close rate, churn and expansion revenue into one executive view.</p><div class="next"><b>Action:</b> Connect payment + CRM actuals; keep projections visually separate from collected revenue.</div></div>
      <div class="card offer"><span class="badge warn">ACCESS</span><h3>Owner vs Employee Permissions</h3><p>The ecosystem contains founder ownership/IP/succession material and employee operating material. Those should never be exposed through the same access level.</p><div class="next"><b>Action:</b> Enforce owner/admin/manager/employee/client roles and expose only the minimum information needed for each role.</div></div>
    </div>
  `;
  why.after(panel);

  const activation = document.createElement('section');
  activation.className = 'panel why';
  activation.innerHTML = `
    <div class="eyebrow">AUTOMATIC OWNER PRIORITY QUEUE</div>
    <h2>Do these in this order — not all businesses at once</h2>
    <div class="grid">
      <div class="card"><span class="badge ready">1 • MONEY NOW</span><h3>Sentinel Zero + Website Opportunity Engine</h3><p>Use the strongest immediate acquisition lanes to create paying customers and proof. Do not dilute the five-person team across dozens of ventures.</p></div>
      <div class="card"><span class="badge ready">2 • CROSS-SELL</span><h3>Automation + Business Operating Systems</h3><p>Once a client exists, solve documented workflow/follow-up problems and increase account value without paying to reacquire the customer.</p></div>
      <div class="card"><span class="badge warn">3 • FINISH CONNECTION</span><h3>AI Communications / CallFlow</h3><p>Finish live telephony, centralized CRM logging, health monitoring and compliance gates before treating calling as fully production-ready.</p></div>
      <div class="card"><span class="badge warn">4 • STANDARDIZE</span><h3>Recurring Support + Live Payments</h3><p>Turn one-time wins into subscriptions, support, payment collection and measurable retention after live payment authorization is connected.</p></div>
      <div class="card"><span class="badge future">5 • AFTER PROOF</span><h3>Turnkey Licensing / Marketplace</h3><p>Package only offers with real customers, margins, SOPs, delivery capacity and legal review. Proof comes before broad operator licensing.</p></div>
      <div class="card"><span class="badge future">6 • LATER</span><h3>Embedded Payments / Crypto</h3><p>Build merchant payment volume on licensed rails first. Proprietary regulated payment/token work belongs after traction, compliance capacity and partners.</p></div>
    </div>
  `;
  panel.after(activation);

  const current = document.createElement('section');
  current.className = 'panel';
  current.innerHTML = `
    <div class="eyebrow">CURRENT PLATFORM STATE • SEP 16 2026 AUDIT</div>
    <h2>Current-state layer above the historical registry</h2>
    <div class="metrics">
      <div class="metric"><strong>16</strong><span>Vercel projects currently visible</span></div>
      <div class="metric"><strong>2 / 16</strong><span>Vercel projects showing Git link</span></div>
      <div class="metric"><strong>5</strong><span>Render web services</span></div>
      <div class="metric"><strong>0 / 5</strong><span>Render platform health-check paths configured</span></div>
      <div class="metric"><strong>TEST</strong><span>Connected Stripe account mode</span></div>
    </div>
    <p class="muted">This layer is intentionally separate from the 389 recovered baseline so historical audit numbers are not silently rewritten when new systems are added.</p>
  `;
  activation.after(current);
});
