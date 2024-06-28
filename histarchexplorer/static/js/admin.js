function toggleFields(form, enabled) {
    const fields = form.querySelectorAll('input, textarea');
    fields.forEach(field => {
        if (enabled) {
            field.dataset.originalValue = field.value;
            field.removeAttribute('disabled');
        } else {
            field.value = field.dataset.originalValue;
            field.setAttribute('disabled', 'disabled');
        }
    });
}

function toggleButtons(entryId, isEditing) {
    ['edit', 'delete', 'save', 'cancel'].forEach(action => {
        document.getElementById(`${action}${entryId}`).classList.toggle(
            'd-none',
            action === 'edit' || action === 'delete' ? isEditing : !isEditing
        );
    });
}

function changeEdit(entryId, enabled) {
    const form = document.getElementById(`form${entryId}`);
    toggleFields(form, enabled);
    toggleButtons(entryId, enabled);
}


function addEntry(category) {
    const hiddenField = document.getElementById('currentTab');
    hiddenField.value = category.replace('nav-', '');
    console.log(hiddenField.value)

    document.querySelectorAll('.modal-input').forEach(el => el.classList.add('d-none'));
    document.querySelectorAll(`.${hiddenField.value}-show`).forEach(el => el.classList.remove('d-none'));

    const modal = new bootstrap.Modal(document.getElementById('addEntryModal'));
    modal.show();
}

(() => {
    'use strict';

    const forms = document.querySelectorAll('.needs-validation');

    // Loop over each form and add submit event listener to prevent submission if invalid
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        });
    });
})();

document.getElementById('resetButton').addEventListener('click', function () {
    if (confirm('Are you sure you want to reset the settings?')) {
        window.location.href = '/reset';
    }
});


function deleteEntry(id, name, tab) {
    const deleteName = document.getElementById('deleteName');
    deleteName.textContent = name;

    const confirmedDelete = document.getElementById('confirmedDelete');
    confirmedDelete.href = `/admin/delete_entry/${id}/${tab}`;
}

function deleteLink(linkId, startName, configProperty, endName, tab, entry) {
    const deleteName = document.getElementById('deleteName');
    deleteName.textContent = `${startName} - ${configProperty} - ${endName} ?`;

    const confirmedDelete = document.getElementById('confirmedDelete');
    confirmedDelete.href = `/admin/delete_link/${linkId}/${tab}/${entry}`;

    const myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    myModal.show();
}


const connectionSelects = document.querySelectorAll('.connection-select');

connectionSelects.forEach(selectConnection => {
    selectConnection.addEventListener('change', () => {
        const isEnabled = selectConnection.selectedIndex !== 0;

        // Enable/Disable next and previous sibling elements based on selection
        if (selectConnection.nextElementSibling) {
            selectConnection.nextElementSibling.disabled = !isEnabled;
        }
        if (selectConnection.previousElementSibling) {
            selectConnection.previousElementSibling.disabled = isEnabled;
        }

        // Locate the save button and selected option data
        const saveButton = selectConnection.parentNode.querySelector('button:last-child');
        const optionData = selectConnection.options[selectConnection.selectedIndex];

        // Call setSaveValues with relevant parameters
        setSaveValues(selectConnection.classList, saveButton, optionData, selectConnection);
    });
});

function setSaveValues(classList, saveButton, info, thisElement) {
    const {value} = info;

    if (classList.contains('link-type')) {
        saveButton.dataset.domain = info.getAttribute('data-entry');
        saveButton.dataset.direction = info.getAttribute('data-direction');
        saveButton.dataset.property = value;

        const selectNode = thisElement.nextElementSibling; // Next sibling is the select dropdown
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
    console.log(button);

    let domain = button.dataset.domain;
    let range = button.dataset.range;

    if (button.dataset.direction !== 'direct') {
        [domain, range] = [range, domain];
    }

    const {property, role, tab, entry} = button.dataset;

    // Construct URL and navigate
    window.location.href = `/admin/add_link/${domain}/${range}/${property}/${role}/${tab}/${entry}`;
}


const accordionContainer = document.getElementById('mapsAccordion');
new Sortable(accordionContainer, {
    animation: 150,
    handle: '.accordion-button', // Specify the handle for sorting
    onEnd: function (evt) {
        // This function runs when sorting is done
        var items = Array.from(accordionContainer.getElementsByClassName('accordion-item'));
       items.forEach((item, index) => {
            item.setAttribute("data-order", index + 1);
        });

        // Map items to array of objects with order and id
        let sortedItems = items.map(item => ({
            order: item.getAttribute("data-order"),
            id: item.getAttribute("data-id")
        }));
        saveSortOrder(sortedItems, 'maps')
    }
});


const linksSort = document.getElementById('nav-main-project-links');
let sortedItems = [];

new Sortable(linksSort, {
    animation: 150,
    handle: '.d-flex', // Specify the handle for sorting
    onEnd: function (evt) {
        const items = Array.from(linksSort.getElementsByClassName('d-flex'));
        // Update order attribute based on visual sorting
        items.forEach((item, index) => {
            item.setAttribute("data-order", index + 1);
        });

        // Map items to array of objects with order and id
        let sortedItems = items.map(item => ({
            order: item.getAttribute("data-order"),
            id: item.getAttribute("data-id")
        }));
        saveSortOrder(sortedItems, 'links')
    }
});


function saveSortOrder(items, table) {
    fetch('/sortlinks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({criteria: items, table: table}),
    })
}

