// ============================================================
//  MAP_OVERVIEW.JS — self-contained mini map for overview tile
// ============================================================

(function () {
  // Wait for data and container to be ready
  function init() {
    const mapData = entityData.overviewMap;
    const name = entityData.entity.title || "Entity";
    const container = document.getElementById("muuri-map");

    if (!mapData || !container) {
      console.warn("⏳ Waiting for overviewMap or map container...");
      return setTimeout(init, 300);
    }

    // Normalize GeoJSON data
    const features = mapData.type === "FeatureCollection"
      ? mapData.features
      : mapData.features || [mapData];

    if (!Array.isArray(features) || !features.length) {
      console.warn("⚠️ No features in overviewMap.");
      return;
    }

    // Basic map setup
    const map = new maplibregl.Map({
      container,
      style: "https://api.maptiler.com/maps/topo-v2/style.json?key=E7Jrgaazm79UlTuEI5f5",
      center: [0, 0],
      zoom: 5,
      attributionControl: false,
      maxZoom: 22,
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");
    map.addControl(new maplibregl.ScaleControl(), "bottom-left");

    // Extend bounds helper
    const bounds = new maplibregl.LngLatBounds();
    const extendBounds = (geometry) => {
      if (!geometry?.type || !geometry?.coordinates) return;
      const coords = geometry.coordinates;

      switch (geometry.type) {
        case "Point":
          bounds.extend(coords);
          break;
        case "LineString":
          coords.forEach(c => bounds.extend(c));
          break;
        case "Polygon":
          coords.flat().forEach(c => bounds.extend(c));
          break;
        case "MultiPolygon":
          coords.flat(2).forEach(c => bounds.extend(c));
          break;
      }
    };

    // Load map
    map.on("load", () => {
      // Add GeoJSON source
      map.addSource("overview-geojson", {
        type: "geojson",
        data: { type: "FeatureCollection", features }
      });

      // Layers (aligned with your color palette)
      const layerDefs = [
        { id: "overview-polygons", type: "fill", color: "#92BCEA", opacity: 0.35, filter: ["==", "$type", "Polygon"] },
        { id: "overview-lines", type: "line", color: "#4078C0", width: 2, filter: ["==", "$type", "LineString"] },
        { id: "overview-points", type: "circle", color: "#007cbf", radius: 6, filter: ["==", "$type", "Point"] },
        { id: "overview-outline", type: "line", color: "#355070", width: 2, filter: ["==", "$type", "Polygon"] },
      ];

      for (const l of layerDefs) {
        const paint =
          l.type === "fill"
            ? { "fill-color": l.color, "fill-opacity": l.opacity }
            : l.type === "circle"
              ? { "circle-color": l.color, "circle-radius": l.radius }
              : { "line-color": l.color, "line-width": l.width };
        map.addLayer({ id: l.id, type: l.type, source: "overview-geojson", paint, filter: l.filter });
      }

      // Fit bounds
      features.forEach(f => extendBounds(f.geometry));
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 50, duration: 0 });
      }

      // Optional markers for points
      features
        .filter(f => f.geometry?.type === "Point")
        .forEach(f => {
          const [lng, lat] = f.geometry.coordinates;
          new maplibregl.Marker({ color: "#007cbf" })
            .setLngLat([lng, lat])
            .setPopup(new maplibregl.Popup().setHTML(
              `<b>${f.properties?.title || name}</b><br>${f.properties?.description || ""}`
            ))
            .addTo(map);
        });

      // Cursor hover
      ["overview-polygons", "overview-lines", "overview-points"].forEach(layer => {
        map.on("mouseenter", layer, () => map.getCanvas().style.cursor = "pointer");
        map.on("mouseleave", layer, () => map.getCanvas().style.cursor = "");
      });
    });

    // Expand button
    const expandButton = document.getElementById("expand-button");
    if (expandButton) {
      expandButton.addEventListener("click", () => {
        if (window.activateTab) window.activateTab("map");
      });
    }
  }

  init();
})();
