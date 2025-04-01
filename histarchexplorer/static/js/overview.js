
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

document.getElementById("overview-content").innerHTML =
    `
<div><h1>TEST Blabla</h1></div>

 <div class="${entity.description_class}">
    <div class="item-content">
      <div class="muuri-description">
        <span class="tile-label">DESCRIPTION</span>
        <p>${entity.description}</p>
      </div>
    </div>
 </div>

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
`;






