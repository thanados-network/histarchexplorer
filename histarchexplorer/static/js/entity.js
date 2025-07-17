let loadedTabs = []
let notYetClickedTabs = tabsToLoad


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
    if (typeof(grid) !== 'undefined') grid.refreshItems().layout();
}, 300);
});

let loadedCount = 0; // Track completed tab loads

async function loadHTML(id, tab, index, totalTabs) {
    //console.log(id)
    //console.log(tab)

    let urlbase = `/get_entity/${id}/${tab}`
    if (id === 0) urlbase =  `/get_entities/${tab}`
    //console.log(urlbase)

    const response = await fetch(urlbase);

    if (response.status === 404) {
        console.error(`Error 404: Content for tab "${tab}" not found.`);

        document.querySelectorAll(`.to-remove-${tab}`).forEach(element => {
            element.remove();
            //console.log(`Removed element with class "to-remove-${tab}".`);
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
        //console.log(`Removed element with class "to-remove-${tab}".`);
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

    loadedTabs.push(tab);
    //console.log(`HTML, CSS, and scripts for "${tab}" loaded in correct order!`);
    //console.log(loadedTabs);


    loadedCount++; // Increase count when a tab is fully loaded
    checkAndRemoveSpinner(totalTabs);
}

// Function to check if all tabs are loaded and remove the spinner
function checkAndRemoveSpinner(totalTabs) {
    if (loadedCount >= totalTabs) {
        document.querySelectorAll(".to-remove-spinner").forEach(element => {
            element.remove();
            //console.log("Spinner removed.");
        });
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


tabsToLoad.forEach((tab, index) => {
    if (!loadedTabs.includes(tab)) {
        loadHTML(entityId, tab, index, tabsToLoad.length);
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
    root.style.setProperty('--right-sidebar-width', isExpanded ? '600px' : '0px');
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
