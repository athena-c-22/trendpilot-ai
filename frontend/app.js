(function () {
  const topicInput = document.getElementById('topic');
  const runBtn = document.getElementById('runBtn');
  const fileUpload = document.getElementById('fileUpload');
  const inputSection = document.getElementById('inputSection');
  const statusSection = document.getElementById('statusSection');
  const statusText = document.getElementById('statusText');
  const statusDetail = document.getElementById('statusDetail');
  const errorSection = document.getElementById('errorSection');
  const errorCard = document.getElementById('errorCard');
  const reportSection = document.getElementById('reportSection');
  const reportTopic = document.getElementById('reportTopic');
  const themeToggle = document.getElementById('themeToggle');

  const contentIds = {
    market_overview: 'contentMarketOverview',
    competitor_landscape: 'contentCompetitors',
    target_audience: 'contentAudience',
    pricing_strategy: 'contentPricing',
    marketing_channels: 'contentChannels',
    launch_plan: 'contentLaunch',
    key_insights: 'contentInsights',
    risks_and_mitigations: 'contentRisks',
  };

  const sectionIds = {
    market_overview: 'blockMarketOverview',
    competitor_landscape: 'blockCompetitors',
    target_audience: 'blockAudience',
    pricing_strategy: 'blockPricing',
    marketing_channels: 'blockChannels',
    launch_plan: 'blockLaunch',
    key_insights: 'blockInsights',
    risks_and_mitigations: 'blockRisks',
  };

  function getInitialTheme() {
    const stored = window.localStorage ? window.localStorage.getItem('trendpilot-theme') : null;
    if (stored === 'light' || stored === 'dark') return stored;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
    return 'dark';
  }

  function applyTheme(theme) {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || getInitialTheme();
    const next = current === 'light' ? 'dark' : 'light';
    applyTheme(next);
    if (window.localStorage) {
      window.localStorage.setItem('trendpilot-theme', next);
    }
  }

  applyTheme(getInitialTheme());

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      toggleTheme();
    });
  }

  function show(el) {
    el.classList.remove('hidden');
  }

  function hide(el) {
    el.classList.add('hidden');
  }

  function setStatus(message, detail) {
    statusText.textContent = message;
    statusDetail.textContent = detail || '';
  }

  function showError(message) {
    errorCard.textContent = message;
    show(errorSection);
    hide(statusSection);
    hide(reportSection);
  }

  function clearError() {
    hide(errorSection);
  }

  function renderReport(report, topic) {
    reportTopic.textContent = topic;

    function setBlock(key, render) {
      const contentId = contentIds[key];
      const sectionId = sectionIds[key];
      if (!contentId || !sectionId) return;
      const el = document.getElementById(contentId);
      const section = document.getElementById(sectionId);
      if (!el || !section) return;
      const content = report[key];
      if (content !== undefined && content !== null && content !== '' && (typeof content !== 'object' || (Array.isArray(content) && content.length > 0))) {
        el.innerHTML = render(content);
        show(section);
      } else {
        hide(section);
      }
    }

    setBlock('market_overview', function (v) {
      return '<p>' + escapeHtml(String(v)) + '</p>';
    });

    setBlock('competitor_landscape', function (arr) {
      if (!Array.isArray(arr) || arr.length === 0) return '<p>No competitors listed.</p>';
      return arr
        .map(
          (c) =>
            '<div class="item-card"><strong>' +
            escapeHtml(c.name || c) +
            '</strong>' +
            (c.positioning ? '<span>' + escapeHtml(c.positioning) + '</span>' : '') +
            (c.strength ? '<span> ' + escapeHtml(c.strength) + '</span>' : '') +
            '</div>'
        )
        .join('');
    });

    setBlock('target_audience', function (arr) {
      if (!Array.isArray(arr) || arr.length === 0) return '<p>No segments defined.</p>';
      return arr
        .map(
          (a) =>
            '<div class="item-card"><strong>' +
            escapeHtml(a.segment || a) +
            '</strong>' +
            (a.description ? '<span>' + escapeHtml(a.description) + '</span>' : '') +
            '</div>'
        )
        .join('');
    });

    setBlock('pricing_strategy', function (v) {
      return '<p>' + escapeHtml(String(v)) + '</p>';
    });

    setBlock('marketing_channels', function (arr) {
      if (!Array.isArray(arr) || arr.length === 0) return '<p>No channels specified.</p>';
      return arr
        .map(
          (c) =>
            '<div class="item-card"><strong>' +
            escapeHtml(c.channel || c) +
            '</strong>' +
            (c.tactics ? '<span>' + escapeHtml(c.tactics) + '</span>' : '') +
            '</div>'
        )
        .join('');
    });

    setBlock('launch_plan', function (arr) {
      if (!Array.isArray(arr) || arr.length === 0) return '<p>No launch phases.</p>';
      return arr
        .map(
          (l) =>
            '<div class="item-card"><strong>' +
            escapeHtml(l.phase || l) +
            '</strong>' +
            (l.actions ? '<span>' + escapeHtml(l.actions) + '</span>' : '') +
            '</div>'
        )
        .join('');
    });

    setBlock('key_insights', function (arr) {
      if (!Array.isArray(arr) || arr.length === 0) return '<p>None.</p>';
      return '<ul>' + arr.map((i) => '<li>' + escapeHtml(String(i)) + '</li>').join('') + '</ul>';
    });

    setBlock('risks_and_mitigations', function (arr) {
      if (!Array.isArray(arr) || arr.length === 0) return '<p>None.</p>';
      return arr
        .map(
          (r) =>
            '<div class="item-card"><strong>Risk:</strong> ' +
            escapeHtml(r.risk || r) +
            (r.mitigation ? '<span><strong>Mitigation:</strong> ' + escapeHtml(r.mitigation) + '</span>' : '') +
            '</div>'
        )
        .join('');
    });

    show(reportSection);
    hide(statusSection);
    hide(errorSection);
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function getApiBase() {
    const base = document.querySelector('meta[name="api-base"]');
    if (base && base.getAttribute('content')) {
      return base.getAttribute('content').replace(/\/$/, '');
    }
    return window.location.origin;
  }

  function getApiKey() {
    const meta = document.querySelector('meta[name="api-key"]');
    return meta ? (meta.getAttribute('content') || '').trim() : '';
  }

  runBtn.addEventListener('click', async function () {
    const topic = (topicInput.value || '').trim();
    if (!topic) {
      showError('Please enter a topic.');
      return;
    }

    clearError();
    runBtn.disabled = true;
    show(statusSection);
    hide(reportSection);

    const base = getApiBase();
    const apiKey = getApiKey();

    try {
      if (fileUpload && fileUpload.files && fileUpload.files.length > 0) {
        setStatus('Uploading documents…', 'Adding to knowledge base');
        const formData = new FormData();
        for (let i = 0; i < fileUpload.files.length; i++) {
          formData.append('files', fileUpload.files[i]);
        }
        const uploadRes = await fetch(base + '/upload', {
          method: 'POST',
          headers: apiKey ? { 'X-API-Key': apiKey } : {},
          body: formData,
        });
        const uploadData = await uploadRes.json().catch(function () { return {}; });
        if (!uploadRes.ok) {
          const msg = uploadData.detail || uploadRes.statusText || 'Upload failed';
          showError(typeof msg === 'string' ? msg : JSON.stringify(msg));
          runBtn.disabled = false;
          return;
        }
        if (uploadData.errors && uploadData.errors.length > 0) {
          setStatus('Running research pipeline…', 'Some uploads had issues. ' + uploadData.errors.join(' '));
        }
      }

      setStatus('Running research pipeline…', 'Search → Data → Fact-check → Strategy');

      const headers = { 'Content-Type': 'application/json' };
      if (apiKey) headers['X-API-Key'] = apiKey;
      const res = await fetch(base + '/research', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ topic: topic }),
      });

      const data = await res.json().catch(function () {
        return { detail: res.statusText || 'Request failed' };
      });

      if (!res.ok) {
        if (res.status === 401) {
          showError('Invalid or missing API key. If this site requires a key, contact the administrator.');
          return;
        }
        if (res.status === 429) {
          showError('Rate limit exceeded. Please try again in a minute.');
          return;
        }
        const msg = Array.isArray(data.detail) ? data.detail.map(function (d) { return d.msg; }).join(', ') : (data.detail || data.message || res.statusText);
        showError(msg || 'Something went wrong.');
        return;
      }

      renderReport(data.report || {}, data.topic || topic);
    } catch (err) {
      showError(err.message || 'Network error. Is the backend running at ' + getApiBase() + '?');
    } finally {
      runBtn.disabled = false;
    }
  });

  topicInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      runBtn.click();
    }
  });
})();
