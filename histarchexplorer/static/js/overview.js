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

       <div class="item item-half">
       <h1>3</h1>
       <p> Ja, was ist denn das?</p>
       </div>
       
        <div class="item item-half">
       <h1>4</h1>
       <p> Ja, was ist denn das?</p>
       </div>
    </div>
   
       
        <div class="item">
        <h1>2</h1>
        <p> 2. Muuri</p>
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

    const grid = new Muuri(gridElement, { layoutOnResize: true });
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

window.requestAnimationFrame(() => {
    initializeMuuri();


    const mapContainer = document.getElementById('muuri-map');
    if (mapContainer && typeof L !== 'undefined' && gisData) {
        const map = L.map('muuri-map').setView(
            [gisData.coordinates[1], gisData.coordinates[0]], 13
        );

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        L.marker([gisData.coordinates[1], gisData.coordinates[0]]).addTo(map)
            .bindPopup(entityName)
            .openPopup();
    }

}, 100);


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