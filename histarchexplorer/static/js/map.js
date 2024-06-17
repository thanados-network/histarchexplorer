document.addEventListener('DOMContentLoaded', function () {
    function initializeMap() {
        var accessToken = 'V2rWGMya8xJMEMpkjnXgkkPXM17NNEk3cNum1RvNUKMU6nspY9Bdi02PSyns93EA';

        // Initialize the map
        var map = L.map('map').setView([47.5162, 14.5501], 6);

        // Define Jawg Light tile layer
        var Jawg_Light = L.tileLayer('https://tile.jawg.io/jawg-light/{z}/{x}/{y}{r}.png?access-token=' + accessToken, {
            attribution: '<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            minZoom: 0,
            maxZoom: 22
        });

        // Add Jawg Light tile layer to the map
        Jawg_Light.addTo(map);
    }
    initializeMap();
});
