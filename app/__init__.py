from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from app.geocoder import get_address_result
from app.census_acs import retrieve_census_data
from app.query_data_census import get_census_stats
import json
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    @app.route('/')
    def index():
        #login not mandatory for now 
        #if "user" not in session:
        #    return redirect(url_for("login"))
        return render_template("index.html")

    @app.route('/login', methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            #Temporary login until database is set up
            if username == "admin" and password == "admin":
                session["user"] = username
                return redirect(url_for("index"))
            else:
                return render_template("login.html", error="Invalid username or password")
        return render_template("login.html")

    @app.route('/logout')
    def logout():
        session.pop("user", None)
        return redirect(url_for("login"))

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
            return census_data
        except Exception as e:
            return {"error": str(e)}

    @app.route('/api/query', methods=["POST"])
    def query():
        try:
            query_ids = request.get_json()["geoids"]
            stats = request.get_json()["stats"]
            census_stats = get_census_stats(query_ids, stats)
            return jsonify(census_stats)
        except Exception as e:
            return {"error": str(e)}
        
        




    return app
