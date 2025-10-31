const bounds = new maplibregl.LngLatBounds();

const geomFeatureIds = [...new Set(mapData.features.map(f => f.properties.id))];

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
    addRasterMaps(map, geomFeatureIds);
    const layerControl = new LayerControl();
    map.addControl(layerControl, 'top-left');
    map.layerControl = layerControl;
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
        {
            id: 'entity-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#92BCEA',
            opacity: 0.3,
            filterType: 'Polygon',
            systemClass: 'place'
        },
        {
            id: 'entity-outline',
            type: 'line',
            source: 'feature-data',
            color: '#355070',
            width: 2,
            filterType: 'Polygon',
            systemClass: 'place'
        },
        {
            id: 'entity-linestring',
            type: 'line',
            source: 'feature-data',
            color: '#4078C0',
            width: 2,
            filterType: 'LineString',
            systemClass: 'place'
        },
        {
            id: 'entity-points',
            type: 'circle',
            source: 'feature-data',
            color: '#3366BB',
            radius: 9,
            filterType: 'Point',
            systemClass: 'place'
        },
        {
            id: 'feature-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#57C4C4',
            opacity: 0.6,
            filterType: 'Polygon',
            systemClass: 'feature'
        },
        {
            id: 'feature-outline',
            type: 'line',
            source: 'feature-data',
            color: '#2E5F5F',
            width: 2,
            filterType: 'Polygon',
            systemClass: 'feature'
        },
        {
            id: 'feature-linestring',
            type: 'line',
            source: 'feature-data',
            color: '#5FDDD3',
            width: 4,
            filterType: 'LineString',
            systemClass: 'feature'
        },
        {
            id: 'feature-points',
            type: 'circle',
            source: 'feature-data',
            color: '#1B8282',
            radius: 9,
            filterType: 'Point',
            systemClass: 'feature'
        },
        {
            id: 'stratigraphic-unit-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#B38E5D',
            opacity: 0.6,
            filterType: 'Polygon',
            systemClass: 'stratigraphic_unit'
        },
        {
            id: 'stratigraphic-unit-outline',
            type: 'line',
            source: 'feature-data',
            color: '#80623A',
            width: 2,
            filterType: 'Polygon',
            systemClass: 'stratigraphic_unit'
        },
        {
            id: 'stratigraphic-unit-linestring',
            type: 'line',
            source: 'feature-data',
            color: '#C49A6C',
            width: 4,
            filterType: 'LineString',
            systemClass: 'stratigraphic_unit'
        },
        {
            id: 'stratigraphic-unit-points',
            type: 'circle',
            source: 'feature-data',
            color: '#9D6A21',
            radius: 9,
            filterType: 'Point',
            systemClass: 'stratigraphic_unit'
        },
        {
            id: 'artifact-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#D45C2C',
            opacity: 0.6,
            filterType: 'Polygon',
            systemClass: 'artifact'
        },
        {
            id: 'artifact-outline',
            type: 'line',
            source: 'feature-data',
            color: '#993D1A',
            width: 2,
            filterType: 'Polygon',
            systemClass: 'artifact'
        },
        {
            id: 'artifact-linestring',
            type: 'line',
            source: 'feature-data',
            color: '#F0784A',
            width: 4,
            filterType: 'LineString',
            systemClass: 'artifact'
        },
        {
            id: 'artifact-points',
            type: 'circle',
            source: 'feature-data',
            color: '#B5411D',
            radius: 9,
            filterType: 'Point',
            systemClass: 'artifact'
        },
        {
            id: 'human-remains-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#A36BAA',
            opacity: 0.6,
            filterType: 'Polygon',
            systemClass: 'human_remains'
        },
        {
            id: 'human-remains-outline',
            type: 'line',
            source: 'feature-data',
            color: '#5D3F67',
            width: 2,
            filterType: 'Polygon',
            systemClass: 'human_remains'
        },
        {
            id: 'human-remains-linestring',
            type: 'line',
            source: 'feature-data',
            color: '#85519C',
            width: 4,
            filterType: 'LineString',
            systemClass: 'human_remains'
        },
        {
            id: 'human-remains-points',
            type: 'circle',
            source: 'feature-data',
            color: '#6D4D86',
            radius: 9,
            filterType: 'Point',
            systemClass: 'human_remains'
        },
        {
            id: 'this-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#ff0000',
            opacity: 0.7,
            filterType: 'Polygon'
        },
        {
            id: 'this-polygon-outline',
            type: 'line',
            source: 'feature-data',
            color: '#3e0505',
            width: 0,
            filterType: 'Polygon'
        },
        {
            id: 'this-linestring',
            type: 'line',
            source: 'feature-data',
            color: '#ff0000',
            width: 2,
            filterType: 'LineString'
        },
        {
            id: 'this-points',
            type: 'circle',
            source: 'feature-data',
            color: 'rgba(255,0,0,0.8)',
            radius: 8,
            filterType: 'Point'
        },
        {
            id: 'highlight-polygon',
            type: 'fill',
            source: 'feature-data',
            color: '#FF4444',
            opacity: 0.5,
            filterType: 'Polygon'
        },
        {
            id: 'highlight-polygon-outline',
            type: 'line',
            source: 'feature-data',
            color: 'rgba(255,255,255,0.8)',
            width: 3,
            filterType: 'Polygon'
        },
        {
            id: 'highlight-linestring',
            type: 'line',
            source: 'feature-data',
            color: 'rgba(255,68,68,0.63)',
            width: 3,
            filterType: 'LineString'
        },
        {
            id: 'highlight-points',
            type: 'circle',
            source: 'feature-data',
            color: 'rgba(255,68,68,0.86)',
            radius: 9,
            filterType: 'Point'
        }
    ];

    layers.forEach(layer => addLayer(layer));
    highlightFeatures();
}


const mapVectorLayers = ['feature-polygon', 'feature-points', 'feature-linestring', 'stratigraphic-unit-polygon', 'stratigraphic-unit-points', 'stratigraphic-unit-linestring', 'entity-polygon', 'entity-linestring', 'entity-points',
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

class LayerControl {
    constructor() {
        this.modalInitialized = false;
    }

    onAdd(map) {
        this.map = map;
        this.container = document.createElement('div');
        this.container.className = 'maplibregl-ctrl layer-control-ctrl';

        const button = document.createElement('button');
        button.className = 'layer-toggle-btn';
        button.innerHTML = '🗺️';
        this.container.appendChild(button);

        const panel = document.createElement('div');
        panel.className = 'layer-panel';
        this.container.appendChild(panel);

        // open by default
        panel.classList.remove('hidden');
        button.style.display = 'none';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'layer-close-btn';
        closeBtn.innerHTML = '×';
        closeBtn.onclick = () => {
            panel.classList.add('hidden');
            button.style.display = 'block';
        };
        panel.appendChild(closeBtn);

        button.onclick = () => {
            panel.classList.remove('hidden');
            button.style.display = 'none';
        };

        map.once('styledata', () => this._buildPanel(panel));

        return this.container;
    }

    // your predefined layer groups
    _getLayerGroups() {
        return {
            this: {
                Polygon: ["this-polygon"],
                Outline: ["this-outline"],
                LineString: ["this-linestring"],
                Point: ["this-points"]
            },
            place: {
                Polygon: ["entity-polygon"],
                Outline: ["entity-outline"],
                LineString: ["entity-linestring"],
                Point: ["entity-points"]
            },
            feature: {
                Polygon: ["feature-polygon"],
                Outline: ["feature-outline"],
                LineString: ["feature-linestring"],
                Point: ["feature-points"]
            },
            stratigraphic_unit: {
                Polygon: ["stratigraphic-unit-polygon"],
                Outline: ["stratigraphic-unit-outline"],
                LineString: ["stratigraphic-unit-linestring"],
                Point: ["stratigraphic-unit-points"]
            },
            artifact: {
                Polygon: ["artifact-polygon"],
                Outline: ["artifact-outline"],
                LineString: ["artifact-linestring"],
                Point: ["artifact-points"]
            },
            human_remains: {
                Polygon: ["human-remains-polygon"],
                Outline: ["human-remains-outline"],
                LineString: ["human-remains-linestring"],
                Point: ["human-remains-points"]
            }
        };
    }

    _buildPanel(panel) {
        const layerGroups = this._getLayerGroups();
        const groupNames = Object.keys(layerGroups).sort((a, b) => a === 'this' ? -1 : b === 'this' ? 1 : 0);

        groupNames.forEach(groupName => {
            const geometries = layerGroups[groupName];
            const isThisGroup = groupName === 'this';

            let totalCount = 0;
            ["Polygon", "LineString", "Point"].forEach(geomType => {
                totalCount += mapData.features.filter(f => f.properties?.class === groupName && f.geometry.type === geomType).length;
            });
            let label = groupName + 's';

            if (isThisGroup) {
                label = "Selection: " + entityData.entity.title;

                ["Polygon", "LineString", "Point"].forEach(geomType => {
                    totalCount += mapData.features.filter(f => f.properties?.id === entityId && f.geometry.type === geomType).length;
                    console.log(groupName)
                    console.log(totalCount)
                });

            }


            if (!isThisGroup && totalCount === 0) return;

            const groupDiv = document.createElement('div');
            groupDiv.className = 'layer-group';
            const visible = Object.values(geometries).flat().some(id => this._isVisible(id));


            label = label[0].toUpperCase() + label.slice(1);


            groupDiv.innerHTML = `
        <div class="group-header">
          <label>
            <input type="checkbox" ${visible ? 'checked' : ''} data-group="${groupName}">
            ${label.replace(/_/g, ' ')} <span class="count">(${totalCount})</span>
          </label>
          <button class="edit-btn" data-group="${groupName}">▶</button>
        </div>
        <div class="edit-menu hidden"></div>
      `;
            panel.appendChild(groupDiv);

            const editMenu = groupDiv.querySelector('.edit-menu');

            ["Polygon", "LineString", "Point"].forEach(geomType => {
                const layers = geometries[geomType] || [];
                const layerExists = layers.some(id => this.map.getLayer(id));
                let featureCount = mapData.features.filter(f => f.properties?.class === groupName && f.geometry.type === geomType).length;
                if (isThisGroup) featureCount = mapData.features.filter(f => f.properties?.id === entityId && f.geometry.type === geomType).length;
                if (!isThisGroup && featureCount === 0) return;

                let fillColor = '#888', outlineColor = '#000', width = 2, opacity = 1, radius = 8;

                if (geomType === 'Polygon') {
                    const fillLayerId = layers[0];
                    const outlineLayerId = geometries['Outline']?.[0];
                    if (fillLayerId && this.map.getLayer(fillLayerId)) {
                        fillColor = this.map.getPaintProperty(fillLayerId, 'fill-color') ?? fillColor;
                        opacity = this.map.getPaintProperty(fillLayerId, 'fill-opacity') ?? opacity;
                    }
                    if (outlineLayerId && this.map.getLayer(outlineLayerId)) {
                        outlineColor = this.map.getPaintProperty(outlineLayerId, 'line-color') ?? outlineColor;
                        width = this.map.getPaintProperty(outlineLayerId, 'line-width') ?? width;
                    }
                } else if (geomType === 'LineString') {
                    const lineLayerId = layers[0];
                    if (lineLayerId && this.map.getLayer(lineLayerId)) {
                        fillColor = this.map.getPaintProperty(lineLayerId, 'line-color') ?? fillColor;
                        width = this.map.getPaintProperty(lineLayerId, 'line-width') ?? width;
                        opacity = this.map.getPaintProperty(lineLayerId, 'line-opacity') ?? opacity;
                    }
                } else if (geomType === 'Point') {
                    const pointLayerId = layers[0];
                    if (pointLayerId && this.map.getLayer(pointLayerId)) {
                        fillColor = this.map.getPaintProperty(pointLayerId, 'circle-color') ?? fillColor;
                        outlineColor = this.map.getPaintProperty(pointLayerId, 'circle-stroke-color') ?? outlineColor;
                        radius = this.map.getPaintProperty(pointLayerId, 'circle-radius') ?? radius;
                        width = this.map.getPaintProperty(pointLayerId, 'circle-stroke-width') ?? width;
                        opacity = this.map.getPaintProperty(pointLayerId, 'circle-opacity') ?? opacity;
                    }
                }

                const symbol = this._getSymbolForGeom(geomType, fillColor, outlineColor, width, opacity);
                const geomDiv = document.createElement('div');
                geomDiv.className = 'edit-geom';
                geomDiv.innerHTML = `
          <div class="geom-header d-flex justify-content-between align-items-center">
            <label class="geom-toggle">
              <input type="checkbox" ${layerExists ? 'checked' : ''} data-geom="${geomType}" data-group="${groupName}">
              ${geomType}<span class="geom-count">(${featureCount})</span>
            </label>
                    <button class="style-btn btn btn-sm btn-light d-flex align-items-center" data-group="${groupName}" data-geom="${geomType}">
          <span class="symbol" data-group="${groupName}" data-geom="${geomType}">${symbol}</span>
        </button>
          </div>
        `;
                if (featureCount > 0) editMenu.appendChild(geomDiv);
            });
            /*                    Sortable.create(editMenu, {
                        handle: '.geom-header', // Drag by geometry header
                        animation: 150,
                        onEnd: (evt) => {
                            this._updateMapLayerOrder();
                        }
                    });*/
        });

        const imagesGroup = document.createElement('div');
        imagesGroup.className = 'layer-group';

        const imagesHeader = document.createElement('div');
        imagesHeader.id = 'images-header';
        imagesHeader.className = 'group-header d-none';
        imagesHeader.innerHTML = `
              <label>
                <input type="checkbox" checked data-group="images">
                Images 
                <span id="imagecount" class="count">
                    <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                    <span class="visually-hidden" role="status">Loading...</span>
                </span>
            </div>
              </label>
              <button class="edit-btn" title="Toggle images">▼</button>
            `;

        imagesGroup.appendChild(imagesHeader);

// ✅ The real working legend container
        const imagesMenu = document.createElement('div');
        imagesMenu.className = 'edit-menu';
        imagesMenu.id = 'legend-images'; // This is where addRasterMaps() appends items
        imagesGroup.appendChild(imagesMenu);

        panel.appendChild(imagesGroup);


        imagesMenu.classList.add('hidden');
        imagesHeader.querySelector('.edit-btn').textContent = '▶';


        const toggleBtn = imagesHeader.querySelector('.edit-btn');
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent event bubbling to parent groups
            const imagesMenu = imagesHeader.nextElementSibling; // select the actual menu
            if (!imagesMenu) return;
            const isHidden = imagesMenu.classList.toggle('hidden');
            toggleBtn.textContent = isHidden ? '▶' : '▼';
        });


        panel.addEventListener('change', (e) => this._handleCheckboxChange(e));
        panel.addEventListener('click', (e) => this._handleClick(e));

        /*Sortable.create(panel, {
            handle: '.group-header', // Drag by the header
            animation: 150,
            onEnd: (evt) => {
                this._updateMapLayerOrder();
            }
        });*/

    }

    _updateMapLayerOrder() {
        const panel = this.container.querySelector('.layer-panel');
        const layerGroups = this._getLayerGroups();

        // Iterate over groups in DOM order (top to bottom)
        panel.querySelectorAll('.layer-group').forEach(groupDiv => {
            const groupName = groupDiv.querySelector('input[type="checkbox"]').dataset.group;
            const editMenu = groupDiv.querySelector('.edit-menu');

            // Collect child layers in DOM order
            const layerIds = [];
            editMenu.querySelectorAll('input[data-geom]').forEach(cb => {
                const geom = cb.dataset.geom;
                const layers = (geom === 'Polygon')
                    ? [...(layerGroups[groupName]['Polygon'] || []), ...(layerGroups[groupName]['Outline'] || [])]
                    : layerGroups[groupName][geom];
                layerIds.push(...layers);
            });

            // Move each layer on map from bottom to top
            layerIds.forEach((layerId, idx) => {
                if (this.map.getLayer(layerId)) {
                    // Move layer above the next layer in array, or top if last
                    const nextLayer = layerIds[idx + 1] || undefined;
                    this.map.moveLayer(layerId, nextLayer);
                }
            });
        });
    }

    // --- New: Add "Images" Section Dynamically ---
    addImageLegendEntry(img) {
        if (!this.container) return;
        let imageGroup = this.container.querySelector('.layer-group.images');
        if (!imageGroup) {
            imageGroup = document.createElement('div');
            imageGroup.className = 'layer-group images';
            imageGroup.innerHTML = `
        <div class="group-header">
          <label>
            <input type="checkbox" class="group-checkbox" checked data-group="images">
            Images
          </label>
        </div>
        <div class="group-content" style="margin-left:1rem;"></div>
      `;
            this.container.appendChild(imageGroup);

            const parentCheckbox = imageGroup.querySelector('.group-checkbox');
            parentCheckbox.addEventListener('change', (e) => {
                const checked = e.target.checked;
                imageGroup.querySelectorAll('input[data-layer]').forEach(cb => {
                    cb.checked = checked;
                    const layerId = cb.dataset.layer;
                    if (this.map.getLayer(layerId)) {
                        this.map.setLayoutProperty(layerId, 'visibility', checked ? 'visible' : 'none');
                    }
                });
            });
        }

        const itemsContainer = imageGroup.querySelector('.group-content');
        const layerId = `image_layer_${img.id}`;
        const opacity = 0.9;

        const item = document.createElement('div');
        item.className = 'legend-item d-flex align-items-center justify-content-between my-1';
        item.innerHTML = `
              <label class="d-flex align-items-center gap-2 flex-grow-1">
                <input type="checkbox" checked data-layer="${layerId}">
                <span>${img.name || 'Image ' + img.id}</span>
              </label><br>
              <input type="range" min="0" max="1" step="0.05" value="${opacity}" data-opacity="${layerId}" style="width:80px;">
            `;
        itemsContainer.appendChild(item);


        const checkbox = item.querySelector('input[data-layer]');
        checkbox.addEventListener('change', (e) => {
            const visible = e.target.checked ? 'visible' : 'none';
            if (this.map.getLayer(layerId)) this.map.setLayoutProperty(layerId, 'visibility', visible);
        });

        const slider = item.querySelector('input[data-opacity]');
        slider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            if (this.map.getLayer(layerId)) this.map.setPaintProperty(layerId, 'raster-opacity', val);
        });
    }

    _handleCheckboxChange(e) {
        const target = e.target;
        if (target.type !== 'checkbox') return;
        const group = target.dataset.group;
        const geom = target.dataset.geom;
        const layerGroups = this._getLayerGroups();

        if (group === 'images' && !geom) {
            const checkboxes = this.container.querySelectorAll('#legend-images input[type="checkbox"][data-layer]');
            checkboxes.forEach(cb => {
                cb.checked = target.checked;
                const layerId = cb.dataset.layer;
                if (this.map.getLayer(layerId)) {
                    this.map.setLayoutProperty(layerId, 'visibility', target.checked ? 'visible' : 'none');
                }
            });
            return; // stop further processing
        }

        if (group && !geom) {
            ["Polygon", "LineString", "Point"].forEach(childGeom => {
                const layers = (childGeom === 'Polygon')
                    ? [...(layerGroups[group]['Polygon'] || []), ...(layerGroups[group]['Outline'] || [])]
                    : layerGroups[group][childGeom];
                layers.forEach(id => {
                    if (this.map.getLayer(id)) {
                        this.map.setLayoutProperty(id, 'visibility', target.checked ? 'visible' : 'none');
                    }
                });
                const childCb = this.container.querySelector(`input[data-group="${group}"][data-geom="${childGeom}"]`);
                if (childCb) childCb.checked = target.checked;
            });
        } else if (group && geom) {
            const layers = (geom === 'Polygon')
                ? [...(layerGroups[group]['Polygon'] || []), ...(layerGroups[group]['Outline'] || [])]
                : layerGroups[group][geom];
            layers.forEach(id => {
                if (this.map.getLayer(id)) {
                    this.map.setLayoutProperty(id, 'visibility', target.checked ? 'visible' : 'none');
                }
            });
        }
    }

    _handleClick(e) {
        const btn = e.target;
        if (btn.classList.contains('edit-btn')) {
            const menu = btn.closest('.layer-group').querySelector('.edit-menu');
            const isOpen = !menu.classList.contains('hidden');
            menu.classList.toggle('hidden');
            btn.textContent = isOpen ? '▶' : '▼';
        }

        if (btn.classList.contains('style-btn')) {
            this._openStyleModal(btn.dataset.group, btn.dataset.geom);
        }
    }

    _openStyleModal(group, geom) {
        if (!this.modalInitialized) this._initModal();

        const modal = document.getElementById('styleModal');
        modal.dataset.group = group;
        modal.dataset.geom = geom;

        document.querySelectorAll('.style-field').forEach(el => el.classList.add('d-none'));

        const layers = this._getLayerGroups()[group];
        let fillColor = '#888', outlineColor = '#000', width = 2, opacity = 1, radius = 8;

        if (geom === 'Polygon') {
            const fillLayer = this.map.getLayer(layers['Polygon']?.[0]);
            const outlineLayer = this.map.getLayer(layers['Outline']?.[0]);
            if (fillLayer) {
                fillColor = this._getLayerColor(layers['Polygon'][0]);
                opacity = this.map.getPaintProperty(layers['Polygon'][0], 'fill-opacity') ?? 1;
            }
            if (outlineLayer) {
                outlineColor = this._getLayerColor(layers['Outline'][0]);
                width = this.map.getPaintProperty(layers['Outline'][0], 'line-width') ?? 1;
            }
            document.getElementById('polygon-fields').classList.remove('d-none');
        } else if (geom === 'LineString') {
            const lineLayer = this.map.getLayer(layers['LineString']?.[0]);
            if (lineLayer) {
                fillColor = this._getLayerColor(layers['LineString'][0]);
                width = this.map.getPaintProperty(layers['LineString'][0], 'line-width') ?? 2;
                opacity = this.map.getPaintProperty(layers['LineString'][0], 'line-opacity') ?? 1;
            }
            document.getElementById('line-fields').classList.remove('d-none');
        } else if (geom === 'Point') {
            const pointLayer = this.map.getLayer(layers['Point']?.[0]);
            if (pointLayer) {
                fillColor = this._getLayerColor(layers['Point'][0]);
                outlineColor = this.map.getPaintProperty(layers['Point'][0], 'circle-stroke-color') ?? '#000';
                radius = this.map.getPaintProperty(layers['Point'][0], 'circle-radius') ?? 8;
                width = this.map.getPaintProperty(layers['Point'][0], 'circle-stroke-width') ?? 1;
                opacity = this.map.getPaintProperty(layers['Point'][0], 'circle-opacity') ?? 1;
            }
            document.getElementById('point-fields').classList.remove('d-none');
        }

        document.getElementById('fillColor').value = fillColor;
        document.getElementById('outlineColor').value = outlineColor;
        document.getElementById('outlineWidth').value = width;
        document.getElementById('fillOpacity').value = opacity;

        document.getElementById('lineColor').value = fillColor;
        document.getElementById('lineWidth').value = width;
        document.getElementById('lineOpacity').value = opacity;

        document.getElementById('pointColor').value = fillColor;
        document.getElementById('pointOutlineColor').value = outlineColor;
        document.getElementById('pointRadius').value = radius;
        document.getElementById('pointOutlineWidth').value = width;
        document.getElementById('pointOpacity').value = opacity;

        new bootstrap.Modal(modal).show();
    }

    _applyStyleChanges(group, geom) {
        const layers = this._getLayerGroups()[group];

        let fillColor, outlineColor, width, opacity, radius;

        if (geom === 'Polygon') {
            fillColor = document.getElementById('fillColor').value;
            outlineColor = document.getElementById('outlineColor').value;
            width = parseFloat(document.getElementById('outlineWidth').value);
            opacity = parseFloat(document.getElementById('fillOpacity').value);

            (layers['Polygon'] || []).forEach(id => {
                if (this.map.getLayer(id)) {
                    this.map.setPaintProperty(id, 'fill-color', fillColor);
                    this.map.setPaintProperty(id, 'fill-opacity', opacity);
                }
            });
            (layers['Outline'] || []).forEach(id => {
                if (this.map.getLayer(id)) {
                    this.map.setPaintProperty(id, 'line-color', outlineColor);
                    this.map.setPaintProperty(id, 'line-width', width);
                }
            });
        } else if (geom === 'LineString') {
            fillColor = document.getElementById('lineColor').value;
            width = parseFloat(document.getElementById('lineWidth').value);
            opacity = parseFloat(document.getElementById('lineOpacity').value);

            (layers['LineString'] || []).forEach(id => {
                if (this.map.getLayer(id)) {
                    this.map.setPaintProperty(id, 'line-color', fillColor);
                    this.map.setPaintProperty(id, 'line-width', width);
                    this.map.setPaintProperty(id, 'line-opacity', opacity);
                }
            });
        } else if (geom === 'Point') {
            fillColor = document.getElementById('pointColor').value;
            outlineColor = document.getElementById('pointOutlineColor').value;
            radius = parseFloat(document.getElementById('pointRadius').value);
            width = parseFloat(document.getElementById('pointOutlineWidth').value);
            opacity = parseFloat(document.getElementById('pointOpacity').value);

            (layers['Point'] || []).forEach(id => {
                const layer = this.map.getLayer(id);
                if (!layer) return;
                if (layer.type === 'circle') {
                    this.map.setPaintProperty(id, 'circle-radius', radius);
                    this.map.setPaintProperty(id, 'circle-color', fillColor);
                    this.map.setPaintProperty(id, 'circle-stroke-color', outlineColor);
                    this.map.setPaintProperty(id, 'circle-stroke-width', width);
                    this.map.setPaintProperty(id, 'circle-opacity', opacity);
                }
            });
        }

        // Update legend symbol
        const symbolEl = this.container.querySelector(`.symbol[data-group="${group}"][data-geom="${geom}"]`);
        if (symbolEl) {
            if (geom === 'Point') symbolEl.innerHTML = this._getSymbolForGeom(geom, fillColor, outlineColor, radius, opacity);
            else symbolEl.innerHTML = this._getSymbolForGeom(geom, fillColor, outlineColor, width, opacity);
        }

        bootstrap.Modal.getInstance(document.getElementById('styleModal')).hide();
    }

    _initModal() {
        const modalHTML = `
      <div class="modal fade" id="styleModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Edit Style</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div id="polygon-fields" class="style-field">
                <label>Fill Color <input type="color" id="fillColor"></label><br>
                <label>Fill Opacity <input type="number" id="fillOpacity" min="0" max="1" step="0.05"></label><br>
                <label>Outline Color <input type="color" id="outlineColor"></label><br>
                <label>Outline Width <input type="number" id="outlineWidth" min="0" max="10" step="0.1"></label>
              </div>
            
              <div id="line-fields" class="style-field d-none">
                <label>Line Color <input type="color" id="lineColor"></label><br>
                <label>Line Width <input type="number" id="lineWidth" min="0" max="10" step="0.1"></label><br>
                <label>Line Opacity <input type="number" id="lineOpacity" min="0" max="1" step="0.05"></label>
              </div>
            
              <div id="point-fields" class="style-field d-none">
                <label>Point Color <input type="color" id="pointColor"></label><br>
                <label>Outline Color <input type="color" id="pointOutlineColor"></label><br>
                <label>Radius <input type="number" id="pointRadius" min="1" max="20" step="0.5"></label><br>
                <label>Outline Width <input type="number" id="pointOutlineWidth" min="0" max="10" step="0.1"></label><br>
                <label>Opacity <input type="number" id="pointOpacity" min="0" max="1" step="0.05"></label>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="button" id="applyStyle" class="btn btn-primary">Apply</button>
            </div>
          </div>
        </div>
      </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        document.getElementById('applyStyle').addEventListener('click', () => {
            const modal = document.getElementById('styleModal');
            const group = modal.dataset.group;
            const geom = modal.dataset.geom;
            this._applyStyleChanges(group, geom);
        });

        this.modalInitialized = true;
    }

    _isVisible(id) {
        return this.map.getLayoutProperty(id, 'visibility') !== 'none';
    }

    _getLayerColor(layerId) {
        const layer = this.map.getLayer(layerId);
        if (!layer) return '#000';
        const prop = layer.type === 'fill' ? 'fill-color' : layer.type === 'line' ? 'line-color' : 'circle-color';
        const val = this.map.getPaintProperty(layerId, prop);
        return typeof val === 'string' ? val : '#000';
    }

    _getSymbolForGeom(type, fillColor, outlineColor = '#000', width = 2, opacity = 1) {
        if (type === 'Polygon') {
            return `<svg width="20" height="20" style="opacity:${opacity}">
        <rect x="1" y="1" width="18" height="18" fill="${fillColor}" stroke="${outlineColor}" stroke-width="${width}"/>
      </svg>`;
        }
        if (type === 'LineString') {
            return `<svg width="18" height="18" style="opacity:${opacity}">
        <line x1="2" y1="9" x2="16" y2="9" stroke="${fillColor}" stroke-width="${width}"/>
      </svg>`;
        }
        if (type === 'Point') {
            return `<svg width="16" height="16" style="opacity:${opacity}">
        <circle cx="8" cy="8" r="5" fill="${fillColor}" stroke="${outlineColor}" stroke-width="1"/>
      </svg>`;
        }
        return '';
    }
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
    // Todo: sidebar conntect can be loaded directly with /presentation_view/${ids},
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

function computeBottomRight(tl, tr, bl) {
    const dx1 = tr[0] - tl[0];
    const dy1 = tr[1] - tl[1];
    const dx2 = bl[0] - tl[0];
    const dy2 = bl[1] - tl[1];
    return [tl[0] + dx1 + dx2, tl[1] + dy1 + dy2];
}

async function addImageToMap(map, img, maxSize = 2048) {
    const id = img.id;
    const coords = img.bbox;
    const name = img.name;
    const description = img.description;
    const manifestUrl = `https://thanados.openatlas.eu/api/iiif_manifest/2/${id}`;
    const imageUrl = await getIiifImageUrl(manifestUrl, 2048);

    if (!imageUrl || !coords) return;
    if (!coords || coords.length < 2) return;

    let coordinates;

    if (coords.length === 2) {
        coordinates = getNormalizedCorners(coords);
    } else if (coords.length === 3) {
        // Rotiertes Overlay (3 Punkte)
        const topLeft = [coords[0][1], coords[0][0]];
        const topRight = [coords[1][1], coords[1][0]];
        const bottomLeft = [coords[2][1], coords[2][0]];
        const bottomRight = computeBottomRight(topLeft, topRight, bottomLeft);
        coordinates = [topLeft, topRight, bottomRight, bottomLeft];
    }

    const sourceId = `image_${id}`;
    const layerId = `image_layer_${id}`;

    if (map.getLayer(layerId)) map.removeLayer(layerId);
    if (map.getSource(sourceId)) map.removeSource(sourceId);

    map.addSource(sourceId, {
        type: 'image',
        url: imageUrl,
        coordinates: coordinates
    });

    map.addLayer({
        id: layerId,
        type: 'raster',
        source: sourceId,
        properties: {name: name, description: description},
        paint: {
            'raster-opacity': 0.9
        }
    });

    const imageCountElement = document.getElementById('imagecount');
    const imagesHeader = document.getElementById('images-header');
    if (imageCountElement) {
        const currentCount = map.getStyle().layers.filter(l => l.id.startsWith('image_layer_')).length;
        imageCountElement.innerHTML = `(${currentCount})`;
        if (currentCount > 0) imagesHeader.classList.remove('d-none');
    }
}

async function addRasterMaps(map, ids) {
    // Wait until the LayerControl panel is ready
    await new Promise(resolve => {
        if (map._isStyleLoaded) return resolve();
        map.once('styledata', resolve);
    });

    const legendContainer = map.getContainer().querySelector('#legend-images');
    if (!legendContainer) {
        console.warn('Legend container for images not found');
        return;
    }

    for (const id of ids) {
        try {
            const response = await fetch(`/get_rastermaps/${id}`);
            if (!response.ok) {
                console.warn(`Error with ID ${id}: ${response.status}`);
                continue;
            }

            const data = await response.json();
            if (data[0]) {

                const images = Array.isArray(data) && Array.isArray(data[0]) ? data[0] : data;

                for (const img of images) {
                    await addImageToMap(map, img);

                    // ✅ Add to legend
                    const layerId = `image_layer_${img.id}`;
                    const item = document.createElement('div');
                    item.className = 'image-legend-item';
                    item.innerHTML = `
                    <label>
                        <input type="checkbox" checked data-layer="${layerId}">
                        ${img.name}
                    </label> <br>
                    Opacity: 
                    <input type="range" min="0" max="1" step="0.1" value="0.9" data-layer="${layerId}" title="Opacity">
                `;
                    legendContainer.appendChild(item);

                    // Toggle visibility
                    item.querySelector('input[type="checkbox"]').addEventListener('change', (e) => {
                        const visible = e.target.checked ? 'visible' : 'none';
                        if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', visible);
                    });

                    // Adjust opacity
                    item.querySelector('input[type="range"]').addEventListener('input', (e) => {
                        const opacity = parseFloat(e.target.value);
                        if (map.getLayer(layerId)) map.setPaintProperty(layerId, 'raster-opacity', opacity);
                    });
                }
            }
        } catch (err) {
            console.error(`Fehler beim Laden von ID ${id}:`, err);
        }
    }
}


async function getIiifImageUrl(manifestUrl, maxSize = 2048) {
    const response = await fetch(manifestUrl);
    const manifest = await response.json();

    // Try to locate the image resource in the IIIF manifest
    const canvas = manifest.sequences?.[0]?.canvases?.[0];
    const resource = canvas?.images?.[0]?.resource;
    const serviceId = resource?.service?.['@id'] || resource?.['@id'];

    if (!serviceId) {
        console.warn('No IIIF service found in manifest:', manifestUrl);
        return null;
    }

    // Detect original file extension from @id or service URL
    const sourceUrl = resource?.['@id'] || '';
    const extMatch = sourceUrl.match(/\.(png|jpg|jpeg|tif|gif)$/i);
    const ext = extMatch ? extMatch[1].toLowerCase() : 'jpg';

    // Use png if available to preserve transparency
    const format = ext === 'png' ? 'png' : 'jpg';

    // Construct IIIF URL with max size constraint and proper format
    const iiifUrl = `${serviceId}/full/!${maxSize},${maxSize}/0/default.${format}`;


    return iiifUrl;
}


function getNormalizedCorners(coords) {
    if (!coords || coords.length < 2) return null;

    const [lat1, lon1] = coords[0];
    const [lat2, lon2] = coords[1];

    const minLat = Math.min(lat1, lat2);
    const maxLat = Math.max(lat1, lat2);
    const minLon = Math.min(lon1, lon2);
    const maxLon = Math.max(lon1, lon2);

    // Top-left, top-right, bottom-right, bottom-left (for MapLibre)
    return [
        [minLon, maxLat],
        [maxLon, maxLat],
        [maxLon, minLat],
        [minLon, minLat]
    ];
}
