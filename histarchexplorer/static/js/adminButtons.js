function toggleFields(form, enabled) {
    var fields = form.querySelectorAll('input, textarea');
    fields.forEach(function (field) {
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


function addEntry(category){
 console.log(category)

    hiddenField = document.getElementById('currentTab')
    hiddenField.value = category.replace('nav-','')
    console.log(hiddenField.value)

    const categoryClasses = {
        'projects': ['projects-show'],
        'institutions': ['institution-show'],
        'persons': ['persons-show']
    };

    const allClasses = ['projects-show', 'institution-show', 'persons-show'];
    allClasses.forEach(cls => {
        document.querySelectorAll('.' + cls).forEach(el => el.classList.add('d-none'));
    });

    (categoryClasses[hiddenField.value] || []).forEach(cls => {
        document.querySelectorAll('.' + cls).forEach(el => el.classList.remove('d-none'));
    });


const modal = new bootstrap.Modal(document.getElementById('addEntryModal'));
    modal.show();
}


function deleteEntry(id, name, tab) {
       console.log('delete?')
       deleteName = document.getElementById('deleteName')
       deleteName.innerHTML = name
       confirmedDelete = document.getElementById('confirmedDelete')
       const deleteUrl = "{{ url_for('admin') }}delete_entry/" + id + "/" + tab
       confirmedDelete.setAttribute("href", deleteUrl)
        }
