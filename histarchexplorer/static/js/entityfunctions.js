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

function calculateTimeBP(dateString) {
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
    return 0 - daysBP;
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

function createSortLevel(id, fields, classList, typeIds,) {
    const div = document.createElement('div');
    div.classList.add('row', 'align-items-end', 'mb-2');
    div.dataset.id = id;
    let showClasses = false;
    let showTypes = false;
    if (fields.includes('class') && classList.length > 1) {showClasses = true}
    if (fields.includes('type') && typeIds.length > 1) {showTypes = true}
    div.innerHTML = `
    <div class="col">
      <select class="form-select sort-field">
        ${fields.includes('name') ? `<option value="name">Name</option>` : ''}
        ${showClasses ? `<option value="class">Class</option>` : ''}
        ${showTypes ? `<option value="type">Type</option>` : ''}
        ${fields.includes('beginDBP') ? `<option value="beginDBP">Begin</option>` : ''}
        ${fields.includes('endDBP') ? `<option value="endDBP">End</option>` : ''}
      </select>
    </div>
    <div class="col">
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

function collectAndGroupMatchingData(jsonData, keysToMatch, categoriesToMatch, typeIds) {
    const result = {};
    if (!Array.isArray(categoriesToMatch)) {
        console.warn("categoriesToMatch must be an array");
        return result;
    }

    const keyGroups = [];

    keysToMatch.forEach(currentKey => {
        const section = jsonData[currentKey];
        if (!Array.isArray(section)) return;

        const filteredEntries = section
            .filter(entry => entry?.category && categoriesToMatch.includes(entry.category))
            .map(entry => ({
                id: entry.id,
                label: entry.name,
                children: cloneWithChildren(entry.children, typeIds)
            }))

            .filter(entry => entry.id && (
                typeIds.includes(entry.id) || (entry.children?.length > 0)
            ));


        let foundGroup = false;
        for (const group of keyGroups) {
            if (deepEqual(group.data, filteredEntries)) {
                group.keys.push(currentKey);
                foundGroup = true;
                break;
            }
        }
        if (!foundGroup) {
            keyGroups.push({ keys: [currentKey], data: filteredEntries });
        }
    });

    keyGroups.forEach(group => {
        const combinedKey = group.keys.join(", ");
        result[combinedKey] = group.data;
    });

    //console.log(result);

    return result;
}

function cloneWithChildren(items, typeIds) {
    if (!Array.isArray(items)) return [];

    return items
        .map(item => {

            const filteredChildren = cloneWithChildren(item.children, typeIds);

            if (typeIds.includes(item.id) || filteredChildren.length > 0) {
                return {
                    id: item.id,
                    label: item.name,
                    children: filteredChildren
                };
            }
            return null;
        })
        .filter(Boolean);
}


function deepEqual(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
}

function getSortedDistinctTimeline(data, stringKey, numberKey) {
    const seen = new Set();

    const filtered = data
        .filter(item => item[stringKey] && typeof item[numberKey] === "number")
        .filter(item => {
            if (seen.has(item[stringKey])) return false;
            seen.add(item[stringKey]);
            return true;
        })
        .map(item => ({
            string: item[stringKey],
            number: item[numberKey]
        }))
        .sort((a, b) => a.number - b.number);

    return filtered;
}

function getDaysBPBfromString(values, dates) {
    const min = values[0];
    const max = values[1];
    let earliest = dates.filter(date => date.string === min)[0];
    let latest = dates.filter(date => date.string === max);
    latest = latest[latest.length - 1];
    return [earliest.number, latest.number];
}
