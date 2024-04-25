function setTheme(mode = 'auto') {
    let modeToUse;
    const colorModes = ['light', 'dark']
    const colorStored = colorModes.includes(localStorage.getItem('bs-theme'))

    // Set modeToUse based on the provided mode parameter or localStorage value
    if (colorModes.includes(mode)) {
        modeToUse = mode;
        localStorage.setItem('bs-theme', mode);
    } else {
        // If mode is not provided or invalid, determine mode based on user's system preference or localStorage
        modeToUse = window.matchMedia('(prefers-color-scheme: dark)').matches && !colorStored
            ? 'dark'
            : colorStored
                ? localStorage.getItem('bs-theme')
                : 'light';
    }

    // Apply theme to the root element
    const rootElement = document.documentElement;
    rootElement.setAttribute('data-bs-theme', modeToUse);

    // Hide the current theme's element and show the other one
    const modeNotChosen = modeToUse === 'dark' ? 'light' : 'dark';
    document.getElementById(modeToUse).classList.add('d-none');
    document.getElementById(modeNotChosen).classList.remove('d-none');

    const logo = document.getElementById('logo');
    if (logo) {
        const logoSrc = `/static/images/logos/logo_mode_${modeToUse}.svg`;
        logo.setAttribute('src', logoSrc);
    }
}

// Function to handle system mode change
function systemModeChange() {
    const mode = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    setTheme(mode);
}

// Listen for changes in system color scheme and update the theme accordingly
window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', systemModeChange);

// Set initial theme based on localStorage or system preference
setTheme();

