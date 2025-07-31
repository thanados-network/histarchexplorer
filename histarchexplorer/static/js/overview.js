const overviewGrid = new Muuri('.grid-muuri', {
    layout: {
        fillGaps: true,
    },
    sortData: {
        type: (item) => item.getElement().getAttribute('data-type')
    }
});

overviewGrid.sort((a, b) => {
    const order = ['description', 'map', 'image', 'reference'];
    const aType = a.getElement().getAttribute('data-type');
    const bType = b.getElement().getAttribute('data-type');
    return order.indexOf(aType) - order.indexOf(bType);
});

overviewGrid.layout();

window.addEventListener('resize', () => {
    clearTimeout(overviewGrid.resizeTimeout);
    overviewGrid.resizeTimeout = setTimeout(() => {
        overviewGrid.refreshItems().layout();
    }, 300);
});

// remove 3D Model spinner, when loaded
document.querySelectorAll('model-viewer').forEach(model => {
    model.addEventListener('poster-dismissed', () => {
        const wrapper = model.closest('.model-wrapper');
        if (wrapper) {
            const spinner = wrapper.querySelector('.spinner');
            if (spinner) spinner.style.display = 'none';
        }
        overviewGrid.refreshItems().layout();
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
        overviewGrid.refreshItems().layout();
    }, 500);
});


function observeModelSizeChanges() {
    const ro = new ResizeObserver(() => {
        overviewGrid.refreshItems().layout();
    });

    document.querySelectorAll('model-viewer').forEach(model => {
        ro.observe(model);
    });
}
