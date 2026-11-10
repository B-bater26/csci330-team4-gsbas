import os
import requests
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

ACS_URL = "https://api.census.gov/data/2024/acs/acs5"
def clean(raw):
    if raw is None:
        return None
    value = float(raw)
    return value if value >= 0 else None


def get_census_stats(geoids, codes):
    try:
        # Create a dictionary of geoids
        grouped_geo = defaultdict(set)
        results = {}

        # For each group in the geoid, get the state and county and add it to grouped_geo
        for group in geoids:
            grouped_geo[group[:2], group[2:5]].add(group)

        # For each state and county and wanted item in grouped geo, call Census ACS for data in that block
        for (state, county), wanted_item in grouped_geo.items():     
            params = {
                "get": ",".join(codes),
                "for": "block group:*",
                "in": f"state:{state} county:{county} tract:*",
                "key": os.getenv("CENSUS_API_KEY")
            }
            response = requests.get(ACS_URL, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Grab the headers and all the rows from json
            header, *rows = response.json()

            # For each row in the rows, zip together a dictionary of the rows' state, county, tract, and block group
            for row in rows:
                d = dict(zip(header, row))
                geoid = d["state"] + d["county"] + d["tract"] + d["block group"]
                # If the geoid grabbed is not in our list, throw it away
                if geoid not in wanted_item:
                    continue
                
                # If we do want it, check to make sure it isn't empty or an error, then add it to results list
                results[geoid] = {code: clean(d[code]) for code in codes}
        return results
    except Exception as e:
        return {"Error" : str(e)}