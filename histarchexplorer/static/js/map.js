const bounds = new maplibregl.LngLatBounds();

function extendBounds(feature) {
    const {type, coordinates} = feature.geometry;
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


const onePointFeature = (mapData.features.length === 1 && mapData.features[0].geometry.type === 'Point');

mapData.features.forEach(extendBounds);

const center = bounds.getCenter();

const map = new maplibregl.Map({
    container: 'mymap',
    center: [center.lng, center.lat],
    style: 'https://api.maptiler.com/maps/topo-v2/style.json?key=E7Jrgaazm79UlTuEI5f5',
    zoom: 17,
    maxPitch: 85,
    maxZoom: 25,
});

map.on('load', () => {
    addSkybox();
    addGeoJsonSources();
    addLayers();
    addControls();
    addTerrain();
    if (!notYetClickedTabs.includes('map') && !onePointFeature) map.fitBounds(bounds, {padding: 200});
    map.setFilter('this-polygon', ['all', ['==', 'main', true], ['==', '$type', 'Polygon']]);
    map.setFilter('this-linestring', ['all', ['==', 'main', true], ['==', '$type', 'LineString']]);
    map.setFilter('this-points', ['all', ['==', 'main', true], ['==', '$type', 'Point']]);
    setPointer(mapVectorLayers)
});

function addTerrain() {
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

function addControls() {
    map.addControl(new maplibregl.NavigationControl({visualizePitch: true, showZoom: true, showCompass: true}));
}

function addGeoJsonSources() {
    map.addSource('feature-data', {type: 'geojson', data: mapData});
}

function addLayers() {
    const layers = [
         { id: 'entity-polygon', type: 'fill', source: 'feature-data', color: '#92BCEA', opacity: 0.3, filterType: 'Polygon', systemClass: 'place' },
         { id: 'entity-outline', type: 'line', source: 'feature-data', color: '#355070', width: 2, filterType: 'Polygon', systemClass: 'place' },
         { id: 'entity-linestring', type: 'line', source: 'feature-data', color: '#4078C0', width: 2, filterType: 'LineString', systemClass: 'place' },
         { id: 'entity-points', type: 'circle', source: 'feature-data', color: '#3366BB', radius: 9, filterType: 'Point', systemClass: 'place' },
         { id: 'feature-polygon', type: 'fill', source: 'feature-data', color: '#57C4C4', opacity: 0.6, filterType: 'Polygon', systemClass: 'feature' },
         { id: 'feature-outline', type: 'line', source: 'feature-data', color: '#2E5F5F', width: 2, filterType: 'Polygon', systemClass: 'feature' },
         { id: 'feature-linestring', type: 'line', source: 'feature-data', color: '#5FDDD3', width: 4, filterType: 'LineString', systemClass: 'feature' },
         { id: 'feature-points', type: 'circle', source: 'feature-data', color: '#1B8282', radius: 9, filterType: 'Point', systemClass: 'feature' },
         { id: 'stratigraphic-unit-polygon', type: 'fill', source: 'feature-data', color: '#B38E5D', opacity: 0.6, filterType: 'Polygon', systemClass: 'stratigraphic_unit' },
         { id: 'stratigraphic-unit-outline', type: 'line', source: 'feature-data', color: '#80623A', width: 2, filterType: 'Polygon', systemClass: 'stratigraphic_unit' },
         { id: 'stratigraphic-unit-linestring', type: 'line', source: 'feature-data', color: '#C49A6C', width: 4, filterType: 'LineString', systemClass: 'stratigraphic_unit' },
         { id: 'stratigraphic-unit-points', type: 'circle', source: 'feature-data', color: '#9D6A21', radius: 9, filterType: 'Point', systemClass: 'stratigraphic_unit' },
         { id: 'artifact-polygon', type: 'fill', source: 'feature-data', color: '#D45C2C', opacity: 0.6, filterType: 'Polygon', systemClass: 'artifact' },
         { id: 'artifact-outline', type: 'line', source: 'feature-data', color: '#993D1A', width: 2, filterType: 'Polygon', systemClass: 'artifact' },
         { id: 'artifact-linestring', type: 'line', source: 'feature-data', color: '#F0784A', width: 4, filterType: 'LineString', systemClass: 'artifact' },
         { id: 'artifact-points', type: 'circle', source: 'feature-data', color: '#B5411D', radius: 9, filterType: 'Point', systemClass: 'artifact' },
         { id: 'human-remains-polygon', type: 'fill', source: 'feature-data', color: '#A36BAA', opacity: 0.6, filterType: 'Polygon', systemClass: 'human_remains' },
         { id: 'human-remains-outline', type: 'line', source: 'feature-data', color: '#5D3F67', width: 2, filterType: 'Polygon', systemClass: 'human_remains' },
         { id: 'human-remains-linestring', type: 'line', source: 'feature-data', color: '#85519C', width: 4, filterType: 'LineString', systemClass: 'human_remains' },
         { id: 'human-remains-points', type: 'circle', source: 'feature-data', color: '#6D4D86', radius: 9, filterType: 'Point', systemClass: 'human_remains' },
        //{ id: 'entity-polygon', type: 'fill', source: 'feature-data', color: '#92BCEA', opacity: 0.3, filterType: 'Polygon', systemClass: 'Place' },
        //{ id: 'entity-outline', type: 'line', source: 'feature-data', color: '#355070', width: 2, filterType: 'Polygon', systemClass: 'Place' },
        //{ id: 'entity-linestring', type: 'line', source: 'feature-data', color: '#4078C0', width: 2, filterType: 'LineString', systemClass: 'Place' },
        //{ id: 'entity-points', type: 'circle', source: 'feature-data', color: '#3366BB', radius: 9, filterType: 'Point', systemClass: 'Place' },
        //{ id: 'feature-polygon', type: 'fill', source: 'feature-data', color: '#57C4C4', opacity: 0.6, filterType: 'Polygon', systemClass: 'Feature' },
        //{ id: 'feature-outline', type: 'line', source: 'feature-data', color: '#2E5F5F', width: 2, filterType: 'Polygon', systemClass: 'Feature' },
        //{ id: 'feature-linestring', type: 'line', source: 'feature-data', color: '#5FDDD3', width: 4, filterType: 'LineString', systemClass: 'Feature' },
        //{ id: 'feature-points', type: 'circle', source: 'feature-data', color: '#1B8282', radius: 9, filterType: 'Point', systemClass: 'Feature' },
        //{ id: 'stratigraphic-unit-polygon', type: 'fill', source: 'feature-data', color: '#B38E5D', opacity: 0.6, filterType: 'Polygon', systemClass: 'Stratigraphic unit' },
        //{ id: 'stratigraphic-unit-outline', type: 'line', source: 'feature-data', color: '#80623A', width: 2, filterType: 'Polygon', systemClass: 'Stratigraphic unit' },
        //{ id: 'stratigraphic-unit-linestring', type: 'line', source: 'feature-data', color: '#C49A6C', width: 4, filterType: 'LineString', systemClass: 'Stratigraphic unit' },
        //{ id: 'stratigraphic-unit-points', type: 'circle', source: 'feature-data', color: '#9D6A21', radius: 9, filterType: 'Point', systemClass: 'Stratigraphic unit' },
        //{ id: 'artifact-polygon', type: 'fill', source: 'feature-data', color: '#D45C2C', opacity: 0.6, filterType: 'Polygon', systemClass: 'Artifact' },
        //{ id: 'artifact-outline', type: 'line', source: 'feature-data', color: '#993D1A', width: 2, filterType: 'Polygon', systemClass: 'Artifact' },
        //{ id: 'artifact-linestring', type: 'line', source: 'feature-data', color: '#F0784A', width: 4, filterType: 'LineString', systemClass: 'Artifact' },
        //{ id: 'artifact-points', type: 'circle', source: 'feature-data', color: '#B5411D', radius: 9, filterType: 'Point', systemClass: 'Artifact' },
        //{ id: 'human-remains-polygon', type: 'fill', source: 'feature-data', color: '#A36BAA', opacity: 0.6, filterType: 'Polygon', systemClass: 'Human remains' },
        //{ id: 'human-remains-outline', type: 'line', source: 'feature-data', color: '#5D3F67', width: 2, filterType: 'Polygon', systemClass: 'Human remains' },
        //{ id: 'human-remains-linestring', type: 'line', source: 'feature-data', color: '#85519C', width: 4, filterType: 'LineString', systemClass: 'Human remains' },
        //{ id: 'human-remains-points', type: 'circle', source: 'feature-data', color: '#6D4D86', radius: 9, filterType: 'Point', systemClass: 'Human remains' },

        { id: 'this-polygon', type: 'fill', source: 'feature-data', color: '#ff0000', opacity: 0.7, filterType: 'Polygon' },
        { id: 'this-polygon-outline', type: 'line', source: 'feature-data', color: '#3e0505', width: 2, filterType: 'Polygon' },
        { id: 'this-linestring', type: 'line', source: 'feature-data', color: '#ff0000', width: 2, filterType: 'LineString' },
        { id: 'this-points', type: 'circle', source: 'feature-data', color: 'rgba(255,0,0,0.8)', radius: 8, filterType: 'Point' },
        { id: 'highlight-polygon', type: 'fill', source: 'feature-data', color: '#FF4444', opacity: 0.5, filterType: 'Polygon' },
        { id: 'highlight-polygon-outline', type: 'line', source: 'feature-data', color: 'rgba(255,255,255,0.8)', width: 3, filterType: 'Polygon' },
        { id: 'highlight-linestring', type: 'line', source: 'feature-data', color: 'rgba(255,68,68,0.63)', width: 3, filterType: 'LineString' },
        { id: 'highlight-points', type: 'circle', source: 'feature-data', color: 'rgba(255,68,68,0.86)', radius: 9, filterType: 'Point' }
    ];

    layers.forEach(layer => addLayer(layer));
    highlightFeatures();
}


const mapVectorLayers = ['feature-polygon', 'feature-points', 'feature-points', 'stratigraphic-unit-polygon', 'stratigraphic-unit-points', 'stratigraphic-unit-points', 'entity-polygon', 'entity-linestring', 'entity-points',
    'artifact-polygon', 'artifact-linestring', 'artifact-points', 'human-remains-polygon', 'human-remains-linestring', 'human-remains-points']

function addLayer({id, type, source, color, width = 1, opacity = 1, radius = 4, filterType, systemClass = null}) {
    const paintStyles = {
        fill: {'fill-color': color, 'fill-opacity': opacity},
        line: {'line-color': color, 'line-width': width, 'line-opacity': opacity},
        circle: {'circle-color': color, 'circle-radius': radius}
    };

    const filter = systemClass ? ['all', ['==', '$type', filterType], ['==', 'class', systemClass]] : ['==', '$type', filterType];

    map.addLayer({id, type, source, paint: paintStyles[type], filter});
}

map.on('click', (e) => {
    if (!map.getLayer('highlight-polygon')) {
        console.warn("Highlight layers not ready yet");
        return;
    }

    const clickedFeatures = map.queryRenderedFeatures(e.point, {
        layers: mapVectorLayers
    });

    if (!clickedFeatures.length) return;

    const featureNames = clickedFeatures.map(f =>
        `<button class="map-popup-hoverlink" onclick="setSidebarContent(${f.properties.id})" data-id="${f.properties.id}">${f.properties.label} (${f.properties.class})</button>`
    );
    featureIds = clickedFeatures.map(f => f.properties.id);

    highlightFeatures(featureIds);
    showPopup(e.lngLat, featureNames);
});


function highlightFeatures(featureIds = []) {
    console.log("Highlighting IDs:", featureIds);
    console.log("Layers available:", map.getStyle().layers.map(l => l.id));

    const layerConfigs = {
        'highlight-polygon': 'Polygon',
        'highlight-polygon-outline': 'Polygon',
        'highlight-linestring': 'LineString',
        'highlight-points': 'Point'
    };

    Object.entries(layerConfigs).forEach(([layerId, type]) => {
        if (!map.getLayer(layerId)) {
            console.warn(`Layer ${layerId} not found`);
            return;
        }
        map.setFilter(layerId, [
            'all',
            ['in', 'id', ...featureIds],
            ['==', '$type', type]
        ]);
    });
}


function showPopup(lngLat, featureNames) {
    if (featureNames.length === 0) return;

    new maplibregl.Popup({closeOnClick: true})
        .setLngLat(lngLat)
        .setHTML(featureNames.join('<br>'))
        .addTo(map);
    document.querySelectorAll(".map-popup-hoverlink").forEach(button => {
        button.addEventListener("mouseenter", () => {
            const featureId = parseInt(button.getAttribute("data-id"));
            highlightFeatures([featureId]); // Call the function with the feature ID
        });

        button.addEventListener("mouseleave", () => {
            highlightFeatures(featureIds); // Optionally remove the highlight when mouse leaves

        });
    })
}

function setPointer(layers) {
    layers.forEach(layer => {
        map.on('mouseenter', layer, () => map.getCanvas().style.cursor = 'pointer');
        map.on('mouseleave', layer, () => map.getCanvas().style.cursor = '');
    });
}

function setSidebarContent(id, mode = 'toggle') {
    if (!rightSidebarcontent.map.opened) {
                toggleRightSidebar('map', 'open');
                rightSidebarcontent.map.opened = true
            }
    const startTime = performance.now(); // Start timing
    const contentDiv = document.getElementById('right-sidebar');

    // Show a centered Bootstrap spinner
    contentDiv.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <div class="spinner-border text-secondary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;

    fetch(`/get_entity/${id}/feature`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load content for feature`);
            }
            return response.text(); // Get the HTML content
        })
        .then(html => {
            const endTime = performance.now(); // End timing
            const fetchTime = ((endTime - startTime) / 1000).toFixed(2); // Convert to seconds

            // Append fetch time info to the HTML
            const updatedHtml = html + `<p style="font-size: 12px; color: gray;">Loaded in ${fetchTime} s</p>`;

            contentDiv.innerHTML = updatedHtml;


        })
        .catch(error => {
            console.error("Error loading right sidebar content:", error);
            contentDiv.innerHTML = `<p style="color: red; text-align: center;">Failed to load content.</p>`;
        });
}




document.getElementById('tab-map').addEventListener('click', function (event) {
    //console.log('map clicked')
    if (notYetClickedTabs.includes('map') && !onePointFeature) {
        setTimeout(() => {
            //console.log('map clicked for the first time');
            notYetClickedTabs = notYetClickedTabs.filter(item => item !== 'map');
            map.fitBounds(bounds, {padding: 200});
        }, 300);
    }
})
