// ======== INITIALIZATION ========
(async function initMap() {
    // Wait until both DOM and data are ready
    if (document.readyState === "loading") {
        await new Promise(resolve => document.addEventListener("DOMContentLoaded", resolve));
    }

    const entityData = await window.entityData;

    renderAllBreadcrumbs(entityData);

})();

subunitsToggleView('tile')