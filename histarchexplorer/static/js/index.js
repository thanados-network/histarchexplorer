const indexImageContainer = document.getElementById('index-image');
const mapContainer = document.getElementById('map');

if (imgOrMap === 'map') {
    mapContainer.style.display = 'block';
    const map = L.map('map', {
        zoom: 13,
        zoomControl: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        dragging: false,
        tap: false
    }).setView([47.5162, 14.5501], 7);

    chosenMap.addTo(map);
} else {
    indexImageContainer.style.display = 'block';
    indexImageContainer.style.backgroundImage = 'url('+ imgString +')'
}