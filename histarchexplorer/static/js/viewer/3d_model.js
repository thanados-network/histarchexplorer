document.addEventListener("DOMContentLoaded", async () => {
  const viewer = document.getElementById("mainModel");
  const spinner = document.querySelector(".spinner");

  try {
    // Fetch PresentationView JSON from API
    const viewEntity = await fetchPresentationView(file_id);

    // Extract the 3D model file (you said always one)
    const file_data = viewEntity.files[0];
    if (!file_data) throw new Error("No 3D model found in presentation view");

    // Set the model URL dynamically
    viewer.src = file_data.url;

    // 4️⃣ Spinner control
    viewer.addEventListener("poster-dismissed", () => spinner?.remove());
    setTimeout(() => spinner?.remove(), 5000);

    // --- Toolbox actions ---
    const btnReset = document.getElementById("btn-reset");
    const btnRotate = document.getElementById("btn-rotate");
    const btnLight = document.getElementById("btn-light");
    const btnBg = document.getElementById("btn-bg");
    const btnDownload = document.getElementById("btn-download");

    // Info button
    document.getElementById("btn-info").addEventListener("click", () => {
      createInfoOverlay(viewEntity, file_data);
    });

    // Reset camera
    btnReset.addEventListener("click", () => {
      viewer.cameraOrbit = "0deg 75deg auto";
    });

    // Toggle auto-rotate
    btnRotate.addEventListener("click", () => {
      viewer.autoRotate = !viewer.autoRotate;
      btnRotate.classList.toggle("active", viewer.autoRotate);
    });

    // Toggle lighting
    let isBright = true;
    btnLight.addEventListener("click", () => {
      isBright = !isBright;
      viewer.shadowIntensity = isBright ? 1 : 0.2;
      viewer.environmentImage = isBright ? "neutral" : "legacy";
      btnLight.innerHTML = isBright
        ? '<i class="bi bi-brightness-high"></i>'
        : '<i class="bi bi-moon"></i>';
    });

    // Toggle background
    let darkMode = false;
    btnBg.addEventListener("click", () => {
      darkMode = !darkMode;
      viewer.style.backgroundColor = darkMode ? "#212529" : "#f8f9fa";
      btnBg.innerHTML = darkMode
        ? '<i class="bi bi-square"></i>'
        : '<i class="bi bi-square-half"></i>';
    });

    // Download model
    btnDownload.addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = file_data.url + "?download=true";
      a.download = file_data.title || "model.glb";
      a.click();
    });

  } catch (err) {
    console.error("3D model load error:", err);
    spinner?.remove();
    const wrapper = document.querySelector(".model-viewer-wrapper");
    wrapper.innerHTML = `<p class="text-danger">Failed to load 3D model.</p>`;
  }
});
