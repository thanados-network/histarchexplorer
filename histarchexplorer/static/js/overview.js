window.grid = new Muuri('.grid-muuri', {
    layout: {
        fillGaps: true,
    },
    sortData: {
        type: (item) => item.getElement().getAttribute('data-type')
    }
});

window.grid.sort((a, b) => {
    const order = ['description', 'map', 'image', 'reference'];
    const aType = a.getElement().getAttribute('data-type');
    const bType = b.getElement().getAttribute('data-type');
    return order.indexOf(aType) - order.indexOf(bType);
});

window.grid.layout();
// var grid = new Muuri('.grid', {dragEnabled: true});


//window.onload = function () {
//    setTimeout(() => {
//        window.grid.refreshItems().layout();
//    }, 500);
//};
//
//
//function observeModelSizeChanges() {
//    const ro = new ResizeObserver(() => {
//        if (grid) grid.refreshItems().layout();
//    });
//
//    document.querySelectorAll('model-viewer').forEach(model => {
//        ro.observe(model);
//    });
//}
//
//let resizeTimeout;
//
//window.addEventListener('resize', () => {
//    clearTimeout(resizeTimeout);
//    resizeTimeout = setTimeout(() => {
//        window.grid.refreshItems().layout();
//    }, 300);
//});
//


//3d Model Spinner removal when 3dmodel loaded
document.querySelectorAll('model-viewer').forEach(model => {
    model.addEventListener('poster-dismissed', () => {
        const wrapper = model.closest('.model-wrapper');
        if (wrapper) {
            const spinner = wrapper.querySelector('.spinner');
            if (spinner) spinner.style.display = 'none';
        }
        if (window.grid) {
            window.grid.refreshItems().layout();
        }
    });
});

window.addEventListener('DOMContentLoaded', () => {
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


document.addEventListener('DOMContentLoaded', () => {
    if (window.grid) {
        setTimeout(() => {
            window.grid.refreshItems().layout();
        }, 500);
        window.grid.refreshItems().layout();
    }
});

