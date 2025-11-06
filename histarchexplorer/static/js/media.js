// ======== CONFIG: COLORS + ICONS ========
const renderTypeStyles = {
  "all": {color: "#6c757d", icon: "bi-grid-3x3-gap-fill"},
  "3d_model": {color: "#c77dff", icon: "bi-box"},
  "image": {color: "#06d6a0", icon: "bi-image"},
  "video": {color: "#118ab2", icon: "bi-play-btn-fill"},
  "pdf": {color: "#ef476f", icon: "bi-filetype-pdf"},
  "svg": {color: "#ffd166", icon: "bi-filetype-svg"},
  "unknown": {color: "#adb5bd", icon: "bi-question-circle"}
};


// ======== INITIALIZATION ========
(() => {
  const container = document.querySelector(".grid-media");
  const filterBar = document.getElementById("media-filters");
  const data = window.entityData || entityData;

  if (!container) {
    console.warn("No .grid-media container found");
    return;
  }
  if (!data?.entity?.files) {
    console.warn("entityData.entity.files not found");
    return;
  }

  const files = data.entity.files;

  // --- Step 1: Create a map of webp posters by ID ---
  const posterMap = {};
  files
    .filter(f => f.render_type === "webp" && f.title)
    .forEach(f => {
      posterMap[f.title] = f.url;
    });

  // --- Step 2: Filter out webp files from rendering ---
  const visibleFiles = files.filter(f => f.render_type !== "webp");

  // --- Step 3: Build media grid dynamically ---
  visibleFiles.forEach(image => {
    const item = createMediaItem(image, posterMap);
    item.dataset.renderType = image.render_type || "unknown";
    container.appendChild(item);
  });

  // --- Step 4: Initialize Muuri layout ---
window.mediaGrid = new Muuri(".grid-media", {
  layout: {
    fillGaps: true,
    horizontal: false,
    rounding: true
  },
  dragEnabled: false,
  layoutDuration: 300,
  layoutEasing: "ease-out"
});

  setTimeout(() => window.mediaGrid.refreshItems().layout(), 500);

  // --- Step 5: Initialize helpers ---
  if (filterBar) initFilterBar(filterBar, visibleFiles);
  handleModelViewers();
  initPopovers();
  initMoreImagesButton();
})();

// ======== POST-LAYOUT BEAUTIFICATION ========
function styleAndSortMediaTiles() {
  if (!window.mediaGrid) return;

  // Color borders by render type
  document.querySelectorAll(".item-media").forEach(el => {
    const type = el.dataset.renderType || "unknown";
    const color = renderTypeStyles[type]?.color || "#ccc";
    el.style.border = `2px solid ${color}`;
    el.style.borderRadius = "0.5rem";
  });

  // Group/sort tiles by render_type
  window.mediaGrid.sort((a, b) => {
    const typeA = a.getElement().dataset.renderType || "";
    const typeB = b.getElement().dataset.renderType || "";
    return typeA.localeCompare(typeB);
  });

  window.mediaGrid.refreshItems().layout();
}

// Run once Muuri is ready
setTimeout(styleAndSortMediaTiles, 500);

// ======== CREATE MEDIA ITEM ========
function createMediaItem(image, posterMap) {
  const alt = image.title || "Image";

  const item = document.createElement("div");
  item.className = "item item-half item-media";

  const content = document.createElement("div");
  content.className = "item-content item-content-full";
  item.appendChild(content);

  const muuri = document.createElement("div");
  muuri.className = "muuri-images";
  content.appendChild(muuri);

  const imageDiv = document.createElement("div");
  imageDiv.className = "image position-relative";
  muuri.appendChild(imageDiv);

  // --- Media type switch ---
  switch (image.render_type) {
    case "3d_model":
      imageDiv.appendChild(create3DModel(image, alt, posterMap));
      break;
    case "video":
      imageDiv.appendChild(createVideo(image, alt));
      break;
    case "pdf":
      imageDiv.appendChild(createPDF(image, alt));
      break;
    case "image":
      imageDiv.appendChild(createImage(image, alt));
      break;
    case "svg":
      imageDiv.appendChild(createSVG(image, alt));
      break;
    default:
      const fallback = document.createElement("img");
      fallback.src = image.url || "/static/img/placeholder.png";
      fallback.alt = alt;
      imageDiv.appendChild(fallback);
  }

  // --- Info popover ---
  if (image.description || image.license || image.creator || image.license_holder) {
    const caption = document.createElement("div");
    caption.className = "mt-2 text-center small text-muted";
    caption.textContent = image.title || "";

    const popoverId = `popover-content-${image.id}`;
    const hiddenDiv = document.createElement("div");
    hiddenDiv.id = popoverId;
    hiddenDiv.className = "d-none";
    hiddenDiv.innerHTML = `
      ${image.description ? `<div class="mb-2">${image.description}</div>` : ""}
      ${image.license ? `<div><b>License:</b> ${image.license}</div>` : ""}
      ${image.creator ? `<div><b>Creator:</b> ${image.creator}</div>` : ""}
      ${image.license_holder ? `<div><b>License holder:</b> ${image.license_holder}</div>` : ""}
    `;
    caption.appendChild(hiddenDiv);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-light ms-2";
    btn.setAttribute("data-bs-toggle", "popover");
    btn.setAttribute("data-bs-title", image.title || "");
    btn.setAttribute("data-popover-content", `#${popoverId}`);
    btn.innerHTML = `<i class="bi bi-info-circle"></i>`;
    caption.appendChild(btn);

    imageDiv.appendChild(caption);
  }
// --- Add "resize" / full-view button ---
  const viewBtn = document.createElement("button");
  viewBtn.className = "btn btn-sm btn-light position-absolute top-0 end-0 m-2";
  viewBtn.innerHTML = `<i class="bi bi-arrows-fullscreen"></i>`;
  viewBtn.title = "Open full view";

  viewBtn.addEventListener("click", () => {
    const originId = window.entityData?.entity?.id;
    const type = image.render_type;
    let url = `/view/${type}/${image.id}`;

    window.open(url);
  });

  imageDiv.appendChild(viewBtn);

  return item;
}


// ======== HELPERS FOR EACH MEDIA TYPE ========

function create3DModel(image, alt, posterMap = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = "model-wrapper";
  wrapper.style = "height:300px;position:relative;";

  // Match by same file ID
  const poster = posterMap[image.title] || "";
  wrapper.innerHTML = `
    <div class="spinner"></div>
    <model-viewer
      src="${image.url}"
      alt="${alt}"
      ${poster ? `poster="${poster}"` : ""}
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


function createVideo(image) {
  const wrapper = document.createElement("div");
  wrapper.className = "video-wrapper position-relative";
  wrapper.style = "height:300px;overflow:hidden;";
  wrapper.innerHTML = `
    <video class="w-100 h-100 rounded shadow-sm" src="${image.url}" controls preload="metadata">
      Your browser does not support the video tag.
    </video>
    <button class="btn btn-sm btn-light position-absolute top-0 end-0 m-2" type="button">
      <i class="bi bi-arrows-fullscreen"></i>
    </button>
  `;
  wrapper.querySelector("button").addEventListener("click", e => {
    e.currentTarget.previousElementSibling.requestFullscreen();
  });
  return wrapper;
}

function createImage(image, alt) {
  const img = document.createElement("img");
  img.src = image.iiif_base_path
    ? `${image.iiif_base_path}/full/400,/0/default.jpg`
    : image.url;
  img.alt = alt;
  return img;
}

function createPDF(image, alt) {
  const wrapper = document.createElement("div");


  const img = document.createElement("img");
  img.src = `${image.iiif_base_path}/full/400,/0/default.jpg`;
  img.alt = alt;
  wrapper.appendChild(img);
  return wrapper;
}

function createSVG(image) {
  const obj = document.createElement("object");
  obj.type = "image/svg+xml";
  obj.data = image.url;
  obj.className = "w-100 h-100 border-0";
  obj.style.height = "300px";
  return obj;
}


// ======== MUURI + MODEL-VIEWER SUPPORT ========

function handleModelViewers() {
  const observeResize = new ResizeObserver(() => {
    window.mediaGrid?.refreshItems().layout();
  });

  // Wait until <model-viewer> is available
  const init = () => {
    document.querySelectorAll("model-viewer").forEach(model => {
      observeResize.observe(model);
      model.addEventListener("poster-dismissed", () => {
        const spinner = model.closest(".model-wrapper")?.querySelector(".spinner");
        if (spinner) spinner.style.display = "none";
        window.mediaGrid?.refreshItems().layout();
      });
    });
  };

  if (customElements.get("model-viewer")) {
    init();
  } else {
    customElements.whenDefined("model-viewer").then(init);
  }
}


// ======== POPOVER HANDLER ========

function initPopovers() {
  new bootstrap.Popover(document.body, {
    selector: "[data-bs-toggle='popover']",
    html: true,
    container: "body",
    trigger: "focus",
    placement: "top",
    sanitize: false,
    content: function () {
      const sel = this.getAttribute("data-popover-content");
      const node = sel ? document.querySelector(sel) : null;
      return node ? node.innerHTML : "";
    },
    title: function () {
      return this.getAttribute("data-bs-title") || "";
    }
  });
}


// ======== “MORE IMAGES” TAB HANDLER ========

function initMoreImagesButton() {
  document.addEventListener("click", (e) => {
    const btn = e.target.closest('#show-more-images[data-target="#tab-pane-media"]');
    if (!btn) return;

    const tabTrigger = document.querySelector(
      `[data-bs-toggle="tab"][data-bs-target="#tab-pane-media"]`
    );
    if (!tabTrigger) {
      console.warn("No tab trigger found for #tab-pane-media");
      return;
    }

    const tab = new bootstrap.Tab(tabTrigger);
    tab.show();

    setTimeout(() => {
      document.querySelector("#tab-pane-media")?.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }, 300);
  });
}

function initFilterBar(container, images) {
  // Collect unique render types
  const types = [...new Set(images.map(img => img.render_type || "unknown"))];

  // Style the filter bar itself
  container.classList.add("d-flex", "justify-content-center", "flex-wrap", "gap-3", "mb-4");

  // Add "All" button
  const allBtn = createFilterButton("All", "all", true);
  container.appendChild(allBtn);

  // Add one button per type
  types.forEach(type => {
    const label = type.replace("_", " ");
    container.appendChild(createFilterButton(label, type));
  });

  // Handle click filtering
  container.addEventListener("click", e => {
    const btn = e.target.closest("button[data-filter]");
    if (!btn) return;

    // Update active state
    container.querySelectorAll("button").forEach(b => {
      b.classList.remove("active");
      const t = b.dataset.filter;
      const c = renderTypeStyles[t]?.color || "#adb5bd";
      b.style.color = c;
      b.style.background = "transparent";
      b.style.opacity = "0.6";
    });

    btn.classList.add("active");
    const activeColor = renderTypeStyles[btn.dataset.filter]?.color || "#adb5bd";
    btn.style.color = activeColor;
    btn.style.background = "transparent";
    btn.style.opacity = "1";

    const filterType = btn.dataset.filter;
    if (filterType === "all") {
      window.mediaGrid.filter(() => true);
    } else {
      window.mediaGrid.filter(item => item.getElement().dataset.renderType === filterType);
    }
  });
}

function createFilterButton(label, type, active = false) {
  const {color, icon} = renderTypeStyles[type] || renderTypeStyles["unknown"];
  const btn = document.createElement("button");
  btn.className = "btn btn-filter";
  btn.dataset.filter = type;

  // Set up style
  btn.style.background = "transparent";
  btn.style.border = "none";
  btn.style.color = color;
  btn.style.fontSize = "2rem";
  btn.style.lineHeight = "1";
  btn.style.opacity = active ? "1" : "0.6";
  btn.style.transition = "all 0.2s ease";

  // Icon + label
  btn.innerHTML = `
    <i class="bi ${icon}" title="${label}" style="color:${color};"></i>
  `;

  // Hover behavior
  btn.addEventListener("mouseenter", () => {
    btn.style.transform = "scale(1.2)";
    btn.style.opacity = "1";
  });
  btn.addEventListener("mouseleave", () => {
    if (!btn.classList.contains("active")) btn.style.opacity = "0.6";
    btn.style.transform = "scale(1)";
  });

  return btn;
}


