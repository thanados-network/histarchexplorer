const _entityPageConfigEl = document.getElementById('entity-page-data');
const _entityPageConfig = _entityPageConfigEl
    ? JSON.parse(_entityPageConfigEl.textContent || '{}')
    : {};

var tabsToLoad = _entityPageConfig.tabsToLoad || [];
var entityId = _entityPageConfig.entityId ?? 0;

if (entityId === 0) {
    window.data = _entityPageConfig.data || {entities: []};
    window.typeTreeData = _entityPageConfig.typeTreeData || {};
    window.viewClasses = _entityPageConfig.viewClasses || {};
    window.getEntitiesForTab = function (tabName) {
        const validClasses = (window.viewClasses && window.viewClasses[tabName]) || [];
        if (!window.data || !Array.isArray(window.data.entities)) return [];
        return window.data.entities.filter(entity => validClasses.includes(entity.class));
    };

    if (Array.isArray(window.data.entities)) {
        window.data.entities.forEach(entity => {
            entity.beginDBP = calculateTimeBP(entity.begin);
            entity.endDBP = calculateTimeBP(entity.end);
            if (entity.begin) entity.beginString = makeLocalDate(entity.begin).localdate;
            if (entity.end) entity.endString = makeLocalDate(entity.end).localdate;

            entity.all = [entity.description, entity.class, entity.type, entity.name]
                .filter(v => v !== null && v !== undefined && v !== '')
                .map(v => String(v).replace(/[\r\n]+/g, ' '))
                .join(' ');
        });
    }
} else {
    const initialEntityData = _entityPageConfig.data || null;
    window.entityData = initialEntityData
        ? Promise.resolve(initialEntityData)
        : fetchEntityData(entityId);
    (async function initializeEntity() {
        const resolvedData = await window.entityData;
        if (!resolvedData) {
            console.error("❌ Failed to load entityData.");
            return;
        }
        window.entityResolved = resolvedData;
        renderAllBreadcrumbs(resolvedData);
        document.dispatchEvent(
            new CustomEvent("entityReady", {detail: resolvedData}));
    })();
}

let loadedTabs = []
let notYetClickedTabs = tabsToLoad
const initialPresetId = new URLSearchParams(window.location.search).get('preset');
let initialPresetApplied = false;

function initContentPopovers(container) {
    container.querySelectorAll('[data-bs-toggle="popover"]').forEach(trigger => {
        bootstrap.Popover.getOrCreateInstance(trigger, {
            html: true,
            trigger: 'click',
            placement: 'bottom',
            container: 'body'});
    });
}

document.getElementById('toggleSidebar').addEventListener('click', function () {
    const nav_sidebar = document.getElementById('nav-sidebar');
    const root = document.documentElement;
    nav_sidebar.classList.toggle('expanded');
    nav_sidebar.classList.toggle('d-none');

    if (nav_sidebar.classList.contains('expanded')) {
        root.style.setProperty('--sidebar-width', '150px');
    } else {
        root.style.setProperty('--sidebar-width', '60px');
    }
    setTimeout(() => {
        if (typeof (grid) !== 'undefined') grid.refreshItems().layout();
    }, 300);
});

let loadedCount = 0; // Track completed tab loads

async function loadHTML(id, tab, index, totalTabs) {

    let urlbase = `/get_entity/${id}/${tab}`
    if (id === 0) urlbase = `/get_entities/${tab}`
    if (id === 0) urlbase = `/get_entities/${tab}`

    const response = await fetch(urlbase);

    if (response.status === 404) {
        console.error(`Error 404: Content for tab "${tab}" not found.`);

        document.querySelectorAll(`.to-remove-${tab}`).forEach(element => {
            element.remove();
        });

        loadedCount++; // Increase count even for missing tabs
        checkAndRemoveSpinner(totalTabs);
        return;
    }

    if (response.status !== 200) {
        console.error(`Unexpected response status: ${response.status}`);
        return;
    }

    document.querySelectorAll(`.to-remove-${tab}`).forEach(element => {
        element.classList.toggle('d-none');
    });

    const htmlText = await response.text();
    const targetElement = document.getElementById(`pane-content-${tab}`);

    if (!targetElement) {
        console.error("Target element not found!");
        return;
    }

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlText;

    const cssPromises = Array.from(tempDiv.querySelectorAll('link[rel="stylesheet"]')).map(link => {
        return new Promise(resolve => {
            if (!document.querySelector(`link[href="${link.href}"]`)) {
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = link.href;
                newLink.onload = resolve;
                document.head.appendChild(newLink);
            } else {
                resolve(); // Already loaded
            }
        });
    });

    await Promise.all(cssPromises);

    targetElement.innerHTML = tempDiv.innerHTML;

    const scripts = Array.from(tempDiv.querySelectorAll('script'));
    if (tab === tabsToLoad[0]) notYetClickedTabs = notYetClickedTabs.filter(item => item !== tab);
    for (const script of scripts) {
        await loadScript(script);
    }

    initContentPopovers(targetElement);

    if (tab === 'catalogue') {
        const cataloguePane = document.getElementById('tab-pane-catalogue');
        if (cataloguePane && cataloguePane.classList.contains('active')) {
            const anchor = `#entity-${entityId}`;
            window.location.href = anchor;
            window.location.hash = anchor;
        }
    }

    loadedTabs.push(tab);


    loadedCount++; // Increase count when a tab is fully loaded
    checkAndRemoveSpinner(totalTabs);
}

// Function to check if all tabs are loaded and remove the spinner
function checkAndRemoveSpinner(totalTabs) {
    if (loadedCount >= totalTabs) {
        document.querySelectorAll(".to-remove-spinner").forEach(element => {
            element.remove();
        });

        if (
            entityId == 0 &&
            initialPresetId &&
            !initialPresetApplied &&
            typeof window.activatePresetById === 'function'
        ) {
            initialPresetApplied = true;
            setTimeout(() => {
                window.activatePresetById(initialPresetId);
            }, 50);
        }

        // In production, background caching for related entities (children, super entities, relations)
        // can be enabled here to pre-warm the cache after the entity view is loaded.
        // if (typeof entityId !== 'undefined' && entityId > 0) {
        //     fetch(`/api/cache-related/${entityId}`);
        // }
    }
}


// Load a script dynamically and wait for it to finish loading
function loadScript(script) {
    if (script.type &&
        script.type !== 'text/javascript' &&
        script.type !== 'application/javascript') {
        return Promise.resolve();
    }
    return new Promise(resolve => {
        const newScript = document.createElement('script');

        if (script.src) {
            newScript.src = script.src;
            newScript.onload = resolve;
            newScript.onerror = resolve;
        } else {
            newScript.textContent = script.textContent;
            resolve();
        }

        document.body.appendChild(newScript);
    });
}

if (entityId == 0) {
    loadedCount = loadedTabs.length;
    if (loadedCount >= tabsToLoad.length) {
        checkAndRemoveSpinner(tabsToLoad.length);
    } else {
        tabsToLoad.forEach((tab, index) => {
            if (!loadedTabs.includes(tab)) {
                loadHTML(entityId, tab, index, tabsToLoad.length);
            }
        });
    }
} else {
    (async function loadTabs() {
        // Wait until the entity data is fetched
        const data = await window.entityData;
        if (!data) {
            console.error("❌ Failed to load entityData.");
            return;
        }

        if (!data.spatial.features.length > 0) tabsToLoad = tabsToLoad.filter(t => t !== 'map');

        if (data.hierarchy.subs === 0) {
            tabsToLoad = tabsToLoad.filter(t => t !== 'subunits');
        }

        if (
            !(
                Array.isArray(data.images) &&
                data.images.length > 0 &&
                data.images.some(img => img && img.from_super_entity === false)
            )
        ) {
            tabsToLoad = tabsToLoad.filter(t => t !== 'media');
        }

        loadedCount = loadedTabs.length;
        if (loadedCount >= tabsToLoad.length) {
            checkAndRemoveSpinner(tabsToLoad.length);
        } else {
            tabsToLoad.forEach((tab, index) => {
                if (!loadedTabs.includes(tab)) {
                    loadHTML(entityId, tab, index, tabsToLoad.length);
                }
            });
        }
    })();
}

document.addEventListener('DOMContentLoaded', function () {
    // Activate a tab by name, optionally skipping pushState (for popstate navigation)
    function activateTab(tabName, skipPushState = false) {
        const tabElement = document.querySelector(`#tab-${tabName}`);
        if (tabElement) {
            // Activate using Bootstrap's Tab API
            new bootstrap.Tab(tabElement).show();
            // Only update history if needed
            if (!skipPushState) {
                let newUrl = `/entity/${entityId}/${tabName}`;
                if (entityId === 0) newUrl = `/entities/${tabName}`;

                if (window.location.pathname !== newUrl) {
                    history.pushState({tab: tabName}, '', newUrl);
                }
            }
        }
    }

    // Extract the tab name from the current URL path.
    function getTabNameFromUrl() {
        const parts = window.location.pathname.split('/');
        if (entityId === 0) {
            return parts.length >= 3 && parts[2]
                ? parts[2]
                : (tabsToLoad[0] || 'places');
        }
        return parts.length >= 4 ? parts[3] : 'overview';
    }

    // On page load: set initial state and activate the initial tab.
    const initialTab = getTabNameFromUrl();
    history.replaceState(
        {tab: initialTab},
        '',
        window.location.pathname + window.location.search);
    activateTab(initialTab, true);

    // Listen for tab changes on any element with data-bs-toggle="tab"
    const tabElements = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabElements.forEach(function (el) {
        el.addEventListener('shown.bs.tab', function (event) {
            const tabName = event.target.id.replace('tab-', '');
            // Only push state if we're really switching tabs.
            if (!history.state || history.state.tab !== tabName) {
                let newUrl = `/entity/${entityId}/${tabName}`;
                if (entityId === 0) newUrl = `/entities/${tabName}`;
                history.pushState({tab: tabName}, '', newUrl);
            }


            setTimeout(() => {
                const gridName = `${tabName}Grid`;
                if (window[gridName]) {
                    window[gridName].refreshItems().layout();
                }
            }, 500);

        });
    });

    // Listen for popstate (back/forward navigation)
    window.addEventListener('popstate', function (event) {
        if (event.state && event.state.tab) {
            activateTab(event.state.tab, true);
        } else {
            // Fallback: if no state, parse the URL.
            const tabName = getTabNameFromUrl();
            activateTab(tabName, true);
        }
    });
});

let rightSidebarcontent = {};

// Initialize rightSidebarcontent if tabsToLoad is defined and is an array
if (Array.isArray(tabsToLoad)) {
    tabsToLoad.forEach(tab => {
        rightSidebarcontent[tab] = {
            content: '',
            opened: false
        };
    });
}

// Function to update sidebar content
function setRightSidebarContent(content) {
    const rightSidebar = document.getElementById('right-sidebar');
    if (rightSidebar) {
        rightSidebar.innerHTML = content;
    } else {
        console.warn("Right sidebar element not found.");
    }
}

// Toggle sidebar state
function toggleRightSidebar(currentTab, mode = 'toggle') {
    const rightSidebar = document.getElementById('right-sidebar');
    const root = document.documentElement;

    if (!rightSidebar || !rightSidebarcontent[currentTab]) return;

    let isExpanded = rightSidebar.classList.contains('right-expanded');

    if (mode === 'open') {
        isExpanded = true;
        rightSidebar.classList.add('right-expanded');
    } else if (mode === 'close') {
        isExpanded = false;
        rightSidebar.classList.remove('right-expanded');
    } else {
        isExpanded = !isExpanded;
        rightSidebar.classList.toggle('right-expanded');
    }

    rightSidebarcontent[currentTab].opened = isExpanded;
    // Keep a user-resized width across open/close within the same session.
    if (isExpanded) {
        const stored = root.style.getPropertyValue('--right-sidebar-width').trim();
        const width = (stored && stored !== '0px') ? stored : '33vw';
        root.style.setProperty('--right-sidebar-width', width);
    } else {
        root.style.setProperty('--right-sidebar-width', '0px');
    }
}

// Attach event listeners to sidebar buttons
document.querySelectorAll('#nav-sidebar .nav-link').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.id.replace('tab-', ''); // Extract tab name
        const rightSidebar = document.getElementById('right-sidebar');
        const root = document.documentElement;

        if (!rightSidebarcontent[tabName]) {
            console.warn(`No content found for tab: ${tabName}`);
            return;
        }

        setRightSidebarContent(rightSidebarcontent[tabName].content);

        // Restored map content needs its popovers/carousels re-wired.
        if (tabName === 'map' && typeof window.initMapSidebarFeatures === 'function') {
            window.initMapSidebarFeatures(rightSidebar);
        }

        // Ensure sidebar state is consistent with the clicked tab
        const shouldBeOpen = rightSidebarcontent[tabName].opened;
        const isCurrentlyOpen = rightSidebar.classList.contains('right-expanded');

        if (!shouldBeOpen && isCurrentlyOpen) {
            toggleRightSidebar(tabName, 'toggle');
        } else if (shouldBeOpen && !isCurrentlyOpen) {
            toggleRightSidebar(tabName, 'toggle');
        }
    });
});

// Set initial content if tabsToLoad has elements
if (tabsToLoad?.length > 0 && rightSidebarcontent[tabsToLoad[0]]?.content) {
    setRightSidebarContent(rightSidebarcontent[tabsToLoad[0]].content);
}

// ===== Breadcrumbs (global renderer) =====
document.addEventListener("DOMContentLoaded", () => {
    const initialData = window.entityResolved || window.entityData;
    if (initialData) renderAllBreadcrumbs(initialData);

    // === Re-render whenever a Bootstrap tab becomes visible ===
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener("shown.bs.tab", () => {
            const currentData = window.entityResolved || window.entityData;
            if (currentData) renderAllBreadcrumbs(currentData);
        });
    });

    // === Optional: also re-render when custom events fire (e.g., AJAX reloads) ===
    document.addEventListener("entityUpdated", e => {
        const updatedData = e.detail?.entityData || window.entityResolved || window.entityData;
        if (updatedData) renderAllBreadcrumbs(updatedData);
    });
});

document.addEventListener('shown.bs.tab', function (event) {
    const tab = event.target;
    const scrollTarget = tab.getAttribute('data-scroll-target');
    if (!scrollTarget) {
        window.location.hash = '';
        return;
    }
    const targetAnchor = '#' + scrollTarget;
    setTimeout(() => { window.location.href = targetAnchor; }, 500);
});
