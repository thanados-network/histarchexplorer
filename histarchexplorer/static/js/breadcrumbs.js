function renderAllBreadcrumbs(entityData, show = true) {
  if (!show || !entityData?.entity || !entityData?.hierarchy?.root) {return;}

  const entity = entityData.entity;
  const hierarchy = entityData.hierarchy;

  // Build breadcrumb nav
  const nav = document.createElement("nav");
  nav.setAttribute("aria-label", "breadcrumb");
  const ol = document.createElement("ol");
  ol.className = "breadcrumb";
  ol.style.setProperty("--bs-breadcrumb-divider", "''");

  const li = document.createElement("li");
    li.className = "breadcrumb-item head-breadcrumb";

    const a = document.createElement("a");
    a.className = "text-decoration-none";
    a.textContent = (entity.system_class).toUpperCase().replace('_', ' ') + ':';

    li.appendChild(a);
    ol.appendChild(li);

  // Ancestors: now actual links
  hierarchy.root.forEach(ancestor => {
    const li = document.createElement("li");
    li.className = "breadcrumb-item";

    const a = document.createElement("a");
    a.href = `/entity/${ancestor.id}`;
    a.className = "text-decoration-none";
    a.textContent = ancestor.name;

    li.appendChild(a);
    ol.appendChild(li);
  });

  // Active entity
  const activeClass = systemClassMap[entity.system_class?.toLowerCase()] || "";
  const activeLi = document.createElement("li");
  activeLi.className = `breadcrumb-item active breadcrumb-${activeClass}`;
  activeLi.setAttribute("aria-current", "page");
  activeLi.textContent = entity.title;
  ol.appendChild(activeLi);

  nav.appendChild(ol);

  // Insert into every .breadcrumbs container
  document.querySelectorAll(".breadcrumbs").forEach(container => {
    container.innerHTML = "";
    container.appendChild(nav.cloneNode(true));
  });
}

// Auto render
document.addEventListener("DOMContentLoaded", () => {
  if (window.entityData) renderAllBreadcrumbs(window.entityData);
});

// Re-render on tab change
document.addEventListener("shown.bs.tab", () => {
  if (window.entityData) renderAllBreadcrumbs(window.entityData);
});
