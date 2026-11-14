// Retrieve area statistics for a given location and radius
async function getAreaStats(data, radius) {
    let state = data.geo_data.state.STATE;
    let county = data.geo_data.county.COUNTY;

    // Finding census block groups
    let tigerData = await tigerLayer(state, county);
    let blockGroups = bufferAgainst(radius, tigerData);

    let geoids = blockGroups.map(block => block.properties.GEOID);
    let stats = [...new Set(["B01003_001E", ...checkbox_values()])];

    let response = await fetch("/api/query", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({geoids: geoids, stats: stats})
    });

    let censusData = await response.json();

    return generate_outputs(censusData);
}

// Compare button
document.getElementById("compareButton").onclick = async function() {
    let address1 = document.getElementById("compareAdress1").value;
    let address2 = document.getElementById("compareAdress2").value;

    document.getElementById("area1-results").innerHTML = "<h3>Area 1 Results</h3>";
    document.getElementById("area2-results").innerHTML = "<h3>Area 2 Results</h3>";

    delete_features();

    let response1 = await fetch("/api/geocode?address=" + encodeURIComponent(address1));
    let data1 = await response1.json();

    let response2 = await fetch("/api/geocode?address=" + encodeURIComponent(address2));
    let data2 = await response2.json();

    if (!Number.isFinite(data1.latitude) || !Number.isFinite(data1.longitude) ||
    !Number.isFinite(data2.latitude) || !Number.isFinite(data2.longitude)) {
    alert("Please enter two valid addresses.");
    return;
}


// Create a radius around each address
let radius1 = turfBuffer(data1.latitude, data1.longitude, "blue");
let radius2 = turfBuffer(data2.latitude, data2.longitude, "red");

// Get statistics for each area
let stats1 = await getAreaStats(data1, radius1);
let stats2 = await getAreaStats(data2, radius2);

console.log("Area 1 stats:", stats1);
console.log("Area 2 stats:", stats2);

// Display Results
if (!document.getElementById("pop_check").checked) {
    delete stats1.Population;
    delete stats2.Population;
}

if (!document.getElementById("home_owner_check").checked) {
    delete stats1["Home Owners"];
    delete stats2["Home Owners"];
}

display_outputs(stats1, "area1-results");
display_outputs(stats2, "area2-results");

document.getElementById("area1-results").insertAdjacentHTML(
    "afterbegin", "<h3>Area 1 Results</h3>"
);

document.getElementById("area2-results").insertAdjacentHTML(
    "afterbegin", "<h3>Area 2 Results</h3>"
);



};