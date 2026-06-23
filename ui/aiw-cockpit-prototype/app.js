// Simple UI prototype script

// Load runs data
async function loadRuns() {
  const resp = await fetch('fixtures/runs.json');
  return await resp.json();
}

function renderSidebar() {
  const items = document.querySelectorAll('.sidebar li');
  items.forEach(it => {
    it.addEventListener('click', () => {
      document.querySelectorAll('.sidebar li').forEach(el => el.classList.remove('active'));
      it.classList.add('active');
      showPage(it.dataset.page);
    });
  });
}

function showPage(page) {
  const sections = {
    dashboard: renderDashboard,
    runs: renderRunsList,
    analysis: renderAnalysis,
    agents: renderAgents,
    providers: renderProviders,
    context: renderContext,
    settings: renderSettings,
  };
  const content = document.getElementById('content');
  content.innerHTML = '';
  if (sections[page]) sections[page]();
}

function renderDashboard() {
  const content = document.getElementById('content');
  const html = `
    <h2>Dashboard</h2>
    <div class="card-grid">
      <div class="card"><strong>Runs hoje</strong><br><span id="runs-today">0</span></div>
      <div class="card"><strong>Pendentes de revisão</strong><br><span id="pending-reviews">0</span></div>
      <div class="card"><strong>Validações falhas</strong><br><span id="failed-validations">0</span></div>
      <div class="card"><strong>Último erro</strong><br><span id="last-error">-</span></div>
    </div>
    <h3>Runs recentes</h3>
    <div id="recent-runs"></div>
  `;
  content.innerHTML = html;
  loadRuns().then(runs => {
    document.getElementById('runs-today').textContent = runs.filter(r=>new Date(r.started_at).toDateString()===new Date().toDateString()).length;
    document.getElementById('pending-reviews').textContent = runs.filter(r=>r.status==='pending').length;
    document.getElementById('failed-validations').textContent = runs.filter(r=>r.validation==='failed').length;
    const lastErrorRun = runs.find(r=>r.status==='error');
    document.getElementById('last-error').textContent = lastErrorRun ? lastErrorRun.run_id : '-';
    const recent = runs.slice(0,5);
    const recentHtml = recent.map(r=>`<div class="card"><strong>${r.run_id}</strong><br>${r.mission}<br>Status: ${r.status}</div>`).join('');
    document.getElementById('recent-runs').innerHTML = recentHtml;
  });
}

function renderRunsList() {
  const content = document.getElementById('content');
  const html = `
    <h2>Runs List</h2>
    <input type="text" id="filter" placeholder="Filtrar..." style="margin-bottom:1rem; padding:0.3rem; width:200px;">
    <table class="table" id="runs-table">
      <thead><tr><th>Run ID</th><th>Agent</th><th>Mission</th><th>Status</th><th>Started at</th><th>Validation</th><th>Detalhes</th></tr></thead>
      <tbody></tbody>
    </table>
  `;
  content.innerHTML = html;
  const tbody = document.querySelector('#runs-table tbody');
  function populate(runs) {
    tbody.innerHTML = runs.map(r=>`<tr>
      <td>${r.run_id}</td>
      <td>${r.agent}</td>
      <td>${r.mission}</td>
      <td>${r.status}</td>
      <td>${new Date(r.started_at).toLocaleString()}</td>
      <td>${r.validation}</td>
      <td><button data-id="${r.run_id}">Detalhes</button></td>
    </tr>`).join('');
    document.querySelectorAll('#runs-table button').forEach(btn=>{
      btn.addEventListener('click',()=>{showRunDetail(btn.dataset.id);});
    });
  }
  loadRuns().then(runs=>{populate(runs);window.allRuns=runs;});
  document.getElementById('filter').addEventListener('input',e=>{
    const term=e.target.value.toLowerCase();
    const filtered=window.allRuns.filter(r=>Object.values(r).some(v=>String(v).toLowerCase().includes(term)));
    populate(filtered);
  });
}

function showRunDetail(runId) {
  const run = window.allRuns.find(r=>r.run_id===runId);
  if(!run) return;
  const content=document.getElementById('content');
  const html=`
    <h2>Run Detail - ${run.run_id}</h2>
    <p><strong>Agent:</strong> ${run.agent}</p>
    <p><strong>Mission:</strong> ${run.mission}</p>
    <p><strong>Status:</strong> ${run.status}</p>
    <p><strong>Started at:</strong> ${new Date(run.started_at).toLocaleString()}</p>
    <div class="tabs">
      <button data-tab="log">Log</button>
      <button data-tab="diff">Diff</button>
      <button data-tab="handoff">Handoff</button>
      <button data-tab="validator">Validator</button>
      <button data-tab="analysis">Analysis</button>
    </div>
    <div id="tab-content"></div>
    <button id="approve" style="margin-top:1rem;">Approve</button>
    <button id="reject" style="margin-left:0.5rem;">Reject</button>
  `;
  content.innerHTML=html;
  const tabs=document.querySelectorAll('.tabs button');
  tabs.forEach(t=>t.addEventListener('click',()=>{showTab(t.dataset.tab,run);}));
  document.getElementById('approve').addEventListener('click',()=>{run.status='approved'; alert('Approved (simulated)');});
  document.getElementById('reject').addEventListener('click',()=>{run.status='rejected'; alert('Rejected (simulated)');});
  // default tab
  showTab('log',run);
}

function showTab(tab,run) {
  const container=document.getElementById('tab-content');
  let html='';
  if(tab==='log') html=`<pre>${run.log_excerpt||'No log'}</pre>`;
  else if(tab==='diff') html=`<pre>${run.diff_summary||'No diff'}</pre>`;
  else if(tab==='handoff') html=`<pre>${run.handoff||'No handoff'}</pre>`;
  else if(tab==='validator') {
    html=`<ul class="checklist">${run.checks.map(c=>`<li class="${c.result}">${c.name}: ${c.result}</li>`).join('')}</ul>`;
  } else if(tab==='analysis') {
    html=`<p>Status: ${run.analysis?.status||'N/A'}</p><p>Comments: ${run.analysis?.comments||'N/A'}</p>`;
  }
  container.innerHTML=html;
}

function renderAnalysis(){document.getElementById('content').innerHTML='<h2>Analysis (placeholder)</h2>';}
function renderAgents(){document.getElementById('content').innerHTML='<h2>Agents (mocked cards)</h2><div class="card-grid">'+
  ['Hermes Executor','Validator','Integrator','Context Builder','OpenRouter','Local/Ollama futuro'].map(name=>`<div class="card"><strong>${name}</strong></div>`).join('')+'</div>';}
function renderProviders(){document.getElementById('content').innerHTML='<h2>Providers (mocked)</h2><div class="card-grid">'+
  ['OpenRouter','Local/Ollama','Azure','AWS'].map(name=>`<div class="card"><strong>${name}</strong></div>`).join('')+'</div>';}
function renderContext(){
  const content = document.getElementById('content');
  const html = `
    <h2>Context Resilience</h2>
    <ul class="checklist">
      <li class="passed">Compact summary</li>
      <li class="passed">Resume prompt</li>
      <li class="passed">Run state persisted</li>
      <li class="passed">Fallback model</li>
      <li class="passed">/new policy</li>
    </ul>
    <div class="card-grid">
      <div class="card"><strong>Compact summary</strong><br>${run?.analysis?.comments || 'N/A'}</div>
      <div class="card"><strong>Resume prompt</strong><br>Ready for next run.</div>
      <div class="card"><strong>Run state persisted</strong><br>${run?.status || 'N/A'}</div>
      <div class="card"><strong>Fallback model</strong><br>none</div>
      <div class="card"><strong>/new policy</strong><br>Use /new after context pressure.</div>
    </div>
  `;
  content.innerHTML = html;
}

function renderSettings(){document.getElementById('content').innerHTML='<h2>Settings (placeholder)</h2>';}

// Init
document.addEventListener('DOMContentLoaded',()=>{renderSidebar();showPage('dashboard');});
