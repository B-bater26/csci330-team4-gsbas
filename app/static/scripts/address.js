// Input Set Up
let addInputField = document.getElementById("addressInput");
let addressValue;
let loading = false;

// Input Enter
addInputField.addEventListener('keydown', function (event) {
    if (event.key === "Enter") {
        addressValue = addInputField.value;
        console.log(addressValue);
        startWorkflow(addressValue)
    }
})

// Geocode Retrieval and Tiger Plotting
async function geocode(address) {
    const gsbas_cg_base = 'http://127.0.0.1:5000/api/geocode'
    const params = new URLSearchParams({
        address: `${address}`
    })
    const gsbas_cg_URL = `${gsbas_cg_base}?${params}`
    try {
        console.log("Fetching Geocode Data")

        const response = await fetch(gsbas_cg_URL, {
            signal: AbortSignal.timeout(30000)
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        console.log("Fetched Geocode Data!")

        const geocode_data = await response.json();
        console.log(geocode_data)
        const geo_data = geocode_data.geo_data;
        const state = geo_data.state.STATE;
        const county = geo_data.county.COUNTY;
        const lat = geocode_data.latitude
        const lng = geocode_data.longitude
        tigerLayer(state, county)



        const businessMarker = L.marker([lat, lng]).addTo(map)

        console.log(`Successful Address Plot at ${state}, ${county}`)
        return geocode_data

    } catch (error) {
        if (error.name === 'TimeoutError') {
            console.error("Timeout: ", error.message);
        } else {
            console.error("Geocoding Error in JS: ", error.message);
        }

        return { "error": error }
    }
}



// Input to Output Workflow
async function startWorkflow(address) {
    let geocodeData = geocode(address)
}


