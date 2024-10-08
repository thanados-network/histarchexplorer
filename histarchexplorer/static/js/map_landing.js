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
