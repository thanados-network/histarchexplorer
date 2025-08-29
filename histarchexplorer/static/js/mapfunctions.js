function addSkybox(map) {
    map.setSky({
        "sky-color": "#b2ddfa",
        "horizon-color": "#FFFFFF",
        "fog-color": "#FFFFFF",
        "fog-ground-blend": 0.8,
        "horizon-fog-blend": 0.1,
        "sky-horizon-blend": 0.6,
        "atmosphere-blend": 0.5,
    });
}

function addTerrain(map) {
    const terrainUrl = 'https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=E7Jrgaazm79UlTuEI5f5';

    map.addSource('terrainSource', {type: 'raster-dem', url: terrainUrl, tileSize: 256});
    map.addSource('hillshadeSource', {type: 'raster-dem', url: terrainUrl, tileSize: 256});

    map.addLayer({
        id: 'hills',
        type: 'hillshade',
        source: 'hillshadeSource',
        layout: {visibility: 'visible'},
        paint: {'hillshade-shadow-color': 'rgba(71,59,36,0.56)'}
    });

    map.addControl(new maplibregl.TerrainControl({source: 'terrainSource', exaggeration: 1}));
}

function addGeoJsonSources(map, data) {
    map.addSource('feature-data', {type: 'geojson', data: data});
}

function setPointer(layers, map) {
    layers.forEach(layer => {
        map.on('mouseenter', layer, () => {
            map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', layer, () => {
            map.getCanvas().style.cursor = '';
        });
    });
}

function addControls(map) {
    map.addControl(new maplibregl.NavigationControl({visualizePitch: true, showZoom: true, showCompass: true}));
}

function highlightFeatures(featureIds = [], map) {
    map.setFilter('highlight-polygon', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'Polygon']]);
    map.setFilter('highlight-polygon-outline', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'Polygon']]);
    map.setFilter('highlight-linestring', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'LineString']]);
    map.setFilter('highlight-points', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'Point']]);
}

function showPopup(lngLat, featureNames, map) {
    if (featureNames.length === 0) return;

    new maplibregl.Popup({closeOnClick: true})
        .setLngLat(lngLat)
        .setHTML(featureNames.join('<br>'))
        .addTo(map);
    document.querySelectorAll(".map-popup-hoverlink").forEach(button => {
        button.addEventListener("mouseenter", () => {
            const featureId = parseInt(button.getAttribute("data-id"));
            highlightFeatures([featureId], map); // Call the function with the feature ID
        });

        button.addEventListener("mouseleave", () => {
            highlightFeatures(featureIds, map); // Optionally remove the highlight when mouse leaves

        });
    })
}

