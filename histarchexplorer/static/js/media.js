// ======== INITIALIZATION ========
(() =>  {
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

  const images = data.entity.files;
  console.log("Found images:", images.length);

  // Build media grid dynamically
  images.forEach(image => {
    const item = createMediaItem(image);
    item.dataset.renderType = image.render_type || "unknown";
    container.appendChild(item);
  });

  // Initialize Muuri layout
  window.mediaGrid = new Muuri(".grid-media", {
    layout: { fillGaps: true }
  });

  setTimeout(() => window.mediaGrid.refreshItems().layout(), 500);

  // Setup filters
  if (filterBar) {
    initFilterBar(filterBar, images);
  }

  // Setup 3D model spinner handling
  handleModelViewers();

  // Setup Bootstrap popovers
  initPopovers();

  // Setup “More images” button linking
  initMoreImagesButton();
})();



// ======== CREATE MEDIA ITEM ========
function createMediaItem(image) {
  const alt = image.title || "Image";

  const item = document.createElement("div");
  item.className = "item item-half";

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
      imageDiv.appendChild(create3DModel(image, alt));
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

  return item;
}


// ======== HELPERS FOR EACH MEDIA TYPE ========

function create3DModel(image, alt) {
  const wrapper = document.createElement("div");
  wrapper.className = "model-wrapper";
  wrapper.style = "height:300px;position:relative;";
  wrapper.innerHTML = `
    <div class="spinner"></div>
    <model-viewer src="${image.url}" alt="${alt}" camera-controls
      ar ar-modes="webxr scene-viewer quick-look"
      shadow-intensity="1" autoplay
      style="width:100%;height:100%;"></model-viewer>
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
  const link = document.createElement("a");
  link.href = `/render_pdf/${image.id}`;
  link.target = "_blank";
  link.className =
    "hover-max position-absolute bottom-0 end-0 m-2 text-dark bg-white bg-opacity-75 px-2 py-1 rounded";
  link.innerHTML = `<i class="bi bi-filetype-pdf" style="font-size:1.5em;"></i>`;
  wrapper.appendChild(link);

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

// ======== FILTERING ========

function initFilterBar(container, images) {
  // Collect unique render types
  const types = [...new Set(images.map(img => img.render_type || "unknown"))];

  // Add "All" button
  const allBtn = createFilterButton("All", "all", true);
  container.appendChild(allBtn);

  // Add one button per type
  types.forEach(type => {
    const label = type.replace("_", " ");
    container.appendChild(createFilterButton(label, type));
  });

  // Click handling
  container.addEventListener("click", e => {
    const btn = e.target.closest("button[data-filter]");
    if (!btn) return;

    // Update active state
    container.querySelectorAll("button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    const filterType = btn.getAttribute("data-filter");
    if (filterType === "all") {
      window.mediaGrid.filter(() => true);
    } else {
      window.mediaGrid.filter(item => item.getElement().dataset.renderType === filterType);
    }
  });
}

function createFilterButton(label, type, active = false) {
  const btn = document.createElement("button");
  btn.className = `btn btn-sm ${active ? "btn-primary" : "btn-outline-primary"}`;
  btn.textContent = label;
  btn.dataset.filter = type;
  return btn;
}
