document.addEventListener("DOMContentLoaded", async () => {
  try {
    // Fetch PresentationView JSON
    const viewEntity = await fetchPresentationView(file_id);

    // 2Extract IIIF manifest URL
    const manifestUrl = viewEntity.files[0].iiif_manifest;
    if (!manifestUrl) throw new Error("No IIIF manifest found in presentation view");

    // 3Build Mirador configuration dynamically
    const config = {
      id: "iiif-viewer",
      layout: "1x1",
      mainMenuSettings: { show: false },
      workspaceControlPanel: { enabled: false },
      window: {
        allowClose: false,
        defaultSideBarPanel: "info",
        sideBarOpenByDefault: false,
        allowMaximize: false,
        allowTopMenuButton: false,
        defaultView: "single",
        sideBarOpen: true,
      },
      workspace: { type: "mosaic" },
      language: language || "en",
      availableLanguages: {
        de: "Deutsch",
        en: "English",
      },
      windows: [
        { loadedManifest: manifestUrl },
      ],
    };

    // Initialize Mirador viewer
    Mirador.viewer(config);

  } catch (err) {
    console.error("IIIF viewer error:", err);
    const container = document.getElementById("iiif-viewer");
    container.innerHTML = `<p class="text-danger">Failed to load IIIF manifest.</p>`;
  }
});
