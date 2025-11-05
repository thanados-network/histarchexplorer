/**
 * Creates a Bootstrap modal overlay for media viewers.
 * @param {Object} viewEntity - The PresentationView JSON.
 * @param {Object} file_data - The file object (from viewEntity.files[0]).
 */
function createInfoOverlay(viewEntity, file_data) {
  // Remove any existing modal
  document.getElementById("viewerInfoModal")?.remove();

  // Create modal container
  const modal = document.createElement("div");
  modal.className = "modal fade";
  modal.id = "viewerInfoModal";
  modal.tabIndex = -1;
  modal.setAttribute("aria-labelledby", "viewerInfoLabel");
  modal.setAttribute("aria-hidden", "true");

  // Build modal inner HTML
  const fileHTML = `
    <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="viewerInfoLabel">${file_data.title || "Untitled file"}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <p><strong>Creator:</strong> ${file_data.creator || "Unknown"}</p>
            <p><strong>License:</strong> ${file_data.license || "—"}</p>
            <p><strong>License holder:</strong> ${file_data.license_holder || "—"}</p>
          </div>
          <hr>
          ${buildRelationsSection(viewEntity.relations)}
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  `;
  modal.innerHTML = fileHTML;
  document.body.appendChild(modal);

  // Initialize and show modal
  const bsModal = new bootstrap.Modal(modal, { keyboard: true });
  bsModal.show();
}

/**
 * Builds HTML for the relations section.
 */
function buildRelationsSection(relations) {
  if (!relations || Object.keys(relations).length === 0) {
    return `<p class="text-muted">No related entities available.</p>`;
  }

  let html = `<h4 class="mt-2">Related Entities</h4>`;
  for (const [systemClass, relationList] of Object.entries(relations)) {
    html += `<h5 class="mt-3 text-capitalize">${systemClass.replace(/_/g, " ")}</h5><ul class="list-unstyled">`;

    relationList.forEach(rel => {
      const desc =
        (rel.description?.en || rel.description?.de || rel.description || "")
          .replace(/<\/?[^>]+(>|$)/g, ""); // strip HTML if any
      const truncated = desc.split(/\s+/).slice(0, 100).join(" ");
      const stdType =
        rel.types && rel.types.length
          ? ` (${rel.types[0].title})`
          : "";

      html += `
        <li class="mb-3">
          <a href="/entity/${rel.id}" target="_blank" class="fw-semibold text-decoration-none">
            ${rel.name || "Unnamed Entity"}${stdType}
          </a>
          <p class="text-muted small mt-1">
            ${truncated}${desc.split(/\s+/).length > 100 ? "..." : ""}
          </p>
        </li>
      `;
    });

    html += `</ul>`;
  }

  return html;
}
