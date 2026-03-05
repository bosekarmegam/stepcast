/* stepcast dashboard — app.js */
'use strict';

const API = '';

// ─── State ────────────────────────────────────────────────────────────────────
let currentView = 'runs';

// ─── DOM helpers ─────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ─── Navigation ──────────────────────────────────────────────────────────────
function showView(name) {
  currentView = name;
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  $(`view-${name}`).classList.remove('hidden');
  $(`nav-${name}`).classList.add('active');
  if (name === 'runs') loadRuns();
  if (name === 'stats') loadStats();
}

$('nav-runs').addEventListener('click', e => { e.preventDefault(); showView('runs'); });
$('nav-stats').addEventListener('click', e => { e.preventDefault(); showView('stats'); });
$('btn-refresh').addEventListener('click', () => loadRuns());
$('filter-status').addEventListener('change', () => loadRuns());
$('detail-close').addEventListener('click', () => $('detail-overlay').classList.add('hidden'));
$('detail-overlay').addEventListener('click', e => {
  if (e.target === $('detail-overlay')) $('detail-overlay').classList.add('hidden');
});

// ─── Runs list ─────────────────────────────────────────────────────────────
async function loadRuns() {
  const status = $('filter-status').value;
  const url = `${API}/api/runs?limit=100${status ? `&status=${status}` : ''}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(resp.statusText);
    const runs = await resp.json();
    renderRuns(runs);
  } catch (err) {
    $('runs-body').innerHTML = `<tr><td colspan="5" class="empty">Error: ${err.message}</td></tr>`;
  }
}

function fmtDuration(secs) {
  if (secs < 1) return `${(secs * 1000).toFixed(0)}ms`;
  if (secs < 60) return `${secs.toFixed(2)}s`;
  const m = Math.floor(secs / 60), s = Math.round(secs % 60);
  return `${m}m ${s}s`;
}

function fmtDate(iso) {
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

function renderRuns(runs) {
  const tbody = $('runs-body');
  if (!runs.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">No runs yet. Run a pipeline to see results here.</td></tr>';
    return;
  }
  tbody.innerHTML = runs.map(r => `
    <tr data-id="${r.id}" class="run-row">
      <td><strong>${escHtml(r.pipeline_name)}</strong></td>
      <td><span class="badge ${r.success ? 'passed' : 'failed'}">${r.success ? 'Passed' : 'Failed'}</span></td>
      <td>${fmtDuration(r.total_time)}</td>
      <td style="color:var(--text-muted);font-size:.85rem">${fmtDate(r.timestamp)}</td>
      <td><button class="btn-detail" data-id="${r.id}">Details →</button></td>
    </tr>
  `).join('');

  // Click detail buttons
  tbody.querySelectorAll('.btn-detail').forEach(btn => {
    btn.addEventListener('click', e => { e.stopPropagation(); loadDetail(btn.dataset.id); });
  });
  // Click row
  tbody.querySelectorAll('.run-row').forEach(row => {
    row.addEventListener('click', () => loadDetail(row.dataset.id));
  });
}

// ─── Run detail ─────────────────────────────────────────────────────────────
async function loadDetail(id) {
  try {
    const resp = await fetch(`${API}/api/runs/${id}`);
    if (!resp.ok) throw new Error(resp.statusText);
    const run = await resp.json();
    renderDetail(run);
  } catch (err) {
    alert(`Failed to load run: ${err.message}`);
  }
}

function renderDetail(run) {
  $('detail-name').textContent = `📡 ${run.pipeline_name}`;
  $('detail-meta').innerHTML = `
    <span class="badge ${run.success ? 'passed' : 'failed'}">${run.success ? 'Passed' : 'Failed'}</span>
    &nbsp; ${fmtDuration(run.total_time)} total &nbsp;·&nbsp; ${fmtDate(run.timestamp)}
    &nbsp;·&nbsp; ${run.steps?.length || 0} steps
  `;
  const steps = run.steps || [];
  $('detail-steps').innerHTML = steps.map(s => `
    <div class="step-item ${s.status}">
      <div class="step-header">
        <span class="badge ${s.status}">${s.status}</span>
        <span class="step-label">${escHtml(s.label)}</span>
        <span class="step-duration">${fmtDuration(s.duration)}</span>
      </div>
      ${s.stdout ? `<div class="step-stdout">${escHtml(s.stdout)}</div>` : ''}
      ${s.error ? `<div class="step-stdout" style="color:var(--red)">${escHtml(s.error)}</div>` : ''}
      ${s.narration ? `<div class="step-narration">💬 ${escHtml(s.narration)}</div>` : ''}
    </div>
  `).join('');
  $('detail-overlay').classList.remove('hidden');
}

// ─── Stats ───────────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const resp = await fetch(`${API}/api/stats`);
    const s = await resp.json();
    $('stat-total').textContent = s.total;
    $('stat-passed').textContent = s.passed;
    $('stat-failed').textContent = s.failed;
    $('stat-avg').textContent = s.avg_time ? fmtDuration(s.avg_time) : '—';
  } catch (err) {
    console.error('Stats error', err);
  }
}

// ─── Utilities ───────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── Init ─────────────────────────────────────────────────────────────────────
loadRuns();
