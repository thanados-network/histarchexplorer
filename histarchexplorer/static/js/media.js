window.mediaGrid = null;

document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.grid-media');
    if (!container) return;

     window.mediaGrid.refreshItems().layout();

    setTimeout(() => {
        window.mediaGrid.refreshItems().layout();
    }, 700);
});

window.mediaGrid = new Muuri('.grid-media', {
    layout: {
        fillGaps: true,
    }
});

// remove 3D Model spinner, when loaded
document.querySelectorAll('model-viewer').forEach(model => {
    model.addEventListener('poster-dismissed', () => {
        const wrapper = model.closest('.model-wrapper');
        if (wrapper) {
            const spinner = wrapper.querySelector('.spinner');
            if (spinner) spinner.style.display = 'none';
        }
        window.mediaGrid.refreshItems().layout();
    });
});

// DOM loaded, initialize optional models
document.addEventListener('DOMContentLoaded', () => {
    if (customElements.get('model-viewer')) {
        initModelViewers();
        observeModelSizeChanges();
    } else {
        customElements.whenDefined('model-viewer').then(() => {
            initModelViewers();
            observeModelSizeChanges();
        });
    }

    setTimeout(() => {
        window.mediaGrid.refreshItems().layout();
    }, 500);
});


function observeModelSizeChanges() {
    const ro = new ResizeObserver(() => {
        window.mediaGrid.refreshItems().layout();
    });

    document.querySelectorAll('model-viewer').forEach(model => {
        ro.observe(model);
    });
}


// Link for more images
document.addEventListener('click', (e) => {
  const btn = e.target.closest('#show-more-images[data-target="#tab-pane-media"]');
  if (!btn) return;

  // Find the tab trigger that controls #tab-pane-media
  const tabTrigger = document.querySelector(`[data-bs-toggle="tab"][data-bs-target="#tab-pane-media"]`);
  if (!tabTrigger) {
    console.warn('No tab trigger found for #tab-pane-media');
    return;
  }

  // Activate the tab using Bootstrap’s API
  const tab = new bootstrap.Tab(tabTrigger);
  tab.show();

  // Smooth scroll into view once active
  setTimeout(() => {
    document.querySelector('#tab-pane-media')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 300);
});


