import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACS_URL = "https://api.census.gov/data/2024/acs/acs5"

def retrieve_census_data(fips):
    try:
        state = fips[0]
        county = fips[1]
        tract = fips [2]
        block_group = fips[3]
        
        params = {
            "get": "NAME,B19013_001E",
            "for": f"block group:{block_group}",
            "in": f"state:{state} county:{county} tract:{tract}",
            "key": os.getenv("CENSUS_API_KEY")
        }
        response = requests.get(ACS_URL, params=params, timeout=15)
        data = response.json()
        response.raise_for_status()
        if data[1][1] == -666666666:
            return {"Blocked" : "Census Data is blocked for this area due to privacy restrictions"}
        return data
    except Exception as e:
        return {"Error" : str(e)}