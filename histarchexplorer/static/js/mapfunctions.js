// MAPFUNCTIONS.JS — General file for all mapfunctions

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

/**
 * Processes a FeatureCollection to add representative points for non-point geometries.
 * These points are used as markers when the original geometry is too small at low zoom levels.
 * @param {Object} featureCollection - The GeoJSON FeatureCollection to process.
 * @returns {Object} The updated FeatureCollection.
 */
function processRepresentativePoints(featureCollection) {
    if (!featureCollection || !featureCollection.features) return featureCollection;

    const newFeatures = [];
    featureCollection.features.forEach(feature => {
        if (!feature.geometry) return;
        const type = feature.geometry.type;

        if (type === 'Polygon' || type === 'MultiPolygon' || type === 'LineString' || type === 'MultiLineString') {
            const bounds = new maplibregl.LngLatBounds();

            const extendBounds = (geom) => {
                if (!geom || !geom.coordinates) return;
                const gType = geom.type;
                const coords = geom.coordinates;
                if (gType === 'Point') {
                    bounds.extend(coords);
                } else if (gType === 'LineString' || gType === 'MultiPoint') {
                    coords.forEach(c => bounds.extend(c));
                } else if (gType === 'Polygon' || gType === 'MultiLineString') {
                    coords.forEach(ring => ring.forEach(c => bounds.extend(c)));
                } else if (gType === 'MultiPolygon') {
                    coords.forEach(poly => poly.forEach(ring => ring.forEach(c => bounds.extend(c))));
                }
            };

            extendBounds(feature.geometry);

            if (!bounds.isEmpty()) {
                const center = bounds.getCenter();
                const sw = bounds.getSouthWest();
                const ne = bounds.getNorthEast();

                // Calculate diagonal distance in meters using Haversine approximation
                const lat1 = sw.lat * Math.PI / 180;
                const lat2 = ne.lat * Math.PI / 180;
                const deltaLat = (ne.lat - sw.lat) * Math.PI / 180;
                const deltaLng = (ne.lng - sw.lng) * Math.PI / 180;

                const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
                          Math.cos(lat1) * Math.cos(lat2) *
                          Math.sin(deltaLng / 2) * Math.sin(deltaLng / 2);
                const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                const size = 6371000 * c; // Earth radius in meters

                if (size > 0) {
                    const lat = center.lat;
                    // Formula: zoom = log2((pixel_size * circumference * cos(lat)) / (size * tile_size))
                    const threshold = Math.log2((40 * 40075016 * Math.cos(lat * Math.PI / 180)) / (size * 256));

                    newFeatures.push({
                        type: 'Feature',
                        geometry: {
                            type: 'Point',
                            coordinates: [center.lng, center.lat]
                        },
                        properties: {
                            ...feature.properties,
                            representative: true,
                            hide_point_zoom: threshold,
                            fade_start_zoom: threshold - 1
                        }
                    });
                }
            }
        }
    });

    featureCollection.features.push(...newFeatures);
    return featureCollection;
}

