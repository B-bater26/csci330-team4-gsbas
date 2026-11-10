// Check Checkbox values
function checkbox_values() {
    let codes = [];
    for (const checkbox of document.querySelectorAll(".check:checked")) {
        codes.push(...checkbox.value.split(","));
    }
    console.log(codes);
    if (codes.length === 0) {
        return ["B01003_001E"];
    }
    return [...new Set(codes)];
}





