console.log("related_entities:", related_entities);

function geometryCollectionToFeatureCollection(geometryCollection) {
    return {
        type: "FeatureCollection",
        features: geometryCollection.geometries.map(geometry => ({
            type: "Feature",
            geometry: {
                type: geometry.type,
                coordinates: geometry.coordinates
            },
            properties: {
                title: geometry.title || '',
                description: geometry.description || ''
            }
        }))
    };
}

const systemClassMap = {
    'place': 'places',
    'feature': 'places',
    'stratigraphic unit': 'places',
    'move': 'events',
    'acquisition': 'events',
    'modification': 'events',
    'activity': 'events',
    'group': 'actors',
    'person': 'actors',
    'event': 'events',
    'artifact': 'items',
    'source': 'sources',
    'file': 'files'
};
/*Icons for Hierarchy */
function getEntityIcon(entity) {
    const systemClass = entity.system_class.toLowerCase();
    if (['feature', 'stratigraphic unit'].includes(systemClass)) {
        return '/static/images/entity_icons/place.png';
    } else if (['move', 'acquisition', 'modification', 'activity'].includes(systemClass)) {
        return '/static/images/entity_icons/event.png';
    } else {
        return `/static/images/entity_icons/${systemClass}.png`;
    }
}


console.log('categorized_types:', categorized_types);

document.getElementById("overview-content").innerHTML =
    `
     <div class="col flex-column grid-muuri">
      <div class="item item-half hierarchy-item">
       ${entity.ancestor_entities && entity.ancestor_entities.length > 0 ? `
        ${entity.ancestor_entities.map(ancestorEntity => `
            <div class="hierarchy-button">
                <button type="button" class="btn btn-whitish rounded-5">
                    <a href="/landing/${ancestorEntity.id}" class="nude-link text-decoration-none">
                        ${ancestorEntity.standard_type.icon} ${ancestorEntity.name}
                    </a>
                </button>
                <div class="hierarchy-line"></div>
            </div>
        `).join('')}
    ` : ''}

    ${entity.system_class && (['group', 'person'].includes(entity.system_class.toLowerCase())) && main_image ? `
        <div class="entity-card__icon">
            <img src="${main_image.url}" alt="${entity.name}" />
        </div>
        <div class="hierarchy-card-label">${entity.name}</div>
    ` : `
        <div class="main-entity-ellipse main-entity-ellipse--${systemClassMap[entity.system_class.toLowerCase()] || ''}">
            <div class="entity-card__icon">
                <img src="${getEntityIcon(entity)}" alt="${entity.system_class}" />
            </div>
            <div class="hierarchy-card-label mb-0">${entity.name}</div>
            <div class="entity-type mb-0">
                ${entity.standard_type ? `<p>${entity.standard_type.label.toUpperCase()}</p>` : ''}
            </div>
            <div class="entity-date">
                <p>${entity.formated_date}</p>
                ${entity.types && entity.types.map(type => type.root === 'Chronology' ? `<p>${type.label || 'No date available'}</p>` : '').join('')}
            </div>
        </div>
    `}

    ${entity.subunits && entity.subunits.length > 0 ? `
        <div class="hierarchy-button">
            <div class="hierarchy-line"></div>
            <button type="button" class="btn btn-whitish rounded-5" disabled>
                <i class="bi bi-diagram-3"></i>
                <span class="nude-link">
                    ${entity.subunits.length} ${entity.subunits.length === 1 ? "Subentity" : "Subentities"}
                </span>
            </button>
        </div>
    ` : ''}
    </div>
    
       <div class="${entity.description_class}">
        <div class="item-content">
          <div class="muuri-description">
            <span class="tile-label">DESCRIPTION</span>
            <p>${entity.description}</p>
          </div>
        </div>
       </div>
   
       ${categorized_types ? `
  <div class="item-half">
    <div class="item-content">
      <span class="tile-label">ATTRIBUTES</span>
      <div class="categorized-types">
        ${Object.entries(categorized_types).map(([label, value]) => `
          <p class="tile-sub-label text-uppercase mt-3">
            ${value[0].icon} ${label}
          </p>
          ${value.map(type => `
            <div class="badge bg-dark-subtle text-wrap m-1">
              <h6 class="m-0 text-center">
                ${type.type.label}
                ${type.type.value && type.type.unit ? `: ${type.type.value} ${type.type.unit}` : ''}
              </h6>
            </div>
          `).join('')}
        `).join('')}
      </div>
    </div>
  </div>
` : ''}
         
       ${entity.geometry ? `
  <div class="item">
    <div class="map-wrapper">
      <div class="item-content item-content-full">
        <div class="location">
          <div id="muuri-map"></div>
          <button id="expand-button" class="btn btn-light btn-sm">
            <i class="bi bi-arrows-fullscreen"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
` : ''}
     
       ${main_image && !['actor', 'person'].includes(entity.system_class.toLowerCase()) ? `
  <div class="item">
    <div class="item-content item-content-full">
      <div class="muuri-images">
        <div class="image">
          ${main_image.iiif_base_path ? `
            <img src="${main_image.iiif_base_path}/full/max/0/default.jpg" alt="${main_image.title}" />
          ` : `
            <img src="${main_image.url}" alt="${main_image.title}" />
          `}
        </div>
      </div>
    </div>
  </div>
` : ''}
     
       ${images && images.length ? `
  ${images.map((depiction, index) => !depiction.main_image ? `
    <div class="${index < 3 ? 'item-half' : 'item'}">
      <div class="item-content item-content-full">
        <div class="image">
          <a href="/view_file/${depiction.id_}">
            <img
              src="${depiction.iiif_base_path 
                      ? `${depiction.iiif_base_path}/full/max/0/default.jpg` 
                      : depiction.url}"
              alt="${depiction.title}"
            />
          </a>
        </div>
      </div>
    </div>
  ` : '').join('')}
` : ''}
       
        <div class="item item-half">
        <h1>2</h1>
        <p> 2. Muuri</p>
       </div>
       
       <div class="item item-half">
       <h1>3</h1>
       <p> Ja, was ist denn das?</p>
       </div>
       
        <div class="item item-half">
       <h1>4</h1>
       <p> Ja, was ist denn das?</p>
       </div>
    
      
      ${entity.relations && entity.relations.length > 0 ? `
  <div class="item item-wide">
    <div class="item-content">
      <div class="muuri-references">
        <p class="tile-label text-uppercase">References</p>
        <ul class="no-bullets">
          ${entity.relations
            .filter(rel => ['bibliography', 'edition', 'external_reference'].includes(rel.relation_system_class))
            .map(rel => {
              const icon = rel.relation_system_class === 'bibliography'
                ? '<i class="bi bi-book"></i>'
                : '<i class="bi bi-box-arrow-up-right"></i>';

              const name = rel.relation_system_class === 'external_reference'
                ? (() => {
                    const parts = rel.label.split('/');
                    return `<a href="${rel.label}" class="reference-name" target="_blank" rel="noopener">${parts.slice(0, 3).join('/')}</a>`;
                  })()
                : `<a href="/entity/${rel.relation_to_id}" class="reference-name">${rel.label}</a>`;

              const description = rel.relation_description
                ? `<p class="reference-description">${rel.relation_description}</p>`
                : '';

              return `
                <li>
                  <div class="reference-content">
                    <div class="reference-header">
                      ${icon}
                      ${name}
                    </div>
                    ${description}
                  </div>
                </li>
              `;
            }).join('')}
        </ul>
      </div>
    </div>
  </div>
` : ''}

       
       ${related_entities ? `
  <div class="item item-wide">
    <div class="item-content">
      <div class="muuri-references">
        <p class="tile-label text-uppercase">References</p>
        <ul class="no-bullets">
          ${Object.entries(related_entities).map(([key, type_]) => 
            (key === "Bibliography" || key === "External reference") ? 
              Object.values(type_).flat().map(item => {
                const icon = key === "Bibliography" 
                  ? '<i class="bi bi-book"></i>'
                  : '<i class="bi bi-box-arrow-up-right"></i>';
                const name = key === "Bibliography"
                  ? `<a href="/entity/${item.id}" class="reference-name">${item.name}</a>`
                  : (() => {
                      const parts = item.name.split('/');
                      return `<a href="${item.name}" class="reference-name">${parts.slice(0, 3).join('/')}</a>`;
                    })();
                const description = `
                  <p class="reference-description">
                    ${item.description || ''}
                    ${(item.relations || []).filter(rel => rel.relation_to_id === entity.id)
                      .map(rel => rel.relation_description).join(' ')}
                  </p>
                `;
                return `
                  <li>
                    <div class="reference-content">
                      <div class="reference-header">
                        ${icon}
                        ${name}
                      </div>
                      ${description}
                    </div>
                  </li>
                `;
              }).join('') : ''
          ).join('')}
        </ul>
      </div>
    </div>
  </div>
` : ''}
</div>
`;

document.addEventListener("DOMContentLoaded", function () {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].forEach(el => new bootstrap.Popover(el, {
        html: true,
        sanitize: false
    }));
});


// Muuri after html injection
function initializeMuuri() {
    const gridElement = document.querySelector('.grid-muuri');
    if (!gridElement) return;

    const grid = new Muuri(gridElement, { layoutOnResize: true,
    layout: { fillGaps: true,
    }});

    window.muuriGrid = grid;

    const container = gridElement.parentElement;
    if (container) {
        new ResizeObserver(forceMuuriLayout).observe(container);
    }

    window.addEventListener('resize', forceMuuriLayout);
}

function forceMuuriLayout() {
    const grid = window.muuriGrid;
    if (grid) {
        grid.synchronize();
        grid.refreshItems();
        grid.layout(true);
    }
}

//Map
window.requestAnimationFrame(() => {
    initializeMuuri();

    const mapContainer = document.getElementById('muuri-map');
    if (mapContainer && typeof L !== 'undefined' && gisData) {
        const map = L.map('muuri-map');

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // convert gisData to GeometryCollection if single geometry point
        const convertedGeometryCollection = (gisData.type === 'GeometryCollection')
            ? gisData
            : {
                type: 'GeometryCollection',
                geometries: [gisData]
            };

        const featureCollection = geometryCollectionToFeatureCollection(convertedGeometryCollection);


        console.log('FeatureCollection:', featureCollection);

        const geoLayer = L.geoJSON(featureCollection, {
            onEachFeature: function (feature, layer) {
                const { title, description } = feature.properties;
                layer.bindPopup(`<b>${entityName}</b><br><b>${title}</b><br>${description}`);
            }
        }).addTo(map);

        const bounds = geoLayer.getBounds();
        if (bounds.isValid()) {
            map.fitBounds(bounds, { maxZoom: 13 });
        }

        setTimeout(() => map.invalidateSize(), 200);
    }
});




function activateTab(tabName, skipPushState = false) {
    const tabElement = document.querySelector(`#tab-${tabName}`);
    if (tabElement) {
        new bootstrap.Tab(tabElement).show();
        if (!skipPushState) {
            const newUrl = `/entity/${entityId}/${tabName}`;
            if (window.location.pathname !== newUrl) {
                history.pushState({tab: tabName}, '', newUrl);
            }
        }
    }
}

const expandButton = document.getElementById('expand-button');
const tabName = 'map';
expandButton.addEventListener('click', event => {
    window.activateTab('map');
});