const gisArray = Array.isArray(gisData) ? gisData : [gisData];

// Wrap gisArray into a FeatureCollection
const featureCollection = {
  type: "FeatureCollection",
  features: gisArray.map((item) => ({
    type: "Feature",
    geometry: {
      type: item.type,
      coordinates: item.coordinates
    },
    properties: {
      title: item.title,
      description: item.description,
      shapeType: item.shapeType,
      locationId: item.locationId
    }
  }))
};


// Initialize MapLibre map
const overview_map = new maplibregl.Map({
  container: 'muuri-map',
  style: 'https://api.maptiler.com/maps/bright/style.json?key=E7Jrgaazm79UlTuEI5f5',
  center: [0, 0],
  zoom: 10,
  interactive: true
});

// Add zoom scale
overview_map.addControl(new maplibregl.ScaleControl(), 'bottom-left');

// Add GeoJSON data as source + layer
overview_map.on('load', () => {
  overview_map.addSource('point-data', {
    type: 'geojson',
    data: featureCollection
  });

  // Add a layer for click and hover interactions
  overview_map.addLayer({
    id: 'point-layer',
    type: 'circle',
    source: 'point-data',
    paint: {
      'circle-radius': 6,
      'circle-color': '#007cbf'
    }
  });

  // Add one marker per point
  featureCollection.features.forEach((feature) => {
    console.log(feature.geometry.coordinates);
    new maplibregl.Marker()
      .setLngLat(feature.geometry.coordinates)
      .setPopup(
        new maplibregl.Popup().setHTML(
          `<b>${entityName}</b><p><b>${feature.properties.title}</b> ${feature.properties.description}</p>`
        )
      )
      .addTo(overview_map);
  });

  // Fit map to all points, or center if only one point
const bounds = new maplibregl.LngLatBounds();
featureCollection.features.forEach((f) => {
  bounds.extend(f.geometry.coordinates);
});

if (featureCollection.features.length > 1) {
  overview_map.fitBounds(bounds, { padding: 40, maxZoom: 12 });
} else if (featureCollection.features.length === 1) {
  // Single point: center and zoom level 12
  overview_map.setCenter(bounds.getCenter());
  overview_map.setZoom(12);
} else {
  // No points: fallback center/zoom
  overview_map.setCenter([0, 0]);
  overview_map.setZoom(2);
}

  // Change cursor on hover
  overview_map.on('mouseenter', 'point-layer', () => {
    overview_map.getCanvas().style.cursor = 'pointer';
  });
  overview_map.on('mouseleave', 'point-layer', () => {
    overview_map.getCanvas().style.cursor = '';
  });
});

// Expand/Shrink logic
const expandButton = document.getElementById('expand-button');
const mapContainer = document.querySelector('.map-wrapper');
const muuriMap = document.getElementById('muuri-map');

expandButton.addEventListener('click', () => {
  setTimeout(() => {
    muuriMap.classList.toggle('expanded-map');
    mapContainer.classList.toggle('expanded-map');

    const locationTile = document.querySelector('.map-wrapper').parentElement;
    if (locationTile) {
      locationTile.classList.toggle('item');
    }

    document.querySelectorAll('.item, .item-content').forEach(item => {
      if (!item.contains(muuriMap)) {
        item.classList.toggle('hidden');
      }
    });

    if (muuriMap.classList.contains('expanded-map')) {
      expandButton.innerHTML = '<i class="bi bi-fullscreen-exit"></i>';
      overview_map.dragPan.enable();
      overview_map.scrollZoom.enable();
      overview_map.doubleClickZoom.enable();
      overview_map.touchZoomRotate.enable();
    } else {
      expandButton.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';
      overview_map.dragPan.disable();
      overview_map.scrollZoom.disable();
      overview_map.doubleClickZoom.disable();
      overview_map.touchZoomRotate.disable();
    }

    overview_map.resize();
    if (window.grid) grid.refreshItems().layout();
  }, 300);
});
