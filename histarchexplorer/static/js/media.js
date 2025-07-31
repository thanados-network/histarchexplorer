document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.grid-media');
  if (!container) return;

  const mediaGrid = new Muuri('.grid-media', {
    layout: {
      fillGaps: true,
    },
    items: '.item-half'
  });

  mediaGrid.refreshItems().layout();
});