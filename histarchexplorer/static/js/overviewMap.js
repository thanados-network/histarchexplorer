// ============================================================
//  OVERVIEWMAP.JS — async mini map for overview tile
// ============================================================

(async function initOverviewMap() {
  // Wait for DOM to be ready
  if (document.readyState === "loading") {
    await new Promise(resolve =>
      document.addEventListener("DOMContentLoaded", resolve)
    );
  }

  // Wait for entity data
  const data = await window.entityData;
  if (!data || !data.entity) {
    console.error("❌ entityData missing for overviewMap.js");
    return;
  }

  const entity = data.entity;
  const mapData = data.overviewMap;
  // const name = entity.title || "Entity";
  // console.log("✅ overviewMap.js: entity ready", name);

  const container = document.getElementById("muuri-map");
  if (!mapData || !container) {
    console.warn("⚠️ overviewMap or map container missing");
    return;
  }

  // Normalize GeoJSON
  const features =
    mapData.type === "FeatureCollection"
      ? mapData.features
      : mapData.features || [mapData];

  if (!Array.isArray(features) || !features.length) {
    console.warn("⚠️ No features in overviewMap.");
    return;
  }

  // === MapLibre setup ===
  const overviewMap = new maplibregl.Map({
    container,
    style:
      "https://api.maptiler.com/maps/topo-v2/style.json?key=E7Jrgaazm79UlTuEI5f5",
    center: [0, 0],
    zoom: 5,
    attributionControl: false,
    maxZoom: 22,
  });

  overviewMap.addControl(new maplibregl.NavigationControl(), "top-right");
  overviewMap.addControl(new maplibregl.ScaleControl(), "bottom-left");

  const bounds = new maplibregl.LngLatBounds();
  const extendBounds = geometry => {
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

  // === Once map style is ready ===
  overviewMap.on("load", () => {
    // GeoJSON source
    overviewMap.addSource("overview-geojson", {
      type: "geojson",
      data: { type: "FeatureCollection", features },
    });

    // Layers
    const layers = [
      {
        id: "overview-polygons",
        type: "fill",
        color: "#92BCEA",
        opacity: 0.35,
        filter: ["==", "$type", "Polygon"],
      },
      {
        id: "overview-lines",
        type: "line",
        color: "#4078C0",
        width: 2,
        filter: ["==", "$type", "LineString"],
      },
      {
        id: "overview-points",
        type: "circle",
        color: "#007cbf",
        radius: 6,
        filter: ["==", "$type", "Point"],
      },
      {
        id: "overview-outline",
        type: "line",
        color: "#355070",
        width: 2,
        filter: ["==", "$type", "Polygon"],
      },
    ];

    for (const l of layers) {
      const paint =
        l.type === "fill"
          ? { "fill-color": l.color, "fill-opacity": l.opacity }
          : l.type === "circle"
          ? { "circle-color": l.color, "circle-radius": l.radius }
          : { "line-color": l.color, "line-width": l.width };
      overviewMap.addLayer({
        id: l.id,
        type: l.type,
        source: "overview-geojson",
        paint,
        filter: l.filter,
      });
    }

    // Fit bounds
    features.forEach(f => extendBounds(f.geometry));
    if (!bounds.isEmpty()) {
      overviewMap.fitBounds(bounds, { padding: 50, duration: 0 });
    }

    // Optional markers
    features
      .filter(f => f.geometry?.type === "Point")
      .forEach(f => {
        const [lng, lat] = f.geometry.coordinates;
        new maplibregl.Marker({ color: "#007cbf" })
          .setLngLat([lng, lat])
          .setPopup(
            new maplibregl.Popup().setHTML(
              `<b>${f.properties?.title || name}</b><br>${f.properties?.description || ""}`
            )
          )
          .addTo(overviewMap);
      });

    // Cursor hover
    ["overview-polygons", "overview-lines", "overview-points"].forEach(layer => {
      overviewMap.on("mouseenter", layer, () => (overviewMap.getCanvas().style.cursor = "pointer"));
      overviewMap.on("mouseleave", layer, () => (overviewMap.getCanvas().style.cursor = ""));
    });
  });

  // Optional expand-to-map button
  const expandButton = document.getElementById("expand-button");
  if (expandButton) {
    expandButton.addEventListener("click", () => {
      if (window.activateTab) window.activateTab("map");
    });
  }
})();
