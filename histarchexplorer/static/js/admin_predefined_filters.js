(() => {
  const list = document.getElementById('predefinedFiltersList');
  const modalElement = document.getElementById('predefinedFilterModal');
  if (!list || !modalElement) return;

  const form = document.getElementById('predefined-filter-form');
  const modal = new bootstrap.Modal(modalElement);
  const iconType = document.getElementById('filter-icon-type');
  const iconValue = document.getElementById('filter-icon-value');
  const iconFile = document.getElementById('filter-icon-file');
  const preview = document.getElementById('filter-icon-preview');
  const tabsSelect = document.getElementById('predefined-filter-tabs');
  const classesSelect = document.getElementById('predefined-filter-classes');
  const caseStudiesSelect = document.getElementById(
    'predefined-filter-case-studies');
  const languageButtons = form.querySelectorAll('.predefined-lang-btn');
  const localizedInputs = {
    label: document.getElementById('predefined-filter-label-input'),
    description: document.getElementById('predefined-filter-description-input')
  };
  const selectedLanguages = {
    label: window.language || 'en',
    description: window.language || 'en'
  };

  function getHiddenInput(field, language) {
    return form.querySelector(
      `[name="${field}_${language}"]`);
  }

  function updateLanguageButtonState(field, language) {
    const hiddenInput = getHiddenInput(field, language);
    const hasValue = hiddenInput && hiddenInput.value.trim() !== '';
    languageButtons.forEach(button => {
      if (button.dataset.field !== field || button.dataset.lang !== language) {
        return;
      }
      button.classList.remove('btn-primary', 'active', 'btn-success', 'btn-danger');
      if (selectedLanguages[field] === language) {
        button.classList.add('btn-primary', 'active');
      } else {
        button.classList.add(hasValue ? 'btn-success' : 'btn-danger');
      }
    });
  }

  function switchFieldLanguage(field, language) {
    selectedLanguages[field] = language;
    const hiddenInput = getHiddenInput(field, language);
    localizedInputs[field].value = hiddenInput ? hiddenInput.value : '';
    languageButtons.forEach(button => {
      if (button.dataset.field === field) {
        updateLanguageButtonState(field, button.dataset.lang);
      }
    });
  }

  function bindLocalizedField(field) {
    localizedInputs[field].addEventListener('input', event => {
      const currentLanguage = selectedLanguages[field];
      const hiddenInput = getHiddenInput(field, currentLanguage);
      if (hiddenInput) hiddenInput.value = event.target.value;
      updateLanguageButtonState(field, currentLanguage);
    });
  }

  function initializeLanguageFields() {
    ['label', 'description'].forEach(field => {
      const firstButton = form.querySelector(
        `.predefined-lang-btn[data-field="${field}"]`);
      if (firstButton && !getHiddenInput(field, selectedLanguages[field])) {
        selectedLanguages[field] = firstButton.dataset.lang;
      }
      bindLocalizedField(field);
      switchFieldLanguage(field, selectedLanguages[field]);
    });
  }

  function setValues(name, values) {
    const input = form.elements[name];
    if (input.tomselect) {
      input.tomselect.clear(true);
      input.tomselect.setValue((values || []).map(String), true);
      return;
    }
    const selected = new Set(values || []);
    form.querySelectorAll(`[name="${name}"] option`).forEach(option => {
      option.selected = selected.has(option.value);
    });
  }

  function initializeMultiSelect(element) {
    if (!element || typeof TomSelect !== 'function' || element.tomselect) {
      return;
    }
    const select = new TomSelect(element, {
      plugins: {
        remove_button: {
          title: 'Remove this item'
        }
      },
      create: false,
      hideSelected: true,
      closeAfterSelect: false,
      maxOptions: null,
      dropdownParent: 'body'
    });
    if (select.dropdown) select.dropdown.style.zIndex = '2000';
  }

  function updateIconPreview() {
    const isImage = iconType.value === 'img';
    iconValue.classList.toggle('d-none', isImage);
    iconFile.classList.toggle('d-none', !isImage);
    if (isImage) iconFile.value = iconValue.value;
    preview.replaceChildren();
    if (iconType.value === 'css' && iconValue.value) {
      const icon = document.createElement('i');
      icon.className = iconValue.value.includes('bi ') ? iconValue.value : `bi ${iconValue.value}`;
      icon.classList.add('fs-5');
      preview.appendChild(icon);
    } else if (iconType.value === 'img' && iconValue.value) {
      const image = document.createElement('img');
      image.src = `/static/images/icons/${iconValue.value}`;
      image.alt = '';
      image.className = 'w-100 h-100';
      preview.appendChild(image);
    }
  }

  function populate(filter) {
    form.reset();
    const parameters = filter ? filter.filter_parameters : {};
    const icon = filter && filter.icon ? filter.icon : {};
    form.action = filter
      ? `/admin/predefined_filters/${filter.id}/edit`
      : '/admin/predefined_filters/add';
    Object.entries(filter ? filter.label_values : {}).forEach(([language, value]) => {
      const input = getHiddenInput('label', language);
      if (input) input.value = value;
    });
    Object.entries(filter ? filter.description_values : {}).forEach(
      ([language, value]) => {
        const input = getHiddenInput('description', language);
        if (input) input.value = value;
      });
    iconType.value = icon.type || '';
    iconValue.value = icon.value || '';
    setValues('tabs', filter ? filter.tabs : []);
    setValues('classes', parameters.classes);
    setValues('case_study_ids', parameters.case_study_ids && parameters.case_study_ids.map(String));
    form.elements.type_ids.value = (parameters.type_ids || []).join(', ');
    ['begin_from', 'begin_to', 'end_from', 'end_to'].forEach(name => {
      form.elements[name].value = parameters[name] || '';
    });
    form.elements.include_subtypes.checked = Boolean(parameters.include_subtypes);
    form.elements.include_no_begin.checked = parameters.include_no_begin !== false;
    form.elements.include_no_end.checked = parameters.include_no_end !== false;
    switchFieldLanguage('label', selectedLanguages.label);
    switchFieldLanguage('description', selectedLanguages.description);
    updateIconPreview();
  }

  document.getElementById('add-predefined-filter').addEventListener('click', () => {
    populate(null);
    modal.show();
  });

  function updatePositions() {
    const filterElements = list.querySelectorAll('.predefined-filter-item');
    filterElements.forEach((el, index) => {
      const position = el.querySelector('.position');
      if (position) position.textContent = index + 1;
    });
  }

  function getCriteria() {
    return Array.from(list.querySelectorAll('.predefined-filter-item')).map(
      (item, index) => ({
        id: item.dataset.id,
        order: index + 1
      }));
  }

  async function saveOrder() {
    const criteria = getCriteria();
    if (!criteria.length) return;
    try {
      const response = await fetch('/admin/predefined_filters/order', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({criteria})
      });
      if (!response.ok) throw new Error('Unable to save filter order.');
    } catch (error) {
      window.alert(error.message);
    }
  }

  list.addEventListener('click', event => {
    const button = event.target.closest('.edit-predefined-filter');
    if (!button) return;
    populate(JSON.parse(button.closest('.predefined-filter-item').dataset.filter));
    modal.show();
  });
  iconType.addEventListener('change', updateIconPreview);
  iconValue.addEventListener('input', updateIconPreview);
  iconFile.addEventListener('change', () => {
    iconValue.value = iconFile.value;
    updateIconPreview();
  });
  languageButtons.forEach(button => {
    button.addEventListener('click', () => {
      switchFieldLanguage(button.dataset.field, button.dataset.lang);
    });
  });
  initializeMultiSelect(tabsSelect);
  initializeMultiSelect(classesSelect);
  initializeMultiSelect(caseStudiesSelect);
  initializeLanguageFields();

  new Sortable(list, {
    animation: 150,
    handle: '.predefined-filter-drag-handle',
    draggable: '.predefined-filter-item',
    onEnd: async () => {
      updatePositions();
      await saveOrder();
    }
  });

  updatePositions();
})();