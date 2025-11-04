function renderAllBreadcrumbs(entityData, show = true) {
  if (!show || !entityData?.entity || !entityData?.hierarchy?.root) return;

  const entity = entityData.entity;
  const hierarchy = entityData.hierarchy;

  const systemClassMap = {
    "place": "places",
    "feature": "places",
    "stratigraphic_unit": "places",
    "move": "events",
    "acquisition": "events",
    "modification": "events",
    "activity": "events",
    "group": "actors",
    "person": "actors",
    "event": "events",
    "artifact": "items",
    "source": "sources",
    "file": "files"
  };

  // build the breadcrumb markup once
  const nav = document.createElement("nav");
  nav.setAttribute("aria-label", "breadcrumb");
  const ol = document.createElement("ol");
  ol.className = "breadcrumb";
  ol.style.setProperty("--bs-breadcrumb-divider", "''");

  hierarchy.root.forEach(ancestor => {
    const li = document.createElement("li");
    li.className = "breadcrumb-item";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-link p-0 text-decoration-none";
    btn.textContent = ancestor.name;
    btn.addEventListener("click", () => {
      if (typeof loadEntityView === "function") loadEntityView(ancestor.id);
    });

    li.appendChild(btn);
    ol.appendChild(li);
  });

  const activeClass = systemClassMap[entity.system_class?.toLowerCase()] || "";
  const activeLi = document.createElement("li");
  activeLi.className = `breadcrumb-item active breadcrumb-${activeClass}`;
  activeLi.setAttribute("aria-current", "page");
  activeLi.textContent = entity.title;
  ol.appendChild(activeLi);

  nav.appendChild(ol);

  // insert into every .breadcrumbs element found on the page
  document.querySelectorAll(".breadcrumbs").forEach(container => {
    container.innerHTML = "";
    container.appendChild(nav.cloneNode(true));
  });
}

// automatically render on load
document.addEventListener("DOMContentLoaded", () => {
  if (window.entityData) renderAllBreadcrumbs(window.entityData);
});

// optionally re-render when tabs are shown
document.addEventListener("shown.bs.tab", () => {
  if (window.entityData) renderAllBreadcrumbs(window.entityData);
});
