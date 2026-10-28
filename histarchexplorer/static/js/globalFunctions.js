
/**
 * Fetches a PresentationView model from the Flask backend.
 * @param {number} id - The entity ID.
 * @returns {Promise<Object>} The JSON response.
 */
async function fetchPresentationView(id) {
  try {
    const response = await fetch(`/presentation-view/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch PresentationView ${id}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching presentation view:", error);
    return null;
  }
}

/**
 * Fetches a entityData from the Flask backend.
 * @param {number} id - The entity ID.
 * @returns {Promise<Object>} The JSON response.
 */
async function fetchEntityData(id) {
  try {
    const response = await fetch(`/entity-data/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch entityData ${id}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching entityData view:", error);
    return null;
  }
}

/**
 * Creates the "IIIF" link button shown in image captions. It opens the same
 * viewer as the full view button on the image.
 * @param {Object} file - The file object (needs `id`).
 * @returns {HTMLAnchorElement} The link element.
 */
function createIiifLink(file) {
  const label = window.overviewTranslations?.openIiifViewer || "Open in IIIF viewer";
  const link = document.createElement("a");
  link.className = "btn btn-sm btn-light ms-2";
  link.href = `/view/image/${file.id}`;
  link.target = "_blank";
  link.rel = "noopener";
  link.title = label;
  link.setAttribute("aria-label", label);
  const icon = document.createElement("img");
  icon.className = "iiif-icon";
  icon.src = "/static/images/icons/iiif.svg";
  icon.alt = "IIIF";
  link.appendChild(icon);
  return link;
}

/**
 * Returns the URL of a large image version for the lightbox.
 * @param {Object} file - The file object (`iiif_base_path` and/or `url`).
 * @returns {string} The image URL.
 */
function getLightboxSrc(file) {
  return file.iiif_base_path
    ? `${file.iiif_base_path}/full/!1600,1600/0/default.jpg`
    : file.url;
}

/**
 * Opens an image in a Bootstrap modal (lightbox) on the current page.
 * The modal is created once and reused.
 * @param {Object} options
 * @param {string} options.src - Image URL.
 * @param {string} [options.fallback] - URL used if `src` fails to load.
 * @param {string} [options.title] - Title shown above the image.
 */
function openImageLightbox({src, fallback = "", title = ""}) {
  let modalEl = document.getElementById("image-lightbox");
  if (!modalEl) {
    modalEl = document.createElement("div");
    modalEl.id = "image-lightbox";
    modalEl.className = "modal fade";
    modalEl.tabIndex = -1;
    modalEl.setAttribute("aria-hidden", "true");
    modalEl.innerHTML = `
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h6 class="modal-title"></h6>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center p-2">
            <img class="image-lightbox-img img-fluid" alt="">
          </div>
        </div>
      </div>`;
    document.body.appendChild(modalEl);
    modalEl.addEventListener("hidden.bs.modal", () => {
      modalEl.querySelector("img").removeAttribute("src");
    });
  }
  const img = modalEl.querySelector("img");
  img.onerror = () => {
    if (fallback && img.src !== new URL(fallback, window.location.href).href) img.src = fallback;
  };
  img.alt = title;
  img.src = src;
  modalEl.querySelector(".modal-title").textContent = title;
  bootstrap.Modal.getOrCreateInstance(modalEl).show();
}

// Buttons rendered by Jinja carry the image data in data-lightbox-* attributes.
document.addEventListener("click", (event) => {
  const btn = event.target.closest("[data-lightbox-src]");
  if (!btn) return;
  openImageLightbox({
    src: btn.dataset.lightboxSrc,
    fallback: btn.dataset.lightboxFallback,
    title: btn.dataset.lightboxTitle
  });
});
