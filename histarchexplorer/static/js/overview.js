let grid = new Muuri('.grid-muuri', {
    layout: {
        fillGaps: true,
    }
});

// var grid = new Muuri('.grid', {dragEnabled: true});


window.onload = function () {
    setTimeout(() => {
        grid.refreshItems().layout();
    }, 500);
};

// Wait for DOM and model-viewer
window.addEventListener('DOMContentLoaded', () => {
    if (customElements.get('model-viewer')) {
        initMuuri();
    } else {
        customElements.whenDefined('model-viewer').then(() => {
            initMuuri();
        });
    }
});

function observeModelSizeChanges() {
  const ro = new ResizeObserver(() => {
    if (grid) grid.refreshItems().layout();
  });

  document.querySelectorAll('model-viewer').forEach(model => {
    ro.observe(model);
  });
}

let resizeTimeout;

window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        grid.refreshItems().layout();
    }, 300);
});

console.log("overview.js geladen");
//3d Model Spinner removal when 3dmodel loaded
document.querySelectorAll('model-viewer').forEach(model => {
    model.addEventListener('poster-dismissed', () => {
        console.log('Poster dismissed, Modell geladen.');
        const wrapper = model.closest('.model-wrapper');
        if (wrapper) {
            const spinner = wrapper.querySelector('.spinner');
            if (spinner) spinner.style.display = 'none';
        }
    });
});

window.addEventListener('DOMContentLoaded', () => {
  console.log("overview.js geladen");

  if (customElements.get('model-viewer')) {
    initModelViewers();
    initMuuri();
    observeModelSizeChanges();
  } else {
    customElements.whenDefined('model-viewer').then(() => {
      initModelViewers();
      initMuuri();
      observeModelSizeChanges();
    });
  }
});