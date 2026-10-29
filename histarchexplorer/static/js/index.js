/**
 * Histarchexplorer - Modern Landing Page Controller
 * Handles lazy-loaded MapLibre clustering, citation copying, and hero interactions.
 */

let landingMap = null;
let mapInitialized = false;

/**
 * Configure and initialize the clustered sites map.
 */
async function initializeClusteredMap(mapElementId, styleUrl) {
  if (mapInitialized) return;
  mapInitialized = true;

  const mapContainer = document.getElementById(mapElementId);
  if (!mapContainer) return;

  const loader = document.getElementById('map-loading-indicator');
  if (loader) loader.classList.remove('d-none');

  try {
    const defaultStyle =
      'https://api.maptiler.com/maps/bright/style.json?key=E7Jrgaazm79UlTuEI5f5';
    const finalStyle = (styleUrl || '').trim() || defaultStyle;
    landingMap = new maplibregl.Map({
      container: mapElementId,
      style: finalStyle,
      center: [14.55, 47.52],
      zoom: 6,
      scrollZoom: false,
      attributionControl: true
    });

    landingMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

    landingMap.on('error', () => {
      if (loader) loader.classList.add('d-none');
    });

    landingMap.on('load', async () => {
      try {
        const geojsonUrl = mapContainer.getAttribute('data-geojson-url') || '/api/landing/sites-geojson';
        const response = await fetch(geojsonUrl);
        if (!response.ok) {
          throw new Error(`Failed to load sites: ${response.statusText}`);
        }
        const geojson = await response.json();

        landingMap.addSource('sites-cluster', {
          type: 'geojson',
          data: geojson,
          cluster: true,
          clusterMaxZoom: 14,
          clusterRadius: 50
        });

        // 1. Cluster circles
        landingMap.addLayer({
          id: 'clusters',
          type: 'circle',
          source: 'sites-cluster',
          filter: ['has', 'point_count'],
          paint: {
            'circle-color': [
              'step',
              ['get', 'point_count'],
              '#23cba7',
              50,
              '#1db192',
              200,
              '#14866f'
            ],
            'circle-radius': [
              'step',
              ['get', 'point_count'],
              18,
              50,
              24,
              200,
              30
            ],
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff'
          }
        });

        // 2. Cluster count numbers
        landingMap.addLayer({
          id: 'cluster-count',
          type: 'symbol',
          source: 'sites-cluster',
          filter: ['has', 'point_count'],
          layout: {
            'text-field': '{point_count_abbreviated}',
            'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
            'text-size': 12
          },
          paint: {
            'text-color': '#ffffff'
          }
        });

        // 3. Unclustered individual site points
        landingMap.addLayer({
          id: 'unclustered-point',
          type: 'circle',
          source: 'sites-cluster',
          filter: ['!', ['has', 'point_count']],
          paint: {
            'circle-color': '#23cba7',
            'circle-radius': 7,
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff'
          }
        });

        // Cluster click -> zoom in
        landingMap.on('click', 'clusters', async e => {
          const features = landingMap.queryRenderedFeatures(e.point, { layers: ['clusters'] });
          const clusterId = features[0].properties.cluster_id;
          const clusterSource = landingMap.getSource('sites-cluster');

          clusterSource.getClusterExpansionZoom(clusterId, (err, zoom) => {
            if (err) return;
            landingMap.easeTo({
              center: features[0].geometry.coordinates,
              zoom: zoom + 0.5
            });
          });
        });

        // Unclustered point click -> show popup
        landingMap.on('click', 'unclustered-point', e => {
          const coordinates = e.features[0].geometry.coordinates.slice();
          const { id, name, dating } = e.features[0].properties;
          const detailsLabel = mapContainer.getAttribute('data-label-view-details') || 'View details';

          while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
          }

          const popupHtml = `
            <div class="site-map-popup p-2">
              <h6 class="fw-bold mb-1 text-dark">${name}</h6>
              ${dating ? `<p class="small text-muted mb-2"><i class="bi bi-clock me-1"></i>${dating}</p>` : ''}
              <a href="/entity/${id}" class="btn btn-sm btn-outline-success w-100">
                <i class="bi bi-arrow-right-circle me-1"></i>${detailsLabel}
              </a>
            </div>
          `;

          new maplibregl.Popup({ offset: 12 })
            .setLngLat(coordinates)
            .setHTML(popupHtml)
            .addTo(landingMap);
        });

    // Mouse hover cursor
        landingMap.on('mouseenter', 'clusters', () => {
          landingMap.getCanvas().classList.add('cursor-pointer');
        });
        landingMap.on('mouseleave', 'clusters', () => {
          landingMap.getCanvas().classList.remove('cursor-pointer');
        });
        landingMap.on('mouseenter', 'unclustered-point', () => {
          landingMap.getCanvas().classList.add('cursor-pointer');
        });
        landingMap.on('mouseleave', 'unclustered-point', () => {
          landingMap.getCanvas().classList.remove('cursor-pointer');
        });

        // Adjust bounds if features exist
        if (geojson.features && geojson.features.length > 0) {
          const bounds = new maplibregl.LngLatBounds();
          geojson.features.forEach(f => bounds.extend(f.geometry.coordinates));
          landingMap.fitBounds(bounds, { padding: 40, maxZoom: 10 });
        }
      } catch (err) {
        console.error('Error fetching landing sites geojson:', err);
      } finally {
        if (loader) loader.classList.add('d-none');
      }
    });
  } catch (err) {
    console.error('MapLibre initialization error:', err);
    if (loader) loader.classList.add('d-none');
  }
}

/**
 * Lazy loading via IntersectionObserver
 */
function setupLazyMap(mapElementId, styleUrl) {
  const mapElement = document.getElementById(mapElementId);
  if (!mapElement) return;

  const activateBtn = document.getElementById('btnActivateMap');
  if (activateBtn) {
    activateBtn.addEventListener('click', () => {
      activateBtn.classList.add('d-none');
      initializeClusteredMap(mapElementId, styleUrl);
    });
  }

  if ('IntersectionObserver' in window) {
    const scrollContainer = document.querySelector('.page-wrapper');
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          initializeClusteredMap(mapElementId, styleUrl);
          obs.disconnect();
        }
      });
    }, {
      root: scrollContainer || null,
      rootMargin: '200px'
    });

    observer.observe(mapElement);
  } else {
    initializeClusteredMap(mapElementId, styleUrl);
  }
}

/**
 * Scientific Citation Copy Helper
 */
function setupCitationCopy() {
  const copyBtn = document.getElementById('btnCopyCitation');
  const citationText = document.getElementById('citationContent');

  if (!copyBtn || !citationText) return;

  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(citationText.textContent.trim());
      const originalText = copyBtn.innerHTML;
      const copiedLabel = copyBtn.getAttribute('data-label-copied') || 'Copied!';
      copyBtn.innerHTML = `<i class="bi bi-check2 me-1"></i>${copiedLabel}`;
      copyBtn.classList.remove('btn-outline-primary');
      copyBtn.classList.add('btn-success');
      setTimeout(() => {
        copyBtn.innerHTML = originalText;
        copyBtn.classList.remove('btn-success');
        copyBtn.classList.add('btn-outline-primary');
      }, 2500);
    } catch (err) {
      console.warn('Clipboard write failed:', err);
    }
  });

  const tabApa = document.getElementById('tabCitationApa');
  const tabBibtex = document.getElementById('tabCitationBibtex');
  if (tabApa && tabBibtex && citationText) {
    tabApa.addEventListener('click', () => {
      tabApa.classList.add('active');
      tabBibtex.classList.remove('active');
      citationText.textContent = citationText.getAttribute('data-apa') || '';
    });
    tabBibtex.addEventListener('click', () => {
      tabBibtex.classList.add('active');
      tabApa.classList.remove('active');
      citationText.textContent = citationText.getAttribute('data-bibtex') || '';
    });
  }
}

/**
 * Clean OpenAtlas description strings for compact preview display.
 */
function cleanSearchDescription(rawDesc) {
  if (!rawDesc || typeof rawDesc !== 'string') return '';
  const withoutMarkers = rawDesc
    .replace(/##[a-z]{2}_##/gi, '')
    .replace(/##_[a-z]{2}##/gi, '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (withoutMarkers.length <= 120) return withoutMarkers;
  return `${withoutMarkers.slice(0, 120)}…`;
}

/**
 * Render status message (loading / empty / error) inside the search dropdown.
 */
function renderSearchStatus(dropdown, message, isSpinner = false) {
  dropdown.textContent = '';
  const wrapper = document.createElement('div');
  wrapper.className = 'p-3 text-muted small d-flex align-items-center gap-2';
  if (isSpinner) {
    const spinner = document.createElement('span');
    spinner.className = 'spinner-border spinner-border-sm text-primary';
    spinner.setAttribute('role', 'status');
    wrapper.appendChild(spinner);
  }
  const textSpan = document.createElement('span');
  textSpan.textContent = message;
  wrapper.appendChild(textSpan);
  dropdown.appendChild(wrapper);
  dropdown.classList.remove('d-none');
}

/**
 * Render search result items into the hero dropdown using DocumentFragment.
 */
function renderSearchResults(dropdown, results) {
  dropdown.textContent = '';
  const fragment = document.createDocumentFragment();

  results.slice(0, 20).forEach(item => {
    const rawId = String(item.id || '');
    const entityId = rawId.split('/').pop();
    if (!entityId) return;

    const link = document.createElement('a');
    link.href = `/entity/${encodeURIComponent(entityId)}`;
    link.className = 'hero-search-item d-block text-decoration-none p-3 border-bottom';
    link.setAttribute('role', 'option');

    const topRow = document.createElement('div');
    topRow.className = 'd-flex justify-content-between align-items-center gap-2';

    const titleSpan = document.createElement('span');
    titleSpan.className = 'fw-semibold text-dark text-truncate';
    titleSpan.textContent = item.name || `#${entityId}`;
    topRow.appendChild(titleSpan);

    if (item.system_class) {
      const badge = document.createElement('span');
      badge.className = 'badge bg-secondary-subtle text-secondary rounded-pill small';
      badge.textContent = String(item.system_class).replace(/_/g, ' ');
      topRow.appendChild(badge);
    }

    link.appendChild(topRow);

    const cleanDesc = cleanSearchDescription(item.description);
    if (cleanDesc) {
      const descP = document.createElement('p');
      descP.className = 'small text-muted mb-0 mt-1 text-truncate';
      descP.textContent = cleanDesc;
      link.appendChild(descP);
    }

    fragment.appendChild(link);
  });

  dropdown.appendChild(fragment);
  dropdown.classList.remove('d-none');
}

/**
 * Initialize Hero live search autocomplete dropdown against /search_live.
 */
function setupHeroSearch() {
  const searchForm = document.getElementById('heroSearchForm');
  const searchInput = document.getElementById('heroSearchInput');
  const dropdown = document.getElementById('heroSearchDropdown');
  if (!searchForm || !searchInput || !dropdown) return;

  const loadingLabel = searchInput.getAttribute('data-label-loading') || 'Searching...';
  const noResultsLabel = searchInput.getAttribute('data-label-no-results') || 'No results found';

  let debounceTimer = null;
  let activeIndex = -1;
  let requestCounter = 0;

  const updateActiveItem = items => {
    items.forEach((el, idx) => {
      el.classList.toggle('active', idx === activeIndex);
    });
    if (activeIndex >= 0 && items[activeIndex]) {
      items[activeIndex].scrollIntoView({ block: 'nearest' });
    }
  };

  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim();
    activeIndex = -1;
    if (debounceTimer) clearTimeout(debounceTimer);

    if (query.length < 2) {
      dropdown.classList.add('d-none');
      dropdown.textContent = '';
      return;
    }

    debounceTimer = setTimeout(async () => {
      const currentReq = ++requestCounter;
      renderSearchStatus(dropdown, loadingLabel, true);

      try {
        const url = `/search_live?q=${encodeURIComponent(query)}&system_class=all`;
        const response = await fetch(url);
        if (currentReq !== requestCounter) return;
        if (!response.ok) {
          throw new Error(`Search failed: ${response.status}`);
        }
        const results = await response.json();
        if (currentReq !== requestCounter) return;

        if (!Array.isArray(results) || results.length === 0) {
          renderSearchStatus(dropdown, noResultsLabel, false);
        } else {
          renderSearchResults(dropdown, results);
        }
      } catch (err) {
        console.error('Hero live search error:', err);
        if (currentReq === requestCounter) {
          renderSearchStatus(dropdown, noResultsLabel, false);
        }
      }
    }, 250);
  });

  searchInput.addEventListener('keydown', e => {
    if (dropdown.classList.contains('d-none')) return;
    const items = Array.from(dropdown.querySelectorAll('.hero-search-item'));
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = (activeIndex + 1) % items.length;
      updateActiveItem(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + items.length) % items.length;
      updateActiveItem(items);
    } else if (e.key === 'Enter' && activeIndex >= 0 && items[activeIndex]) {
      e.preventDefault();
      window.location.href = items[activeIndex].href;
    } else if (e.key === 'Escape') {
      dropdown.classList.add('d-none');
      activeIndex = -1;
    }
  });

  document.addEventListener('click', e => {
    if (!searchForm.contains(e.target)) {
      dropdown.classList.add('d-none');
      activeIndex = -1;
    }
  });
}

function initLandingPage() {
  const mapStyleUrl = (window.landingMapStyle || '').trim();
  setupLazyMap('landing-cluster-map', mapStyleUrl);
  setupCitationCopy();
  setupHeroSearch();

  if (window.landingStats && typeof window.initLandingCharts === 'function') {
    window.initLandingCharts(window.landingStats);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLandingPage);
} else {
  initLandingPage();
}
