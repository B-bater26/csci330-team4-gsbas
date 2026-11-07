import requests

def generate_results(loc, geo):
    data = {
        "latitude": loc["coordinates"]["y"],
        "longitude": loc["coordinates"]["x"],
        "address": loc["matchedAddress"],
        "geo_data": {
            "census_block": geo["2020 Census Blocks"][0],
            "census_tract": geo["Census Tracts"][0],
            "county": geo["Counties"][0],
            "state": geo["States"][0],
        }
    }
    return data

def get_address_result(address):
    try:
        LOC_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
        params_loc = {
            "address": address,
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json"
        }

        req = requests.get(LOC_URL, params=params_loc, timeout=10)
        req.raise_for_status()
        req_data = req.json()
        matches = req_data["result"]['addressMatches']
        if not matches:
            raise Exception("Error: No matches")
        matched_loc = matches[0]
        matched_geo = matched_loc["geographies"]

        results = generate_results(matched_loc, matched_geo)
        return results
    except Exception as e:
        return {"Error": str(e)}



def build_address(street, city, state, zip_code):
    if '' in (street, city, state, zip_code):
        print("You are missing a value")
        return f"Error: {e}"
    address = f"{street}, {city}, {state} {zip_code}"
    print(address)
    return address