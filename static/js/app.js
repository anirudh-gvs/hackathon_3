/* Offline DocScan - Main Application Script */

// Application state
const AppState = {
  currentFile: null,
  currentFileName: null,
  currentResult: null,
  currentPage: 'dashboard',
  processingStages: [
    { id: 'reading', label: 'Reading file', icon: '📄' },
    { id: 'ocr', label: 'OCR Processing', icon: '👁️' },
    { id: 'layout', label: 'Layout Detection', icon: '📐' },
    { id: 'extraction', label: 'Extracting Structured Data', icon: '🧠' },
    { id: 'validation', label: 'Validating Results', icon: '✓' }
  ],
  stats: {
    totalDocuments: 0,
    medicalReports: 0,
    invoices: 0,
    receipts: 0,
    successRate: 0,
    avgProcessingTime: 0
  }
};

// Utility functions
function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
}

function showNotification(message, type = 'success', duration = 3000) {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => notification.classList.add('show'), 100);
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }, duration);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function getFileIcon(fileType) {
  const icons = {
    'PDF': '📄',
    'Image': '🖼️',
    'Text': '📝'
  };
  return icons[fileType] || '📄';
}

// Navigation
function initNavigation() {
  const navItems = $$('.nav-item');
  
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const page = item.dataset.page;
      navigateToPage(page);
    });
  });
}

function navigateToPage(pageName) {
  AppState.currentPage = pageName;
  
  // Update active nav item
  $$('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.page === pageName);
  });
  
  // Show active page
  $$('.page').forEach(page => {
    page.classList.toggle('active', page.id === `${pageName}-page`);
  });
  
  // Load page-specific data
  if (pageName === 'history') {
    loadHistory();
  } else if (pageName === 'dashboard') {
    loadStats();
  }
}

// Processing Pipeline
function createPipelineElement() {
  const container = document.createElement('div');
  container.className = 'pipeline';
  AppState.processingStages.forEach((stage, index) => {
    const stageEl = document.createElement('div');
    stageEl.className = 'pipeline-stage';
    stageEl.dataset.stage = stage.id;
    stageEl.innerHTML = `
      <div class="pipeline-icon" id="icon-${stage.id}">
        <span>${index + 1}</span>
      </div>
      <span class="pipeline-text">${stage.label}</span>
    `;
    container.appendChild(stageEl);
  });
  return container;
}

function updatePipeline(stageId, completed = false) {
  const stageEl = $(`.pipeline-stage[data-stage="${stageId}"]`);
  if (!stageEl) return;
  
  const iconEl = stageEl.querySelector('.pipeline-icon');
  
  if (completed) {
    stageEl.classList.add('completed');
    iconEl.innerHTML = '<span class="pipeline-icon-check">✓</span>';
  } else {
    stageEl.classList.add('active');
    iconEl.innerHTML = '<span class="pipeline-icon-spinner">⟳</span>';
  }
}

// Scan functionality
function initScanPage() {
  const form = $('#scanForm');
  const fileInput = $('#file');
  const schemaSelect = $('#schema');
  const previewPanel = $('.preview-panel');
  const extractionPanel = $('.extraction-panel');
  const previewContent = $('.preview-content');
  const extractionContent = $('.extraction-content');
  
  fileInput.addEventListener('change', handleFileSelect);
  form.addEventListener('submit', handleScanSubmit);
  
  // Zoom controls
  $('#zoomInBtn')?.addEventListener('click', () => zoomPreview(1.2));
  $('#zoomOutBtn')?.addEventListener('click', () => zoomPreview(0.8));
  $('#fitWidthBtn')?.addEventListener('click', () => fitPreview('width'));
  $('#fitPageBtn')?.addEventListener('click', () => fitPreview('page'));
}

let currentZoom = 1;
let pdfDoc = null;

async function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  
  AppState.currentFile = file;
  currentZoom = 1;
  
  // Show the scan-layout so preview is visible, hide extraction panel initially
  document.getElementById('scan-results').style.display = 'grid';
  const extractionContent = $('.extraction-content');
  extractionContent.innerHTML = '<p class="text-muted">Submit the document to extract data.</p>';
  
  previewCurrentFile(file);
}

async function previewCurrentFile(file) {
  const previewContent = $('.preview-content');
  const fileType = file.name.split('.').pop().toLowerCase();
  
  previewContent.innerHTML = '<div class="skeleton" style="width: 100%; height: 200px;"></div>';
  
  if (fileType === 'pdf') {
    await renderPDFPreview(file);
  } else if (['png', 'jpg', 'jpeg', 'tiff', 'bmp'].includes(fileType) || file.type.startsWith('image/')) {
    previewImage(file, previewContent);
  }
}

function previewImage(file, container) {
  const reader = new FileReader();
  reader.onload = (e) => {
    container.innerHTML = `
      <img class="preview-image" src="${e.target.result}" style="transform: scale(${currentZoom});" alt="Document preview">
    `;
  };
  reader.readAsDataURL(file);
}

async function renderPDFPreview(file) {
  const previewContent = $('.preview-content');
  const reader = new FileReader();
  
  reader.onload = async (e) => {
    // For offline mode, use embed tag as fallback (no CDN)
    const blobUrl = URL.createObjectURL(file);
    previewContent.innerHTML = `
      <embed class="preview-pdf-page" src="${blobUrl}" type="application/pdf" style="width: 100%; height: 400px;">
    `;
    // Clean up blob URL after a delay
    setTimeout(() => URL.revokeObjectURL(blobUrl), 30000);
  };
  reader.readAsArrayBuffer(file);
}

async function renderPDFPage(pdf, pageNumber) {
  const previewContent = $('.preview-content');
  const page = await pdf.getPage(pageNumber);
  const viewport = page.getViewport({ scale: 1.5 * currentZoom });
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  
  await page.render({
    canvasContext: ctx,
    viewport: viewport
  }).promise;
  
  previewContent.innerHTML = '';
  previewContent.appendChild(canvas);
}

async function renderPDFThumbnails(pdf) {
  const thumbnailsContainer = $('.pdf-thumbnails');
  thumbnailsContainer.innerHTML = '';
  
  for (let i = 1; i <= Math.min(pdf.numPages, 10); i++) {
    const page = await pdf.getPage(i);
    const viewport = page.getViewport({ scale: 0.3 });
    const canvas = document.createElement('canvas');
    canvas.className = 'pdf-thumbnail';
    canvas.dataset.page = i;
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    
    const ctx = canvas.getContext('2d');
    await page.render({
      canvasContext: ctx,
      viewport: viewport
    }).promise;
    
    canvas.addEventListener('click', () => renderPDFPage(pdf, i));
    thumbnailsContainer.appendChild(canvas);
  }
  
  if (thumbnailsContainer.firstChild) {
    thumbnailsContainer.firstChild.classList.add('active');
  }
}

function zoomPreview(factor) {
  currentZoom *= factor;
  const previewImg = $('.preview-image');
  if (previewImg) {
    previewImg.style.transform = `scale(${currentZoom})`;
  }
}

function fitPreview(mode) {
  currentZoom = 1;
  const previewImg = $('.preview-image');
  if (previewImg) {
    previewImg.style.transform = `scale(1)`;
    previewImg.style.maxWidth = mode === 'width' ? '100%' : '100%';
    previewImg.style.maxHeight = mode === 'width' ? 'none' : '100%';
  }
}

async function handleScanSubmit(e) {
  e.preventDefault();
  console.log('Scan submitted');
  
  const fileInput = $('#file');
  const schemaSelect = $('#schema');
  const modeSelect = $('#mode');
  const formData = new FormData();
  
  if (!fileInput.files[0]) {
    showNotification('Please select a file', 'error');
    return;
  }
  
  formData.append('file', fileInput.files[0]);
  formData.append('schema', schemaSelect.value);
  formData.append('mode', modeSelect.value);
  
  // Show pipeline & reset extraction results (keep preview visible)
  const pipelineContainer = $('.pipeline-container');
  pipelineContainer.innerHTML = '';
  pipelineContainer.appendChild(createPipelineElement());
  const extractionContent = $('.extraction-content');
  
  const isQuickMode = modeSelect.value === 'quick';
  extractionContent.innerHTML = isQuickMode 
    ? '<p class="text-muted">Quick extraction in progress...</p>'
    : '<p class="text-muted">Running LLM inference... (this takes 15-30s)</p>';
  
  // Start pipeline - mark reading and OCR as complete
  setTimeout(() => {
    updatePipeline('reading', true);
    updatePipeline('ocr', true);
    updatePipeline('layout', true);
    updatePipeline('extraction', false);
  }, 100);
  
  // Disable submit button to prevent double submission
  const submitBtn = e.target.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = isQuickMode ? 'Processing...' : 'Processing... (15-30s)';
  }
  
  try {
    console.log('Sending request to /api/scan...');
    const res = await fetch('/api/scan', {
      method: 'POST',
      body: formData
    });
    console.log('Response received, status:', res.status);
    
    // API returned - extraction is done
    updatePipeline('extraction', true);
    updatePipeline('validation', false);
    
    const data = await res.json();
    console.log('Response data:', data);
    
    // Validation complete
    updatePipeline('validation', true);
    
    if (!res.ok) {
      showNotification(data.error || 'Processing failed', 'error');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Process Document';
      }
      return;
    }
    
    AppState.currentResult = data.result;
    AppState.currentFileName = fileInput.files[0].name;
    renderExtractionForm(data.result, schemaSelect.value);
    document.getElementById('scan-results').style.display = 'grid';
    console.log('Results displayed');
    
    // Scroll to results
    document.getElementById('scan-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    showNotification('Document processed successfully!', 'success');
    
  } catch (err) {
    console.error('Request failed:', err);
    showNotification(`Request failed: ${err.message}`, 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Process Document';
    }
  }
}

function renderExtractionForm(result, schema) {
  const extractionContent = $('.extraction-content');
  
  // Always show raw JSON as a fallback
  let html = '<div class="extraction-form">';
  html += `
    <details style="margin-bottom: 1rem;">
      <summary style="cursor: pointer; color: var(--color-accent); font-weight: 500;">View Raw JSON</summary>
      <pre style="background: var(--color-bg-primary); padding: 1rem; border-radius: var(--radius-md); overflow-x: auto; font-size: 0.8rem; margin-top: 0.5rem; white-space: pre-wrap;">${JSON.stringify(result, null, 2)}</pre>
    </details>
  `;
  
  if (schema === 'medical') {
    html += `
      <div class="form-group">
        <label class="form-label field-label">Patient Name</label>
        <input type="text" class="form-input" value="${result.patient_name || ''}" data-field="patient_name">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Date</label>
        <input type="text" class="form-input" value="${result.date || ''}" data-field="date">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Doctor</label>
        <input type="text" class="form-input" value="${result.doctor || ''}" data-field="doctor">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Diagnosis</label>
        <textarea class="form-textarea" data-field="diagnosis">${Array.isArray(result.diagnosis) ? result.diagnosis.join(', ') : ''}</textarea>
      </div>
      <div class="form-group">
        <label class="form-label field-label">Medications</label>
        <textarea class="form-textarea" data-field="medications">${result.medications ? result.medications.map(m => m.name).join(', ') : ''}</textarea>
      </div>
      <div class="form-group">
        <label class="form-label field-label">Notes</label>
        <textarea class="form-textarea" data-field="notes">${result.notes || ''}</textarea>
      </div>
    `;
  } else if (schema === 'receipt') {
    html += `
      <div class="form-group">
        <label class="form-label field-label">Vendor</label>
        <input type="text" class="form-input" value="${result.vendor || ''}" data-field="vendor">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Date</label>
        <input type="text" class="form-input" value="${result.date || ''}" data-field="date">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Total</label>
        <input type="number" step="0.01" class="form-input" value="${result.total || ''}" data-field="total">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Tax</label>
        <input type="number" step="0.01" class="form-input" value="${result.tax || ''}" data-field="tax">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Payment Method</label>
        <input type="text" class="form-input" value="${result.payment_method || ''}" data-field="payment_method">
      </div>
    `;
  } else {
    html += `
      <div class="form-group">
        <label class="form-label field-label">Title</label>
        <input type="text" class="form-input" value="${result.title || ''}" data-field="title">
      </div>
      <div class="form-group">
        <label class="form-label field-label">Summary</label>
        <textarea class="form-textarea" data-field="summary">${result.summary || ''}</textarea>
      </div>
      <div class="form-group">
        <label class="form-label field-label">Key Facts</label>
        <textarea class="form-textarea" data-field="key_facts">${Array.isArray(result.key_facts) ? result.key_facts.join('\n') : ''}</textarea>
      </div>
    `;
  }
  
  html += `
    <div class="extraction-actions">
      <button class="btn btn-secondary" onclick="resetChanges()">Reset Changes</button>
    </div>
    <div class="export-grid" style="margin-top: 1.5rem;">
      <button class="btn btn-primary btn-sm" onclick="downloadJSON()">Download JSON</button>
      <button class="btn btn-secondary btn-sm" onclick="downloadCSV()">Download CSV</button>
      <button class="btn btn-secondary btn-sm" onclick="downloadPDF()">Download PDF</button>
      <button class="btn btn-secondary btn-sm" onclick="copyJSON()">Copy JSON</button>
      <button class="btn btn-secondary btn-sm" onclick="copyText()">Copy Text</button>
      <button class="btn btn-secondary btn-sm" onclick="downloadMarkdown()">Download Markdown</button>
      ${AppState.currentFileName ? `<button class="btn btn-secondary btn-sm" onclick="downloadOriginalFile()">Download Original</button>` : ''}
    </div>
  </div>`;
  
  extractionContent.innerHTML = html;
}

function resetChanges() {
  if (AppState.currentResult) {
    renderExtractionForm(AppState.currentResult, $('#schema').value);
  }
}

function downloadJSON() {
  if (!AppState.currentResult) return;
  const blob = new Blob([JSON.stringify(AppState.currentResult, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `extraction-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showNotification('JSON downloaded', 'success');
}

function downloadCSV() {
  if (!AppState.currentResult) return;
  let csv = 'Field,Value\n';
  for (const [key, value] of Object.entries(AppState.currentResult)) {
    if (Array.isArray(value)) {
      value.forEach((v, i) => {
        if (typeof v === 'object') {
          csv += `${key}[${i}],${JSON.stringify(v)}\n`;
        } else {
          csv += `${key}[${i}],${v}\n`;
        }
      });
    } else {
      csv += `${key},${value}\n`;
    }
  }
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `extraction-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  showNotification('CSV downloaded', 'success');
}

function downloadPDF() {
  if (!AppState.currentResult) return;
  const schema = $('#schema').value;
  const title = AppState.currentResult.title || AppState.currentResult.vendor || 'Extracted Data';
  const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${title}</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; color: #1e293b; }
h1 { border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem; }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
th, td { text-align: left; padding: 0.5rem; border-bottom: 1px solid #e2e8f0; }
th { background: #f8fafc; font-weight: 600; }
.footer { margin-top: 2rem; font-size: 0.8rem; color: #94a3b8; text-align: center; }
</style></head><body>
<h1>${title}</h1>
<table>${Object.entries(AppState.currentResult).map(([k, v]) =>
  `<tr><th>${k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</th><td>${
    Array.isArray(v) ? (v.length ? v.map(i => typeof i === 'object' ? JSON.stringify(i) : i).join('<br>') : '—') :
    v ?? '—'
  }</td></tr>`
).join('')}</table>
<div class="footer">Generated by Offline DocScan &mdash; ${new Date().toLocaleString()}</div>
<script>window.print()</script>
</body></html>`;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}.html`;
  a.click();
  URL.revokeObjectURL(url);
  showNotification('HTML file downloaded. Open and print to save as PDF.', 'success');
}

async function copyJSON() {
  if (!AppState.currentResult) return;
  try {
    await navigator.clipboard.writeText(JSON.stringify(AppState.currentResult, null, 2));
    showNotification('JSON copied to clipboard', 'success');
  } catch {
    fallbackCopy(JSON.stringify(AppState.currentResult, null, 2), 'JSON');
  }
}

async function copyText() {
  if (!AppState.currentResult) return;
  const text = Object.entries(AppState.currentResult)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
    .join('\n');
  try {
    await navigator.clipboard.writeText(text);
    showNotification('Text copied to clipboard', 'success');
  } catch {
    fallbackCopy(text, 'Text');
  }
}

function fallbackCopy(text, label) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    showNotification(`${label} copied to clipboard`, 'success');
  } catch {
    showNotification(`Could not copy ${label}. Select and copy manually.`, 'error');
  }
  document.body.removeChild(ta);
}

function downloadMarkdown() {
  if (!AppState.currentResult) return;
  let md = '# Extracted Data\n\n';
  for (const [key, value] of Object.entries(AppState.currentResult)) {
    if (Array.isArray(value)) {
      md += `**${key}:**\n`;
      value.forEach(v => md += `- ${typeof v === 'object' ? JSON.stringify(v) : v}\n`);
    } else {
      md += `**${key}:** ${value}\n\n`;
    }
  }
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `extraction-${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
  showNotification('Markdown downloaded', 'success');
}

// History
async function loadHistory() {
  const historyList = $('.history-list');
  historyList.innerHTML = '<div class="skeleton" style="height: 100px;"></div>';
  
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    
    if (data.length === 0) {
      historyList.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📁</div>
          <p>No documents scanned yet. Go to the Scan page to get started!</p>
        </div>
      `;
      return;
    }
    
    historyList.innerHTML = '';
    data.reverse().forEach(record => {
      const item = document.createElement('div');
      item.className = 'history-item';
      item.innerHTML = `
        <div class="history-item-info">
          <div class="history-item-title">
            ${getFileIcon(record.file_type)} ${record.source_file}
          </div>
          <div class="history-item-meta">
            <span>${formatDate(record.created_at)}</span>
            <span>${record.doc_type || 'Document'}</span>
            <span class="status-badge ${record.status === 'success' ? 'status-success' : 'status-failed'}">
              ${record.status === 'success' ? '✓ Success' : '✗ Failed'}
            </span>
          </div>
        </div>
        <div class="history-item-actions">
          <button class="btn btn-sm btn-secondary" onclick="downloadHistoryFile('${record.source_file}')">Download</button>
          <button class="btn btn-sm btn-secondary" onclick="exportHistoryRecord(${record.id})">Export</button>
          <button class="btn btn-sm btn-danger" onclick="deleteHistoryRecord(${record.id})">Delete</button>
        </div>
      `;
      historyList.appendChild(item);
    });
  } catch (err) {
    historyList.innerHTML = `<div class="error">Failed to load history: ${err.message}</div>`;
  }
}

async function deleteHistoryRecord(id) {
  try {
    const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
    if (res.ok) {
      showNotification('Record deleted', 'success');
      loadHistory();
    }
  } catch (err) {
    showNotification('Failed to delete: ' + err.message, 'error');
  }
}

function downloadOriginalFile() {
  const filename = AppState.currentFileName;
  if (!filename) return;
  const a = document.createElement('a');
  a.href = `/api/download/${encodeURIComponent(filename)}`;
  a.download = filename;
  a.click();
  showNotification('Downloading original file', 'success');
}

function downloadHistoryFile(filename) {
  const a = document.createElement('a');
  a.href = `/api/download/${encodeURIComponent(filename)}`;
  a.download = filename;
  a.click();
  showNotification('Downloading file', 'success');
}

function exportHistoryRecord(id) {
  // Placeholder
  showNotification('Export functionality for history records', 'info');
}

// Dashboard
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    
    AppState.stats = {
      totalDocuments: data.total_documents || 0,
      successRate: data.success_rate || 0,
      avgProcessingTime: data.avg_processing_time || 0
    };
    
    // Count by doc type
    const docTypes = data.by_doc_type || {};
    AppState.stats.medicalReports = docTypes['Medical Report'] || 0;
    AppState.stats.receipts = docTypes['Receipt'] || 0;
    AppState.stats.invoices = docTypes['Invoice'] || 0;
    
    renderStats();
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

function renderStats() {
  $('#stat-total').textContent = AppState.stats.totalDocuments;
  $('#stat-success-rate').textContent = `${AppState.stats.successRate}%`;
  $('#stat-avg-time').textContent = `${AppState.stats.avgProcessingTime}s`;
  $('#stat-medical').textContent = AppState.stats.medicalReports;
  $('#stat-receipts').textContent = AppState.stats.receipts;
  $('#stat-invoices').textContent = AppState.stats.invoices;
}

// Search
function initSearch() {
  const searchInput = $('.history-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const searchTerm = e.target.value.toLowerCase();
      $$('.history-item').forEach(item => {
        const title = item.querySelector('.history-item-title').textContent.toLowerCase();
        item.style.display = title.includes(searchTerm) ? '' : 'none';
      });
    });
  }
}

// Monitor
let monitorPollId = null;
let monitorHistory = { cpu: [], memory: [], timestamps: [] };

function initMonitor() {
  updateMonitor();
  monitorPollId = setInterval(updateMonitor, 1000);
}

async function updateMonitor() {
  try {
    const res = await fetch('/api/system/metrics');
    if (!res.ok) return;
    const data = await res.json();

    monitorHistory = {
      cpu: data.cpu_history || monitorHistory.cpu,
      memory: data.memory_history || monitorHistory.memory,
      timestamps: data.timestamps || monitorHistory.timestamps,
    };

    const cpuPercent = Math.round(data.cpu_percent) || 0;
    const memPercent = Math.round(data.memory_percent) || 0;
    const cpuVal = $('#monitor-cpu');
    const ramVal = $('#monitor-ram');
    const cpuBar = $('#monitor-cpu-bar');
    const ramBar = $('#monitor-ram-bar');
    const cpuValExp = $('#monitor-cpu-val');
    const ramValExp = $('#monitor-ram-val');
    const dot = $('#monitor-dot');
    const cores = $('#monitor-cores');
    const procCpu = $('#monitor-proc-cpu');
    const threads = $('#monitor-threads');
    const disk = $('#monitor-disk');
    const network = $('#monitor-network');
    const inference = $('#monitor-inference');
    const gpu = $('#monitor-gpu');

    if (cpuVal) cpuVal.textContent = `${cpuPercent}%`;
    if (ramVal) ramVal.textContent = data.memory_used_mb ? `${Math.round(data.memory_used_mb)} MB` : '0 MB';

    if (cpuBar) {
      cpuBar.style.width = `${Math.min(cpuPercent, 100)}%`;
      cpuBar.className = 'monitor-bar' + (cpuPercent > 80 ? ' monitor-bar-danger' : cpuPercent > 50 ? ' monitor-bar-warning' : '');
    }
    if (ramBar) {
      ramBar.style.width = `${Math.min(memPercent, 100)}%`;
    }
    if (cpuValExp) cpuValExp.textContent = `${cpuPercent}%`;
    if (ramValExp) ramValExp.textContent = `${memPercent}%`;

    if (dot) {
      dot.className = 'monitor-dot' + (cpuPercent > 80 ? ' danger' : cpuPercent > 50 ? ' warning' : '');
    }

    if (cores) cores.textContent = data.cpu_cores || '-';
    if (procCpu) procCpu.textContent = `${Math.round(data.process_cpu_percent || 0)}%`;
    if (threads) threads.textContent = data.active_threads || '-';
    if (disk) disk.textContent = `${data.disk_used_gb || 0} / ${data.disk_total_gb || 0} GB`;
    if (network) network.textContent = data.network_status || 'Offline';
    if (inference) inference.textContent = data.inference_engine || 'llama.cpp';
    if (gpu) gpu.textContent = data.gpu_used ? 'Used' : 'Not Used';

    const engineTag = $('#monitor-engine');
    if (engineTag) {
      engineTag.textContent = data.inference_details === 'GPU Accelerated' ? 'GPU' : 'CPU';
    }

    drawMonitorChart();
  } catch (err) {
    console.error('Monitor update failed:', err);
  }
}

function drawMonitorChart() {
  const canvas = $('#monitor-chart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  const dpr = window.devicePixelRatio || 1;

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, width, height);

  const cpuData = monitorHistory.cpu;
  const memData = monitorHistory.memory;
  const len = Math.max(cpuData.length, memData.length);
  if (len < 2) return;

  const step = width / 59;

  ctx.beginPath();
  ctx.strokeStyle = '#3b82f6';
  ctx.lineWidth = 1.5;
  cpuData.forEach((v, i) => {
    const x = i * step;
    const y = height - (v / 100) * (height - 4) - 2;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.beginPath();
  ctx.strokeStyle = '#f59e0b';
  ctx.lineWidth = 1.5;
  memData.forEach((v, i) => {
    const x = i * step;
    const y = height - (v / 100) * (height - 4) - 2;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.font = '9px sans-serif';
  ctx.fillStyle = '#64748b';
  ctx.textAlign = 'left';
  ctx.fillText('60s', 4, height - 3);
}

// Export functions

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initScanPage();
  initSearch();
  loadStats();
  initMonitor();
});