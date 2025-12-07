// ============================================================
//  OVERVIEW.JS — rebuilt with full render functions
// ============================================================

function relayout(delay = 0) {

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
  const currentLang = window.currentLanguage;
  const preferred = [];

  if (currentLang) {
    preferred.push(currentLang);
  }
  if (currentLang !== 'en') {
    preferred.push('en');
  }
  if (currentLang !== 'de' && 'en' !== 'de') {
    preferred.push('de');
  }

  for (const key of preferred) {
    if (descObj[key]) {
      return descObj[key];
    }
  }

  for (const v of Object.values(descObj)) {
    if (v) {
      return v;
    }
  }
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
    const modalHost = h("div", {html: citeButton.modal_html});
    document.body.appendChild(modalHost);
  }
  relayout(50);
}

function renderToolbox(citeButton, refreshButton) {
  const toolbox = document.getElementById("js-entity-toolbox");
  if (!toolbox) return;

  // Clear old content
  toolbox.innerHTML = "";

  // --- Cite button ---
  if (citeButton?.button_html) {
    const citeWrap = document.createElement("div");
    citeWrap.innerHTML = citeButton.button_html;
    toolbox.appendChild(citeWrap);
    if (citeButton.modal_html) {
      const modalHost = document.createElement("div");
      modalHost.innerHTML = citeButton.modal_html;
      document.body.appendChild(modalHost);
    }
  }

  // --- Refresh button ---
  if (refreshButton && typeof refreshButton === "string" && refreshButton.trim() !== "") {
    const refreshWrap = document.createElement("div");
    refreshWrap.innerHTML = refreshButton;
    toolbox.appendChild(refreshWrap);
  }


  toolbox.classList.add("d-flex", "gap-2", "align-items-center", "mb-2");
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
  observer.observe(document.body, {childList: true, subtree: true});
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
    [h("i", {class: "bi bi-diagram-3 me-1"}), h("span", {text: "Subentities"})]
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
  if (text) el.innerHTML = text;
  relayout(10);
}

function renderMapTile(entity) {
  const tile = document.getElementById("tile-map");
  if (!tile) return;
  tile.hidden = false
  if (entity.overviewMap.type === "FeatureCollection") {
    if (entity.overviewMap.features.length === 0) tile.hidden = true
  }
  ;
  relayout(10);
}


function renderAttributes(categorizedTypes) {
  const tile = document.getElementById("tile-attributes");
  const host = document.getElementById("js-attributes");
  if (!tile || !host || !categorizedTypes || !Object.keys(categorizedTypes).length) return;
  host.innerHTML = "";
  Object.entries(categorizedTypes).forEach(([bucket, items]) => {
    const label = h("p", {
      class: "tile-sub-label text-uppercase mt-3",
      html: `${(items?.[0]?.icon || "")} ${capitalizeWords(bucket.replaceAll("_", " "))}`
    });
    host.appendChild(label);
    items.forEach((entry) => {
      const t = entry.type || {};
      const vu = t.value && t.unit ? `: ${t.value} ${t.unit}` : "";
      const badge = h("div", {
          class: "badge custom-badge text-wrap m-1",
          "data-id": t.id || ""
        },
        h("h6", {class: "m-0 text-center", text: `${t.title || ""}${vu}`})
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
  list.append(h('h4', {
    class: "",
    html: `References`
  }))
  entity.references.forEach((ref) => {
    if (!["bibliography", "external_reference"].includes(ref.system_class)) return;
    const isBibl = ref.system_class === "bibliography";
    const icon = isBibl ? "bi-book" : "bi-box-arrow-up-right";
    const name = isBibl
      ? `<a href="/entity/${ref.id}" class="reference-name">${ref.title || ""}</a>`
      : `<a href="${ref.title}" class="reference-name">${(ref.title || "").split("/").slice(0, 3).join("/")}</a>`;
    const li = h("li", {}, h("div", {class: "reference-content"}, [
      h("div", {
        class: "reference-header",
        html: `<i class="bi ${icon}"></i> ${name}`
      }),
      h("p", {
        class: "reference-description",
        text: `${ref.citation || ""} ${(ref.pages || "").replace("##main", "")}`.trim()
      })
    ]));
    list.appendChild(li);
  });
  tile.hidden = false;
  relayout(10);
}

(async function initOverview() {
  // --- Wait until DOM is ready ---
  if (document.readyState === "loading") {
    await new Promise(resolve =>
      document.addEventListener("DOMContentLoaded", resolve));
  }

  // --- Wait for entityData Promise ---
  const data = await window.entityData;
  if (!data) {
    console.error("❌ entityData failed to load for overview");
    return;
  }

  // console.log("✅ Overview tab: entityData ready", data);

  const entity = data.entity || {};
  entity.overviewMap = data.overviewMap || {};
  const categorizedTypes = data.categorizedTypes || {};
  const citeButton = data.citeButton || {};
  const refreshButton = data.refreshButton || {};
  const mainImage = data.mainImage;
  const initialImages = data.initialImage;
  const allImages = (data.images || []).filter(img => img?.from_super_entity === false);
  const additionalFilesOverview = window.additionalFilesOverview || 0;

  const grid = document.querySelector(".grid-overview");
  if (!grid) {
    console.error("Grid container missing!");
    return;
  }

  // === Helper DOM builder ===
  const h = (tag, opts = {}, children = []) => {
    const el = document.createElement(tag);
    Object.entries(opts).forEach(([k, v]) => {
      if (k === "class") el.className = v;
      else if (k === "html") el.innerHTML = v;
      else if (k === "text") el.textContent = v;
      else if (k.startsWith("on") && typeof v === "function")
        el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v);
    });
    (Array.isArray(children) ? children : [children])
      .filter(Boolean)
      .forEach(c => el.appendChild(c));
    return el;
  };

  // === MAIN INFO TILE (Cite + entity card + description) ===
  const infoTile = h("div", {class: "item hierarchy-item"}, [
    // Toolbox container (for cite + refresh)
    h("div", {class: "entity-toolbox", id: "js-entity-toolbox"}),
    (() => {
      const sc = (entity.system_class || "").toLowerCase();
      const section = systemClassMap[sc] || "";
      const isPersonOrGroup = ["group", "person"].includes(sc);
      const cardInner = isPersonOrGroup
        ? `
        <div class="entity-card__icon">
          ${mainImage?.url ? `<img src="${mainImage.url}" alt="${entity.title}"/>` : ""}
        </div>
        <div class="hierarchy-card-label" data-system-class="${sc}">${entity.title || ""}</div>
        <div class="entity-date"><p>${dateTemplate(entity.start, entity.end)}</p></div>
      `
        : `
        <div class="main-entity-ellipse main-entity-ellipse--${section}">
           <!-- <div class="entity-card__icon">
            ${
          ["feature", "stratigraphic unit"].includes(sc)
            ? `<img src="/static/images/entity_icons/place.png" alt="${entity.system_class}">`
            : ["move", "acquisition", "modification", "activity"].includes(sc)
              ? `<img src="/static/images/entity_icons/event.png" alt="${entity.system_class}">`
              : `<img src="/static/images/entity_icons/${sc}.png" alt="${entity.system_class}">`
        }
          </div> -->
          <div class="hierarchy-card-label mb-0">${entity.title || ""}</div>
          <div class="entity-type mb-0">
            ${
          (entity.types || [])
            .filter(t => t?.is_standard)
            .map(t => `<p>${(t.title || "").toUpperCase()}</p>`)
            .join("")
        }
          </div>
          <div class="entity-date">
            ${
          (entity.start || entity.end)
            ? `<p>${dateTemplate(entity.start, entity.end)}</p>`
            : ""
        }
          </div>
        </div>
      `;
      return h("div", {class: "old-entity-card", html: cardInner});
    })(),
    h("div", {
      class: "item-content",
      "data-type": "types",
      id: "tile-attributes"
    }, [
      h("div", {id: "js-attributes"})]),
    h("div", {class: "item-content", "data-type": "description"}, [
      h("div", {class: "muuri-description"}, [
        h("span", {class: "tile-label", text: "DESCRIPTION"}),
        h("p", {id: "js-description"}),
      ]),
    ]),
  ]);
  grid.appendChild(infoTile);

  // === SECONDARY TILES ===
  const imageTile = h("div", {
    class: "item",
    id: "tile-main-image",
    hidden: true
  }, [
    h("div", {class: "item-content item-content-full"}, [
      h("div", {id: "js-main-image"}),
    ]),
  ]);
  const galleryTile = h("div", {
    class: "item item-half",
    id: "tile-initial-images",
    hidden: true
  }, [
    h("div", {class: "item-content item-content-full"}, [
      h("div", {id: "js-initial-images", class: "d-flex flex-wrap gap-2"}),
    ]),
  ]);
  /*  const attrTile = h("div", {
      class: "item item-half",
      id: "tile-attributes",
      hidden: true
    }, [
      h("div", {class: "item-content"}, [h("div", {id: "js-attributes"})]),
    ]);*/
  const mapTile = h("div", {
    class: "item",
    id: "tile-map",
    hidden: true,
    title: "Click to open detailed Map"
  }, [
    h("div", {class: "item-content item-content-full"}, [
      h("div", {id: "muuri-map", href: "/map", style: "height:300px;"}),
    ]),
  ]);
  const refTile = h("div", {
    class: "item item-wide",
    id: "tile-references",
    hidden: true
  }, [
    h("div", {class: "item-content"}, [
      h("ul", {id: "js-references", class: "no-bullets"}),
    ]),
  ]);

  grid.append(mapTile, imageTile, galleryTile, refTile);

  // === RENDER DATA ===
  if (typeof renderToolbox === "function") renderToolbox(citeButton, refreshButton);

  if (typeof wireCitationCopy === "function") wireCitationCopy();
  if (typeof renderHierarchyButtons === "function") renderHierarchyButtons();
  if (typeof renderEntityCard === "function") renderEntityCard(entity, mainImage);
  if (typeof renderDescription === "function") renderDescription(entity);
  if (typeof renderMapTile === "function") renderMapTile(entity);
  if (typeof renderAttributes === "function") renderAttributes(categorizedTypes);
  if (typeof renderReferences === "function") renderReferences(entity);

  // === MEDIA OVERVIEW ===
  let files = [];
  if (mainImage) files.push(mainImage);
  if (Array.isArray(initialImages)) files.push(...initialImages);
  files = (files || []).filter(f => f?.from_super_entity === false);
  if (typeof renderOverviewMediaTiles === "function") {
    renderOverviewMediaTiles(files, allImages, additionalFilesOverview);
  }

  // === MUURI GRID INIT ===
  window.overviewGrid = new Muuri(".grid-overview", {
    layout: {fillGaps: true, horizontal: false, rounding: true},
    layoutDuration: 200,
    layoutEasing: "ease-out",
    dragEnabled: false,
  });

  const refTileHtml = document.getElementById('tile-references');
  const refTileItem = overviewGrid.getItem(refTileHtml);
  overviewGrid.move(refTileItem, overviewGrid.getItems().length - 1);

  setTimeout(() => window.overviewGrid.refreshItems().layout(), 500);
  renderAllBreadcrumbs(data);
})();

