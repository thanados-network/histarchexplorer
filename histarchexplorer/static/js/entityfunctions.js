function makeLocalDate(dateString) {

    let result = {'datestring': dateString, 'localdate': ''}
    let addition = ''
    let addValue = 0
    if (typeof (dateString) === 'undefined') {
        result.localdate = '?';
        return result
    }

    if (dateString[0] === '-') {
        addition = ' BC'
        addValue = 1
    }

    let parts = dateString.split('-');
    let year = parseInt(parts[0 + addValue], 10);
    let month = parseInt(parts[1 + addValue], 10) - 1; // months are zero-based
    let day = parseInt(parts[2 + addValue], 10);
    let date = new Date(year, month, day);


    if (dateString.includes('-01-01') || dateString.includes('-12-31') || isNaN(month)) {
        result.localdate = year + addition
        return result
    }

// Format the date based on the user's locale

    if (isValidDate(date)) {
        const formattedDate = new Intl.DateTimeFormat(language).format(date);
        result.localdate = formattedDate + addition
        return result;
    } else {
        return '?'
    }
}

function isValidDate(d) {

    return d instanceof Date && !isNaN(d);
}

function calculateTimeBP(dateString, isBegin) {
    //if (!dateString && isBegin) dateString = '-999999999-01-01'; // Default placeholder for begin
    //if (!dateString && !isBegin) dateString = '999999999-01-01'; // Default placeholder for begin

    if (!dateString) {
        return null
    }
    const today = new Date();
    const currentMonth = today.getMonth(); // 0-11
    const currentYear = today.getFullYear();
    const currentDay = today.getDate(); // 1-31

    const daysPerMonth = 365.2525 / 12;
    const daysSinceZero = currentYear * 365.2525 + currentMonth * daysPerMonth + currentDay;

    let isNegative = false;
    let yearPartEndIndex = dateString.indexOf('-');
    if (dateString[0] === '-') {
        isNegative = true;
        yearPartEndIndex = dateString.indexOf('-', 1);
    }
    if (yearPartEndIndex === -1) yearPartEndIndex = dateString.length;

    let yearFromString = parseInt(dateString.substring(0, yearPartEndIndex));
    if (isNaN(yearFromString)) yearFromString = 0;

    let monthFromString = parseInt(dateString.substring(yearPartEndIndex + 1, yearPartEndIndex + 3));
    if (isNaN(monthFromString)) monthFromString = 0; else monthFromString -= 1;

    let dayFromString = parseInt(dateString.substring(yearPartEndIndex + 4, yearPartEndIndex + 6));
    if (isNaN(dayFromString)) dayFromString = 0;

    const daysToZero = isNegative
        ? (yearFromString * 365.2525 - (monthFromString) * daysPerMonth) + dayFromString
        : yearFromString * 365.2525 + monthFromString * daysPerMonth + dayFromString;

    const daysBP = daysSinceZero - daysToZero;
    return 0-daysBP;
}

function fieldHasValues(entities, field) {
    return entities.some(entity => {
        const value = entity[field];
        return value !== undefined && value !== null && String(value).trim() !== "";
    });
}

function translateDescription(text) {
    {
        if (text) {
            const pattern = new RegExp(`##${language}_##([\\s\\S]*?)##_${language}##`, 'm');
            const match = text.match(pattern);
            if (match && match[1]) {
                return match[1].trim();
            }
            return text;
        }
        return '';
    }
}

function getUniqueValues(data, field) {
    return [...new Set(data.map(row => row[field]).filter(Boolean))].sort();
}

function createSortLevel(id, fields) {
    const div = document.createElement('div');
    div.classList.add('row', 'align-items-end', 'mb-2');
    div.dataset.id = id;

    div.innerHTML = `
    <div class="col">
      <label class="form-label">Sort by</label>
      <select class="form-select sort-field">
        ${fields.includes('name') ? `<option value="name">Name</option>`:''}
        ${fields.includes('class') ? `<option value="class">Class</option>`:''}
        ${fields.includes('type') ? `<option value="type">Type</option>`:''}
        ${fields.includes('beginDBP') ? `<option value="beginDBP">Begin</option>`:''}
        ${fields.includes('endDBP') ? `<option value="endDBP">End</option>`:''}
      </select>
    </div>
    <div class="col">
      <label class="form-label">Direction</label>
      <select class="form-select sort-direction">
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>
    </div>
    <div class="col-auto">
      <button type="button" class="btn btn-outline-danger remove-sort-level">Remove</button>
    </div>
  `;

    return div;
}

function getKeysWithValues(dataArray) {
    const keysWithValues = new Set();

    if (!Array.isArray(dataArray) || dataArray.length === 0) {
        return [];
    }

    dataArray.forEach(obj => {
        for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                const value = obj[key];
                if (value !== null && typeof value !== 'undefined') {
                    if (typeof value === 'string' && value.trim() === '') {
                        continue;
                    }
                    keysWithValues.add(key);
                }
            }
        }
    });

    return Array.from(keysWithValues);
}
