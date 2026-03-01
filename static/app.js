/* =============================================================
   Smart Data Cleaning — Client-side logic (polished)
   ============================================================= */

let sessionId = null;

// ---------- DOM refs ----------
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loading-text');

// ---------- Screen navigation ----------
const screens = ['upload', 'preview', 'options', 'results'];

function showScreen(name) {
  const idx = screens.indexOf(name);

  // Hide all screens first
  screens.forEach(s => {
    const el = document.getElementById(`screen-${s}`);
    el.classList.remove('active');
    el.style.display = 'none';
  });

  // Small delay so the exit → enter animation feels smooth
  setTimeout(() => {
    const target = document.getElementById(`screen-${name}`);
    target.style.display = 'block';
    // Force reflow before adding active class for animation
    void target.offsetWidth;
    target.classList.add('active');
  }, 80);

  // Update step pills
  const pills = document.querySelectorAll('.step-pill');
  pills.forEach((pill, i) => {
    pill.classList.remove('active', 'done');
    if (i < idx) pill.classList.add('done');
    if (i === idx) pill.classList.add('active');
  });

  // Update connectors
  for (let c = 1; c <= 3; c++) {
    const conn = document.getElementById(`conn-${c}`);
    if (conn) {
      conn.classList.toggle('done', c <= idx);
    }
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetApp() {
  sessionId = null;
  fileInput.value = '';
  // Reset all option controls
  document.getElementById('opt-missing').value = '';
  document.getElementById('opt-duplicates').checked = false;
  document.getElementById('opt-whitespace').checked = false;
  document.getElementById('opt-outliers').value = '';
  document.getElementById('opt-constant').checked = false;
  document.getElementById('opt-encode').value = '';
  document.getElementById('opt-scale').value = '';
  document.getElementById('opt-datetime').checked = false;
  document.getElementById('opt-log').checked = false;
  document.getElementById('opt-text').checked = false;
  if (window.appCharts) {
    window.appCharts.forEach(c => c.destroy());
    window.appCharts = [];
  }
  document.getElementById('vis-container').innerHTML = '';
  showScreen('upload');
  showToast('Ready for a new file!', 'success');
}

// ---------- Toast notification ----------
function showToast(message, type = 'success') {
  // Remove existing toasts
  document.querySelectorAll('.toast').forEach(t => t.remove());

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toastOut 0.35s ease forwards';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// ---------- Loading helpers ----------
function showLoading(msg = 'Processing…') {
  loadingText.textContent = msg;
  loading.classList.add('active');
}
function hideLoading() {
  loading.style.animation = 'fadeIn 0.25s ease reverse forwards';
  setTimeout(() => {
    loading.classList.remove('active');
    loading.style.animation = '';
  }, 250);
}

// ---------- Upload ----------
uploadZone.addEventListener('click', (e) => {
  if (e.target === fileInput) return;
  fileInput.click();
});

uploadZone.addEventListener('dragover', e => {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.add('drag-over');
});
uploadZone.addEventListener('dragleave', (e) => {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.remove('drag-over');
});
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.remove('drag-over');
  if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) handleFile(fileInput.files[0]);
});

async function handleFile(file) {
  showLoading('Uploading & analysing your data…');
  const form = new FormData();
  form.append('file', file);

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (parseErr) {
      throw new Error('Server returned invalid response');
    }
    if (!res.ok) throw new Error(data.error || 'Upload failed');

    sessionId = data.session_id;
    renderPreview(data);

    // Fetch visualizations
    fetch(`/api/visualize?session_id=${sessionId}&type=raw`)
      .then(res => res.json())
      .then(visData => renderCharts(visData))
      .catch(e => console.error("Could not load charts:", e));

    hideLoading();

    // Brief pause before showing preview so loading fade-out completes
    setTimeout(() => {
      showScreen('preview');
      const issueCount = data.analysis.issues.length;
      if (issueCount > 0) {
        showToast(`Found ${issueCount} issue${issueCount > 1 ? 's' : ''} in your data`, 'success');
      } else {
        showToast('Data looks clean! No issues detected.', 'success');
      }
    }, 300);
  } catch (err) {
    hideLoading();
    showToast('Upload error: ' + err.message, 'error');
  }
}

// ---------- Render Preview ----------
function renderPreview({ filename, preview, analysis }) {
  document.getElementById('filename-badge').textContent = filename;

  // Stats
  const statsRow = document.getElementById('stats-row');
  const issueCount = analysis.issues.length;
  statsRow.innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${analysis.rows.toLocaleString()}</div>
      <div class="stat-label">Rows</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${analysis.columns}</div>
      <div class="stat-label">Columns</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${issueCount}</div>
      <div class="stat-label">Issues Found</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${analysis.column_info.filter(c => c.missing > 0).length}</div>
      <div class="stat-label">Cols w/ Missing</div>
    </div>
  `;

  // Issues
  const issueList = document.getElementById('issue-list');
  if (issueCount === 0) {
    issueList.innerHTML = '<div class="no-issues">✅ No issues detected — your data looks clean!</div>';
  } else {
    issueList.innerHTML = analysis.issues.map(iss => `
      <div class="issue-item">
        <span class="issue-badge ${iss.severity}">${iss.severity}</span>
        <span class="issue-col">${escHtml(iss.column)}</span>
        <span class="issue-detail">${escHtml(iss.detail)}</span>
      </div>
    `).join('');
  }

  // Data table
  renderTable('preview-thead', 'preview-tbody', preview);
}

// ---------- Run Cleaning ----------
document.getElementById('btn-run-clean').addEventListener('click', runCleaning);

async function runCleaning() {
  if (!sessionId) {
    showToast('Please upload a file first.', 'error');
    return;
  }

  const body = {
    session_id: sessionId,
    missing_strategy: val('opt-missing'),
    remove_duplicates: checked('opt-duplicates'),
    trim_whitespace: checked('opt-whitespace'),
    handle_outliers: val('opt-outliers'),
    remove_constant_cols: checked('opt-constant'),
    encode_categorical: val('opt-encode'),
    scale_numeric: val('opt-scale'),
    extract_datetime: checked('opt-datetime'),
    log_transform: checked('opt-log'),
    text_cleaning: checked('opt-text'),
  };

  showLoading('Cleaning & preprocessing your data…');
  try {
    const res = await fetch('/api/clean', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (parseErr) {
      throw new Error('Server returned invalid response');
    }
    if (!res.ok) throw new Error(data.error || 'Cleaning failed');

    renderResults(data);
    hideLoading();

    setTimeout(() => {
      showScreen('results');
      showToast(`Done! ${data.changes.length} change${data.changes.length !== 1 ? 's' : ''} applied.`, 'success');
    }, 300);
  } catch (err) {
    hideLoading();
    showToast('Cleaning error: ' + err.message, 'error');
  }
}

// ---------- Render Results ----------
function renderResults({ preview, changes, rows, columns }) {
  // Summary
  document.getElementById('results-summary').innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${rows.toLocaleString()}</div>
      <div class="stat-label">Final Rows</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${columns.toLocaleString()}</div>
      <div class="stat-label">Final Columns</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">${changes.length}</div>
      <div class="stat-label">Changes Made</div>
    </div>
  `;

  // Change list
  const changeList = document.getElementById('change-list');
  if (changes.length === 0) {
    changeList.innerHTML = '<div class="no-changes">No changes were applied — the data was already clean with these settings.</div>';
  } else {
    changeList.innerHTML = changes.map(ch => `
      <div class="change-card">
        <div class="change-card-header">
          <span class="change-op">${escHtml(ch.operation)}</span>
          <span class="change-col">${escHtml(ch.column)}</span>
          <span class="change-affected">${ch.rows_affected.toLocaleString()} rows affected</span>
        </div>
        <div class="change-samples">
          <div class="sample-box sample-before">${formatSample(ch.before_sample)}</div>
          <span class="sample-arrow">→</span>
          <div class="sample-box sample-after">${formatSample(ch.after_sample)}</div>
        </div>
      </div>
    `).join('');
  }

  // Cleaned data table (limit columns shown to 30 to avoid browser lag)
  if (preview.length) {
    let cols = Object.keys(preview[0]);
    let truncated = false;
    if (cols.length > 30) {
      cols = cols.slice(0, 30);
      truncated = true;
    }
    renderTable('results-thead', 'results-tbody', preview, cols, truncated);
  }
}

// ---------- Shared table renderer ----------
function renderTable(theadId, tbodyId, data, columns, truncated) {
  if (!data || data.length === 0) return;
  const cols = columns || Object.keys(data[0]);

  document.getElementById(theadId).innerHTML =
    '<tr>' + cols.map(c => `<th>${escHtml(c)}</th>`).join('')
    + (truncated ? '<th style="color:var(--text-muted);">…</th>' : '')
    + '</tr>';

  document.getElementById(tbodyId).innerHTML =
    data.slice(0, 100).map(row => '<tr>' + cols.map(c => {
      const v = row[c];
      if (v === null || v === undefined) return '<td class="null-val">null</td>';
      return `<td>${escHtml(String(v))}</td>`;
    }).join('')
      + (truncated ? '<td style="color:var(--text-muted);">…</td>' : '')
      + '</tr>').join('');
}

// ---------- Download ----------
document.getElementById('btn-download').addEventListener('click', () => {
  if (!sessionId) return;
  const fmt = document.getElementById('download-format').value;
  window.location.href = `/api/download?session_id=${sessionId}&format=${fmt}`;
  showToast('Download started!', 'success');
});

// ---------- Util ----------
function val(id) { return document.getElementById(id).value || null; }
function checked(id) { return document.getElementById(id).checked; }

function escHtml(str) {
  if (str === null || str === undefined) return '';
  const div = document.createElement('div');
  div.textContent = String(str);
  return div.innerHTML;
}

function formatSample(sample) {
  if (!sample) return '—';
  if (typeof sample === 'object' && !Array.isArray(sample)) {
    // dict-like (scaling before/after)
    const entries = Object.entries(sample).slice(0, 3);
    return entries.map(([k, v]) =>
      `<strong>${escHtml(k)}:</strong> ${escHtml(JSON.stringify(v))}`
    ).join('<br>') + (Object.keys(sample).length > 3 ? '<br>…' : '');
  }
  if (Array.isArray(sample)) {
    return sample.slice(0, 5).map(v => escHtml(String(v ?? 'null'))).join(', ')
      + (sample.length > 5 ? ', …' : '');
  }
  return escHtml(String(sample));
}

// ---------- Chart.js Rendering ----------
window.appCharts = [];

function renderCharts(visData) {
  const container = document.getElementById('vis-container');
  container.innerHTML = '';

  if (window.appCharts) {
    window.appCharts.forEach(c => c.destroy());
    window.appCharts = [];
  }

  // Helper to create a canvas wrapper
  function createCanvasWrapper(title) {
    const wrap = document.createElement('div');
    wrap.style.cssText = "background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; width: calc(50% - 0.5rem); min-width: 300px; height: 350px; display: flex; flex-direction: column; box-sizing: border-box; border: 1px solid rgba(255,255,255,0.1);";
    const h4 = document.createElement('h4');
    h4.textContent = title;
    h4.style.marginBottom = "0.5rem";
    h4.style.fontSize = "0.9rem";
    h4.style.flexShrink = "0";
    wrap.appendChild(h4);

    const innerWrap = document.createElement('div');
    innerWrap.style.position = "relative";
    innerWrap.style.flexGrow = "1";
    innerWrap.style.minHeight = "0"; // Prevents flex child from overflowing

    const canvas = document.createElement('canvas');
    innerWrap.appendChild(canvas);
    wrap.appendChild(innerWrap);
    container.appendChild(wrap);
    return canvas.getContext('2d');
  }

  Chart.defaults.color = "rgba(255,255,255,0.7)";

  // Plot numerical histograms
  if (visData.histograms) {
    for (const [col, data] of Object.entries(visData.histograms)) {
      if (data.counts && data.counts.length) {
        const ctx = createCanvasWrapper(`Distribution: ${col}`);
        const chart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: data.bins.map(b => Number(b).toFixed(2)),
            datasets: [{
              label: 'Frequency',
              data: data.counts,
              backgroundColor: 'rgba(99, 102, 241, 0.7)',
              borderColor: 'rgba(99, 102, 241, 1)',
              borderWidth: 1
            }]
          },
          options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false } } }
        });
        window.appCharts.push(chart);
      }
    }
  }

  // Plot categorical bar charts
  if (visData.bar_charts) {
    for (const [col, data] of Object.entries(visData.bar_charts)) {
      if (data.counts && data.counts.length) {
        const ctx = createCanvasWrapper(`Top Categories: ${col}`);
        const chart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: data.labels,
            datasets: [{
              label: 'Count',
              data: data.counts,
              backgroundColor: 'rgba(16, 185, 129, 0.7)',
              borderColor: 'rgba(16, 185, 129, 1)',
              borderWidth: 1
            }]
          },
          options: { responsive: true, maintainAspectRatio: false }
        });
        window.appCharts.push(chart);
      }
    }
  }
}
