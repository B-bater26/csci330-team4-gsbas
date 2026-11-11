// Map Set Up
const map = L.map('map').setView([33.68906, -79.88669], 10);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 24,
    minZoom: 5,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    wheelPxPerZoomLevel: 120,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


// Plot the layer for TIGER data
async function tigerLayer(state, county) {
    const tigerURL_BASE = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/10/query'
    const params = new URLSearchParams({
        where: `STATE='${state}' AND COUNTY='${county}'`,
        outFields: 'GEOID,STATE,COUNTY,TRACT,BLKGRP,CENTLAT,CENTLON',
        returnGeometry: 'true',
        outSR: '4326',
        f: 'geojson'
    })
    const tiger_URL = `${tigerURL_BASE}?${params}`
    try {
        console.log("Fetching TIGER...")

        const response = await fetch(tiger_URL, {
            signal: AbortSignal.timeout(20000)
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        const data = await response.json();

        console.log("Successful TIGER Plot");
        return data

    } catch (error) {
        if (error.name === 'TimeoutError') {
            console.error("Timeout: ", error.message);
        } else {
            console.error("Tiger Error: ", error.message);
        }

        return { "error": error }
    }
}

// Map Tracking
let map_features = L.layerGroup().addTo(map);

// Delete Map Features
function delete_features() {
    map_features.clearLayers();
}
