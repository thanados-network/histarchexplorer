window.overviewGrid = new Muuri('.grid-muuri', {
    layout: {
        fillGaps: true,
    },
    sortData: {
        type: (item) => item.getElement().getAttribute('data-type')
    }
});

window.overviewGrid.sort((a, b) => {
    const order = ['description', 'map', 'image', 'reference'];
    const aType = a.getElement().getAttribute('data-type');
    const bType = b.getElement().getAttribute('data-type');
    return order.indexOf(aType) - order.indexOf(bType);
});

window.overviewGrid.layout();

window.addEventListener('resize', () => {
    clearTimeout(window.overviewGrid.resizeTimeout);
    window.overviewGrid.resizeTimeout = setTimeout(() => {
        window.overviewGrid.refreshItems().layout();
    }, 300);
});



const observer = new MutationObserver(() => {
  const copyBtn = document.getElementById('copyCitationBtn');
  const citationText = document.getElementById('citationText');

  if (copyBtn && citationText) {
    copyBtn.addEventListener('click', () => {
      const text = citationText.innerText.trim();

      navigator.clipboard.writeText(text)
        .then(() => {
          // Change button text
          copyBtn.innerHTML = '<i class="bi bi-check-circle"></i> Citation copied!';

          // Change button class
          copyBtn.classList.remove('btn-primary');
          copyBtn.classList.add('btn-info');

          // Optional: Revert after 2 seconds
          setTimeout(() => {
            copyBtn.innerHTML = '<i class="bi bi-copy"></i> Copy Citation';
            copyBtn.classList.remove('btn-info');
            copyBtn.classList.add('btn-primary');
          }, 2000);
        })
        .catch(err => {
          console.error('Clipboard copy failed:', err);
        });
    });

    observer.disconnect(); // Stop observing once hooked
  }
});

observer.observe(document.body, { childList: true, subtree: true });

// remove 3D Model spinner, when loaded
document.querySelectorAll('model-viewer').forEach(model => {
    model.addEventListener('poster-dismissed', () => {
        const wrapper = model.closest('.model-wrapper');
        if (wrapper) {
            const spinner = wrapper.querySelector('.spinner');
            if (spinner) spinner.style.display = 'none';
        }
        window.overviewGrid.refreshItems().layout();
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
        window.overviewGrid.refreshItems().layout();
    }, 500);
});


function observeModelSizeChanges() {
    const ro = new ResizeObserver(() => {
        window.overviewGrid.refreshItems().layout();
    });

    document.querySelectorAll('model-viewer').forEach(model => {
        ro.observe(model);
    });
}
