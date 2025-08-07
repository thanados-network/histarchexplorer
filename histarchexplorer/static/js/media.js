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



