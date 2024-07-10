function renderMap(selected_map) {
    const default_image = '/../static/images/index_map_bg/Blank_map_of_Europe_central_network.png';
    const mapContainer = document.getElementById('map');
    const indexImageContainer = document.getElementById('index-image');

    if (!selected_map || selected_map === default_image) {
        mapContainer.style.display = 'none';
        indexImageContainer.style.display = 'block';
    } else {
        // Ensure the map container is displayed before initializing the map
        mapContainer.style.display = 'block';
        indexImageContainer.style.display = 'none';

        const map = L.map('map', {
            zoom: 13,
            zoomControl: false,
            scrollWheelZoom: false,
            doubleClickZoom: false,
            dragging: false,
            tap: false
        }).setView([47.5162, 14.5501], 7);

        const chosenMap = L.tileLayer(selected_map);
        chosenMap.addTo(map);

            map.invalidateSize();
    }
}
