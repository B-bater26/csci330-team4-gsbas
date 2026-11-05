from flask import Flask, render_template, jsonify, request
from app.geocoder import get_address_result

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/api/geocode')
    def geocode():
        address = request.args.get('address')
        result = get_address_result(address)
        return jsonify(str(result))

    return app
