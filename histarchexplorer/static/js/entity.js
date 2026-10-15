let loadedTabs = []
let notYetClickedTabs = tabsToLoad

function initContentPopovers(container) {
    container.querySelectorAll('[data-bs-toggle="popover"]').forEach(trigger => {
        bootstrap.Popover.getOrCreateInstance(trigger, {
            html: true,
            sanitize: false,
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
const loadingTabs = new Set();

function showSidebarTabHeaders(tabs) {
    tabs.forEach(tab => {
        document.querySelectorAll(`li.to-remove-${tab}`).forEach(el => {
            el.classList.remove('d-none');
        });
    });
}

function removeSpinner() {
    document.querySelectorAll(".to-remove-spinner").forEach(element => {
        element.remove();
    });
}

async function loadHTML(id, tab, index, totalTabs) {
    let urlbase = `/get_entity/${id}/${tab}`;
    if (id === 0) urlbase = `/get_entities/${tab}`;

    try {
        const response = await fetch(urlbase);

        if (response.status === 404) {
            console.error(`Error 404: Content for tab "${tab}" not found.`);
            document.querySelectorAll(`.to-remove-${tab}`).forEach(element => {
                element.remove();
            });
            loadedCount++;
            removeSpinner();
            return;
        }

        if (response.status !== 200) {
            console.error(`Unexpected response status: ${response.status}`);
            return;
        }

        document.querySelectorAll(`li.to-remove-${tab}`).forEach(element => {
            element.classList.remove('d-none');
        });
        const pane = document.getElementById(`tab-pane-${tab}`);
        if (pane) pane.classList.remove('d-none');

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
                    resolve();
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

        if (!loadedTabs.includes(tab)) {
            loadedTabs.push(tab);
        }

        loadedCount++;
        removeSpinner();
    } catch (err) {
        console.error(`Error loading HTML for tab ${tab}:`, err);
    }
}

async function ensureTabLoaded(id, tab) {
    if (!tab || loadedTabs.includes(tab) || loadingTabs.has(tab)) {
        return;
    }
    loadingTabs.add(tab);
    try {
        await loadHTML(id, tab, loadedTabs.length, tabsToLoad.length);
    } finally {
        loadingTabs.delete(tab);
    }
}

// Load a script dynamically and wait for it to finish loading
function loadScript(script) {
    return new Promise(resolve => {
        const newScript = document.createElement('script');

        if (script.src) {
            newScript.src = script.src;
            newScript.onload = resolve;
        } else {
            newScript.textContent = script.textContent;
            resolve();
        }

        document.body.appendChild(newScript);
    });
}

if (entityId == 0) {
    showSidebarTabHeaders(tabsToLoad);
    const initialTab = (typeof initialActiveTab !== 'undefined' && initialActiveTab)
        ? initialActiveTab
        : (tabsToLoad[0] || 'places');
    ensureTabLoaded(entityId, initialTab);
} else {
    (async function initIndividualEntityTabs() {
        const data = await window.entityData;
        if (!data) {
            console.error("❌ Failed to load entityData.");
            return;
        }

        if (!data.spatial?.features?.length > 0) {
            tabsToLoad = tabsToLoad.filter(t => t !== 'map');
            document.querySelectorAll('.to-remove-map').forEach(el => el.remove());
        }

        if (data.hierarchy?.subs === 0) {
            tabsToLoad = tabsToLoad.filter(t => t !== 'subunits');
            document.querySelectorAll('.to-remove-subunits').forEach(el => el.remove());
        }

        if (
            !(
                Array.isArray(data.images) &&
                data.images.length > 0 &&
                data.images.some(img => img && img.from_super_entity === false)
            )
        ) {
            tabsToLoad = tabsToLoad.filter(t => t !== 'media');
            document.querySelectorAll('.to-remove-media').forEach(el => el.remove());
        }

        showSidebarTabHeaders(tabsToLoad);
        const initialTab = (typeof initialActiveTab !== 'undefined' && initialActiveTab)
            ? initialActiveTab
            : (tabsToLoad[0] || 'overview');
        ensureTabLoaded(entityId, initialTab);
    })();
}

document.addEventListener('show.bs.tab', function (event) {
    const tabName = event.target.id.replace(/^tab-/, '');
    if (tabName && tabsToLoad.includes(tabName)) {
        ensureTabLoaded(entityId, tabName);
    }
});

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
        return parts.length >= 4 ? parts[3] : 'overview';
    }

    // On page load: set initial state and activate the initial tab.
    const initialTab = getTabNameFromUrl();
    history.replaceState({tab: initialTab}, '', window.location.pathname);
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
                //console.log(gridName)
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
            content: `${tab} Lorem ipsum dolor Lorem ipsum dolor Lorem ipsum dolor Lorem ipsum dolor`,
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
            //console.log(`Tab "${tabName}" should be closed but is open.`);
            toggleRightSidebar(tabName, 'toggle');
        } else if (shouldBeOpen && !isCurrentlyOpen) {
            //console.log(`Tab "${tabName}" should be open but is closed.`);
            toggleRightSidebar(tabName, 'toogle');
        }
    });
});

// Set initial content if tabsToLoad has elements
if (tabsToLoad?.length > 0 && rightSidebarcontent[tabsToLoad[0]]?.content) {
    setRightSidebarContent(rightSidebarcontent[tabsToLoad[0]].content);
}

// ===== Breadcrumbs (global renderer) =====
document.addEventListener("DOMContentLoaded", () => {
    // === Initial render for the first visible tab ===
    if (window.entityData) renderAllBreadcrumbs(window.entityData);

    // === Re-render whenever a Bootstrap tab becomes visible ===
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener("shown.bs.tab", () => {
            if (window.entityData) renderAllBreadcrumbs(window.entityData);
        });
    });

    // === Optional: also re-render when custom events fire (e.g., AJAX reloads) ===
    document.addEventListener("entityUpdated", e => {
        const data = e.detail?.entityData || window.entityData;
        if (data) renderAllBreadcrumbs(data);
    });
});
