let loadedTabs = []

document.getElementById('toggleSidebar').addEventListener('click', function () {
    const nav_sidebar = document.getElementById('nav-sidebar');
    const root = document.documentElement;
    nav_sidebar.classList.toggle('expanded');
    nav_sidebar.classList.toggle('d-none');

    if (nav_sidebar.classList.contains('expanded')) {
        root.style.setProperty('--sidebar-width', '150px');
    } else {
        root.style.setProperty('--sidebar-width', '70px');
    }
});

async function loadHTML(id, tab, index, lastIndex) {
    const response = await fetch(`/getentity/${id}/${tab}`);

    if (response.status === 404) {
        console.error(`Error 404: Content for tab "${tab}" not found.`);

        document.querySelectorAll(`.to-remove-${tab}`).forEach(element => {
            element.remove();
            console.log(`Removed element with class "to-remove-${tab}".`);
        });

        if (index === lastIndex) {
            document.querySelectorAll(".to-remove-spinner").forEach(element => {
                element.remove();
                console.log("Spinner removed.");
            });
        }

        return;
    }

    if (response.status !== 200) {
        console.error(`Unexpected response status: ${response.status}`);
        return;
    }

    document.querySelectorAll(`.to-remove-${tab}`).forEach(element => {
        element.classList.toggle('d-none');
        console.log(`Removed element with class "to-remove-${tab}".`);
    });

    const htmlText = await response.text();
    const targetElement = document.getElementById(`pane-content-${tab}`);

    if (!targetElement) {
        console.error("Target element not found!");
        return;
    }

    // Create a temporary element to parse the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlText;

    // Load stylesheets in order of appearance
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

    await Promise.all(cssPromises); // Ensure all CSS is loaded before scripts

    // Insert HTML content (excluding scripts)
    targetElement.innerHTML = tempDiv.innerHTML;

    // Load scripts sequentially in order of appearance
    const scripts = Array.from(tempDiv.querySelectorAll('script'));

    for (const script of scripts) {
        await loadScript(script);
    }
    loadedTabs.push(tab)
    console.log(`HTML, CSS, and scripts for "${tab}" loaded in correct order!`);
    console.log(loadedTabs)

    if (index === lastIndex) {
            document.querySelectorAll(".to-remove-spinner").forEach(element => {
                element.remove();
                console.log("Spinner removed.");
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
        loadHTML(entityId, tab, index, tabsToLoad.length - 1);
    }
});



