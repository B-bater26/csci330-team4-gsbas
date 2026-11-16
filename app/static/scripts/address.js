// Input Set Up
let addInputField = document.getElementById("addressInput");
let addressValue;
let loading = false;
let outputs = null;
let latestMatchedAddress = "";

// Input Enter
addInputField.addEventListener('keydown', function (event) {
    if (event.key === "Enter" && loading === false) {
        if (document.querySelectorAll(".check:checked").length === 0) {
            alert("Please select at least one option.");
            return;
        }
        addressValue = addInputField.value;
        console.log(addressValue);
        startWorkflow(addressValue)
    } else if (loading === true) {
        console.log("Data loading... please wait.")
    }
})

// Geocode Retrieval and Tiger Plotting
async function geocode(address) {
    const gsbas_cg_base = '/api/geocode'
    const params = new URLSearchParams({
        address: `${address}`
    })
    const gsbas_cg_URL = `${gsbas_cg_base}?${params}`
    try {
        loading = true;
        console.log("Fetching Geocode Data")

        const response = await fetch(gsbas_cg_URL, {
            signal: AbortSignal.timeout(30000)
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        console.log("Fetched Geocode Data!");

        delete_features();

        const geocode_data = await response.json();
        latestMatchedAddress = geocode_data.address;
        console.log(geocode_data)
        if (!geocode_data || !Number.isFinite(geocode_data.latitude) || !Number.isFinite(geocode_data.longitude)) {
            alert("Please enter a valid address.");
            loading = false;
            return;
        }
        const geo_data = geocode_data.geo_data;
        const state = geo_data.state.STATE;
        const county = geo_data.county.COUNTY;
        const lat = geocode_data.latitude
        const lng = geocode_data.longitude
        const tigerData = await tigerLayer(state, county)


        const businessMarker = L.marker([lat, lng]).addTo(map);
        map_features.addLayer(businessMarker)

        const bufferData = turfBuffer(lat, lng);
        showAmenities(lat, lng);

        console.log(`Successful Address Plot at ${state}, ${county}`);

        console.log('Buffering Against...');

        const bufferZones = bufferAgainst(bufferData, tigerData);
        console.log(bufferZones);

        const tiger_zones = L.geoJSON(bufferZones, {
            style: {color: '#3366cc', weight: 1, fillOpacity: 0.1}
        }).addTo(map);

        map_features.addLayer(tiger_zones);

        const census_query = await fipsData(bufferZones);

        console.log(census_query);

        console.log("Generating outputs...");

        outputs = generate_outputs(census_query);

        //Home value displaying owners fix
        if (!document.getElementById("home_owner_check").checked) {
            delete outputs["Home Owners"];
        }
        display_outputs(outputs);

        loading = false;
        return geocode_data

    } catch (error) {
        if (error.name === 'TimeoutError') {
            console.error("Timeout: ", error.message);
        } else {
            console.error("Geocoding Error in JS: ", error.message);
        }

        loading = false;
        return { "error": error }
    }
}

async function startWorkflow(address) {
    let geocodeData = await geocode(address)
}

// Hook into Save Analysis button
document.getElementById("saveAnalysisBtn")?.addEventListener("click", async () => {
    const statusEl = document.getElementById("saveStatus");
    const addr = latestMatchedAddress || document.getElementById("addressInput").value.trim();
    const radiusSlider = document.getElementById("areaRadius");
    const radius = radiusSlider ? parseFloat(radiusSlider.value) : 10;

    // 1. Try reading from rendered output cards
    const liveOutputs = {};
    document.querySelectorAll("#outputs-container .output-card").forEach(card => {
        const titleEl = card.querySelector("h1");
        const valEl = card.querySelector("h2");
        if (titleEl && valEl) {
            const name = titleEl.textContent.trim();
            const num = parseFloat(valEl.textContent.replace(/[^0-9.-]+/g, ""));
            if (name && !isNaN(num)) {
                liveOutputs[name] = num;
            }
        }
    });

    // 2. Fallback to the outputs variable in address.js if cards aren't rendered yet
    const finalOutputs = Object.keys(liveOutputs).length > 0 ? liveOutputs : (typeof outputs !== "undefined" && outputs ? outputs : null);

    if (!addr || !finalOutputs) {
        statusEl.style.color = "#ff6b6b";
        statusEl.textContent = "Press Enter in the address box to load stats first!";
        return;
    }

    statusEl.style.color = "#b0bdd4";
    statusEl.textContent = "Saving...";

    try {
        const res = await fetch("/api/save-analysis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ address: addr, radius: radius, outputs: finalOutputs })
        });
        const result = await res.json();
        if (result.success) {
            statusEl.style.color = "#51cf66";
            statusEl.textContent = `Saved (${radius} mi)! View in Saved Analyses.`;
        } else {
            statusEl.style.color = "#ff6b6b";
            statusEl.textContent = result.error || "Save failed.";
        }
    } catch (err) {
        statusEl.style.color = "#ff6b6b";
        statusEl.textContent = "Network error while saving.";
    }
});