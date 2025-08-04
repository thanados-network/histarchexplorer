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
    //console.log(feature.geometry.coordinates);
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
  overview_map.fitBounds(bounds, { padding: 40, maxZoom: 12, duration: 0 });
} else if (featureCollection.features.length === 1) {
  // Single point: center and zoom level 12
  overview_map.setCenter(bounds.getCenter());
  overview_map.setZoom(12);
}

  // Change cursor on hover
  overview_map.on('mouseenter', 'point-layer', () => {
    overview_map.getCanvas().style.cursor = 'pointer';
  });
  overview_map.on('mouseleave', 'point-layer', () => {
    overview_map.getCanvas().style.cursor = '';
  });
});


const mapContainer = document.querySelector('.map-wrapper');
const muuriMap = document.getElementById('muuri-map');

//link map expand to map-tab
window.activateTab = function(tabName, skipPushState = false) {
    const tabElement = document.querySelector(`#tab-${tabName}`);
    if (tabElement) {
        new bootstrap.Tab(tabElement).show();
        if (!skipPushState) {
            const newUrl = `/entity/${entityId}/${tabName}`;
            if (window.location.pathname !== newUrl) {
                history.pushState({ tab: tabName }, '', newUrl);
            }
        }
    }
};

const expandButton = document.getElementById('expand-button');
const tabName = 'map';
expandButton.addEventListener('click', event => {
    window.activateTab('map');
});
