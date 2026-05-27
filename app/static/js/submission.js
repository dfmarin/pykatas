/**
 * submission.js — Kata editor, submission flow, and feedback rendering
 *
 * Responsibilities:
 *  1. Boot CodeMirror on the #code-editor textarea
 *  2. Render README markdown into the instructions pane via marked.js
 *  3. Handle submit button → POST /api/v1/katas/<id>/submit
 *  4. Poll GET /api/v1/submissions/<id> until terminal status
 *  5. Render structured feedback (tests, lint, metrics) into the panel
 */
'use strict';

(function KataSubmission() {

  /* ── Config ──────────────────────────────────────────────── */
  const POLL_INTERVAL_MS  = 1500;
  const POLL_MAX_ATTEMPTS = 80;     // 80 × 1.5s = 2 minutes max
  const MAX_CODE_BYTES    = 64 * 1024;

  const TERMINAL_STATUSES = new Set(['passed', 'failed', 'error', 'timeout']);

  /* ── DOM refs ───────────────────────────────────────────── */
  const workspace    = document.getElementById('kata-workspace');
  if (!workspace) return;   // Not on kata_detail page

  const kataDataEl   = document.getElementById('kata-data');
  const kataData     = kataDataEl ? JSON.parse(kataDataEl.textContent) : null;
  if (!kataData) return;

  const btnSubmit    = document.getElementById('btn-submit');
  const btnReset     = document.getElementById('btn-reset');
  const submitInfo   = document.getElementById('submit-info');
  const feedbackPanel = document.getElementById('feedback-panel');
  const feedbackInner = document.getElementById('feedback-inner');
  const textareaEl   = document.getElementById('code-editor');

  /* ── CodeMirror Initialisation ──────────────────────────── */
  let editor = null;

  if (typeof CodeMirror !== 'undefined' && textareaEl) {
    editor = CodeMirror.fromTextArea(textareaEl, {
      mode:            'python',
      theme:           'default',       // We override all colours in CSS
      lineNumbers:     true,
      indentUnit:      4,
      tabSize:         4,
      indentWithTabs:  false,
      autoCloseBrackets: true,
      matchBrackets:   true,
      styleActiveLine: true,
      lineWrapping:    false,
      extraKeys: {
        // Tab → 4 spaces
        'Tab': cm => cm.execCommand('insertSoftTab'),
        // Ctrl/Cmd+Enter → submit
        'Ctrl-Enter': () => handleSubmit(),
        'Cmd-Enter':  () => handleSubmit(),
      },
    });

    // Fit editor to its container
    function fitEditor() {
      const area = document.querySelector('.editor-area');
      if (area) {
        editor.setSize('100%', area.clientHeight || '100%');
      }
    }
    fitEditor();
    window.addEventListener('resize', fitEditor);
  }


  /* ── Reset Button ───────────────────────────────────────── */
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (!confirm('Reset to starter code? Your current changes will be lost.')) return;
      if (editor) {
        editor.setValue(kataData.starterCode);
        editor.clearHistory();
        editor.focus();
      }
      closePanel();
      setInfoIdle();
    });
  }

  /* ── Submit Handler ─────────────────────────────────────── */
  if (btnSubmit) {
    btnSubmit.addEventListener('click', handleSubmit);
  }

  async function handleSubmit() {
    if (!btnSubmit || btnSubmit.disabled) return;

    const code = getCode();
    if (!code.trim()) {
      flashInfo('Write some code first.', 'warning');
      return;
    }
    if (new Blob([code]).size > MAX_CODE_BYTES) {
      flashInfo('Code exceeds 64 KB limit.', 'error');
      return;
    }

    setLoading(true);
    closePanel();

    let submissionId;
    try {
      submissionId = await postSubmission(kataData.id, code);
    } catch (err) {
      setLoading(false);
      setInfoError(err.message || 'Could not submit. Try again.');
      return;
    }

    setInfoRunning();
    await pollUntilDone(submissionId);
    setLoading(false);
  }

  /* ── API: POST submission ───────────────────────────────── */
  async function postSubmission(kataId, sourceCode) {
    const res = await fetch(`/api/v1/katas/${encodeURIComponent(kataId)}/submit`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ source_code: sourceCode }),
    });

    if (res.status === 401) throw new Error('You must be logged in to submit.');
    if (res.status === 404) throw new Error('Kata not found.');
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `Server error (${res.status})`);
    }

    const data = await res.json();
    return data.id;
  }

  /* ── API: Poll submission status ────────────────────────── */
  async function pollUntilDone(submissionId) {
    let attempts = 0;

    return new Promise((resolve) => {
      const interval = setInterval(async () => {
        attempts++;

        if (attempts > POLL_MAX_ATTEMPTS) {
          clearInterval(interval);
          setInfoError('Polling timed out. Refresh the page to see results.');
          resolve();
          return;
        }

        let data;
        try {
          const res = await fetch(`/api/v1/submissions/${submissionId}`);
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          data = await res.json();
        } catch (err) {
          // Transient network error — keep polling
          console.warn('[KataUI] Poll error:', err);
          return;
        }

        if (TERMINAL_STATUSES.has(data.status)) {
          clearInterval(interval);
          renderFeedback(data);
          resolve();
        }
        // else: pending/running → keep polling, info bar already shows spinner
      }, POLL_INTERVAL_MS);
    });
  }

  /* ── Feedback Rendering ─────────────────────────────────── */
  function renderFeedback(data) {
    const { escapeHtml, formatMs } = window.KataUI;
    const status = data.status || 'error';

    // Update status bar (below editor)
    setInfoResult(data);

    // Open panel
    feedbackPanel.dataset.status = status;

    const statusMeta  = buildStatusMeta(data, status);
    const testsHtml   = buildTestsHtml(data, escapeHtml);
    const lintHtml    = buildLintHtml(data, escapeHtml);
    const outputHtml  = buildRawOutputHtml(data, escapeHtml);

    feedbackInner.innerHTML = `
      <!-- Status row -->
      <div class="feedback-status-row feedback-status--${status}">
        <span class="feedback-status-label">${STATUS_LABELS[status] || status.toUpperCase()}</span>
        <div class="feedback-metrics">${statusMeta}</div>
      </div>

      ${testsHtml}
      ${lintHtml}
      ${outputHtml}
    `;

    openPanel();
  }

  /* ── Feedback Builders ──────────────────────────────────── */
  const STATUS_LABELS = {
    passed:  '✓ All Tests Passed',
    failed:  '✗ Tests Failed',
    error:   '⚠ Execution Error',
    timeout: '⏱ Time Limit Exceeded',
  };

  function buildStatusMeta(data, status) {
    const { formatMs } = window.KataUI;
    const parts = [];

    // Test count
    const fb = data.feedback_json;
    if (fb && fb.tests) {
      const t = fb.tests;
      if (typeof t.total === 'number') {
        parts.push(`<strong>${t.passed || 0}</strong>/${t.total} tests`);
      }
    }

    // Execution time
    if (data.execution_time_ms != null) {
      parts.push(`<strong>${formatMs(data.execution_time_ms)}</strong>`);
    }

    return parts.join('<span class="submit-info-sep">·</span>');
  }

  function buildTestsHtml(data, escapeHtml) {
    const fb = data.feedback_json;
    if (!fb || !fb.tests || !fb.tests.report) {
      // Fallback: show raw pytest output if no structured report
      if (data.pytest_output) {
        return `
          <p class="feedback-section-title">Output</p>
          <pre class="feedback-raw" style="max-height:180px">${escapeHtml(data.pytest_output)}</pre>
        `;
      }
      return '';
    }

    const tests = fb.tests.report.tests || [];
    if (!tests.length) return '';

    const rows = tests.map(t => {
      const outcome  = t.outcome || 'failed';
      const isPassed = outcome === 'passed';
      const name     = cleanTestName(t.nodeid || t.name || '');
      const errText  = !isPassed && t.call && t.call.longrepr
        ? `<span class="test-error-msg">${escapeHtml(truncate(t.call.longrepr, 300))}</span>`
        : '';

      return `
        <li class="test-row test-row--${isPassed ? 'pass' : 'fail'}">
          <span class="test-icon">${isPassed ? '●' : '○'}</span>
          <div>
            <span class="test-name">${escapeHtml(name)}</span>
            ${errText}
          </div>
        </li>
      `;
    }).join('');

    return `
      <p class="feedback-section-title">Test Results</p>
      <ul class="test-list">${rows}</ul>
    `;
  }

  function buildLintHtml(data, escapeHtml) {
    const fb = data.feedback_json;
    if (!fb || !fb.lint || !fb.lint.issues || !fb.lint.issues.length) return '';

    const rows = fb.lint.issues.map(issue => {
      const loc  = issue.location || {};
      const line = loc.row || 0;
      const col  = loc.column || 0;
      return `
        <li class="lint-row">
          <span class="lint-loc">L${line}:${col}</span>
          <span class="lint-code">${escapeHtml(issue.code || '')}</span>
          <span class="lint-msg">${escapeHtml(issue.message || '')}</span>
        </li>
      `;
    }).join('');

    return `
      <p class="feedback-section-title" style="margin-top:0.75rem">Lint Issues</p>
      <ul class="lint-list">${rows}</ul>
    `;
  }

  function buildRawOutputHtml(data, escapeHtml) {
    const raw = data.stderr || data.stdout || '';
    if (!raw.trim()) return '';

    return `
      <details class="feedback-details">
        <summary>Raw Output</summary>
        <pre class="feedback-raw">${escapeHtml(truncate(raw, 3000))}</pre>
      </details>
    `;
  }

  /* ── Panel Open/Close ───────────────────────────────────── */
  function openPanel() {
    feedbackPanel.classList.add('open');
    // Scroll panel into view on mobile
    if (window.innerWidth < 960) {
      feedbackPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function closePanel() {
    feedbackPanel.classList.remove('open');
    feedbackPanel.removeAttribute('data-status');
    feedbackInner.innerHTML = '';
  }

  /* ── Submit Info Bar States ─────────────────────────────── */
  function setInfoIdle() {
    if (!submitInfo) return;
    submitInfo.innerHTML = `
      <span style="color:var(--text-3);font-size:0.7rem;letter-spacing:0.06em">
        Ready to submit
      </span>
    `;
  }

  function setInfoRunning() {
    if (!submitInfo) return;
    submitInfo.innerHTML = `
      <span class="dot dot--running"></span>
      <span class="submit-info-status running">Executing…</span>
    `;
  }

  function setInfoResult(data) {
    if (!submitInfo) return;
    const { formatMs } = window.KataUI;
    const status = data.status || 'error';

    const fb = data.feedback_json;
    let testSummary = '';
    if (fb && fb.tests && typeof fb.tests.total === 'number') {
      testSummary = `
        <span class="submit-info-sep">·</span>
        <span>${fb.tests.passed || 0}/${fb.tests.total} tests</span>
      `;
    }

    let timeSummary = '';
    if (data.execution_time_ms != null) {
      timeSummary = `
        <span class="submit-info-sep">·</span>
        <span>${formatMs(data.execution_time_ms)}</span>
      `;
    }

    submitInfo.innerHTML = `
      <span class="dot dot--${status}"></span>
      <span class="submit-info-status ${status}">
        ${status.toUpperCase()}
      </span>
      ${testSummary}
      ${timeSummary}
    `;
  }

  function setInfoError(msg) {
    if (!submitInfo) return;
    const { escapeHtml } = window.KataUI;
    submitInfo.innerHTML = `
      <span style="color:var(--error);font-size:0.73rem">${escapeHtml(msg)}</span>
    `;
  }

  function flashInfo(msg, type = 'info') {
    if (!submitInfo) return;
    const prev = submitInfo.innerHTML;
    const color = type === 'error' ? 'var(--error)' : type === 'warning' ? 'var(--warning)' : 'var(--info)';
    submitInfo.innerHTML = `<span style="color:${color};font-size:0.73rem">${msg}</span>`;
    setTimeout(() => { submitInfo.innerHTML = prev; }, 3000);
  }

  /* ── Loading State ──────────────────────────────────────── */
  function setLoading(loading) {
    if (!btnSubmit) return;
    if (loading) {
      btnSubmit.disabled = true;
      btnSubmit.classList.add('btn--loading');
      btnSubmit.dataset.originalText = btnSubmit.textContent;
    } else {
      btnSubmit.disabled = false;
      btnSubmit.classList.remove('btn--loading');
      btnSubmit.textContent = btnSubmit.dataset.originalText || 'Submit Solution';
    }
  }

  /* ── Helpers ────────────────────────────────────────────── */
  function getCode() {
    return editor ? editor.getValue() : (textareaEl ? textareaEl.value : '');
  }

  function cleanTestName(nodeid) {
    // "tests/test_public.py::test_basic_case" → "test_basic_case"
    const parts = nodeid.split('::');
    return parts[parts.length - 1] || nodeid;
  }

  function truncate(str, maxLen) {
    if (!str || str.length <= maxLen) return str;
    return str.slice(0, maxLen) + '\n… (truncated)';
  }

})();
