function setTheme(mode = 'auto') {
  const userMode = localStorage.getItem('bs-theme');
  const sysMode = window.matchMedia('(prefers-color-scheme: light)').matches;
  const useSystem = mode === 'system' || (!userMode && mode === 'auto');
  const modeChosen = useSystem ? 'system' : ['dark', 'light'].includes(mode) ? mode : userMode;

  if (useSystem) {
    localStorage.removeItem('bs-theme');
  } else {
    localStorage.setItem('bs-theme', modeChosen);
  }

  const rootElement = document.documentElement;
  rootElement.setAttribute('data-bs-theme', useSystem ? (sysMode ? 'light' : 'dark') : modeChosen);

  const modeNotChosen = modeChosen === 'dark' ? 'light' : 'dark';
  document.getElementById(modeChosen).classList.add('d-none');
  document.getElementById(modeNotChosen).classList.remove('d-none');
}

setTheme();

window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => setTheme());
