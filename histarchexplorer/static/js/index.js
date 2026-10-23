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
    const finalStyle = styleUrl || 'https://api.maptiler.com/maps/bright/style.json';
    landingMap = new maplibregl.Map({
      container: mapElementId,
      style: finalStyle,
      center: [14.55, 47.52],
      zoom: 6,
      scrollZoom: false,
      attributionControl: true
    });

    landingMap.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

    landingMap.on('load', async () => {
      try {
        const response = await fetch('/api/landing/sites-geojson');
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

          while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
          }

          const popupHtml = `
            <div class="site-map-popup p-2">
              <h6 class="fw-bold mb-1 text-dark">${name}</h6>
              ${dating ? `<p class="small text-muted mb-2"><i class="bi bi-clock me-1"></i>${dating}</p>` : ''}
              <a href="/entity/${id}" class="btn btn-sm btn-outline-success w-100">
                <i class="bi bi-arrow-right-circle me-1"></i>Details ansehen
              </a>
            </div>
          `;

          new maplibregl.Popup({ offset: 12 })
            .setLngLat(coordinates)
            .setHTML(popupHtml)
            .addTo(landingMap);
        });

        // Mouse hover cursor
        landingMap.on('mouseenter', 'clusters', () => { landingMap.getCanvas().style.cursor = 'pointer'; });
        landingMap.on('mouseleave', 'clusters', () => { landingMap.getCanvas().style.cursor = ''; });
        landingMap.on('mouseenter', 'unclustered-point', () => { landingMap.getCanvas().style.cursor = 'pointer'; });
        landingMap.on('mouseleave', 'unclustered-point', () => { landingMap.getCanvas().style.cursor = ''; });

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
      copyBtn.innerHTML = '<i class="bi bi-check2 me-1"></i>Kopiert!';
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

document.addEventListener('DOMContentLoaded', () => {
  const mapStyleUrl = window.landingMapStyle || '';
  setupLazyMap('landing-cluster-map', mapStyleUrl);
  setupCitationCopy();

  if (window.landingStats && typeof window.initLandingCharts === 'function') {
    window.initLandingCharts(window.landingStats);
  }
});
