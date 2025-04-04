let grid = new Muuri('.grid-overview');

// var grid = new Muuri('.grid', {dragEnabled: true});


window.onload = function () {
    setTimeout(() => {
        grid.refreshItems().layout();
    }, 500);
};

window.addEventListener('resize', () => {
    grid.refreshItems().layout();
});
