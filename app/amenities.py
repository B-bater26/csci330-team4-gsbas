# Nearby Amenities - Nathan Miller - CSCI 330
import requests


def get_amenities(lat, lng, miles):
    meters = int(miles * 1609)
    area = f"(around:{meters},{lat},{lng})"
    query = f"""[out:json][timeout:25];
nwr["shop"]{area};
out center 15;
nwr["amenity"~"restaurant|cafe|fast_food"]{area};
out center 15;
nwr["amenity"="parking"]{area};
out center 15;
nwr["highway"="bus_stop"]{area};
out center 15;"""

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        headers={"User-Agent": "csci330-team4-gsbas"},
        timeout=60
    )
    response.raise_for_status()

    places = []
    for item in response.json()["elements"]:
        tags = item.get("tags", {})

        if "shop" in tags:
            kind = "Business"
        elif tags.get("amenity") == "parking":
            kind = "Parking"
        elif tags.get("highway") == "bus_stop":
            kind = "Bus Stop"
        else:
            kind = "Restaurant"

        if "center" in item:
            item_lat = item["center"]["lat"]
            item_lng = item["center"]["lon"]
        else:
            item_lat = item["lat"]
            item_lng = item["lon"]

        places.append({
            "name": tags.get("name", kind),
            "type": kind,
            "lat": item_lat,
            "lng": item_lng
        })
    return places