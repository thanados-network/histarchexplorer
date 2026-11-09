function toggleFields(form, enabled) {
  const fields = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
  const imageButtons = form.querySelectorAll('.select-image-btn');

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

  imageButtons.forEach(btn => {
    if (enabled) {
      btn.removeAttribute('disabled');
    } else {
      btn.setAttribute('disabled', 'disabled');
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

function switchFieldLanguage(fieldKey, entityId, langCode, btn) {
  const capitalizedField = fieldKey.charAt(0).toUpperCase() + fieldKey.slice(1);
  const inputs = document.querySelectorAll(`.lang-input-${fieldKey}-${entityId}`);
  
  inputs.forEach(input => {
    const inputLang = input.dataset.lang;
    const isTarget = (inputLang === langCode);
    const targetInputId = input.id;
    
    // Handle TinyMCE if applicable
    if (input.classList.contains('js-richtext-rich') && typeof tinymce !== 'undefined') {
      const editor = tinymce.get(targetInputId);
      if (editor) {
        const container = editor.getContainer();
        if (container) {
          container.style.display = isTarget ? '' : 'none';
          if (isTarget) {
            if (editor.mode && typeof editor.mode.set === 'function') {
              editor.mode.set('design');
            } else if (typeof editor.setMode === 'function') {
              editor.setMode('design');
            }
            editor.focus();
          }
        }
      } else {
        input.classList.toggle('d-none', !isTarget);
      }
    } else {
      input.classList.toggle('d-none', !isTarget);
    }
    
    // Handle required attribute
    if (input.hasAttribute('data-required-field')) {
      if (isTarget) {
        input.setAttribute('required', 'required');
      } else {
        input.removeAttribute('required');
      }
    }
  });

  // Update button colors
  const buttons = document.querySelectorAll(`.lang-switch-btn-${fieldKey}-${entityId}`);
  buttons.forEach(button => {
    button.classList.remove('btn-primary', 'active', 'btn-success', 'btn-danger');

    const targetLang = button.dataset.lang;
    const targetInputId = `Input${capitalizedField}${entityId}_${targetLang}`;
    const targetInput = document.getElementById(targetInputId);
    
    let hasValue = false;
    if (targetInput) {
      if (targetInput.classList.contains('js-richtext-rich') && typeof tinymce !== 'undefined') {
        const editor = tinymce.get(targetInputId);
        if (editor) {
          hasValue = editor.getContent({format: 'text'}).trim() !== '';
        } else {
          hasValue = targetInput.value.trim() !== '';
        }
      } else {
        hasValue = targetInput.value.trim() !== '';
      }
    }

    if (targetLang === langCode) {
      button.classList.add('btn-primary', 'active');
    } else {
      button.classList.add(hasValue ? 'btn-success' : 'btn-danger');
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

// --- Rich text helpers ---
function initRichText(containerId) {
  if (typeof tinymce === 'undefined') {
    return;
  }

  const container = document.getElementById(containerId);
  if (!container) return;
  
  const textareas = container.querySelectorAll('.js-richtext-rich:not([disabled])');

  textareas.forEach(textarea => {
    const id = textarea.id;

    const editor = tinymce.get(id);
    if (editor) {
      if (editor.mode && typeof editor.mode.set === 'function') {
        editor.mode.set('design');
      } else if (typeof editor.setMode === 'function') {
        editor.setMode('design');
      }
      return;
    }

    tinymce.init({
      target: textarea,
      license_key: 'gpl',
      menubar: false,
      branding: false,
      height: 300,
      plugins: 'link lists image table code',
      toolbar: 'undo redo | blocks | bold italic underline strikethrough | ' +
        'superscript subscript | alignleft aligncenter alignright alignjustify | ' +
        'bullist numlist | table link image | removeformat code',
      convert_urls: false,
      default_link_target: '_blank',
      rel_list: [{title: 'No referrer', value: 'noreferrer noopener'}],
      image_advtab: true,
      paste_as_text: false,
      setup: function (editor) {
        editor.on('init', function () {
          if (textarea.classList.contains('d-none')) {
            const container = editor.getContainer();
            if (container) {
              container.style.display = 'none';
            }
          }
          if (editor.mode && typeof editor.mode.set === 'function') {
            editor.mode.set('design');
          } else if (typeof editor.setMode === 'function') {
            editor.setMode('design');
          }
          if (!textarea.classList.contains('d-none')) {
            editor.focus();
          }
        });
        editor.on('change keyup', function () {
          editor.save();
        });
      }
    });
  });
}

function destroyRichText(containerId) {
  if (typeof tinymce === 'undefined') {
    return;
  }

  const container = document.getElementById(containerId);
  if (!container) return;
  
  const textareas = container.querySelectorAll('.js-richtext-rich');

  textareas.forEach(textarea => {
    const id = textarea.id;
    const editor = tinymce.get(id);
    if (editor) {
      editor.save();
      editor.remove();
    }
  });
}


function changeEdit(entryId, enabled) {
  const formId = `form${entryId}`;
  const form = document.getElementById(formId);
  if (form) {
    if (!enabled) {
      destroyRichText(formId);
    }

    toggleFields(form, enabled);
    toggleButtons(entryId, enabled);

    if (enabled) {
      // Initialize richtext editor when user enters edit mode
      initRichText(formId);
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

let addEntryModalInstance = null;
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
      if (!addEntryModalInstance) {
        addEntryModalInstance = new bootstrap.Modal(modalElement);
      }
      addEntryModalInstance.show();
    }
  }
}

(() => {
  'use strict';

  const forms = document.querySelectorAll('.needs-validation');

  forms.forEach(form => {
    form.addEventListener('submit', event => {
      // Sync TinyMCE editors -> textareas
      if (typeof tinymce !== 'undefined') {
        tinymce.triggerSave();
      }

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

function submitPostAction(url, params = {}) {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = url;

  const csrfToken =
    document.querySelector('meta[name="csrf-token"]')?.content || '';
  if (csrfToken) {
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);
  }

  Object.entries(params).forEach(([key, value]) => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = key;
    input.value = value;
    form.appendChild(input);
  });

  document.body.appendChild(form);
  form.submit();
}

document.getElementById('resetButton')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to reset the settings?')) {
    submitPostAction('/reset');
  }
});

document.getElementById('clearCacheButton')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to clear the cache?')) {
    submitPostAction('/admin/clear-cache');
  }
});


document.getElementById('warmEntityCache')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to warm entity cache? This will take some time.')) {
    submitPostAction('/admin/warm-entity-cache');
  }
});

document.getElementById('refreshStaleEntities')?.addEventListener('click', function () {
  if (confirm('Refetch all entities older than the maximum age? This will take some time.')) {
    submitPostAction('/admin/refresh-stale-entities');
  }
});

document.getElementById('refreshEntityCache')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to refresh the whole entity cache? This will take some time.')) {
    submitPostAction('/admin/refresh-entity-cache');
  }
});

document.getElementById('refreshSystemCache')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to refresh the system cache?')) {
    submitPostAction('/admin/refresh-system-cache');
  }
});

document.getElementById('logoutButton')?.addEventListener('click', function () {
  if (confirm('Are you sure you want to logout?')) {
    window.location.href = '/logout';
  }
});


// --- Image Selector Modal logic ---
const imageSelectorModal = document.getElementById('imageSelectorModal');
if (imageSelectorModal) {
  // Global listener for select-image buttons to open modal programmatically
  // This avoids Bootstrap's default behavior of closing other modals when data-bs-toggle is used
  document.addEventListener('click', function (event) {
    const btn = event.target.closest('.select-image-btn');
    if (btn && !btn.hasAttribute('disabled')) {
      const modalInstance = bootstrap.Modal.getOrCreateInstance(imageSelectorModal);
      modalInstance.show(btn);
      event.preventDefault();
      event.stopPropagation();
    }
  });

  imageSelectorModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const targetInput = button.getAttribute('data-target-input');
    const targetPreview = button.getAttribute('data-target-preview');
    const targetFilename = button.getAttribute('data-target-filename');
    const imageType = button.getAttribute('data-image-type') || 'logo';

    this.setAttribute('data-target-input', targetInput);
    this.setAttribute('data-target-preview', targetPreview);
    this.setAttribute('data-target-filename', targetFilename);

    // Switch grids based on type
    const logoGrid = document.getElementById('logoSelectorGrid');
    const teamGrid = document.getElementById('teamSelectorGrid');
    const assetGrid = document.getElementById('assetSelectorGrid');
    if (logoGrid && teamGrid && assetGrid) {
      logoGrid.classList.toggle('d-none', imageType !== 'logo');
      teamGrid.classList.toggle('d-none', imageType !== 'team');
      assetGrid.classList.toggle('d-none', imageType !== 'asset');
    }

    // Highlight currently selected image
    const currentInput = document.querySelector(targetInput);
    const currentValue = currentInput ? currentInput.value : '';
    this.querySelectorAll('.image-option').forEach(option => {
      const isSelected = option.getAttribute('data-value') === currentValue;
      option.classList.toggle('border-primary', isSelected);
      option.classList.toggle('bg-primary', isSelected);
      option.classList.toggle('bg-opacity-10', isSelected);
    });
  });
}

function selectImageOption(element, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  const modal = document.getElementById('imageSelectorModal');
  const targetInputSelector = modal.getAttribute('data-target-input');
  const targetPreviewSelector = modal.getAttribute('data-target-preview');
  const targetFilenameSelector = modal.getAttribute('data-target-filename');

  const value = element.getAttribute('data-value');
  const filename = element.getAttribute('data-filename') || 'None';

  const targetInput = document.querySelector(targetInputSelector);
  if (targetInput) targetInput.value = value;

  const targetPreview = document.querySelector(targetPreviewSelector);
  if (targetPreview) {
    if (value) {
      targetPreview.src = value;
      targetPreview.classList.remove('d-none');
      const placeholder = document.getElementById('placeholder-' + targetPreview.id.replace('preview-', ''));
      if (placeholder) placeholder.classList.add('d-none');
    } else {
      targetPreview.src = '';
      targetPreview.classList.add('d-none');
      const placeholder = document.getElementById('placeholder-' + targetPreview.id.replace('preview-', ''));
      if (placeholder) placeholder.classList.remove('d-none');
    }
  }

  const targetFilename = document.querySelector(targetFilenameSelector);
  if (targetFilename) {
    targetFilename.textContent = filename === 'None' ? 'No image selected' : filename;
  }

  const modalInstance = bootstrap.Modal.getInstance(modal);
  if (modalInstance) modalInstance.hide();
}

// --- Initialize Rich Text for Add Entry Modal ---
const addEntryModal = document.getElementById('addEntryModal');
if (addEntryModal) {
  addEntryModal.addEventListener('shown.bs.modal', function (event) {
    if (event.target !== addEntryModal) return;
    initRichText('addEntryModal');
  });
  addEntryModal.addEventListener('hide.bs.modal', function (event) {
    if (event.target !== addEntryModal) return;
    destroyRichText('addEntryModal');
  });
}

// Global listener to fix body class when multiple modals are used
document.addEventListener('hidden.bs.modal', function () {
  if (document.querySelectorAll('.modal.show').length > 0) {
    document.body.classList.add('modal-open');
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

document.getElementById('confirmedDelete')?.addEventListener('click', event => {
  const targetUrl = event.currentTarget.getAttribute('href');
  if (targetUrl && targetUrl !== '#') {
    event.preventDefault();
    submitPostAction(targetUrl);
  }
});


const connectionSelects = document.querySelectorAll('.connection-select');

connectionSelects.forEach(selectConnection => {
  selectConnection.addEventListener('change', () => {
    const isEnabled = selectConnection.selectedIndex !== 0;
    const row = selectConnection.closest('.row');
    const targetSelect = row.querySelector('.link-target');
    const roleSelect = row.querySelector('.link-role');
    const saveButton = row.querySelector('button');

    if (selectConnection.classList.contains('link-type')) {
      if (targetSelect) {
        targetSelect.disabled = !isEnabled;
        targetSelect.selectedIndex = 0;
      }
      if (roleSelect) {
        roleSelect.disabled = true;
        roleSelect.selectedIndex = 0;
      }
      if (saveButton) {
        saveButton.disabled = true;
      }
    } else if (selectConnection.classList.contains('link-target')) {
      if (roleSelect) {
        roleSelect.disabled = !isEnabled;
        roleSelect.selectedIndex = 0;
      }
      if (saveButton) {
        saveButton.disabled = true;
      }
    } else if (selectConnection.classList.contains('link-role')) {
      if (saveButton) {
        saveButton.disabled = !isEnabled;
      }
    }

    const optionData = selectConnection.options[selectConnection.selectedIndex];
    setSaveValues(selectConnection.classList, saveButton, optionData, selectConnection);
  });
});

function setSaveValues(classList, saveButton, info, thisElement) {
  if (!saveButton || !info) {
    return;
  }
  const {value} = info;
  const row = thisElement.closest('.row');

  if (classList.contains('link-type')) {
    saveButton.dataset.domain = info.getAttribute('data-entry');
    saveButton.dataset.direction = info.getAttribute('data-direction');
    saveButton.dataset.property = value;

    const selectNode = row.querySelector('.link-target');
    if (selectNode) {
      const configClassToShow = `config-class-${info.getAttribute('data-range')}`;
      Array.from(selectNode.options).forEach((option, i) => {
        option.classList.toggle('d-none', !(option.classList.contains(configClassToShow) || i === 0));
      });
    }
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

  submitPostAction('/admin/add_link/', {
    domain,
    range,
    property,
    role,
    tab,
    entry
  });
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
    handle: '.connected-link-drag-handle',
    draggable: '.connected-link-item',
    onEnd: function (evt) {
      const items = Array.from(
        containerDiv.getElementsByClassName('connected-link-item'));
      items.forEach((item, index) => {
        item.setAttribute("data-order", index + 1);
      });

      const sortedItems = items.map(item => ({
        order: item.getAttribute("data-order"),
        id: item.getAttribute("data-id")
      }));
      if (sortedItems.length) {
        saveSortOrder(sortedItems, 'links');
      }
    }
  });
}

function saveSortOrder(items, table) {
  const csrfToken =
    document.querySelector('meta[name="csrf-token"]')?.content || '';
  fetch('/sortlinks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
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


function updateColorPreview(color) {
  const preview = document.getElementById('new-color-preview');
  if (!preview) return;
  const isValid = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
  preview.style.backgroundColor = isValid ? color : 'transparent';
}

function toggleIconType(id) {
  const typeSelect = document.getElementById(`icon_type_${id}`);
  const cssContainer = document.getElementById(`css_container_${id}`);
  const imgContainer = document.getElementById(`img_container_${id}`);
  const cssInput = document.getElementById(`css_input_${id}`);
  const imgSelect = document.getElementById(`img_select_${id}`);
  const previewContainer = document.getElementById(`preview_container_${id}`);
  if (!typeSelect) return;

  if (typeSelect.value === 'css') {
    cssContainer.classList.remove('d-none');
    imgContainer.classList.add('d-none');
    cssInput.setAttribute('name', `icon_value_${id}`);
    imgSelect.removeAttribute('name');
    updatePreview(id);
  } else if (typeSelect.value === 'img') {
    cssContainer.classList.add('d-none');
    imgContainer.classList.remove('d-none');
    imgSelect.setAttribute('name', `icon_value_${id}`);
    cssInput.removeAttribute('name');
    updatePreview(id);
  } else {
    cssContainer.classList.add('d-none');
    imgContainer.classList.add('d-none');
    cssInput.removeAttribute('name');
    imgSelect.removeAttribute('name');
    if (previewContainer) previewContainer.replaceChildren();
  }
}

function updatePreview(id) {
  const typeSelect = document.getElementById(`icon_type_${id}`);
  const previewContainer = document.getElementById(`preview_container_${id}`);
  if (!typeSelect || !previewContainer) return;

  previewContainer.replaceChildren();
  if (typeSelect.value === 'css') {
    const cssInput = document.getElementById(`css_input_${id}`);
    const val = cssInput ? cssInput.value.trim() : '';
    if (val) {
      let classes = val;
      if (!val.startsWith('bi ') && !val.split(' ').includes('bi')) {
        classes = 'bi ' + val;
      }
      const span = document.createElement('span');
      span.className = 'fs-4';
      const iconEl = document.createElement('i');
      iconEl.className = classes;
      span.appendChild(iconEl);
      previewContainer.appendChild(span);
    }
  } else if (typeSelect.value === 'img') {
    const imgSelect = document.getElementById(`img_select_${id}`);
    const selectedOpt = imgSelect ? imgSelect.selectedOptions[0] : null;
    const iconUrl = selectedOpt ? selectedOpt.dataset.url : '';
    if (iconUrl) {
      const imgEl = document.createElement('img');
      imgEl.src = iconUrl;
      imgEl.className = 'w-100 h-100 object-fit-contain';
      imgEl.alt = 'preview';
      previewContainer.appendChild(imgEl);
    }
  }
}

function addDivision() {
  const container = document.getElementById('type-divisions-container');
  const tpl = document.getElementById('type-division-icon-options');
  if (!container || !tpl) return;

  const index = parseInt(container.dataset.divisionCounter || '0', 10);
  container.dataset.divisionCounter = String(index + 1);
  const ds = container.dataset;

  const col = document.createElement('div');
  col.className = 'col';
  col.setAttribute('data-label', '');
  col.setAttribute('data-division-index', String(index));
  col.innerHTML = `
    <div class="card h-100 shadow-sm border rounded">
      <div class="card-header bg-light d-flex justify-content-between align-items-center py-2">
        <div class="input-group input-group-sm w-75">
          <span class="input-group-text bg-white"><i class="bi bi-tag-fill text-muted"></i></span>
          <input type="text" class="form-control fw-bold"
                 name="label_${index}" required placeholder="${ds.labelPlaceholder || ''}">
        </div>
        <button type="button" class="btn btn-outline-danger btn-sm"
                onclick="removeDivision(this)">
          <i class="bi bi-trash"></i>
        </button>
      </div>
      <div class="card-body p-3">
        <div class="row g-2 align-items-end mb-3">
          <div class="col-md-5">
            <label class="form-label text-muted small fw-bold mb-1">${ds.iconTypeLabel || ''}</label>
            <select class="form-select form-select-sm"
                    name="icon_type_${index}"
                    id="icon_type_${index}"
                    onchange="toggleIconType(${index})">
              <option value="css">CSS Class</option>
              <option value="img">SVG Icon</option>
              <option value="" selected>None</option>
            </select>
          </div>
          <div class="col-md-7">
            <div id="css_container_${index}" class="d-none">
              <label class="form-label text-muted small fw-bold mb-1">
                ${ds.bootstrapIconLabel || ''}
              </label>
              <input type="text" class="form-control form-select-sm"
                     id="css_input_${index}"
                     name="icon_value_${index}"
                     oninput="updatePreview(${index})"
                     placeholder="e.g. bi-tags">
            </div>
            <div id="img_container_${index}" class="d-none">
              <label class="form-label text-muted small fw-bold mb-1">
                ${ds.svgIconLabel || ''}
              </label>
              <select class="form-select form-select-sm"
                      id="img_select_${index}"
                      name="icon_value_${index}"
                      onchange="updatePreview(${index})">
                ${tpl.innerHTML}
              </select>
            </div>
          </div>
        </div>
        <div class="d-flex align-items-center gap-3 mb-3 p-2 bg-light rounded border"
             style="min-height: 48px;">
          <span class="text-muted small fw-bold">${ds.previewLabel || ''}</span>
          <div id="preview_container_${index}"
               class="d-flex align-items-center justify-content-center text-primary"
               style="width: 32px; height: 32px;"></div>
        </div>
        <div class="mb-0">
          <label class="form-label text-muted small fw-bold mb-1">
            ${ds.typeIdsLabel || ''}
          </label>
          <input type="text" class="form-control form-select-sm"
                 name="ids_${index}" placeholder="e.g. 101, 102">
        </div>
      </div>
    </div>`;
  container.appendChild(col);
  toggleIconType(index);
}

function removeDivision(button) {
  button.closest('.col')?.remove();
}

function purgeIdentifier(sysId) {
  if (confirm('Are you sure you want to purge this external identifier from the system?')) {
    document.getElementById(`accordion-item-${sysId}`)?.remove();
  }
}

document.addEventListener('DOMContentLoaded', function () {
  let tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })

  // Colors popover initialization
  const colorsForm = document.getElementById('entity-colors-form');
  if (colorsForm && colorsForm.dataset.availableColors) {
    const availableColors = JSON.parse(colorsForm.dataset.availableColors);
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(popoverTriggerEl => {
      const entityType = popoverTriggerEl.id.replace('display-', '');
      const input = document.getElementById('selected-color-' + entityType);
      const colorGrid = document.createElement('div');
      colorGrid.className = 'color-grid-popover';

      availableColors.forEach(col => {
        const swatch = document.createElement('div');
        swatch.className = 'swatch';
        swatch.style.backgroundColor = col;
        swatch.onclick = (e) => {
          e.stopPropagation();
          input.value = col;
          popoverTriggerEl.style.backgroundColor = col;
          bootstrap.Popover.getInstance(popoverTriggerEl).hide();
        };
        colorGrid.appendChild(swatch);
      });

      new bootstrap.Popover(popoverTriggerEl, {
        content: colorGrid,
        sanitize: false});
    });
  }

  // Legal Notice TinyMCE initialization
  if (typeof tinymce !== 'undefined' && document.querySelector('.tinymce-editor')) {
    tinymce.init({
      selector: '.tinymce-editor',
      license_key: 'gpl',
      menubar: false,
      branding: false,
      height: 300,
      plugins: 'link lists image table code',
      toolbar: 'undo redo | blocks | bold italic underline strikethrough | ' +
        'superscript subscript | alignleft aligncenter alignright alignjustify | ' +
        'bullist numlist | table link image | removeformat code',
      convert_urls: false,
      default_link_target: '_blank',
      rel_list: [{title: 'No referrer', value: 'noreferrer noopener'}],
      image_advtab: true,
      paste_as_text: false,
      setup: function (editor) {
        editor.on('change keyup', function () {
          editor.save();
        });
      }});
  }

  // Footer Content Management initialization
  const sortableLogosContainer = document.getElementById('sortable-logos');
  const footerForm = document.getElementById('footer-logos-form');
  if (sortableLogosContainer && footerForm) {
    const orderInput = document.getElementById('footer-logo-order-input');
    const checkboxes = document.querySelectorAll('.logo-checkbox');
    const orderedLogoIds = JSON.parse(
      sortableLogosContainer.dataset.selectedLogos || '[]');
    let isSavingOrder = false;

    const getSelectedLogoIds = () => Array.from(
      document.querySelectorAll('.logo-checkbox:checked')).map(cb => cb.value);

    const updatePositions = () => {
      sortableLogosContainer.querySelectorAll('.card').forEach((el, index) => {
        el.querySelector('.position').textContent = index + 1;
      });
    };

    const updateOrderInput = () => {
      const logoIds = Array.from(
        sortableLogosContainer.querySelectorAll('.card')).map(
          el => el.getAttribute('data-id'));
      if (orderInput) orderInput.value = JSON.stringify(logoIds);
    };

    const saveOrderOnTheFly = async () => {
      if (isSavingOrder) return;
      const currentOrder = Array.from(
        sortableLogosContainer.querySelectorAll('.card')).map(
          el => el.getAttribute('data-id'));
      if (!currentOrder.length) return;

      isSavingOrder = true;
      const formData = new FormData();
      formData.append('active_sidebar', 'sidebar-footer-content');
      formData.append('footer_logo_order', JSON.stringify(currentOrder));
      getSelectedLogoIds().forEach(logoId => {
        formData.append('footer_logos', logoId);
      });

      try {
        const csrfToken =
          document.querySelector('meta[name="csrf-token"]')?.content || '';
        const response = await fetch(footerForm.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken}});
        if (!response.ok) console.error('Unable to save footer order.');
      } catch (error) {
        console.error('Unable to save footer order.', error);
      } finally {
        isSavingOrder = false;
      }
    };

    const updateSortableList = () => {
      sortableLogosContainer.replaceChildren();
      const checkedLogoIds = getSelectedLogoIds();
      const finalLogoIds = orderedLogoIds.filter(
        id => checkedLogoIds.includes(String(id)));
      checkedLogoIds.forEach(id => {
        if (!finalLogoIds.includes(Number(id))) finalLogoIds.push(Number(id));
      });

      let position = 1;
      finalLogoIds.forEach(logoId => {
        const checkbox = document.getElementById('checkbox-' + logoId);
        if (checkbox) {
          const filename = checkbox.getAttribute('data-filename') || '';
          const url = checkbox.getAttribute('data-url') || '';
          const card = document.createElement('div');
          card.className = 'card';
          card.dataset.id = String(logoId);
          card.style.width = '120px';

          const header = document.createElement('div');
          header.className = 'card-header text-center fw-bold';
          header.innerHTML = `#<span class="position">${position++}</span>`;

          const img = document.createElement('img');
          img.src = url;
          img.className = 'card-img-top p-2';
          img.alt = filename;
          img.style.objectFit = 'contain';
          img.style.height = '80px';

          card.appendChild(header);
          card.appendChild(img);
          sortableLogosContainer.appendChild(card);
        }
      });
      updatePositions();
      updateOrderInput();
    };

    new Sortable(sortableLogosContainer, {
      animation: 150,
      ghostClass: 'blue-background-class',
      onEnd: async function () {
        updatePositions();
        updateOrderInput();
        await saveOrderOnTheFly();
      }});

    checkboxes.forEach(cb => cb.addEventListener('change', updateSortableList));
    footerForm.addEventListener('submit', updateOrderInput);
    updateSortableList();
  }

  // Publications DOI Import & Edit Modal initialization
  const btnImportDoi = document.getElementById('btn_import_doi');
  if (btnImportDoi) {
    const doiInput = document.getElementById('doi_import');
    const doiStatus = document.getElementById('doi_status');
    btnImportDoi.addEventListener('click', function () {
      const doi = doiInput ? doiInput.value.trim() : '';
      if (!doi || !doiStatus) return;

      const fetchingText = btnImportDoi.dataset.fetchingText || 'Fetching data...';
      doiStatus.innerHTML =
        `<span class="text-info"><i class="bi bi-hourglass-split"></i> ${fetchingText}</span>`;

      const formData = new FormData();
      formData.append('doi', doi);
      const csrfToken =
        document.querySelector('meta[name="csrf-token"]')?.content || '';

      fetch(btnImportDoi.dataset.importUrl || '/admin/publications/import_doi', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken}})
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            const span = document.createElement('span');
            span.className = 'text-danger';
            span.textContent = data.error;
            doiStatus.replaceChildren(span);
          } else {
            document.getElementById('pub_title').value = data.title || '';
            document.getElementById('pub_authors').value = data.authors || '';
            document.getElementById('pub_year').value = data.year || '';
            document.getElementById('pub_doi').value = data.doi || '';
            document.getElementById('pub_url').value = data.url || '';
            const span = document.createElement('span');
            span.className = 'text-success';
            span.textContent = btnImportDoi.dataset.successText || 'Imported!';
            doiStatus.replaceChildren(span);
          }
        })
        .catch(error => {
          const span = document.createElement('span');
          span.className = 'text-danger';
          span.textContent = btnImportDoi.dataset.errorText || 'Error.';
          doiStatus.replaceChildren(span);
          console.error('Error:', error);
        });
    });
  }

  const editPubModalEl = document.getElementById('editPubModal');
  if (editPubModalEl) {
    const editPubModal = new bootstrap.Modal(editPubModalEl);
    document.querySelectorAll('.btn-edit-pub').forEach(btn => {
      btn.addEventListener('click', function () {
        const pub = JSON.parse(this.dataset.pub);
        document.getElementById('edit_pub_id').value = pub.id;
        document.getElementById('edit_pub_title').value = pub.title;
        document.getElementById('edit_pub_authors').value = pub.authors || '';
        document.getElementById('edit_pub_year').value = pub.year || '';
        document.getElementById('edit_pub_type').value = pub.publication_type || '';
        document.getElementById('edit_pub_doi').value = pub.doi || '';
        document.getElementById('edit_pub_url').value = pub.url || '';
        document.getElementById('edit_pub_file').value = pub.file_id || '';

        document.querySelectorAll('#edit_pub_projects input[type="checkbox"]').forEach(
          cb => { cb.checked = false; });
        if (pub.entities) {
          pub.entities.forEach(ent => {
            const cb = document.getElementById('edit_proj_' + ent.id);
            if (cb) cb.checked = true;
          });
        }
        editPubModal.show();
      });
    });
  }

  // Type Divisions & External Identifiers preview initialization
  document.querySelectorAll('[data-division-index]').forEach(el => {
    toggleIconType(el.dataset.divisionIndex);
  });
  document.querySelectorAll('#external-identifiers-accordion [data-sys-id]').forEach(el => {
    toggleIconType(el.dataset.sysId);
  });

  // Update URL in address bar when tabs are switched without page reload
  document.addEventListener('shown.bs.tab', function (event) {
    const target = event.target;
    const targetId = target.getAttribute('aria-controls') ||
                     target.getAttribute('data-bs-target')?.replace('#', '');

    if (targetId) {
      const newUrl = `/admin/${targetId}`;
      if (window.location.pathname !== newUrl) {
        window.history.pushState({ tab: targetId }, '', newUrl);
      }
    }
  });
})
