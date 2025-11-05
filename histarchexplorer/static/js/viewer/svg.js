document.addEventListener("DOMContentLoaded", async () => {
  const spinner = document.querySelector(".spinner");
  const container = document.getElementById("svgContainer");
  let panZoomInstance;

  try {
    const viewEntity = await fetchPresentationView(file_id);

    const file_data = viewEntity.files[0];

    const response = await fetch(file_data.url);
    container.innerHTML = await response.text();

    const svgEl = container.querySelector("svg");
    svgEl.setAttribute("width", "100%");
    svgEl.setAttribute("height", "100%");
    svgEl.style.maxWidth = "100%";
    svgEl.style.maxHeight = "100%";

    spinner?.remove();

    // 4️⃣ Initialize pan/zoom
    panZoomInstance = svgPanZoom(svgEl, {
      zoomEnabled: true,
      panEnabled: true,
      controlIconsEnabled: false,
      fit: true,
      center: true,
      maxZoom: 20,
      minZoom: 0.5,
      zoomScaleSensitivity: 0.3,
    });

    document.getElementById("btn-zoom-in").addEventListener("click", () => panZoomInstance.zoomIn());
    document.getElementById("btn-zoom-out").addEventListener("click", () => panZoomInstance.zoomOut());
    document.getElementById("btn-reset").addEventListener("click", () => panZoomInstance.reset());
    document.getElementById("btn-download").addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = file_data.url + "?download=true";
      a.download = file_data.title || "graphic.svg";
      a.click();
    });

    // Info button
    document.getElementById("btn-info").addEventListener("click", () => {
      createInfoOverlay(viewEntity, file_data);
    });

  } catch (err) {
    console.error("SVG load error:", err);
    spinner?.remove();
    container.innerHTML = `<p class="text-danger">Failed to load SVG</p>`;
  }
});
