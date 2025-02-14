const bounds = new maplibregl.LngLatBounds();

// Function to extend bounds based on geometry type
function extendBounds(feature) {
    const { type, coordinates } = feature.geometry;
    switch (type) {
        case 'Point':
            bounds.extend(coordinates);
            break;
        case 'LineString':
        case 'Polygon':
            coordinates.flat(type === 'Polygon' ? 1 : 0).forEach(coord => bounds.extend(coord));
            break;
        case 'MultiPolygon':
            coordinates.flat(2).forEach(coord => bounds.extend(coord));
            break;
    }
}

// Compute bounds for all features
mapData.features.forEach(extendBounds);

const center = bounds.getCenter();

// Initialize map
const map = new maplibregl.Map({
    container: 'mymap',
    center: [center.lng, center.lat],
    style: 'https://api.maptiler.com/maps/topo-v2/style.json?key=E7Jrgaazm79UlTuEI5f5',
    zoom: 14,
    maxPitch: 85,
    maxZoom: 25,
});

map.on('load', () => {
    addSkybox();
    addGeoJsonSources();
    addLayers();
    addControls();
    addTerrain();
    map.fitBounds(bounds, { padding: 200 });
});

// 🔹 Function to add terrain and hillshade sources
function addTerrain() {
    const terrainUrl = 'https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=E7Jrgaazm79UlTuEI5f5';

    map.addSource('terrainSource', { type: 'raster-dem', url: terrainUrl, tileSize: 256 });
    map.addSource('hillshadeSource', { type: 'raster-dem', url: terrainUrl, tileSize: 256 });

    map.addLayer({
        id: 'hills',
        type: 'hillshade',
        source: 'hillshadeSource',
        layout: { visibility: 'visible' },
        paint: { 'hillshade-shadow-color': 'rgba(71,59,36,0.56)' }
    });

    map.addControl(new maplibregl.TerrainControl({ source: 'terrainSource', exaggeration: 1 }));
}

// 🔹 Function to add skybox effect
function addSkybox() {
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

// 🔹 Function to add map controls
function addControls() {
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true, showZoom: true, showCompass: true }));
}

// 🔹 Function to add GeoJSON sources
function addGeoJsonSources() {
    map.addSource('feature-data', { type: 'geojson', data: mapData });
}

// 🔹 Function to add layers dynamically
function addLayers() {
    const layers = [

        { id: 'entity-polygon', type: 'fill', source: 'feature-data', color: '#a6caff', opacity: 0.3, filterType: 'Polygon', systemClass: 'Place' },
        { id: 'entity-outline', type: 'line', source: 'feature-data', color: '#4a4a4a', width: 2, filterType: 'Polygon' , systemClass: 'Place'},
        { id: 'entity-linestring', type: 'line', source: 'feature-data', color: '#007dff', width: 2, filterType: 'LineString', systemClass: 'Place' },
        { id: 'entity-points', type: 'circle', source: 'feature-data', color: '#007dff', radius: 6, filterType: 'Point', systemClass: 'Place' },

        { id: 'feature-polygon', type: 'fill', source: 'feature-data', color: '#088', opacity: 0.6, filterType: 'Polygon', systemClass: 'Feature' },
        { id: 'feature-outline', type: 'line', source: 'feature-data', color: '#4a4a4a', width: 2, filterType: 'Polygon', systemClass: 'Feature' },
        { id: 'feature-linestring', type: 'line', source: 'feature-data', color: '#088', width: 4, filterType: 'LineString', systemClass: 'Feature' },
        { id: 'feature-points', type: 'circle', source: 'feature-data', color: '#004c4c', radius: 6, filterType: 'Point', systemClass: 'Feature' },

        { id: 'stratigraphic-unit-polygon', type: 'fill', source: 'feature-data', color: '#ffcc00', opacity: 0.6, filterType: 'Polygon', systemClass: 'Stratigraphic unit' },
        { id: 'stratigraphic-unit-outline', type: 'line', source: 'feature-data', color: '#4a4a4a', width: 2, filterType: 'Polygon', systemClass: 'Stratigraphic unit' },
        { id: 'stratigraphic-unit-linestring', type: 'line', source: 'feature-data', color: '#ffcc00', width: 4, filterType: 'LineString', systemClass: 'Stratigraphic unit' },
        { id: 'stratigraphic-unit-points', type: 'circle', source: 'feature-data', color: '#ffcc00', radius: 6, filterType: 'Point', systemClass: 'Stratigraphic unit' },

        { id: 'artifact-polygon', type: 'fill', source: 'feature-data', color: '#ff6600', opacity: 0.6, filterType: 'Polygon', systemClass: 'Artifact' },
        { id: 'artifact-outline', type: 'line', source: 'feature-data', color: '#4a4a4a', width: 2, filterType: 'Polygon', systemClass: 'Artifact' },
        { id: 'artifact-linestring', type: 'line', source: 'feature-data', color: '#ff6600', width: 4, filterType: 'LineString', systemClass: 'Artifact' },
        { id: 'artifact-points', type: 'circle', source: 'feature-data', color: '#ff6600', radius: 6, filterType: 'Point', systemClass: 'Artifact' },

        { id: 'human-remains-polygon', type: 'fill', source: 'feature-data', color: '#ff3300', opacity: 0.6, filterType: 'Polygon', systemClass: 'Human remains' },
        { id: 'human-remains-outline', type: 'line', source: 'feature-data', color: '#4a4a4a', width: 2, filterType: 'Polygon', systemClass: 'Human remains' },
        { id: 'human-remains-linestring', type: 'line', source: 'feature-data', color: '#ff3300', width: 4, filterType: 'LineString', systemClass: 'Human remains' },
        { id: 'human-remains-points', type: 'circle', source: 'feature-data', color: '#ff3300', radius: 6, filterType: 'Point', systemClass: 'Human remains' },

        { id: 'highlight-polygon', type: 'fill', source: 'feature-data', color: '#ff0000', opacity: 0.3, filterType: 'Polygon'},
        { id: 'highlight-linestring', type: 'line', source: 'feature-data', color: 'rgba(255,0,0,0.63)', width: 2, filterType: 'LineString' },
        { id: 'highlight-points', type: 'circle', source: 'feature-data', color: 'rgba(255,0,0,0.86)', radius: 6, filterType: 'Point' }
    ];

    layers.forEach(layer => addLayer(layer));
    highlightFeatures()


}

// 🔹 Function to add individual layers
function addLayer({ id, type, source, color, width = 1, opacity = 1, radius = 4, filterType, systemClass = null }) {
    const paintStyles = {
        fill: { 'fill-color': color, 'fill-opacity': opacity },
        line: { 'line-color': color, 'line-width': width, 'line-opacity': opacity },
        circle: { 'circle-color': color, 'circle-radius': radius }
    };

    const filter = systemClass
        ? ['all', ['==', '$type', filterType], ['==', 'class', systemClass]]
        : ['==', '$type', filterType];

    map.addLayer({ id, type, source, paint: paintStyles[type], filter });
}

map.on('click', (e) => {
    highlightFeatures()
    const clickedFeatures = map.queryRenderedFeatures(e.point, {
        layers: ['feature-polygon', 'feature-outline', 'feature-points',
                 'entity-polygon', 'entity-outline', 'entity-linestring', 'entity-points']
    });

    if (!clickedFeatures.length) return;

    const featureNames = clickedFeatures.map(f => f.properties.label + ' (' + f.properties.class + ')' );
    featureIds = clickedFeatures.map(f => f.properties.id);

    highlightFeatures(featureIds);

    showPopup(e.lngLat, featureNames);
});


function highlightFeatures(featureIds = []) {
    map.setFilter('highlight-polygon', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'Polygon']]);
    map.setFilter('highlight-linestring', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'LineString']]);
    map.setFilter('highlight-points', ['all', ['in', 'id', ...featureIds], ['==', '$type', 'Point']]);
}

function showPopup(lngLat, featureNames) {
    if (featureNames.length === 0) return;

    new maplibregl.Popup({ closeOnClick: true })
        .setLngLat(lngLat)
        .setHTML(featureNames.join('<br>'))
        .addTo(map);
}
