from flask import Flask, render_template, jsonify, request
from app.geocoder import get_address_result
from app.census_acs import retrieve_census_data
from app.query_data_census import get_census_stats
import json

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/api/geocode')
    def geocode():
        address = request.args.get('address')
        geocode_result = get_address_result(address)
        return geocode_result

    
    def census_results(fips):
        census_result = retrieve_census_data(fips)
        return jsonify(census_result)

    @app.route('/api/geocode-census')
    def get_data():
        try:
            geocoded_results = geocode()
            geo_data = geocoded_results["geo_data"]
            fips_results = [geo_data["state"]["STATE"],
                            geo_data["county"]["COUNTY"],
                            geo_data["census_tract"]["TRACT"],
                            geo_data["census_block"]["BLKGRP"]
                            ]
            census_data = census_results(fips_results)
            return jsonifycensus_data
        except Exception as e:
            return {"error": str(e)}

    @app.route('/api/query', methods=["POST"])
    def query():
        try:
            query_ids = request.get_json()["geoids"]
            census_stats = get_census_stats(query_ids)
            return jsonify(census_stats)
        except Exception as e:
            return {"error": str(e)}
        
        




    return app
