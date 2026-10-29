/**
 * Landing Page Scientific Charts (Chart.js)
 * Visualizes chronological distribution and typology breakdown.
 */

function isDarkMode() {
  const rootTheme = document.documentElement.getAttribute('data-bs-theme');
  return rootTheme === 'dark' || document.body.classList.contains('dark');
}

function getChartThemeColors() {
  const dark = isDarkMode();
  return {
    textColor: dark ? '#cbd5e1' : '#475569',
    gridColor: dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
    primaryColor: '#23cba7',
    primaryColorSoft: dark ? 'rgba(35, 203, 167, 0.45)' : 'rgba(35, 203, 167, 0.75)',
    accentPalette: [
      '#23cba7', '#e83e8c', '#2980b9', '#fddb6d', '#4477AA', '#EE6677'
    ]
  };
}

let chronoChartInstance = null;
let typologyChartInstance = null;

function renderChronologyChart(containerId, data) {
  const canvas = document.getElementById(containerId);
  if (!canvas || !data || data.length === 0) return;

  const colors = getChartThemeColors();
  const labels = data.map(item => item.century);
  const counts = data.map(item => item.count);

  if (chronoChartInstance) {
    chronoChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');
  const densityLabel = canvas.getAttribute('data-label-density') || 'Dating density';
  const entitiesLabel = canvas.getAttribute('data-label-entities') || 'entities';
  chronoChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: densityLabel,
        data: counts,
        backgroundColor: colors.primaryColorSoft,
        borderColor: colors.primaryColor,
        borderWidth: 1.5,
        borderRadius: 5,
        maxBarThickness: 36
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: isDarkMode() ? '#1e293b' : '#ffffff',
          titleColor: isDarkMode() ? '#f8fafc' : '#0f172a',
          bodyColor: isDarkMode() ? '#e2e8f0' : '#334155',
          borderColor: isDarkMode() ? '#334155' : '#cbd5e1',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: context => ` ${context.parsed.y.toLocaleString()} ${entitiesLabel}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: colors.gridColor },
          ticks: { color: colors.textColor, font: { size: 11 } }
        },
        y: {
          grid: { color: colors.gridColor },
          ticks: { color: colors.textColor, font: { size: 11 } }
        }
      }
    }
  });
}

function renderTypologyChart(containerId, siteTypes, artifactTypes, mode = 'sites') {
  const canvas = document.getElementById(containerId);
  if (!canvas) return;

  const dataset = mode === 'sites' ? siteTypes : artifactTypes;
  if (!dataset || dataset.length === 0) return;

  const colors = getChartThemeColors();
  const labels = dataset.map(item => item.name);
  const counts = dataset.map(item => item.count);

  if (typologyChartInstance) {
    typologyChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');
  typologyChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: colors.accentPalette.slice(0, counts.length),
        borderWidth: isDarkMode() ? 2 : 1,
        borderColor: isDarkMode() ? '#0f172a' : '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: colors.textColor,
            boxWidth: 14,
            padding: 12,
            font: { size: 11 }
          }
        },
        tooltip: {
          backgroundColor: isDarkMode() ? '#1e293b' : '#ffffff',
          titleColor: isDarkMode() ? '#f8fafc' : '#0f172a',
          bodyColor: isDarkMode() ? '#e2e8f0' : '#334155',
          borderColor: isDarkMode() ? '#334155' : '#cbd5e1',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: context => ` ${context.label}: ${context.parsed.toLocaleString()}`
          }
        }
      },
      cutout: '62%'
    }
  });
}

function initLandingCharts(stats) {
  if (!stats || typeof Chart === 'undefined') return;

  renderChronologyChart('chronoChartCanvas', stats.chronology);
  renderTypologyChart('typologyChartCanvas', stats.site_types, stats.artifact_types, 'sites');

  const btnSites = document.getElementById('btnShowSiteTypes');
  const btnArtifacts = document.getElementById('btnShowArtifactTypes');

  if (btnSites && btnArtifacts) {
    btnSites.addEventListener('click', () => {
      btnSites.classList.add('active');
      btnArtifacts.classList.remove('active');
      renderTypologyChart('typologyChartCanvas', stats.site_types, stats.artifact_types, 'sites');
    });

    btnArtifacts.addEventListener('click', () => {
      btnArtifacts.classList.add('active');
      btnSites.classList.remove('active');
      renderTypologyChart('typologyChartCanvas', stats.site_types, stats.artifact_types, 'artifacts');
    });
  }

  // Update charts if theme changes
  const observer = new MutationObserver(() => {
    if (chronoChartInstance) {
      renderChronologyChart('chronoChartCanvas', stats.chronology);
    }
    const currentMode = (btnArtifacts && btnArtifacts.classList.contains('active')) ? 'artifacts' : 'sites';
    if (typologyChartInstance) {
      renderTypologyChart('typologyChartCanvas', stats.site_types, stats.artifact_types, currentMode);
    }
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-bs-theme', 'class']
  });
}

window.initLandingCharts = initLandingCharts;
