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

    @app.route('/comparison')
    def comparison():
        if "user" not in session:
            return redirect(url_for("login"))
        return render_template("comparison.html")

    # Saved Analyses & Symbology Customizer Page
    @app.route('/history')
    def history():
        if "user" not in session or "user_id" not in session:
            return redirect(url_for("login"))

        user_id = session["user_id"]
        saved_analyses = []

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    aq.AnalysisID,
                    aq.AnalysisDate,
                    sl.SavedLocAddress,
                    sl.SavedLocCity,
                    sl.SavedLocState,
                    sl.SavedLocZip,
                    sl.SavedLocRadius,
                    ve.VisShape,
                    ve.VisColor,
                    ve.VisScale,
                    ve.VisSymbol
                FROM analysis_query aq
                JOIN saved_location sl ON aq.SavedLocationID = sl.SavedLocationID
                LEFT JOIN visual_element ve ON aq.AnalysisID = ve.AnalysisID
                WHERE sl.UserID = %s
                ORDER BY aq.AnalysisDate DESC
            """, (user_id,))
            rows = cur.fetchall()

            for row in rows:
                analysis_id = row[0]
                cur.execute(
                    "SELECT StatName, StatValue FROM analysis_result WHERE AnalysisID = %s",
                    (analysis_id,)
                )
                stats = [{"name": s[0], "value": s[1]} for s in cur.fetchall()]

                saved_analyses.append({
                    "analysis_id": analysis_id,
                    "date": row[1].strftime("%Y-%m-%d %H:%M") if row[1] else "",
                    "address": row[2] or f"{row[3] or ''}, {row[4] or ''} {row[5] or ''}".strip(", "),
                    "city": row[3] or "",
                    "state": row[4] or "",
                    "zip": row[5] or "",
                    "radius": float(row[6]) if row[6] is not None else 10.0,
                    "visual": {
                        "shape": row[7] or "circle",
                        "color": row[8] or "#cc3333",
                        "scale": float(row[9]) if row[9] is not None else 1.0,
                        "symbol": row[10] or "storefront"
                    },
                    "stats": stats
                })

            cur.close()
            conn.close()
        except Exception as e:
            return render_template("history.html", analyses=[], error=str(e))

        return render_template("history.html", analyses=saved_analyses)

    # --- FR-03: Save Current Location, Query, Results & Default Symbology ---
    @app.route('/api/save-analysis', methods=["POST"])
    def save_analysis():
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401

        data = request.get_json() or {}
        address = data.get("address", "").strip()
        radius = data.get("radius", 10)
        outputs = data.get("outputs", {})

        if not address:
            return jsonify({"error": "Please search an address before saving."}), 400

        parts = [p.strip() for p in address.split(",")]
        city = parts[1] if len(parts) > 1 else ""
        state = parts[2] if len(parts) > 2 else ""
        zip_code = parts[3] if len(parts) > 3 else ""

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO saved_location (UserID, SavedLocAddress, SavedLocCity, SavedLocState, SavedLocZip, SavedLocRadius)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING SavedLocationID
            """, (session["user_id"], address, city, state, zip_code, radius))
            saved_loc_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO analysis_query (SavedLocationID)
                VALUES (%s)
                RETURNING AnalysisID
            """, (saved_loc_id,))
            analysis_id = cur.fetchone()[0]

            for key, val in outputs.items():
                if isinstance(val, dict):
                    for sub_k, sub_v in val.items():
                        if sub_v is not None:
                            cur.execute(
                                "INSERT INTO analysis_result (AnalysisID, StatName, StatValue) VALUES (%s, %s, %s)",
                                (analysis_id, sub_k, str(round(float(sub_v), 2)))
                            )
                elif val is not None:
                    cur.execute(
                        "INSERT INTO analysis_result (AnalysisID, StatName, StatValue) VALUES (%s, %s, %s)",
                        (analysis_id, key, str(round(float(val), 2)))
                    )

            cur.execute("""
                INSERT INTO visual_element (AnalysisID, VisShape, VisColor, VisScale, VisSymbol)
                VALUES (%s, %s, %s, %s, %s)
            """, (analysis_id, "circle", "#cc3333", 1.0, "storefront"))

            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True, "analysis_id": analysis_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- FR-01: Update & Persist Visual Symbology Elements ---
    @app.route('/api/visual/<int:analysis_id>', methods=["POST"])
    def update_visual(analysis_id):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401

        data = request.get_json() or {}
        vis_shape = data.get("shape", "circle")
        vis_color = data.get("color", "#cc3333")
        vis_scale = float(data.get("scale", 1.0))
        vis_symbol = data.get("symbol", "storefront")

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE visual_element
                SET VisShape = %s, VisColor = %s, VisScale = %s, VisSymbol = %s
                WHERE AnalysisID = %s
            """, (vis_shape, vis_color, vis_scale, vis_symbol, analysis_id))

            if cur.rowcount == 0:
                cur.execute("""
                    INSERT INTO visual_element (AnalysisID, VisShape, VisColor, VisScale, VisSymbol)
                    VALUES (%s, %s, %s, %s, %s)
                """, (analysis_id, vis_shape, vis_color, vis_scale, vis_symbol))

            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Delete a Saved Analysis Entries
    @app.route('/api/analysis/<int:analysis_id>', methods=["DELETE"])
    def delete_analysis(analysis_id):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM saved_location
                WHERE SavedLocationID = (
                    SELECT SavedLocationID FROM analysis_query WHERE AnalysisID = %s
                ) AND UserID = %s
            """, (analysis_id, session["user_id"]))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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