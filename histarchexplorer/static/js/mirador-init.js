document.addEventListener("DOMContentLoaded", function () {
  Mirador.viewer({
    id: 'iiif-viewer',
    windows: [
      {
        manifestId: 'https://example.com/iiif-manifest.json',
        canvasIndex: 0,
      },
    ],
  });
});



