const minRange = document.querySelector('.min-range');
const maxRange = document.querySelector('.max-range');
const minValueInput = document.getElementById('min-value');
const maxValueInput = document.getElementById('max-value');
const range = document.querySelector('.range');

function updateRangeFromInput() {
    let min = parseInt(minValueInput.value);
    let max = parseInt(maxValueInput.value);

    if (min > max) {
        [min, max] = [max, min];
    }

    minRange.value = min;
    maxRange.value = max;
    updateValues();
}

function updateValues() {
    const min = parseInt(minRange.value);
    const max = parseInt(maxRange.value);

    if (min > max) {
        const temp = minRange.value;
        minRange.value = maxRange.value;
        maxRange.value = temp;
    }

    minValueInput.value = minRange.value;
    maxValueInput.value = maxRange.value;

    range.style.left = (min / minRange.max) * 100 + '%';
    range.style.width = ((max - min) / minRange.max) * 100 + '%';
}

minRange.addEventListener('input', updateValues);
maxRange.addEventListener('input', updateValues);
minValueInput.addEventListener('input', updateRangeFromInput);
maxValueInput.addEventListener('input', updateRangeFromInput);

updateValues();
