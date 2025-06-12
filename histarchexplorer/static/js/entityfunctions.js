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
    if (!dateString) dateString = '-9999999999999999999999999999999999999999999999999999-'
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    const currentDay = today.getDate();

    const daysPerMonth = 365.2525 / 12;
    const daysSinceZero = currentYear * 365.2525 + currentMonth * daysPerMonth + currentDay;

    let isNegative = false;
    let stringLength = 9;

    if (dateString[0] === '-') {
        stringLength += 1;
        isNegative = true;
    }

    let yearFromString = parseInt(dateString.substring(0, stringLength)) || 0;
    let monthFromString = (parseInt(dateString.substring(stringLength + 1, stringLength + 3)))-1 || 0;
    let dayFromString = parseInt(dateString.substring(stringLength + 4, stringLength + 6)) || 0;

    const daysToZero = isNegative
        ? (yearFromString * 365.2525 - (monthFromString) * daysPerMonth) + dayFromString
        : yearFromString * 365.2525 + monthFromString * daysPerMonth + dayFromString;

    const daysBP = daysSinceZero - daysToZero;
    return daysBP
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
