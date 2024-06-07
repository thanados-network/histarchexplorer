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
console.log(category.toString())};


function deleteEntry(id, name, tab) {
       console.log('delete?')
       deleteName = document.getElementById('deleteName')
       deleteName.innerHTML = name
       confirmedDelete = document.getElementById('confirmedDelete')
       const deleteUrl = "{{ url_for('admin') }}delete_entry/" + id + "/" + tab
       confirmedDelete.setAttribute("href", deleteUrl)
        }
