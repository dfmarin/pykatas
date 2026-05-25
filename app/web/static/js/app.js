/**
 * app.js — Global UI utilities for Kata Platform
 * Handles: flash auto-dismiss, kata filter, general helpers.
 */
'use strict';

/* ── Flash Message Auto-Dismiss ─────────────────────────────── */
(function initFlash() {
  const container = document.querySelector('.flash-container');
  if (!container) return;

  const flashes = container.querySelectorAll('.flash');

  flashes.forEach((flash, i) => {
    // Click to dismiss immediately
    flash.addEventListener('click', () => dismissFlash(flash));

    // Auto-dismiss after 4s (staggered)
    setTimeout(() => dismissFlash(flash), 4000 + i * 400);
  });

  function dismissFlash(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateX(16px)';
    el.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    setTimeout(() => {
      el.remove();
      if (!container.children.length) container.remove();
    }, 220);
  }
})();

/* ── Kata Filter (index page) ───────────────────────────────── */
(function initFilter() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  if (!filterBtns.length) return;

  const grid         = document.getElementById('kata-grid');
  const countEl      = document.getElementById('kata-count');
  const emptyEl      = document.getElementById('no-filter-results');
  const allCards     = grid ? Array.from(grid.querySelectorAll('.kata-card')) : [];

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;

      // Toggle active state
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');

      // Show/hide cards
      let visible = 0;
      allCards.forEach((card, idx) => {
        const match = filter === 'all' || card.dataset.difficulty === filter;
        card.dataset.hidden = match ? 'false' : 'true';
        if (match) {
          card.style.display = '';
          card.style.animationDelay = `${visible * 35}ms`;
          visible++;
        } else {
          card.style.display = 'none';
        }
      });

      // Update count
      if (countEl) {
        countEl.textContent = `${visible} kata${visible !== 1 ? 's' : ''}`;
      }

      // Empty state
      if (emptyEl) {
        emptyEl.style.display = visible === 0 ? 'block' : 'none';
      }
    });
  });
})();

/* ── Pane Tabs (kata_detail page) ───────────────────────────── */
(function initTabs() {
  const tabBtns = document.querySelectorAll('.pane-tab');
  if (!tabBtns.length) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;

      // Deactivate all tabs + panels
      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      document.querySelectorAll('.pane-panel').forEach(p => p.classList.remove('active'));

      // Activate selected
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      const panel = document.getElementById(`tab-${tabName}`);
      if (panel) panel.classList.add('active');
    });
  });
})();

/* ── Utility: debounce ──────────────────────────────────────── */
function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}

/* ── Utility: escape HTML ───────────────────────────────────── */
function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/* ── Utility: format ms ─────────────────────────────────────── */
function formatMs(ms) {
  if (!ms && ms !== 0) return '—';
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

/* ── Utility: relative time ─────────────────────────────────── */
function timeAgo(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  const diff = Date.now() - date.getTime();
  const s = Math.floor(diff / 1000);
  if (s < 60)  return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s/60)}m ago`;
  return `${Math.floor(s/3600)}h ago`;
}

// Expose utilities globally for submission.js
window.KataUI = { escapeHtml, formatMs, timeAgo };
