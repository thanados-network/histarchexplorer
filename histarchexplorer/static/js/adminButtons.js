function toggleFields(form, enabled) {
    var fields = form.querySelectorAll('input, textarea');
    fields.forEach(function (field) {
        console.log(field)
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
    document.getElementById('edit' + entryId).classList.toggle('d-none', isEditing);
    document.getElementById('delete' + entryId).classList.toggle('d-none', isEditing);
    document.getElementById('save' + entryId).classList.toggle('d-none', !isEditing);
    document.getElementById('cancel' + entryId).classList.toggle('d-none', !isEditing);
}

function changeEdit(entryId, enabled) {
    var form = document.getElementById('form' + entryId);
    toggleFields(form, enabled);
    toggleButtons(entryId, enabled);
}


function addEntry(category) {
    const hiddenField = document.getElementById('currentTab');
    const sanitizedCategory = category.replace('nav-', '');
    hiddenField.value = sanitizedCategory;

    const classToShow = `${sanitizedCategory}-show`;

    document.querySelectorAll('.modal-input').forEach(el => el.classList.add('d-none'));
    document.querySelectorAll(`.${classToShow}`).forEach(el => el.classList.remove('d-none'));

    const modal = new bootstrap.Modal(document.getElementById('addEntryModal'));
    modal.show();
}

(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()