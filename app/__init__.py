import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from app.census_acs import retrieve_census_data
from app.geocoder import get_address_result
from app.query_data_census import get_census_stats
from app.gemini import suggest_stats
from app.amenities import get_amenities
import json

load_dotenv()

def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-fallback-key")

    @app.route('/')
    def index():
        if "user" not in session:
            return redirect(url_for("login"))
        return render_template("index.html", username=session.get("user"))

    @app.route('/comparison')
    def comparison():
        return render_template("comparison.html")

    @app.route('/login', methods=["GET", "POST"])
    def login():
        if "user" in session:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                return render_template("login.html", error="Please enter both username and password.")

            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "SELECT UserID, UserName, UserPassword FROM users WHERE UserName = %s",
                    (username,)
                )
                user_record = cur.fetchone()
                cur.close()
                conn.close()

                if user_record and check_password_hash(user_record[2], password):
                    session["user_id"] = user_record[0]
                    session["user"] = user_record[1]
                    return redirect(url_for("index"))
                else:
                    return render_template("login.html", error="Invalid username or password.")
            except Exception as e:
                return render_template("login.html", error=f"Database error: {str(e)}")

        return render_template("login.html")

    @app.route('/register', methods=["GET", "POST"])
    def register():
        if "user" in session:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not username or not email or not password:
                return render_template("register.html", error="All fields are required.")

            if password != confirm_password:
                return render_template("register.html", error="Passwords do not match.")

            if len(password) < 6:
                return render_template("register.html", error="Password must be at least 6 characters.")

            hashed_pw = generate_password_hash(password)

            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (UserName, UserPassword, UserEmail) VALUES (%s, %s, %s)",
                    (username, hashed_pw, email)
                )
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for("login", registered="1"))
            except psycopg2.IntegrityError:
                return render_template("register.html", error="Username or email already exists.")
            except Exception as e:
                return render_template("register.html", error=f"Database error: {str(e)}")

        return render_template("register.html")

    @app.route('/logout')
    def logout():
        session.clear()
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
            fips_results = [
                geo_data["state"]["STATE"],
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

    @app.route('/api/query-suggestion', methods=["POST"])
    def query_suggestion():
        question = request.get_json()['question']
        suggestion = suggest_stats(question)
        return suggestion
        
    @app.route('/api/amenities')
    def amenities():
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        try:
            return jsonify(get_amenities(lat, lng, 1))
        except Exception as e:
            return {"error": str(e)}  
        




    return app