// Wrap gisData point into a FeatureCollection as MapLibre expects
const featureCollection = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      geometry: {
        type: gisData.type,
        coordinates: gisData.coordinates
      },
      properties: {
        title: gisData.title,
        description: gisData.description,
        shapeType: gisData.shapeType,
        locationId: gisData.locationId
      }
    }
  ]
};

// Initialize MapLibre map
const overview_map = new maplibregl.Map({
  container: 'muuri-map',
  style: 'https://api.maptiler.com/maps/basic/style.json?key=E7Jrgaazm79UlTuEI5f5',
  center: featureCollection.features[0].geometry.coordinates,
  zoom: 13,
  interactive: false
});

// Add zoom scale
overview_map.addControl(new maplibregl.ScaleControl(), 'bottom-left');

// Add GeoJSON data as source + layer
overview_map.on('load', () => {
  overview_map.addSource('point-data', {
    type: 'geojson',
    data: featureCollection
  });

  overview_map.addLayer({
    id: 'point-layer',
    type: 'circle',
    source: 'point-data',
    paint: {
      'circle-radius': 6,
      'circle-color': '#007cbf'
    }
  });

  // Optional: popup on click
  overview_map.on('click', 'point-layer', (e) => {
    const props = e.features[0].properties;
    const coords = e.features[0].geometry.coordinates;
    new maplibregl.Popup()
      .setLngLat(coords)
      .setHTML(`<b>${entityName}</b><p><b>${props.title}</b> ${props.description}</p>`)
      .addTo(overview_map);
  });

  // Change cursor
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
