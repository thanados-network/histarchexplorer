function toggleFields(form, enabled) {
  const fields = form.querySelectorAll('input:not([type="hidden"]), textarea, select');

  fields.forEach(field => {
    if (enabled) {
      field.dataset.originalValue = field.value;
      field.removeAttribute('disabled');
      if (field.hasAttribute('data-required-field')) {
        field.setAttribute('required', 'required');
      }
    } else {
      field.value = field.dataset.originalValue;
      field.setAttribute('disabled', 'disabled');
      field.removeAttribute('required');
      field.classList.remove('is-invalid');
      field.classList.remove('is-valid');
    }
  });
}

function toggleButtons(entryId, isEditing) {
  ['edit', 'delete', 'save', 'cancel'].forEach(action => {
    const button = document.getElementById(`${action}${entryId}`);
    if (button) {
      button.classList.toggle(
        'd-none',
        action === 'edit' || action === 'delete' ? isEditing : !isEditing
      );
    }
  });
}

function toggleMapButtons(mapId, isEditing) {
  ['editMap', 'deleteMap', 'saveMap', 'cancelMap'].forEach(action => {
    const button = document.getElementById(`${action}${mapId}`);
    if (button) {
      button.classList.toggle(
        'd-none',
        action === 'editMap' || action === 'deleteMap' ? isEditing : !isEditing
      );
    }
  });
}

function changeEdit(entryId, enabled) {
  const form = document.getElementById(`form${entryId}`);
  if (form) {
    toggleFields(form, enabled);
    toggleButtons(entryId, enabled);
    if (enabled) {
      form.classList.remove('was-validated');
    }
  }
}

function editMap(mapId, enabled) {
  const form = document.getElementById(`mapForm${mapId}`);
  if (form) {
    toggleFields(form, enabled);
    toggleMapButtons(mapId, enabled);
    if (enabled) {
      form.classList.remove('was-validated');
    }
  }
}

function addMap() {
  const modalElement = document.getElementById('addMapModal');
  if (modalElement) {
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
  }
}

function addEntry(category) {
  const currentTabInput = document.getElementById('currentTab');
  if (currentTabInput) {
    currentTabInput.value = category.replace('nav-', '');

    // Hide all modal category field containers first
    document.querySelectorAll('.modal-category-fields').forEach(el => {
      el.style.display = 'none';
      // Disable all inputs within hidden categories to prevent sending irrelevant data
      el.querySelectorAll('input, textarea, select').forEach(input => {
        input.disabled = true;
      });
    });

    // Show only the container for the selected category and enable its inputs
    const selectedCategoryDiv = document.getElementById(`modal-fields-${category}`);
    if (selectedCategoryDiv) {
      selectedCategoryDiv.style.display = 'block';
      selectedCategoryDiv.querySelectorAll('input, textarea, select').forEach(input => {
        input.disabled = false;
      });
    }

    const modalElement = document.getElementById('addEntryModal');
    if (modalElement) {
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
    }
  }
}

(() => {
  'use strict';

  const forms = document.querySelectorAll('.needs-validation');

  forms.forEach(form => {
    form.addEventListener('submit', event => {
      const saveButton = form.querySelector('button[type="submit"]');
      if (saveButton && !saveButton.classList.contains('d-none') && form.id !== 'caseStudyForm') {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      } else if (form.id !== 'caseStudyForm') {
        event.preventDefault();
        event.stopPropagation();
      }
    });
  });

  const caseStudyForm = document.getElementById('caseStudyForm');
  const caseStudyInputField = document.getElementById('caseStudyHierarchyID');
  const caseStudyIDFeedback = document.getElementById('caseStudyIDFeedback');
  const caseStudyTypeNameSpan = document.getElementById('caseStudyTypeName');

  function updateCaseStudyTypeName(name) {
    if (caseStudyTypeNameSpan) {
      caseStudyTypeNameSpan.textContent = name ? `(${name})` : '';
    }
  }

  function clearCaseStudyIDValidation() {
    if (caseStudyInputField) {
      caseStudyInputField.classList.remove('is-invalid');
      caseStudyInputField.classList.remove('is-valid');
    }
    if (caseStudyForm) {
      caseStudyForm.classList.remove('was-validated');
    }
    if (caseStudyIDFeedback) {
      caseStudyIDFeedback.textContent = 'Please enter a positive integer for the Case Study Hierarchy ID.';
    }
  }

  if (caseStudyInputField) {
    caseStudyInputField.addEventListener('input', async () => {
      const inputValue = caseStudyInputField.value.trim();
      clearCaseStudyIDValidation();

      if (inputValue === '') {
        updateCaseStudyTypeName('');
        return;
      }

      const parsedValue = parseInt(inputValue, 10);

      if (isNaN(parsedValue) || parsedValue <= 0) {
        caseStudyInputField.classList.add('is-invalid');
        if (caseStudyIDFeedback) {
          caseStudyIDFeedback.textContent = 'Please enter a positive integer.';
        }
        updateCaseStudyTypeName('');
        return;
      }

      try {
        const response = await fetch(`/admin/check_case_study_id_ajax/${parsedValue}`);
        const data = await response.json();

        if (data.is_valid) {
          caseStudyInputField.classList.add('is-valid');
          updateCaseStudyTypeName(data.name);
        } else {
          caseStudyInputField.classList.add('is-invalid');
          if (caseStudyIDFeedback) {
            caseStudyIDFeedback.textContent = data.name ?
              `ID ${parsedValue} (${data.name}) is not of type "type".` :
              `ID ${parsedValue} not found or is not of type "type".`;
          }
          updateCaseStudyTypeName('');
        }
      } catch (error) {
        console.error('Error checking Case Study ID:', error);
        caseStudyInputField.classList.add('is-invalid');
        if (caseStudyIDFeedback) {
          caseStudyIDFeedback.textContent = 'An error occurred while validating the ID. Please try again.';
        }
        updateCaseStudyTypeName('');
      }
    });
  }


  if (caseStudyForm) {
    caseStudyForm.addEventListener('submit', async function (event) {
      event.preventDefault();

      const inputValue = caseStudyInputField.value.trim();
      const actionTemplate = caseStudyForm.dataset.actionTemplate;

      clearCaseStudyIDValidation();

      const parsedValue = parseInt(inputValue, 10);

      if (inputValue === '' || isNaN(parsedValue) || parsedValue <= 0) {
        caseStudyInputField.classList.add('is-invalid');
        if (caseStudyIDFeedback) {
          caseStudyIDFeedback.textContent = 'Please enter a positive integer.';
        }
        caseStudyForm.classList.add('was-validated');
        event.stopPropagation();
        return;
      }

      try {
        const validationResponse = await fetch(`/admin/check_case_study_id_ajax/${parsedValue}`);
        const validationData = await validationResponse.json();

        if (validationData.is_valid) {
          const finalActionUrl = actionTemplate + parsedValue;
          const formData = new FormData(this);

          const submitResponse = await fetch(finalActionUrl, {
            method: 'POST',
            body: formData
          });

          if (submitResponse.ok) {
            // Server will redirect on success, so we just force a page reload
            // to ensure flash messages are displayed.
            window.location.href = '/admin';
          } else {
            // This handles HTTP errors (e.g., 400, 500) from the POST request
            console.error('Form submission failed with HTTP status:', submitResponse.status, submitResponse.statusText);
            const errorText = await submitResponse.text();
            console.error('Server response:', errorText);

            caseStudyInputField.classList.add('is-invalid');
            if (caseStudyIDFeedback) {
              caseStudyIDFeedback.textContent = `Failed to save ID. Server responded with ${submitResponse.status}.`;
            }
            caseStudyForm.classList.add('was-validated');
          }

        } else {
          caseStudyInputField.classList.add('is-invalid');
          if (caseStudyIDFeedback) {
            caseStudyIDFeedback.textContent = validationData.name ?
              `ID ${parsedValue} (${validationData.name}) is not of type "type".` :
              `ID ${parsedValue} not found or is not of type "type".`;
          }
          caseStudyForm.classList.add('was-validated');
          event.stopPropagation();
        }
      } catch (error) {
        console.error('Error during final Case Study ID validation or submission:', error);
        caseStudyInputField.classList.add('is-invalid');
        if (caseStudyIDFeedback) {
          caseStudyIDFeedback.textContent = 'An error occurred during validation/submission. Please try again.';
        }
        caseStudyForm.classList.add('was-validated');
        event.stopPropagation();
      }
    });
  }
})();

document.getElementById('resetButton')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to reset the settings?')) {
    window.location.href = '/reset';
  }
});

document.getElementById('clearCacheButton')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to clear the cache?')) {
    window.location.href = '/admin/clear-cache';
  }
});


document.getElementById('warmEntityCache')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to warm entity cache? This will take some time.')) {
    window.location.href = '/admin/warm-entity-cache';
  }
});

document.getElementById('refreshEntityCache')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to refresh the whole entity cache? This will take some time.')) {
    window.location.href = '/admin/refresh-entity-cache';
  }
});

document.getElementById('refreshSystemCache')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to refresh the system cache?')) {
    window.location.href = '/admin/refresh-system-cache';
  }
});

document.getElementById('logoutButton')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to logout?')) {
    window.location.href = '/logout';
  }
});


function deleteEntry(id, name, tab) {
  const deleteName = document.getElementById('deleteName');
  if (deleteName) {
    deleteName.textContent = name;
  }

  const confirmedDelete = document.getElementById('confirmedDelete');
  if (confirmedDelete) {
    confirmedDelete.href = `/admin/delete_entry/${id}/${tab}`;
  }
  const myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
  myModal.show();
}

function deleteMap(id, name) {
  const deleteName = document.getElementById('deleteName');
  if (deleteName) {
    deleteName.textContent = name;
  }

  const confirmedDelete = document.getElementById('confirmedDelete');
  if (confirmedDelete) {
    confirmedDelete.href = `/admin/delete_map/${id}`;
  }
  const myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
  myModal.show();
}


function deleteLink(linkId, startName, configProperty, endName, tab, entry) {
  const deleteName = document.getElementById('deleteName');
  if (deleteName) {
    deleteName.textContent = `${startName} - ${configProperty} - ${endName} ?`;
  }

  const confirmedDelete = document.getElementById('confirmedDelete');
  if (confirmedDelete) {
    confirmedDelete.href = `/admin/delete_link/${linkId}/${tab}/${entry}`;
  }

  const myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
  myModal.show();
}


const connectionSelects = document.querySelectorAll('.connection-select');

connectionSelects.forEach(selectConnection => {
  selectConnection.addEventListener('change', () => {
    const isEnabled = selectConnection.selectedIndex !== 0;

    if (selectConnection.nextElementSibling) {
      selectConnection.nextElementSibling.disabled = !isEnabled;
      if (selectConnection.nextElementSibling.classList.contains('link-target')) {
        selectConnection.nextElementSibling.selectedIndex = 0;
        const roleSelect = selectConnection.nextElementSibling.nextElementSibling;
        if (roleSelect) {
          roleSelect.disabled = true;
          roleSelect.selectedIndex = 0;
        }
        const saveButton = selectConnection.parentNode.querySelector('button:last-child');
        if (saveButton) {
          saveButton.disabled = true;
        }
      }
      if (selectConnection.nextElementSibling.classList.contains('link-role')) {
        selectConnection.nextElementSibling.selectedIndex = 0;
        const saveButton = selectConnection.parentNode.querySelector('button:last-child');
        if (saveButton) {
          saveButton.disabled = !isEnabled;
        }
      }
    } else {
      const saveButton = selectConnection.parentNode.querySelector('button:last-child');
      if (saveButton) {
        saveButton.disabled = !isEnabled;
      }
    }


    const saveButton = selectConnection.parentNode.querySelector('button:last-child');
    const optionData = selectConnection.options[selectConnection.selectedIndex];

    setSaveValues(selectConnection.classList, saveButton, optionData, selectConnection);
  });
});

function setSaveValues(classList, saveButton, info, thisElement) {
  const {value} = info;

  if (classList.contains('link-type')) {
    saveButton.dataset.domain = info.getAttribute('data-entry');
    saveButton.dataset.direction = info.getAttribute('data-direction');
    saveButton.dataset.property = value;

    const selectNode = thisElement.nextElementSibling;
    const configClassToShow = `config-class-${info.getAttribute('data-range')}`;

    Array.from(selectNode.options).forEach((option, i) => {
      option.classList.toggle('d-none', !(option.classList.contains(configClassToShow) || i === 0));
    });
  }

  if (classList.contains('link-target')) {
    saveButton.dataset.range = value;
  }

  if (classList.contains('link-role')) {
    saveButton.dataset.role = value;
  }
}


function saveLinkValues(button) {
  let domain = button.dataset.domain;
  let range = button.dataset.range;

  if (!domain || !range || !button.dataset.property || !button.dataset.role) {
    alert('Please select a connection type, target node, and role.');
    return;
  }

  if (button.dataset.direction !== 'direct') {
    [domain, range] = [range, domain];
  }

  const {property, role, tab, entry} = button.dataset;

  const params = new URLSearchParams({
    domain,
    range,
    property,
    role,
    tab,
    entry
  });

  window.location.href = `/admin/add_link/?${params.toString()}`;
}


const accordionContainer = document.getElementById('mapsAccordion');
if (accordionContainer) {
  new Sortable(accordionContainer, {
    animation: 150,
    handle: '.accordion-button',
    onEnd: function (evt) {
      const items = Array.from(accordionContainer.getElementsByClassName('accordion-item'));
      items.forEach((item, index) => {
        item.setAttribute("data-order", index + 1);
      });

      const sortedItems = items.map(item => ({
        order: item.getAttribute("data-order"),
        id: item.getAttribute("data-id")
      }));
      saveSortOrder(sortedItems, 'maps');
    }
  });
}


const sortableDivs = Array.from(document.getElementsByClassName('link-divs'));

sortableDivs.forEach((item) => {
  makeSortables(item);
});

function makeSortables(containerDiv) {
  new Sortable(containerDiv, {
    animation: 150,
    handle: '.d-flex',
    onEnd: function (evt) {
      const items = Array.from(containerDiv.getElementsByClassName('d-flex'));
      items.forEach((item, index) => {
        item.setAttribute("data-order", index + 1);
      });

      const sortedItems = items.map(item => ({
        order: item.getAttribute("data-order"),
        id: item.getAttribute("data-id")
      }));
      saveSortOrder(sortedItems, 'links');
    }
  });
}

function saveSortOrder(items, table) {
  fetch('/sortlinks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({criteria: items, table: table}),
  })
    .then(response => {
      if (!response.ok) {
        console.error('Failed to save sort order:', response.statusText);
      }
    })
    .catch(error => {
      console.error('Error saving sort order:', error);
    });
}


document.addEventListener('DOMContentLoaded', function () {
  let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})
