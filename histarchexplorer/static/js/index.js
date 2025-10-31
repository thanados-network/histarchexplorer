const indexImageContainer = document.getElementById('index-image');
const mapContainer = document.getElementById('map');

if (imgOrMap === 'map') {
  mapContainer.style.display = 'block';
  const map = new maplibregl.Map({
    container: 'map',
    style: mapStyle,
    center: [14.5501, 47.5162],
    zoom: 7,
    interactive: false
  });

  if (chosenMap) {
    map.on('load', () => {
      map.addSource('chosenMap', {
        type: 'geojson',
        data: chosenMap
      });
      map.addLayer({
        id: 'chosenMapLayer',
        type: 'fill',           // je nach Geometrie: 'line', 'circle', 'fill'
        source: 'chosenMap',
        paint: {
          'fill-color': '#ff0000',
          'fill-opacity': 0.5
        }
      });
    });
  }
} else {
  indexImageContainer.style.display = 'block';
  indexImageContainer.style.backgroundImage = 'url(' + imgString + ')';
}
