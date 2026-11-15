async function showAmenities(lat, lng) {
    const list = document.getElementById("amenities-list");
    list.innerHTML = "<li>Loading nearby places...</li>";

    try {
        const response = await fetch(`/api/amenities?lat=${lat}&lng=${lng}`);
        const places = await response.json();
        if (places.error) throw new Error(places.error);

        if (places.length === 0) {
            list.innerHTML = "<li>No nearby places found.</li>";
            return;
        }

        list.innerHTML = "";
        places.forEach(place => {
            const dot = L.circleMarker([place.lat, place.lng], { radius: 6 })
                .bindPopup(`${place.name} (${place.type})`);
            map_features.addLayer(dot);
            list.innerHTML += `<li>${place.name} - ${place.type}</li>`;
        });
    } catch (error) {
        list.innerHTML = "<li>Couldn't load nearby places. Try again.</li>";
    }
}