from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
from scraper import *
from corrected_scraper import *
from flask import jsonify
import os
import webbrowser
from geopy.geocoders import Nominatim
from weather_api_test import *
import weather_api_test
import create_wx_dial
import requests
import json


import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from openmeteo_sdk.Variable import Variable
from flask import Flask, request, jsonify
from flask_cors import CORS

from find_closest_points import find_closest_point

app = Flask(__name__)

# Allow all origins (for debugging)
CORS(app, supports_credentials=True)

# OR: Allow only your specific frontend domain
CORS(app, resources={r"/*": {"origins": "https://tropicainnovations.pythonanywhere.com"}}, supports_credentials=True)

@app.route('/results')
def results():
    scraper = DashBoard()
    scraper.run()

    return render_template('results.html', proxies=scraper.results)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/splash', methods=['GET', 'POST'])
def splash():
    return render_template('splash.html')

"""
@app.route('/myweather', methods=['GET', 'POST'])
def myweather():
    if request.method == "POST":
        #form = enduserlocation()
        #location = request.form['location']
        # getting input with name = fname in HTML form
        location = request.form.get("location")
        print(location)
        # calling the Nominatim tool
        loc = Nominatim(user_agent="enduser")
        # entering the location name
        getLoc = loc.geocode(location)
        lat = getLoc.latitude
        lon = getLoc.longitude
        #print(lat)
        scraper = ProxyScraper()
        results = scraper.fetch_data()
        scraper.parse_data()
        scraper.generate_map()
        #return "Your name is " + lat + lon
        return render_template('myweather.html', lat=lat, lon=lon)
    return render_template('myweather.html')
    #return render_template('home.html')
"""
"""
@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        print("hello")
        data = request.get_json()
        print("Received POST data:", data)  # Debugging line
        latitude = data.get('lat')
        longitude = data.get('lon')
        print(f'{latitude},{longitude}')

        if latitude is None or longitude is None:
            return jsonify({"error": "Invalid coordinates"}), 400

        weather_json = weather_api_test.get_weather_data(latitude, longitude)
        print("Weather JSON being sent:", weather_json)  # Debugging
        return jsonify(weather_json)
    #return render_template('home.html')
    return render_template("adding_to_template.html")
"""
"""
@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        try:
            data = request.get_json()
            latitude = data.get('lat')
            longitude = data.get('lon')

            if latitude is None or longitude is None:
                return jsonify({"error": "Invalid coordinates"}), 400
             # Find and fetch info for 5 closest points
            closest_five_points_info = find_closest_point(float(latitude), float(longitude))
            print(weather_json)
            if weather_json is None:
                return jsonify({"error": "weather_api_test returned None"}), 500
            print("Weather JSON being sent:", weather_json)
            # Combine both results
            response = {
                "current_location_weather": weather_json,
                "closest_points_weather": closest_five_points_info
            }
            return jsonify(response)
        except Exception as e:
            print(f"Error processing request: {e}")
            print(weather_json)
            return jsonify({"error": str(e)}), 500

    return render_template("homepsge_test_openmeteo_alljavascript.html")
    #return render_template("test_home.html")
"""

@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        try:
            data = request.get_json()
            latitude = data.get('lat')
            longitude = data.get('lon')

            if latitude is None or longitude is None:
                return jsonify({"error": "Invalid coordinates"}), 400

            # Convert to float
            lat = float(latitude)
            lon = float(longitude)

            # Get weather for current location
            #weather_json = weather_api_test.get_weather_data(lat, lon)
            #if weather_json is None:
            #    return jsonify({"error": "weather_api_test returned None"}), 500

            # Get info for 5 closest cities
            closest_points_data = find_closest_point(lat, lon)
            wx_data = requests.get('https://api.open-meteo.com/v1/forecast?latitude='+ str(lat) +'&longitude='+ str(lon) +'&current=weather_code,wind_direction_10m,temperature_2m,dew_point_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,precipitation&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,wind_speed_10m,wind_gusts_10m,wet_bulb_temperature_2m,cape&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto').json()
            temperature = wx_data['current']['temperature_2m']
            dewpoint = wx_data['current']['dew_point_2m']
            wind_speed = wx_data['current']['wind_speed_10m']
            wind_direction = wx_data['current']['wind_direction_10m']

            temp_dial = create_wx_dial.create_dial(float(temperature), float(dewpoint), float(wind_speed), float(wind_direction))[0]
            dew_dial = create_wx_dial.create_dial(float(temperature), float(dewpoint), float(wind_speed), float(wind_direction))[1]
            wind_dial = create_wx_dial.create_dial(float(temperature), float(dewpoint), float(wind_speed), float(wind_direction))[2]


            response = {
                "temp_dial": temp_dial,
                "dew_dial": dew_dial,
                "wind_dial": wind_dial,
                "closest_points_weather": closest_points_data
            }

            return jsonify(response)

        except Exception as e:
            print(f"Error in root(): {e}")
            return jsonify({"error": str(e)}), 500

    #return render_template("homepsge_test_openmeteo_alljavascript.html")
    return render_template("tropica_home_sandbox.html")

"""
@app.route('/', methods=['POST', 'OPTIONS'])
def root():
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add("Access-Control-Allow-Origin", "https://tropicainnovations.pythonanywhere.com")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200

    data = request.get_json()
    latitude = data.get('lat')
    longitude = data.get('lon')

    if latitude is None or longitude is None:
        return jsonify({"error": "Invalid coordinates"}), 400

    weather_json = weather_api_test.get_weather_data(latitude, longitude)

    response = jsonify(weather_json)
    response.headers.add("Access-Control-Allow-Origin", "https://tropicainnovations.pythonanywhere.com")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200
    """
@app.route('/getlocation', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    return jsonify({"latitude": latitude, "longitude": longitude})

@app.route('/model_maps')
def model_maps():
    return render_template('model_maps.html')

@app.route('/tropicahome')
def tropica_home():
    return render_template('Homepage_tropica_sandbox.html')
@app.route('/myweathergfs')
def my_weather_gfs():
    return render_template('create_model_point_forecast_map.html')

@app.route('/myweathergfs')
def my_weather_hrrr():
    return render_template('xreate_forecast_model_map_gfs.html')

@app.route('/radar')
def radar():
    # Create a Folium map centered on the Continental United States
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    # Add the animated weather GIF as an image overlay
    image_url = 'https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif'
    folium.raster_layers.ImageOverlay(
        name='Weather Animation',
        image=image_url,
        bounds=[[24.396308, -125.0], [49.384358, -66.93457]],
        opacity=0.6
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save the map to an HTML file
    m.save('gotime.html')

    return render_template('gotime.html')

from flask import request, render_template
import folium

@app.route('/map')
def map():
    return send_from_directory('/home/tropicainnovations/mysite/static/METAR_map', 'airport_metar_map.html')
"""
@app.route('/map')
def map():
    #return render_template('map.html')
    return send_from_directory('/home/tropicainnovations/', 'airport_metar_map.html')
"""

@app.route('/map1')
def radar_map():
    return send_from_directory('/home/tropicainnovations/', 'airport_metar_map1.html')