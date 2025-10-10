const mapOverview = overviewMap

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

// Extend bounds helper
function extendBounds(bounds, geometry) {
  const { type, coordinates } = geometry;
  switch (type) {
    case "Point":
      bounds.extend(coordinates);
      break;
    case "LineString":
      coordinates.forEach(coord => bounds.extend(coord));
      break;
    case "Polygon":
      coordinates.flat().forEach(coord => bounds.extend(coord));
      break;
    case "MultiPolygon":
      coordinates.flat(2).forEach(coord => bounds.extend(coord));
      break;
  }
}


// Add GeoJSON data as source + layers
overview_map.on("load", () => {
  overview_map.addSource("overview-data", {
    type: "geojson",
    data: entity.geometry_json  // ✅ directly use provided GeoJSON
  });
  // Style layers for each geometry type
  overview_map.addLayer({
    id: "overview-polygon",
    type: "fill",
    source: "overview-data",
    paint: { "fill-color": "#92BCEA", "fill-opacity": 0.4 },
    filter: ["==", "$type", "Polygon"]
  });

  overview_map.addLayer({
    id: "overview-outline",
    type: "line",
    source: "overview-data",
    paint: { "line-color": "#355070", "line-width": 2 },
    filter: ["==", "$type", "Polygon"]
  });

  overview_map.addLayer({
    id: "overview-linestring",
    type: "line",
    source: "overview-data",
    paint: { "line-color": "#4078C0", "line-width": 2 },
    filter: ["==", "$type", "LineString"]
  });

  overview_map.addLayer({
    id: "overview-points",
    type: "circle",
    source: "overview-data",
    paint: { "circle-radius": 6, "circle-color": "#007cbf" },
    filter: ["==", "$type", "Point"]
  });

  // Add markers & popups for points
  if (mapOverview.type === "FeatureCollection") {
    mapOverview.features.forEach((feature) => {
      if (feature.geometry.type === "Point") {
        new maplibregl.Marker()
          .setLngLat(feature.geometry.coordinates)
          .setPopup(
            new maplibregl.Popup().setHTML(
              `<b>${entityName}</b><p><b>${feature.properties.title}</b> ${feature.properties.description}</p>`
            )
          )
          .addTo(overview_map);
      }
    });
  } else if (mapOverview.type === "Feature" && mapOverview.geometry.type === "Point") {
    new maplibregl.Marker()
      .setLngLat(mapOverview.geometry.coordinates)
      .setPopup(
        new maplibregl.Popup().setHTML(
          `<b>${entityName}</b><p><b>${mapOverview.properties.title}</b> ${mapOverview.properties.description}</p>`
        )
      )
      .addTo(overview_map);
  }

  // Fit map to all features
  const bounds = new maplibregl.LngLatBounds();
  const features = mapOverview.type === "FeatureCollection"
    ? mapOverview.features
    : [mapOverview];

  features.forEach((f) => extendBounds(bounds, f.geometry));

  if (features.length > 1) {
    overview_map.fitBounds(bounds, { padding: 40, maxZoom: 12, duration: 0 });
  } else if (features.length === 1) {
    overview_map.setCenter(bounds.getCenter());
    overview_map.setZoom(12);
  }

  // Cursor change for interactivity
  ["overview-polygon", "overview-outline", "overview-linestring", "overview-points"].forEach(layer => {
    overview_map.on("mouseenter", layer, () => overview_map.getCanvas().style.cursor = "pointer");
    overview_map.on("mouseleave", layer, () => overview_map.getCanvas().style.cursor = "");
  });
});

// link map expand to map-tab
window.activateTab = function(tabName, skipPushState = false) {
  const tabElement = document.querySelector(`#tab-${tabName}`);
  if (tabElement) {
    new bootstrap.Tab(tabElement).show();
    if (!skipPushState) {
      const newUrl = `/entity/${entityId}/${tabName}`;
      if (window.location.pathname !== newUrl) {
        history.pushState({ tab: tabName }, "", newUrl);
      }
    }
  }
};

const expandButton = document.getElementById("expand-button");
expandButton.addEventListener("click", () => {
  window.activateTab("map");
});
