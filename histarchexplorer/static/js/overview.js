// ============================================================
//  OVERVIEW.JS — rebuilt with full render functions
// ============================================================

function relayout(delay = 0) {
  if (!window.overviewGrid) return;
  setTimeout(() => window.overviewGrid.refreshItems().layout(), delay);
}

// Utility helpers ------------------------------------------------------------
const h = (tag, opts = {}, children = []) => {
  const el = document.createElement(tag);
  Object.entries(opts).forEach(([k, v]) => {
    if (k === 'class') el.className = v;
    else if (k === 'html') el.innerHTML = v;
    else if (k === 'text') el.textContent = v;
    else if (k.startsWith('on') && typeof v === 'function')
      el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  });
  (Array.isArray(children) ? children : [children])
    .filter(Boolean)
    .forEach(c => el.appendChild(c));
  return el;
};

function capitalizeWords(s) {
  return (s || '').replace(/\b\w/g, c => c.toUpperCase());
}
function pickDescription(descObj) {
  if (!descObj) return null;
  const preferred = ['en', 'de'];
  for (const key of preferred) if (descObj[key]) return descObj[key];
  for (const v of Object.values(descObj)) if (v) return v;
  return null;
}

// ---------------------------------------------------------------------------
// RENDERERS
// ---------------------------------------------------------------------------

function renderCite(citeButton) {
  const wrap = document.getElementById("js-cite-button");
  if (!wrap || !citeButton) return;

  wrap.innerHTML = citeButton.button_html || citeButton.html || "";
  if (citeButton.modal_html) {
    const modalHost = h("div", { html: citeButton.modal_html });
    document.body.appendChild(modalHost);
  }
  relayout(50);
}

function wireCitationCopy() {
  const observer = new MutationObserver(() => {
    const copyBtn = document.getElementById("copyCitationBtn");
    const citationText = document.getElementById("citationText");
    if (copyBtn && citationText) {
      copyBtn.addEventListener("click", () => {
        const text = citationText.innerText.trim();
        navigator.clipboard.writeText(text).then(() => {
          copyBtn.innerHTML =
            '<i class="bi bi-check-circle"></i> Citation copied!';
          setTimeout(() => {
            copyBtn.innerHTML =
              '<i class="bi bi-copy"></i> Copy Citation';
          }, 2000);
        });
      });
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

function renderHierarchyButtons() {
  const host = document.getElementById("js-hierarchy-buttons");
  if (!host) return;
  host.innerHTML = "";

  const btn = h(
    "button",
    {
      class: "btn btn-outline-secondary rounded-pill px-3",
      title: "Show subentities",
    },
    [h("i", { class: "bi bi-diagram-3 me-1" }), h("span", { text: "Subentities" })]
  );
  host.appendChild(btn);
  relayout(10);
}

function systemIconPath(systemClass) {
  const cls = (systemClass || "").toLowerCase();
  if (["feature", "stratigraphic unit"].includes(cls))
    return "/static/images/entity_icons/place.png";
  if (["move", "acquisition", "modification", "activity"].includes(cls))
    return "/static/images/entity_icons/event.png";
  return `/static/images/entity_icons/${cls}.png`;
}

function formatTypeTitles(types) {
  if (!Array.isArray(types)) return "";
  return types
    .filter((t) => t?.is_standard)
    .map((t) => t?.title?.toUpperCase())
    .filter(Boolean)
    .join(" · ");
}

function dateTemplate(start, end) {
  if (!start && !end) return "";
  if (start && end) return `${start} – ${end}`;
  return start || end || "";
}

function renderEntityCard(entity, mainImage) {
  const host = document.getElementById("js-entity-card");
  if (!host || !entity) return;

  let avatar = "";
  const sysClass = (entity.system_class || "").toLowerCase();
  if (["group", "person"].includes(sysClass) && mainImage?.url)
    avatar = `<img src="${mainImage.url}" alt="${entity.title}"/>`;
  else
    avatar = `<img src="${systemIconPath(
      entity.system_class
    )}" alt="${entity.system_class}">`;

  const types = formatTypeTitles(entity.types);
  const dateStr = dateTemplate(entity.start, entity.end);

  host.innerHTML = `
    <div class="text-center">
      <div class="entity-card__icon mb-2">${avatar}</div>
      <h5 class="mb-0">${entity.title || ""}</h5>
      ${types ? `<div class="entity-type"><p>${types}</p></div>` : ""}
      ${dateStr ? `<div class="entity-date"><p>${dateStr}</p></div>` : ""}
    </div>`;
  relayout(10);
}

function renderDescription(entity) {
  const el = document.getElementById("js-description");
  if (!el) return;
  const text = pickDescription(entity?.description);
  if (!text) return;
  el.innerHTML = `<p>${text}</p>`;
  relayout(10);
}

function renderMapTile(entity) {
  const tile = document.getElementById("tile-map");
  if (!tile) return;
  if (!entity?.geometries?.length) return;
  tile.hidden = false;
  relayout(10);
}

function imgEl(src, alt = "") {
  const img = new Image();
  img.src = src;
  img.alt = alt;
  img.className = "img-fluid rounded";
  img.addEventListener("load", () => relayout(50));
  return img;
}

function renderModelViewer(url, alt = "") {
  const wrapper = h(
    "div",
    { class: "model-wrapper", style: "height:300px;position:relative;" },
    [
      h("div", { class: "spinner" }),
      h("model-viewer", {
        src: url,
        alt,
        "camera-controls": "",
        ar: "",
        "ar-modes": "webxr scene-viewer quick-look",
        style: "width:100%;height:100%;",
        "shadow-intensity": "1",
        autoplay: "",
      }),
    ]
  );
  wrapper.querySelector("model-viewer").addEventListener("poster-dismissed", () => {
    const spinner = wrapper.querySelector(".spinner");
    if (spinner) spinner.style.display = "none";
    relayout(50);
  });
  return wrapper;
}

function renderFileBlock(file, host) {
  switch (file.render_type) {
    case "3d_model":
      host.appendChild(renderModelViewer(file.url, file.title || "3D Model"));
      break;
    case "video":
      host.appendChild(
        h("video", { controls: "", class: "w-100 rounded", src: file.url })
      );
      break;
    case "pdf":
      host.appendChild(
        h("a", {
          href: file.url,
          target: "_blank",
          class: "btn btn-outline-secondary",
          text: file.title || "Open PDF",
        })
      );
      break;
    default:
      host.appendChild(imgEl(file.url, file.title || "Image"));
  }
}

function renderMainImage(mainImage) {
  const tile = document.getElementById("tile-main-image");
  if (!tile || !mainImage) return;
  const host = document.getElementById("js-main-image");
  host.innerHTML = "";
  renderFileBlock(mainImage, host);
  tile.hidden = false;
  relayout(10);
}

function renderInitialImages(files) {
  const tile = document.getElementById("tile-initial-images");
  if (!tile || !Array.isArray(files) || !files.length) return;
  const host = document.getElementById("js-initial-images");
  host.innerHTML = "";
  files.forEach((f) => {
    const box = h("div", { class: "flex-grow-1", style: "min-width:220px;max-width:48%;" });
    renderFileBlock(f, box);
    host.appendChild(box);
  });
  tile.hidden = false;
  relayout(10);
}

function renderAttributes(categorizedTypes) {
  const tile = document.getElementById("tile-attributes");
  const host = document.getElementById("js-attributes");
  if (!tile || !host || !categorizedTypes || !Object.keys(categorizedTypes).length) return;
  host.innerHTML = "";
  Object.entries(categorizedTypes).forEach(([bucket, items]) => {
    const label = h("p", { class: "tile-sub-label text-uppercase mt-3", html: `${(items?.[0]?.icon || "")} ${capitalizeWords(bucket.replaceAll("_", " "))}` });
    host.appendChild(label);
    items.forEach((entry) => {
      const t = entry.type || {};
      const vu = t.value && t.unit ? `: ${t.value} ${t.unit}` : "";
      const badge = h("div", { class: "badge custom-badge text-wrap m-1" },
        h("h6", { class: "m-0 text-center", text: `${t.title || ""}${vu}` })
      );
      host.appendChild(badge);
    });
  });
  tile.hidden = false;
  relayout(10);
}

function renderReferences(entity) {
  const tile = document.getElementById("tile-references");
  const list = document.getElementById("js-references");
  if (!tile || !list || !Array.isArray(entity?.references) || !entity.references.length) return;
  list.innerHTML = "";
  entity.references.forEach((ref) => {
    if (!["bibliography", "external_reference"].includes(ref.system_class)) return;
    const isBibl = ref.system_class === "bibliography";
    const icon = isBibl ? "bi-book" : "bi-box-arrow-up-right";
    const name = isBibl
      ? `<a href="/entity/${ref.id}" class="reference-name">${ref.title || ""}</a>`
      : `<a href="${ref.title}" class="reference-name">${(ref.title || "").split("/").slice(0, 3).join("/")}</a>`;
    const li = h("li", {}, h("div", { class: "reference-content" }, [
      h("div", { class: "reference-header", html: `<i class="bi ${icon}"></i> ${name}` }),
      h("p", { class: "reference-description", text: `${ref.citation || ""} ${ref.pages || ""}`.trim() })
    ]));
    list.appendChild(li);
  });
  tile.hidden = false;
  relayout(10);
}

// ---------------------------------------------------------------------------
// BOOTSTRAP
// ---------------------------------------------------------------------------
function startOverview() {
  console.log("🚀 Starting overview render");

  const root = window.entityData || {};
  const entity = root.entity || {};
  const categorizedTypes = root.categorizedTypes || {};
  const citeButton = root.citeButton || {};
  const mainImage = entity.main_image || root.mainImage;
  const initialImages = entity.initial_images || root.initialImage;

  const grid = document.querySelector(".grid-muuri");
  if (!grid) {
    console.error("Grid container missing!");
    return;
  }

  // Create tile shells
  const infoTile = h("div", { class: "item main-info-tile" }, [
    h("div", { class: "item-content" }, [
      h("div", { id: "js-cite-button" }),
      h("div", { id: "js-hierarchy-buttons", class: "mt-2" }),
      h("div", { id: "js-entity-card", class: "mt-3" }),
      h("div", { id: "js-description", class: "mt-3 flex-grow-1 overflow-auto small" })
    ]),
  ]);
  grid.appendChild(infoTile);

  const mapTile = h("div", { class: "item", id: "tile-map", hidden: true }, [
    h("div", { class: "item-content item-content-full" }, [
      h("div", { id: "muuri-map", style: "height:300px;" }),
    ]),
  ]);
  const imageTile = h("div", { class: "item", id: "tile-main-image", hidden: true }, [
    h("div", { class: "item-content item-content-full" }, [
      h("div", { id: "js-main-image" }),
    ]),
  ]);
  const galleryTile = h("div", { class: "item", id: "tile-initial-images", hidden: true }, [
    h("div", { class: "item-content item-content-full" }, [
      h("div", { id: "js-initial-images", class: "d-flex flex-wrap gap-2" }),
    ]),
  ]);
  const attrTile = h("div", { class: "item", id: "tile-attributes", hidden: true }, [
    h("div", { class: "item-content" }, [
      h("div", { id: "js-attributes" }),
    ]),
  ]);
  const refTile = h("div", { class: "item", id: "tile-references", hidden: true }, [
    h("div", { class: "item-content" }, [
      h("ul", { id: "js-references", class: "no-bullets" }),
    ]),
  ]);

  grid.append(mapTile, imageTile, galleryTile, attrTile, refTile);

  // Render content
  renderCite(citeButton);
  wireCitationCopy();
  renderHierarchyButtons();
  renderEntityCard(entity, mainImage);
  renderDescription(entity);
  renderMapTile(entity);
  renderMainImage(mainImage);
  renderInitialImages(initialImages);
  renderAttributes(categorizedTypes);
  renderReferences(entity);

  // Layout
  if (window.overviewGrid) window.overviewGrid.refreshItems().layout();
}

if (document.readyState === "loading")
  document.addEventListener("DOMContentLoaded", startOverview);
else requestAnimationFrame(startOverview);
