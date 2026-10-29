/**
 * Histarchexplorer - OpenAtlas API v1 Search Controller
 * Manages interactive filters (case studies, optional entity classes, timespan chooser),
 * asynchronous table rendering, sorting, pagination, quick-filtering, and CSV export.
 */

(function initSearchPage() {
  const SLIDER_MIN = -2000;
  const SLIDER_MAX = 2000;

  /**
   * Extract localized description text and strip HTML/language markers.
   */
  function cleanDescription(rawDesc) {
    if (!rawDesc || typeof rawDesc !== 'string') return '';
    let text = rawDesc;
    const lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
    const langRegex = new RegExp(`##${lang}_##([\\s\\S]*?)##_${lang}##`, 'i');
    const enRegex = /##en_##([\s\S]*?)##_en##/i;
    const anyBlockRegex = /##[a-z]{2}_##([\s\S]*?)##_[a-z]{2}##/i;

    const match = text.match(langRegex) || text.match(enRegex) || text.match(anyBlockRegex);
    if (match && match[1]) {
      text = match[1];
    }

    return text
      .replace(/##[a-z]{2}_##/gi, '')
      .replace(/##_[a-z]{2}##/gi, '')
      .replace(/<[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * Format a numeric year string into human-readable BC/AD notation.
   */
  function formatYearLabel(yearVal, labels) {
    if (yearVal === null || yearVal === undefined || String(yearVal).trim() === '') {
      return '';
    }
    const num = Number(yearVal);
    if (Number.isNaN(num)) return String(yearVal);
    if (num < 0) return `${Math.abs(num)} ${labels.bc}`;
    return `${num} ${labels.ad}`;
  }

  /**
   * Format client-side timespan fallback if backend display string is empty.
   */
  function resolveTimespanText(item, labels) {
    if (item.timespanDisplay) return item.timespanDisplay;
    const ts = item.timespan;
    if (!ts || typeof ts !== 'object') return '—';
    const extractYear = (bound) => {
      if (!bound || typeof bound !== 'object') return '';
      const raw = bound.earliest || bound.latest || '';
      if (!raw) return '';
      const isBc = raw.startsWith('-');
      const clean = isBc ? raw.slice(1) : raw;
      const yearNum = parseInt(clean.split('-')[0], 10);
      if (!yearNum) return '';
      return isBc ? `${yearNum} ${labels.bc}` : String(yearNum);
    };
    const startStr = extractYear(ts.start);
    const endStr = extractYear(ts.end);
    if (startStr && endStr) {
      return startStr === endStr ? startStr : `${startStr} – ${endStr}`;
    }
    return startStr || endStr || '—';
  }

  /**
   * Build a single table row element for a search result item.
   */
  function createResultRow(item, ctx) {
    const tr = document.createElement('tr');
    tr.className = 'search-result-row';

    const entityId = String(item.id || '').split('/').pop();
    const entityUrl = `${ctx.entityBaseUrl}${encodeURIComponent(entityId)}`;
    const entityName = item.name || ctx.labels.unnamed;
    const sysClass = item.systemClass || item.system_class || '';
    const classMeta = ctx.classMetaMap[sysClass] || {
      label: sysClass.replace(/_/g, ' ') || 'Entity',
      icon: 'bi-tag',
      color_key: 'types',
    };
    const timespanText = resolveTimespanText(item, ctx.labels);
    const csObj = ctx.caseStudyMap[Number(item.caseStudyId)];
    const csAcronym = csObj ? csObj.acronym : '—';
    const descriptionText = cleanDescription(item.description);

    tr.dataset.filterText = `${entityName} ${sysClass} ${timespanText} ${csAcronym} ${descriptionText}`
      .toLowerCase();

    // 1. Entity Name & ID cell
    const tdName = document.createElement('td');
    tdName.className = 'ps-4 py-3';
    const nameWrap = document.createElement('div');
    nameWrap.className = 'd-flex flex-column';
    const titleLink = document.createElement('a');
    titleLink.href = entityUrl;
    titleLink.className = 'fw-semibold text-decoration-none search-entity-link';
    titleLink.textContent = entityName;
    nameWrap.appendChild(titleLink);
    if (entityId) {
      const idSpan = document.createElement('span');
      idSpan.className = 'text-muted extra-small font-monospace';
      idSpan.textContent = `#${entityId}`;
      nameWrap.appendChild(idSpan);
    }
    tdName.appendChild(nameWrap);
    tr.appendChild(tdName);

    // 2. Class cell
    const tdClass = document.createElement('td');
    const classBadge = document.createElement('span');
    classBadge.className = `search-table-class-badge search-class-${classMeta.color_key || 'types'}`;
    const classIcon = document.createElement('i');
    classIcon.className = `bi ${classMeta.icon || 'bi-tag'} me-1`;
    const classText = document.createElement('span');
    classText.textContent = classMeta.label;
    classBadge.appendChild(classIcon);
    classBadge.appendChild(classText);
    tdClass.appendChild(classBadge);
    tr.appendChild(tdClass);

    // 3. Timespan cell
    const tdTime = document.createElement('td');
    if (timespanText && timespanText !== '—') {
      const timeBadge = document.createElement('span');
      timeBadge.className = 'badge bg-body-secondary text-body rounded-pill fw-normal px-2 py-1';
      const timeIcon = document.createElement('i');
      timeIcon.className = 'bi bi-clock-history text-primary me-1';
      const timeSpan = document.createElement('span');
      timeSpan.textContent = timespanText;
      timeBadge.appendChild(timeIcon);
      timeBadge.appendChild(timeSpan);
      tdTime.appendChild(timeBadge);
    } else {
      const emptyTime = document.createElement('span');
      emptyTime.className = 'text-muted small';
      emptyTime.textContent = '—';
      tdTime.appendChild(emptyTime);
    }
    tr.appendChild(tdTime);

    // 4. Case Study cell
    const tdCs = document.createElement('td');
    if (csObj) {
      const csBadge = document.createElement('span');
      csBadge.className = 'badge bg-primary-subtle text-primary rounded-pill fw-medium px-2 py-1';
      csBadge.title = csObj.name || csObj.acronym;
      csBadge.textContent = csObj.acronym;
      tdCs.appendChild(csBadge);
    } else {
      const dash = document.createElement('span');
      dash.className = 'text-muted small';
      dash.textContent = '—';
      tdCs.appendChild(dash);
    }
    tr.appendChild(tdCs);

    // 5. Description cell
    const tdDesc = document.createElement('td');
    tdDesc.className = 'search-desc-cell';
    if (descriptionText) {
      const descDiv = document.createElement('div');
      descDiv.className = 'text-muted small search-desc-clamp';
      descDiv.title = descriptionText;
      descDiv.textContent = descriptionText;
      tdDesc.appendChild(descDiv);
    } else {
      const noDesc = document.createElement('span');
      noDesc.className = 'text-muted small';
      noDesc.textContent = '—';
      tdDesc.appendChild(noDesc);
    }
    tr.appendChild(tdDesc);

    // 6. Action cell
    const tdAction = document.createElement('td');
    tdAction.className = 'text-end pe-4';
    const viewBtn = document.createElement('a');
    viewBtn.href = entityUrl;
    viewBtn.className = 'btn btn-sm btn-outline-primary rounded-pill px-3';
    const viewText = document.createElement('span');
    viewText.textContent = ctx.labels.view;
    const viewIcon = document.createElement('i');
    viewIcon.className = 'bi bi-arrow-right ms-1';
    viewBtn.appendChild(viewText);
    viewBtn.appendChild(viewIcon);
    tdAction.appendChild(viewBtn);
    tr.appendChild(tdAction);

    return tr;
  }

  /**
   * Export currently loaded items to a downloadable CSV file.
   */
  function exportItemsToCsv(items, ctx) {
    if (!Array.isArray(items) || items.length === 0) return;
    const headers = ['ID', 'Name', 'Class', 'Timespan', 'CaseStudy', 'Description'];
    const escapeCsv = (val) => {
      const str = String(val ?? '').replace(/"/g, '""');
      return `"${str}"`;
    };
    const rows = items.map((item) => {
      const sysClass = item.systemClass || item.system_class || '';
      const csObj = ctx.caseStudyMap[Number(item.caseStudyId)];
      return [
        item.id || '',
        item.name || '',
        sysClass,
        resolveTimespanText(item, ctx.labels),
        csObj ? csObj.acronym : '',
        cleanDescription(item.description),
      ].map(escapeCsv).join(',');
    });
    const csvContent = `\uFEFF${headers.join(',')}\n${rows.join('\n')}`;
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'histarchexplorer_search_results.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Main initialization once the DOM is ready.
   */
  function setupSearchApp() {
    const root = document.getElementById('searchAppRoot');
    if (!root) return;

    const config = window.SEARCH_CONFIG || {};
    const initial = config.initialState || {};
    const classMetaMap = config.classMetaMap || {};
    const caseStudyMap = {};
    (config.availableCaseStudies || []).forEach((cs) => {
      caseStudyMap[Number(cs.id)] = cs;
    });

    const labels = {
      unnamed: root.dataset.labelUnnamed || 'Unnamed',
      allClasses: root.dataset.labelAllClasses || 'All Classes',
      allStudies: root.dataset.labelAllStudies || 'All Case Studies',
      loading: root.dataset.labelLoading || 'Loading...',
      error: root.dataset.labelError || 'Error loading results.',
      empty: root.dataset.labelEmpty || 'No results found.',
      view: root.dataset.labelView || 'View',
      bc: root.dataset.labelBc || 'BC',
      ad: root.dataset.labelAd || 'AD',
      anyTime: root.dataset.labelAnyTime || 'Any period',
      from: root.dataset.labelFrom || 'from',
      until: root.dataset.labelUntil || 'until',
      results: root.dataset.labelResults || 'entities',
    };

    const dom = {
      form: document.getElementById('searchMainForm'),
      queryInput: document.getElementById('searchQueryInput'),
      clearQueryBtn: document.getElementById('searchClearQueryBtn'),
      caseStudyPills: document.getElementById('caseStudyPills'),
      entityClassPills: document.getElementById('entityClassPills'),
      timespanPresets: document.getElementById('timespanPresets'),
      sliderMin: document.getElementById('timespanSliderMin'),
      sliderMax: document.getElementById('timespanSliderMax'),
      startDateInput: document.getElementById('startDateInput'),
      endDateInput: document.getElementById('endDateInput'),
      startEraHint: document.getElementById('startEraHint'),
      endEraHint: document.getElementById('endEraHint'),
      timespanBadge: document.getElementById('timespanSummaryBadge'),
      clearTimespanBtn: document.getElementById('clearTimespanBtn'),
      activeFilterBadge: document.getElementById('activeFilterCountBadge'),
      resetAllBtn: document.getElementById('resetAllFiltersBtn'),
      emptyResetBtn: document.getElementById('emptyResetBtn'),
      retryBtn: document.getElementById('retrySearchBtn'),
      quickFilterInput: document.getElementById('tableQuickFilterInput'),
      sortBySelect: document.getElementById('sortBySelect'),
      sortOrderBtn: document.getElementById('sortOrderBtn'),
      sortOrderIcon: document.getElementById('sortOrderIcon'),
      limitSelect: document.getElementById('limitSelect'),
      exportCsvBtn: document.getElementById('exportCsvBtn'),
      totalBadge: document.getElementById('resultsTotalBadge'),
      loadingState: document.getElementById('searchLoadingState'),
      errorState: document.getElementById('searchErrorState'),
      emptyState: document.getElementById('searchEmptyState'),
      tableWrapper: document.getElementById('searchTableWrapper'),
      tbody: document.getElementById('searchResultsTbody'),
      prevPageBtn: document.getElementById('prevPageBtn'),
      nextPageBtn: document.getElementById('nextPageBtn'),
      pageIndicator: document.getElementById('currentPageIndicator'),
      paginationSummary: document.getElementById('paginationSummaryText'),
      sortableHeaders: Array.from(document.querySelectorAll('.sortable-th')),
    };

    const state = {
      query: initial.query || '',
      caseStudies: new Set((initial.case_study_ids || []).map((v) => String(v))),
      entityClasses: new Set(initial.entity_classes || []),
      startDate: initial.start_date ? String(initial.start_date) : '',
      endDate: initial.end_date ? String(initial.end_date) : '',
      sortBy: initial.sort_by || 'name',
      sortOrder: initial.sort_order || 'asc',
      limit: Number(initial.limit) || 50,
      page: Number(initial.page) || 1,
      currentItems: [],
      totalItems: 0,
      hasMore: false,
      requestToken: 0,
    };

    let debounceTimer = null;

    function syncClearQueryBtn() {
      if (!dom.clearQueryBtn || !dom.queryInput) return;
      dom.clearQueryBtn.classList.toggle('d-none', !dom.queryInput.value.trim());
    }

    function updateTimespanUi() {
      const hasStart = state.startDate !== '';
      const hasEnd = state.endDate !== '';
      if (dom.startEraHint) {
        dom.startEraHint.textContent = hasStart
          ? formatYearLabel(state.startDate, labels)
          : `${labels.bc}/${labels.ad}`;
      }
      if (dom.endEraHint) {
        dom.endEraHint.textContent = hasEnd
          ? formatYearLabel(state.endDate, labels)
          : `${labels.bc}/${labels.ad}`;
      }
      if (dom.timespanBadge) {
        const startLbl = formatYearLabel(state.startDate, labels);
        const endLbl = formatYearLabel(state.endDate, labels);
        if (hasStart && hasEnd) {
          dom.timespanBadge.textContent = `${startLbl} – ${endLbl}`;
        } else if (hasStart) {
          dom.timespanBadge.textContent = `${labels.from} ${startLbl}`;
        } else if (hasEnd) {
          dom.timespanBadge.textContent = `${labels.until} ${endLbl}`;
        } else {
          dom.timespanBadge.textContent = labels.anyTime;
        }
      }
      if (dom.clearTimespanBtn) {
        dom.clearTimespanBtn.classList.toggle('d-none', !hasStart && !hasEnd);
      }
      if (dom.timespanPresets) {
        const chips = dom.timespanPresets.querySelectorAll('.search-era-chip');
        chips.forEach((chip) => {
          const matches = (chip.dataset.start || '') === state.startDate
            && (chip.dataset.end || '') === state.endDate;
          chip.classList.toggle('active', matches);
        });
      }
    }

    function syncPillsUi() {
      if (dom.caseStudyPills) {
        const buttons = dom.caseStudyPills.querySelectorAll('[data-cs-id]');
        buttons.forEach((btn) => {
          const id = btn.dataset.csId;
          const isActive = id === 'all' ? state.caseStudies.size === 0 : state.caseStudies.has(id);
          btn.classList.toggle('active', isActive);
        });
      }
      if (dom.entityClassPills) {
        const buttons = dom.entityClassPills.querySelectorAll('[data-class-key]');
        buttons.forEach((btn) => {
          const key = btn.dataset.classKey;
          const isActive = key === 'all' ? state.entityClasses.size === 0 : state.entityClasses.has(key);
          btn.classList.toggle('active', isActive);
        });
      }
    }

    function syncSortUi() {
      if (dom.sortBySelect) dom.sortBySelect.value = state.sortBy;
      if (dom.sortOrderBtn) dom.sortOrderBtn.dataset.order = state.sortOrder;
      if (dom.sortOrderIcon) {
        dom.sortOrderIcon.className = state.sortOrder === 'asc'
          ? 'bi bi-sort-down-alt'
          : 'bi bi-sort-up';
      }
      dom.sortableHeaders.forEach((th) => {
        const isCurrent = th.dataset.sort === state.sortBy;
        th.classList.toggle('active-sort', isCurrent);
      });
    }

    function updateActiveFilterCount() {
      let count = 0;
      if (state.query) count += 1;
      count += state.caseStudies.size;
      count += state.entityClasses.size;
      if (state.startDate || state.endDate) count += 1;
      if (dom.activeFilterBadge) {
        dom.activeFilterBadge.textContent = String(count);
        dom.activeFilterBadge.classList.toggle('d-none', count === 0);
      }
    }

    function buildQueryParams() {
      const params = new URLSearchParams();
      if (state.query) params.set('search', state.query);
      state.caseStudies.forEach((cs) => params.append('caseStudy', cs));
      state.entityClasses.forEach((cls) => params.append('entityClass', cls));
      if (state.startDate) params.set('startDate', state.startDate);
      if (state.endDate) params.set('endDate', state.endDate);
      if (state.sortBy !== 'name') params.set('sortBy', state.sortBy);
      if (state.sortOrder !== 'asc') params.set('sort', state.sortOrder);
      if (state.limit !== 50) params.set('limit', String(state.limit));
      if (state.page > 1) params.set('page', String(state.page));
      return params;
    }

    function syncBrowserUrl() {
      const params = buildQueryParams();
      const qs = params.toString();
      const newUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
      window.history.replaceState(null, '', newUrl);
    }

    function applyTableQuickFilter() {
      if (!dom.tbody || !dom.quickFilterInput) return;
      const needle = dom.quickFilterInput.value.trim().toLowerCase();
      const rows = dom.tbody.querySelectorAll('.search-result-row');
      rows.forEach((row) => {
        const hay = row.dataset.filterText || '';
        row.classList.toggle('d-none', Boolean(needle && !hay.includes(needle)));
      });
    }

    function renderTableRows(items) {
      if (!dom.tbody) return;
      dom.tbody.textContent = '';
      const fragment = document.createDocumentFragment();
      const ctx = {
        entityBaseUrl: root.dataset.entityBaseUrl || '/entity/',
        classMetaMap,
        caseStudyMap,
        labels,
      };
      items.forEach((item) => {
        fragment.appendChild(createResultRow(item, ctx));
      });
      dom.tbody.appendChild(fragment);
      applyTableQuickFilter();
    }

    function setViewState(mode) {
      dom.loadingState.classList.toggle('d-none', mode !== 'loading');
      dom.errorState.classList.toggle('d-none', mode !== 'error');
      dom.emptyState.classList.toggle('d-none', mode !== 'empty');
      dom.tableWrapper.classList.toggle('d-none', mode !== 'table');
    }

    async function runSearch() {
      state.requestToken += 1;
      const currentToken = state.requestToken;
      updateActiveFilterCount();
      syncBrowserUrl();
      setViewState('loading');

      const apiParams = buildQueryParams();
      apiParams.set('limit', String(state.limit));
      apiParams.set('page', String(state.page));
      apiParams.set('sortBy', state.sortBy);
      apiParams.set('sort', state.sortOrder);

      try {
        const response = await fetch(`${root.dataset.apiUrl}?${apiParams.toString()}`);
        if (currentToken !== state.requestToken) return;
        if (!response.ok) {
          setViewState('error');
          return;
        }
        const data = await response.json();
        if (currentToken !== state.requestToken) return;

        state.currentItems = Array.isArray(data.items) ? data.items : [];
        state.totalItems = Number(data.total_items) || 0;
        state.hasMore = Boolean(data.has_more);

        if (dom.totalBadge) {
          dom.totalBadge.textContent = state.totalItems.toLocaleString();
        }
        if (dom.pageIndicator) {
          dom.pageIndicator.textContent = String(state.page);
        }
        if (dom.prevPageBtn) {
          dom.prevPageBtn.disabled = state.page <= 1;
        }
        if (dom.nextPageBtn) {
          dom.nextPageBtn.disabled = !state.hasMore;
        }
        if (dom.paginationSummary) {
          const startIdx = state.currentItems.length ? (state.page - 1) * state.limit + 1 : 0;
          const endIdx = (state.page - 1) * state.limit + state.currentItems.length;
          dom.paginationSummary.textContent = state.currentItems.length
            ? `${startIdx}–${endIdx} / ${state.totalItems.toLocaleString()} ${labels.results}`
            : `0 ${labels.results}`;
        }

        if (state.currentItems.length === 0) {
          setViewState('empty');
        } else {
          renderTableRows(state.currentItems);
          setViewState('table');
        }
      } catch (err) {
        console.error('Search request failed:', err);
        if (currentToken === state.requestToken) {
          setViewState('error');
        }
      }
    }

    function scheduleSearch(delay = 280) {
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        state.page = 1;
        runSearch();
      }, delay);
    }

    function resetAllFilters() {
      state.query = '';
      state.caseStudies.clear();
      state.entityClasses.clear();
      state.startDate = '';
      state.endDate = '';
      state.sortBy = 'name';
      state.sortOrder = 'asc';
      state.page = 1;

      if (dom.queryInput) dom.queryInput.value = '';
      if (dom.startDateInput) dom.startDateInput.value = '';
      if (dom.endDateInput) dom.endDateInput.value = '';
      if (dom.sliderMin) dom.sliderMin.value = String(SLIDER_MIN);
      if (dom.sliderMax) dom.sliderMax.value = String(SLIDER_MAX);
      if (dom.quickFilterInput) dom.quickFilterInput.value = '';

      syncClearQueryBtn();
      syncPillsUi();
      syncSortUi();
      updateTimespanUi();
      runSearch();
    }

    // Bind events
    if (dom.form) {
      dom.form.addEventListener('submit', (e) => {
        e.preventDefault();
        state.query = dom.queryInput ? dom.queryInput.value.trim() : '';
        state.page = 1;
        runSearch();
      });
    }

    if (dom.queryInput) {
      dom.queryInput.addEventListener('input', () => {
        state.query = dom.queryInput.value.trim();
        syncClearQueryBtn();
        scheduleSearch(320);
      });
    }

    if (dom.clearQueryBtn) {
      dom.clearQueryBtn.addEventListener('click', () => {
        if (dom.queryInput) dom.queryInput.value = '';
        state.query = '';
        syncClearQueryBtn();
        state.page = 1;
        runSearch();
      });
    }

    if (dom.caseStudyPills) {
      dom.caseStudyPills.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-cs-id]');
        if (!btn) return;
        const csId = btn.dataset.csId;
        if (csId === 'all') {
          state.caseStudies.clear();
        } else if (state.caseStudies.has(csId)) {
          state.caseStudies.delete(csId);
        } else {
          state.caseStudies.add(csId);
        }
        syncPillsUi();
        state.page = 1;
        runSearch();
      });
    }

    if (dom.entityClassPills) {
      dom.entityClassPills.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-class-key]');
        if (!btn) return;
        const key = btn.dataset.classKey;
        if (key === 'all') {
          state.entityClasses.clear();
        } else if (state.entityClasses.has(key)) {
          state.entityClasses.delete(key);
        } else {
          state.entityClasses.add(key);
        }
        syncPillsUi();
        state.page = 1;
        runSearch();
      });
    }

    if (dom.timespanPresets) {
      dom.timespanPresets.addEventListener('click', (e) => {
        const chip = e.target.closest('.search-era-chip');
        if (!chip) return;
        state.startDate = chip.dataset.start || '';
        state.endDate = chip.dataset.end || '';
        if (dom.startDateInput) dom.startDateInput.value = state.startDate;
        if (dom.endDateInput) dom.endDateInput.value = state.endDate;
        if (dom.sliderMin) {
          dom.sliderMin.value = state.startDate || String(SLIDER_MIN);
        }
        if (dom.sliderMax) {
          dom.sliderMax.value = state.endDate || String(SLIDER_MAX);
        }
        updateTimespanUi();
        state.page = 1;
        runSearch();
      });
    }

    const handleSliderInput = () => {
      if (!dom.sliderMin || !dom.sliderMax) return;
      let minVal = parseInt(dom.sliderMin.value, 10);
      let maxVal = parseInt(dom.sliderMax.value, 10);
      if (minVal > maxVal) {
        [minVal, maxVal] = [maxVal, minVal];
      }
      state.startDate = String(minVal);
      state.endDate = String(maxVal);
      if (dom.startDateInput) dom.startDateInput.value = state.startDate;
      if (dom.endDateInput) dom.endDateInput.value = state.endDate;
      updateTimespanUi();
      scheduleSearch(250);
    };

    if (dom.sliderMin) dom.sliderMin.addEventListener('input', handleSliderInput);
    if (dom.sliderMax) dom.sliderMax.addEventListener('input', handleSliderInput);

    const handleDateNumberInput = () => {
      state.startDate = dom.startDateInput ? dom.startDateInput.value.trim() : '';
      state.endDate = dom.endDateInput ? dom.endDateInput.value.trim() : '';
      if (dom.sliderMin && state.startDate !== '') {
        const clampedMin = Math.max(SLIDER_MIN, Math.min(SLIDER_MAX, Number(state.startDate)));
        if (!Number.isNaN(clampedMin)) dom.sliderMin.value = String(clampedMin);
      }
      if (dom.sliderMax && state.endDate !== '') {
        const clampedMax = Math.max(SLIDER_MIN, Math.min(SLIDER_MAX, Number(state.endDate)));
        if (!Number.isNaN(clampedMax)) dom.sliderMax.value = String(clampedMax);
      }
      updateTimespanUi();
      scheduleSearch(350);
    };

    if (dom.startDateInput) dom.startDateInput.addEventListener('input', handleDateNumberInput);
    if (dom.endDateInput) dom.endDateInput.addEventListener('input', handleDateNumberInput);

    if (dom.clearTimespanBtn) {
      dom.clearTimespanBtn.addEventListener('click', () => {
        state.startDate = '';
        state.endDate = '';
        if (dom.startDateInput) dom.startDateInput.value = '';
        if (dom.endDateInput) dom.endDateInput.value = '';
        if (dom.sliderMin) dom.sliderMin.value = String(SLIDER_MIN);
        if (dom.sliderMax) dom.sliderMax.value = String(SLIDER_MAX);
        updateTimespanUi();
        state.page = 1;
        runSearch();
      });
    }

    if (dom.sortBySelect) {
      dom.sortBySelect.addEventListener('change', () => {
        state.sortBy = dom.sortBySelect.value;
        syncSortUi();
        state.page = 1;
        runSearch();
      });
    }

    if (dom.sortOrderBtn) {
      dom.sortOrderBtn.addEventListener('click', () => {
        state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
        syncSortUi();
        state.page = 1;
        runSearch();
      });
    }

    dom.sortableHeaders.forEach((th) => {
      th.addEventListener('click', () => {
        const field = th.dataset.sort;
        if (!field) return;
        if (state.sortBy === field) {
          state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
          state.sortBy = field;
          state.sortOrder = 'asc';
        }
        syncSortUi();
        state.page = 1;
        runSearch();
      });
    });

    if (dom.limitSelect) {
      dom.limitSelect.value = String(state.limit);
      dom.limitSelect.addEventListener('change', () => {
        state.limit = Number(dom.limitSelect.value) || 50;
        state.page = 1;
        runSearch();
      });
    }

    if (dom.quickFilterInput) {
      dom.quickFilterInput.addEventListener('input', applyTableQuickFilter);
    }

    if (dom.prevPageBtn) {
      dom.prevPageBtn.addEventListener('click', () => {
        if (state.page > 1) {
          state.page -= 1;
          runSearch();
        }
      });
    }

    if (dom.nextPageBtn) {
      dom.nextPageBtn.addEventListener('click', () => {
        if (state.hasMore) {
          state.page += 1;
          runSearch();
        }
      });
    }

    if (dom.exportCsvBtn) {
      dom.exportCsvBtn.addEventListener('click', () => {
        exportItemsToCsv(state.currentItems, {
          classMetaMap,
          caseStudyMap,
          labels,
        });
      });
    }

    if (dom.resetAllBtn) dom.resetAllBtn.addEventListener('click', resetAllFilters);
    if (dom.emptyResetBtn) dom.emptyResetBtn.addEventListener('click', resetAllFilters);
    if (dom.retryBtn) dom.retryBtn.addEventListener('click', runSearch);

    // Initialize UI state from URL/server config and run initial search
    if (dom.startDateInput && state.startDate) dom.startDateInput.value = state.startDate;
    if (dom.endDateInput && state.endDate) dom.endDateInput.value = state.endDate;
    syncClearQueryBtn();
    syncPillsUi();
    syncSortUi();
    updateTimespanUi();
    runSearch();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupSearchApp);
  } else {
    setupSearchApp();
  }
})();
