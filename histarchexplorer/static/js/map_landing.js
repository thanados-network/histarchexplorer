var overview_map = L.map('muuri-map', {
    center: [51.505, -0.09],
    zoom: 13,
    zoomControl: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    touchZoom: false,
    boxZoom: false,
    dragging: false,
});

document.getElementById('muuri-map').removeAttribute('tabindex');

L.control.scale().addTo(overview_map);


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(overview_map);

if (gisData) {
    L.geoJSON(gisData).addTo(overview_map);
    overview_map.fitBounds(L.geoJSON(gisData).getBounds(), {
        maxZoom: 13
    });
    var entityGeom = L.geoJSON(gisData, {
        onEachFeature: function (feature, layer) {
            console.log(feature)
            layer.bindPopup('<b>' + entityName + '</b><p><b>' + feature.title + '</b> ' + feature.description + '</p>');
        }
    }).addTo(overview_map);
}

// Expand Map
const expandButton = document.getElementById('expand-button');
const mapContainer = document.querySelector('.map-wrapper');
const muuriMap = document.getElementById('muuri-map');

expandButton.addEventListener('click', event => {
    setTimeout(() => {
        muuriMap.classList.toggle('expanded-map');
        mapContainer.classList.toggle('expanded-map');

        const locationTile = document.querySelector('.map-wrapper').parentElement;
        if (locationTile) {
            locationTile.classList.toggle('item'); // Toggle the 'item' class
        }
        document.querySelectorAll('.item, .item-content').forEach(item => {
            if (!item.contains(muuriMap)) {
                item.classList.toggle('hidden');
            }
        });
        //Expand-Shrink Button
        if (muuriMap.classList.contains('expanded-map')) {
            expandButton.innerHTML = '<i class="bi bi-fullscreen-exit"></i>';
            //Enable map zoom etc
            overview_map.scrollWheelZoom.enable();
            overview_map.doubleClickZoom.enable();
            overview_map.touchZoom.enable();
            overview_map.boxZoom.enable();
            overview_map.dragging.enable();

        } else {
            expandButton.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';

            overview_map.scrollWheelZoom.disable();
            overview_map.doubleClickZoom.disable();
            overview_map.touchZoom.disable();
            overview_map.boxZoom.disable();
            overview_map.dragging.disable();

            //Recenter when returning to small layout
            if (gisData) {
                overview_map.fitBounds(L.geoJSON(gisData).getBounds(), {
                    maxZoom: 13
                });
            }
        }

        // adjust for new size
        overview_map.invalidateSize();
        grid.refreshItems().layout();
    }, 300);


});
