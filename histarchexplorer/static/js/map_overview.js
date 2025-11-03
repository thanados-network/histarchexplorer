// Defensive, self-contained map renderer for the Overview tile.
// Uses window.overviewMap + window.entityName + #muuri-map container.
// Mirrors your previous approach (sources, layers, markers, fitBounds). :contentReference[oaicite:9]{index=9}

(function () {
  const mapData = window.overviewMap;
  const name = window.entityName || '';

  const container = document.getElementById('muuri-map');
  if (!container || !mapData) return;

  // Basic map
  const map = new maplibregl.Map({
    container: container,
    style: 'https://api.maptiler.com/maps/bright/style.json?key=E7Jrgaazm79UlTuEI5f5',
    center: [0, 0],
    zoom: 10,
    interactive: true
  });

  map.addControl(new maplibregl.ScaleControl(), 'bottom-left');

  // helper to extend bounds
  function extendBounds(bounds, geometry) {
    const { type, coordinates } = geometry;
    switch (type) {
      case 'Point':
        bounds.extend(coordinates);
        break;
      case 'LineString':
        coordinates.forEach(coord => bounds.extend(coord));
        break;
      case 'Polygon':
        coordinates.flat().forEach(coord => bounds.extend(coord));
        break;
      case 'MultiPolygon':
        coordinates.flat(2).forEach(coord => bounds.extend(coord));
        break;
    }
  }

  map.on('load', () => {
    map.addSource('overview-data', {
      type: 'geojson',
      data: mapData
    });

    map.addLayer({
      id: 'overview-polygon',
      type: 'fill',
      source: 'overview-data',
      paint: { 'fill-color': '#92BCEA', 'fill-opacity': 0.4 },
      filter: ['==', '$type', 'Polygon']
    });

    map.addLayer({
      id: 'overview-outline',
      type: 'line',
      source: 'overview-data',
      paint: { 'line-color': '#355070', 'line-width': 2 },
      filter: ['==', '$type', 'Polygon']
    });

    map.addLayer({
      id: 'overview-linestring',
      type: 'line',
      source: 'overview-data',
      paint: { 'line-color': '#4078C0', 'line-width': 2 },
      filter: ['==', '$type', 'LineString']
    });

    map.addLayer({
      id: 'overview-points',
      type: 'circle',
      source: 'overview-data',
      paint: { 'circle-radius': 6, 'circle-color': '#007cbf' },
      filter: ['==', '$type', 'Point']
    });

    // Add markers & popups for point features (optional sugar). :contentReference[oaicite:10]{index=10}
    const features = mapData.type === 'FeatureCollection' ? mapData.features : [mapData];
    features.forEach((f) => {
      if (f?.geometry?.type === 'Point') {
        new maplibregl.Marker()
          .setLngLat(f.geometry.coordinates)
          .setPopup(
            new maplibregl.Popup().setHTML(
              `<b>${name}</b><p><b>${f.properties?.title || ''}</b> ${f.properties?.description || ''}</p>`
            )
          )
          .addTo(map);
      }
    });

    // Fit to data
    const bounds = new maplibregl.LngLatBounds();
    features.forEach((f) => { if (f?.geometry) extendBounds(bounds, f.geometry); });

    if (features.length > 1) {
      map.fitBounds(bounds, { padding: 40, maxZoom: 12, duration: 0 });
    } else if (features.length === 1) {
      map.setCenter(bounds.getCenter());
      map.setZoom(12);
    }

    // Hover cursor
    ['overview-polygon', 'overview-outline', 'overview-linestring', 'overview-points'].forEach(layer => {
      map.on('mouseenter', layer, () => map.getCanvas().style.cursor = 'pointer');
      map.on('mouseleave', layer, () => map.getCanvas().style.cursor = '');
    });
  });

  // Hook the expand button to activate the map tab (same API you used before). :contentReference[oaicite:11]{index=11}
  const expandButton = document.getElementById('expand-button');
  if (expandButton) {
    expandButton.addEventListener('click', () => window.activateTab && window.activateTab('map'));
  }
})();
