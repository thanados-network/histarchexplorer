// ============================================================
//  OVERVIEW_MEDIA.JS — file/media tiles for Overview grid
// ============================================================
// ============================================================
//  MAIN ENTRY POINT — renderOverviewMediaTiles()
// ============================================================
window.renderOverviewMediaTiles = function (files, allImages, additionalFilesOverview = 0) {
  const grid = document.querySelector(".grid-overview, .grid-muuri");
  if (!grid || !Array.isArray(files) || !files.length) return;

  // main + N additional
  const visibleCount = Math.min(files.length, additionalFilesOverview + 1);

  // total media count (prefer entityData.images if you maintain it)
  const totalCount = (allImages.length ?? files.length);

  const showMore = totalCount > visibleCount;
  files.slice(0, visibleCount).forEach((file, idx) => {
    const tile = createOverviewMediaTile(file);

    // If last visible tile AND more files exist → put button under caption
    if (showMore && idx === visibleCount - 1) {
      const button = createViewMoreButton(totalCount);
      const caption = tile.querySelector(".ov-caption");
      if (caption) {
        const spacer = document.createElement("div");
        spacer.className = "mt-2";
        caption.appendChild(spacer);
        caption.appendChild(button);
      }
    }

    grid.appendChild(tile);
  });
};


// ============================================================
//  TILE CREATION
// ============================================================
function createOverviewMediaTile(file) {
  const alt = file.title || "Media file";
  const item = document.createElement("div");
  item.className = "item item-half item-media";
  item.dataset.renderType = file.render_type || "unknown";

  const content = document.createElement("div");
  content.className = "item-content item-content-full";
  item.appendChild(content);

  const muuri = document.createElement("div");
  muuri.className = "muuri-images";
  content.appendChild(muuri);

  const imageDiv = document.createElement("div");
  imageDiv.className = "image position-relative";
  muuri.appendChild(imageDiv);

  // --- Render by type ---
  switch (file.render_type) {
    case "3d_model":
      imageDiv.appendChild(createModelViewer(file, alt));
      break;
    case "video":
      imageDiv.appendChild(createVideo(file, alt));
      break;
    case "image":
      imageDiv.appendChild(createImage(file, alt));
      break;
    case "svg":
      imageDiv.appendChild(createSVG(file));
      break;
    case "pdf":
      imageDiv.appendChild(createPDF(file, alt));
      break;
    default:
      const fallback = document.createElement("img");
      fallback.src = file.url || "/static/img/placeholder.png";
      fallback.alt = alt;
      imageDiv.appendChild(fallback);
  }


  // --- Optional caption & popover ---
// --- Always render a caption with the title ---
const caption = document.createElement("div");
caption.className = "ov-caption mt-2 text-center small text-muted";
caption.textContent = file.title || "";

// Optional popover bits (only if metadata exists)
if (file.description || file.license || file.creator || file.license_holder) {
  const popoverId = `popover-content-${file.id}`;
  const hiddenDiv = document.createElement("div");
  hiddenDiv.id = popoverId;
  hiddenDiv.className = "d-none";
  hiddenDiv.innerHTML = `
    ${file.description ? `<div class="mb-2">${file.description}</div>` : ""}
    ${file.license ? `<div><b>License:</b> ${file.license}</div>` : ""}
    ${file.creator ? `<div><b>Creator:</b> ${file.creator}</div>` : ""}
    ${file.license_holder ? `<div><b>License holder:</b> ${file.license_holder}</div>` : ""}
  `;
  caption.appendChild(hiddenDiv);

  const infoBtn = document.createElement("button");
  infoBtn.type = "button";
  infoBtn.className = "btn btn-sm btn-light ms-2";
  infoBtn.setAttribute("data-bs-toggle", "popover");
  infoBtn.setAttribute("data-bs-title", file.title || "");
  infoBtn.setAttribute("data-popover-content", `#${popoverId}`);
  infoBtn.innerHTML = `<i class="bi bi-info-circle"></i>`;
  caption.appendChild(infoBtn);
}

// Append caption AFTER the media
muuri.appendChild(caption);

  // --- Resize / full-view button ---
  const viewBtn = document.createElement("button");
  viewBtn.className = "btn btn-sm btn-light position-absolute top-0 end-0 m-2";
  viewBtn.innerHTML = `<i class="bi bi-arrows-fullscreen"></i>`;
  viewBtn.title = "Open full view";
  viewBtn.addEventListener("click", () => {
    const type = file.render_type;
    window.open(`/view/${type}/${file.id}`, "_blank");
  });
  imageDiv.appendChild(viewBtn);

  return item;
}

// ============================================================
//  MEDIA TYPE RENDERERS
// ============================================================
function createModelViewer(file, alt) {
  const wrapper = document.createElement("div");
  wrapper.className = "model-wrapper";
  wrapper.style = "height:300px;position:relative;";
  wrapper.innerHTML = `
      <model-viewer
        src="${file.url}"
        alt="${alt}"
        camera-controls
        ar
        ar-modes="webxr scene-viewer quick-look"
        shadow-intensity="1"
        autoplay
        style="width:100%;height:100%;">
      </model-viewer>
    `;
  return wrapper;
}

function createVideo(file) {
  const wrapper = document.createElement("div");
  wrapper.className = "video-wrapper position-relative";
  wrapper.style = "height:300px;overflow:hidden;";
  wrapper.innerHTML = `
      <video class="w-100 h-100 rounded shadow-sm" src="${file.url}" controls preload="metadata"></video>
    `;
  return wrapper;
}

function createImage(file, alt) {
  const img = document.createElement("img");

  // Primary and fallback URLs
  const primary = file.iiif_base_path
    ? `${file.iiif_base_path}/full/400,/0/default.jpg`
    : file.url;
  const fallback = file.url || "/static/img/placeholder.png";

  img.src = primary;
  img.alt = alt;

  // Catch network or server errors (e.g. 404 / 500)
  img.addEventListener("error", () => {
    console.warn(`⚠️ IIIF image failed, falling back to ${fallback}`);
    if (img.src !== fallback) img.src = fallback;
  });

  return img;
}


function createPDF(file, alt) {
  const wrapper = document.createElement("div");
  const img = document.createElement("img");
  img.src = file.iiif_base_path
    ? `${file.iiif_base_path}/full/400,/0/default.jpg`
    : "/static/img/placeholder.png";
  img.alt = alt;
  wrapper.appendChild(img);
  return wrapper;
}

function createSVG(file) {
  const obj = document.createElement("object");
  obj.type = "image/svg+xml";
  obj.data = file.url;
  obj.className = "w-100 h-100 border-0";
  obj.style.height = "300px";
  return obj;
}

// ============================================================
//  "MORE FILES" BUTTON (overlay)
// ============================================================
function createViewMoreButton(totalCount) {
  const btn = document.createElement("button");
  btn.id = "show-more-images";
  btn.className = "btn btn-more-files d-inline-flex align-items-center gap-2";
  btn.type = "button";
  btn.dataset.target = "#tab-pane-media";
  btn.innerHTML = `<i class="bi bi-images"></i> <span>View all ${totalCount} files</span>`;

  btn.addEventListener("click", () => {
    const tabTrigger = document.querySelector(
      `[data-bs-toggle="tab"][data-bs-target="#tab-pane-media"]`
    );
    if (tabTrigger) {
      new bootstrap.Tab(tabTrigger).show();
      setTimeout(() => {
        document.querySelector("#tab-pane-media")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 300);
    }
  });

  return btn;
}
