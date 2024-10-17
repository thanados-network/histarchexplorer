var map = L.map('muuri-map', {
    center: [51.505, -0.09],
    zoom: 13,
    zoomControl: false,
    scrollWheelZoom: false,
    doubleClickZoom: false,
    touchZoom: false,
    boxZoom: false
});

L.control.scale().addTo(map);


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

if (gisData) {
    L.geoJSON(gisData).addTo(map);
    map.fitBounds(L.geoJSON(gisData).getBounds(), {
        maxZoom: 13
    });
    var entityGeom = L.geoJSON(gisData, {
        onEachFeature: function (feature, layer) {
            console.log(feature)
            layer.bindPopup('<b>' + entityName + '</b><p><b>' + feature.title + '</b> ' + feature.description + '</p>');
        }
    }).addTo(map);
}

// Expand Map
const expandButton = document.getElementById('expand-button');
const mapContainer = document.querySelector('.map-wrapper');
//const superMapContainer = document.querySelector('.item-content');
const itemContainer = document.querySelector('.item');
const muuriMap = document.getElementById('muuri-map');

expandButton.addEventListener('click', event => {
    setTimeout(() => {
        muuriMap.classList.toggle('expanded-map');
        mapContainer.classList.toggle('expanded-map');
        //superMapContainer.classList.toggle('expanded-map');
        itemContainer.classList.remove('item');

        // hide other tiles
        document.querySelectorAll('.item, .item-content').forEach(item => {
            if (!item.contains(muuriMap)){
                item.classList.toggle('hidden');
            }
        });

        // adjust for new size
        map.invalidateSize();
        grid.refreshItems().layout();
    }, 300);


});
