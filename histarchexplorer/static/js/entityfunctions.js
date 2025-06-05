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

var minMaxFilterEditor = function(cell, onRendered, success, cancel, editorParams){

    var end;

    var container = document.createElement("span");

    //create and style inputs
    var start = document.createElement("input");
    start.setAttribute("type", "number");
    start.setAttribute("placeholder", "Min");
    start.setAttribute("min", 0);
    start.setAttribute("max", 1000);
    start.style.padding = "4px";
    start.style.width = "50%";
    start.style.boxSizing = "border-box";

    start.value = cell.getValue();

    function buildValues(){
        success({
            start:start.value,
            end:end.value,
        });
    }

    function keypress(e){
        if(e.keyCode == 13){
            buildValues();
        }

        if(e.keyCode == 27){
            cancel();
        }
    }

    end = start.cloneNode();
    end.setAttribute("placeholder", "Max");

    start.addEventListener("change", buildValues);
    start.addEventListener("blur", buildValues);
    start.addEventListener("keydown", keypress);

    end.addEventListener("change", buildValues);
    end.addEventListener("blur", buildValues);
    end.addEventListener("keydown", keypress);


    container.appendChild(start);
    container.appendChild(end);

    return container;
 }

//custom max min filter function
function minMaxFilterFunction(headerValue, rowValue, rowData, filterParams){
    //headerValue - the value of the header filter element
    //rowValue - the value of the column in this row
    //rowData - the data for the row being filtered
    //filterParams - params object passed to the headerFilterFuncParams property

        if(rowValue){
            if(headerValue.start != ""){
                if(headerValue.end != ""){
                    return rowValue >= headerValue.start && rowValue <= headerValue.end;
                }else{
                    return rowValue >= headerValue.start;
                }
            }else{
                if(headerValue.end != ""){
                    return rowValue <= headerValue.end;
                }
            }
        }

    return true; //must return a boolean, true if it passes the filter.
}