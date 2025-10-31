document.addEventListener("DOMContentLoaded", async () => {
  const spinner = document.querySelector(".spinner");
  const iframe = document.getElementById("mainPdf");

  try {
    // Fetch PresentationView JSON
    const viewEntity = await fetchPresentationView(file_id);

    // Extract the PDF file (you said always one file)
    const file_data = viewEntity.files[0];
    if (!file_data) throw new Error("No PDF file found in presentation view");

    // Set the iframe source dynamically
    iframe.src = file_data.url;

    // Hide spinner once loaded
    iframe.addEventListener("load", () => spinner?.remove());
    setTimeout(() => spinner?.remove(), 5000);

  } catch (err) {
    console.error("PDF load error:", err);
    spinner?.remove();
    const container = document.querySelector(".pdf-viewer-wrapper");
    container.innerHTML = `<p class="text-danger">Failed to load PDF.</p>`;
  }
});
