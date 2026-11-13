// Radius Slider Set Up
let areaRadiusInput = document.getElementById("areaRadius");
let areaRadiusValue;

// Buffer around point
function turfBuffer(lat, lng) {
    const businessPoint = turf.point([lng, lat]);
    areaRadiusValue = areaRadiusInput.value;
    areaRadius = parseInt(areaRadiusValue, 10);
    console.log(`Buffer around ${businessPoint} at ${areaRadiusValue} miles`);
    const bufferArea = turf.buffer(businessPoint, areaRadius, { units: "miles" });
    const bufferAreaPoly = L.geoJSON(bufferArea, {
        style: { color: '#cc3333', weight: 1, fillOpacity: 0.5 }
    }).addTo(map);

    map_features.addLayer(bufferAreaPoly);

    map.setView([lat, lng], 10)

    return bufferArea
}

// Test Buffer Against Blocks
function bufferAgainst(buffer, blocks) {
    const bufferZones = blocks.features.filter((block) => {
        const { CENTLON, CENTLAT } = block.properties;
        return turf.booleanPointInPolygon(turf.point([CENTLON, CENTLAT]), buffer);
    });
    return bufferZones

}

// Buffer Zone Data FIPS
async function fipsData(blockGroups) {
    const geoids = blockGroups.map(f => f.properties.GEOID);
    console.log(geoids);

    const gsbas_q_URL = "http://127.0.0.1:5000/api/query";

    const response = await fetch(gsbas_q_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ geoids, stats: checkbox_values() })
    });

    if (!response.ok) throw new Error(`Error During FIPS: ${response.status}`);

    const data = await response.json();
    return data;
}
