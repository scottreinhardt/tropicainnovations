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
            print(temperature)
            dewpoint = wx_data['current']['dew_point_2m']
            wind_speed = wx_data['current']['wind_speed_10m']
            wind_direction = wx_data['current']['wind_direction_10m']

            # Define city_wx outside of for loop to use later to return in main return outside of the for loop with the other data
            city_wx = None

            # Find the closest point to your current location
            if closest_points_data[0]:
                # The closest point should be the first in the list
                closest_city = find_closest_point(lat, lon)[0]

                with open(file_path, 'r') as file:
                    city_data = json.load('/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json')

                for city, data in city_data["cities"].items():
                    # Bec ause there can be multiple cities with the same name, each key in this dictionary may not be completely unique.
                    # Can get idividual keys by verifying they have the same latitude truncated to the nearest whole number.
                    if city.lower() == closest_city and int(data[0]) == int(lat) and int(data[1]) == int(lon):
                        # Return the weather data calculated in the HRRR model from hrrr_point_forecast.py that is dumped to hrrr_dump.json
                        city_wx = {
                            longitude: data[0],
                            latitude: data[1],
                            state: data[2],
                            postal_code: data[3],
                            temp: data[4],
                            dew: data[5],
                            wx_phenomena: data[6],
                            cloud_cover: data[7],
                            prate: data[8],
                            wind_speed: data[9],
                            wind_direction: data[10]
                        }

            # Create temperature dial used in tropica_home_sandbox.html
            temp_dial = create_wx_dial.create_dial(float(temperature), float(dewpoint), float(wind_speed), float(wind_direction))[0]
            dew_dial = create_wx_dial.create_dial(float(temperature), float(dewpoint), float(wind_speed), float(wind_direction))[1]
            wind_dial = create_wx_dial.create_dial(float(temperature), float(dewpoint), float(wind_speed), float(wind_direction))[2]

            response = {
                "temp_dial": temp_dial,
                "dew_dial": dew_dial,
                "wind_dial": wind_dial,
                "closest_points_weather": closest_points_data
            }

            print(response.api)

            return jsonify(response)

        except Exception as e:
            print(f"Error in root(): {e}")
            return jsonify({"error": str(e)}), 500

    #return render_template("homepsge_test_openmeteo_alljavascript.html")
    return render_template("tropica_home_sandbox.html")
"""

@app.route('/', methods=['GET', 'POST'])
def root():
    HRRR_PATH = "/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json"
    if request.method == 'POST':
        try:
            # --- load once, safely ---
            if not os.path.exists(HRRR_PATH):
                return jsonify({"error": f"HRRR file not found: {HRRR_PATH}"}), 500

            with open(HRRR_PATH, 'r') as f:
                city_data = json.load(f)   # <-- use the file handle, not a string
            data = request.get_json()
            latitude = data.get('lat')
            longitude = data.get('lon')

            if latitude is None or longitude is None:
                return jsonify({"error": "Invalid coordinates"}), 400

            # Convert to float
            lat = float(latitude)
            lon = float(longitude)

            # Get weather for current location
            # weather_json = weather_api_test.get_weather_data(lat, lon)
            #if weather_json is None:
            #    return jsonify({"error": "weather_api_test returned None"}), 500

            # Get info for 5 closest cities
            hour_arr, closest_points_data = find_closest_point(lat, lon)
            if not closest_points_data:
                return jsonify({"error": "No closest cities found"}), 500

            data = request.get_json() or {}
             # Assuming the closest city data is in the form of {city_name: {...}}
            closest_city = next(iter(closest_points_data.keys()))
            closest_city, closest_city_weather = next(iter(closest_points_data.items()))
            if closest_city is None:
                return jsonify({"error": "No closest city found"}), 500
            # List items in dict of the 5 closest cities (including the one closest to the current location), and the weather info.
            city_wx_info = list(data.items())
            #current_location_wx = self.jsonify_current_conditions(
            # Get the weather for the current city, or the first item in the closest_points_data dict
            current_location_wx_arr = city_wx_info[0]
            #build_wx_response(lat, lon)
            # json cleaned up version of current_location_wx_arr
            #current_location_wx_jsonified = jsonify_current_conditions(closest_city, current_location_wx_arr)


            # Get the weather for the rest of the 5 cities
            closest_cities_info = city_wx_info[1:]
            wx_data = requests.get('https://api.open-meteo.com/v1/forecast?latitude='+ str(lat) +'&longitude='+ str(lon) +'&current=weather_code,wind_direction_10m,temperature_2m,dew_point_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,precipitation&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,wind_speed_10m,wind_gusts_10m,wet_bulb_temperature_2m,cape&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto').json()
            temperature = wx_data['current']['temperature_2m']
            dewpoint = wx_data['current']['dew_point_2m']
            wind_speed = wx_data['current']['wind_speed_10m']
            wind_direction = wx_data['current']['wind_direction_10m']

            HRRR_PATH = "/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json"
            if not os.path.exists(HRRR_PATH):
                raise FileNotFoundError(f"HRRR file not found: {HRRR_PATH}")

            hour_arr, closest_points_data = find_closest_point(lat, lon)
            if not closest_points_data:
                raise ValueError("No closest cities found")

            first_city, first_city_wx = next(iter(closest_points_data.items()))
            # Find the current conditions for the city closest to you
            current = jsonify_current_conditions(first_city, first_city_wx)
            hrrr_temp = float(current["current_temp"])
            hrrr_dew  = float(current["current_dew"])
            hrrr_wspd = float(current["wind_speed"])
            wind_direction = current["wind_direction"]
            wind_degrees = float(current["wind_degrees"])

            temp_dial, dew_dial, wind_dial = create_wx_dial.create_dial(
                hrrr_temp, hrrr_dew, hrrr_wspd, wind_degrees
            )
            closest_points_weather = jsonified_5_cities(closest_points_data, hour_arr)
            #print(five_cities_jsonified)
            #closest_points_list = [{"city": name, "wx": wx} for name, wx in closest_points_data.items()]

            response = {
                "temp_dial": temp_dial,
                "dew_dial": dew_dial,
                "wind_dial": wind_dial,
                "closest_points_weather": closest_points_weather,
                "closest_points_wx_data_hrrr": current,
            }
            """
            temp_dial = create_wx_dial.create_dial(float(HRRR_Current_Temp), float(HRRR_Current_Dew), float(HRRR_Current_Wind_Speed), float(wind_degrees))[0]
            dew_dial = create_wx_dial.create_dial(float(HRRR_Current_Temp), float(HRRR_Current_Dew), float(HRRR_Current_Wind_Speed), float(wind_degrees))[1]
            wind_dial = create_wx_dial.create_dial(float(HRRR_Current_Temp), float(HRRR_Current_Dew), float(HRRR_Current_Wind_Speed), float(wind_degrees))[2]

            temp_dial, dew_dial, wind_dial = create_wx_dial.create_dial(
                HRRR_Current_Temp, HRRR_Current_Dew, HRRR_Current_Wind_Speed, wind_degrees
            )

            response = {
                "temp_dial": temp_dial,
                "dew_dial": dew_dial,
                "wind_dial": wind_dial,
                "closest_points_weather": closest_cities_info,
                "closest_points_wx_data_hrrr": current_location_wx_arr,
            }
            """

            return jsonify(response)

        except Exception as e:
            print(f"Error in root(): {e}")
            return jsonify({"error": str(e)}), 500

    #return render_template("homepsge_test_openmeteo_alljavascript.html")
    return render_template("tropica_home_sandbox.html")

# Takes the first input from the data array, which is a dict of the weather for the 5 closest locations to you with the first entry being the current location
# Takes a confusing current conditions input and
def jsonify_current_conditions(city_name, current_location_wx):
    # turn self.cityLocations[city_name] = [lat, lon, state, postal_code, temp, dew, wx_phenom, cloud_cover, prate, wind_speed, wind_direction] into json for readability and for ease of access when using this data
    # current_location_wx[6][0] gets the current weather code, which you need to convert to the text description and the url to the icon
    wx_description = wx_condition_to_url_map(current_location_wx[6][0])[0]
    wx_icon_url = wx_condition_to_url_map(current_location_wx[6][0])[1]
    # Seperate Wind Direction from wind Degrees
    # This returns a special "view" object of the dictionary's key-value pairs:
    # next() returns the next key, value pair from the object
    wind_direction, wind_degrees =  next(iter(current_location_wx[10][0].items()))
    current_conditions = {
        "city_name": city_name,
        "latitude": current_location_wx[0],
        "longitude": current_location_wx[1],
        "state": current_location_wx[2],
        "postal_code": current_location_wx[3],
        "current_temp": current_location_wx[4][0],
        "current_dew": current_location_wx[5][0],
        "wx_phenomena_description": wx_description,
        "wx_phenomena_url": wx_icon_url,
        "cloud_cover": current_location_wx[7][0],
        "prate": current_location_wx[8][0],
        "wind_speed": current_location_wx[9][0],
        "wind_direction": wind_direction,
        "wind_degrees": wind_degrees
    }

    return current_conditions

def jsonified_5_cities(closest_points_data, hour_arr):
    out = {}

    for city, wx in closest_points_data.items():
        lat, lon, state, zipcode = wx[0], wx[1], wx[2], wx[3]
        temps        = wx[4]
        dews         = wx[5]
        wx_codes     = wx[6]
        cloud_cover  = wx[7]
        prate        = wx[8]
        wind_speed   = wx[9]
        wind_dir_obj = wx[10]  # list of dicts like {'North East': 63.43}

        city_obj = {
            "city_name": city,
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "zip_code": zipcode,
            "hourly": []
        }

        for hour, t, d, code, cloud, p, wspd, wdir in zip(
            hour_arr, temps, dews, wx_codes, cloud_cover, prate, wind_speed, wind_dir_obj
        ):
            # parse wind direction dict with single key:value
            dir_name, dir_deg = (None, None)
            if isinstance(wdir, dict) and wdir:
                dir_name, dir_deg = next(iter(wdir.items()))

            desc, icon_url = wx_condition_to_url_map(code)

            city_obj["hourly"].append({
                "hour": hour,             # e.g., "2025-08-12T10:00-04:00" or 10
                "temp": t,
                "dew": d,
                "wx_code": code,
                "wx_desc": desc,
                "wx_icon": icon_url,
                "cloud_cover": cloud,
                "prate": p,
                "wind_speed": wspd,
                "wind_dir_text": dir_name,
                "wind_dir_deg": dir_deg
            })

        out[city] = city_obj

    return out
def build_wx_response(lat: float, lon: float) -> dict:
    """
    Does all the work and returns a plain dict.
    Raise exceptions on hard failures so callers can see where it blew up.
    """
    # 1) Load HRRR
    HRRR_PATH = "/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json"
    if not os.path.exists(HRRR_PATH):
        raise FileNotFoundError(f"HRRR file not found: {HRRR_PATH}")
    with open(HRRR_PATH, "r") as f:
        _ = json.load(f)  # keep if you need it

    # 2) Closest points
    closest_points = find_closest_point(lat, lon)
    if not closest_points:
        raise RuntimeError("No closest cities found")
    closest_city, current_arr = next(iter(closest_points.items()))

    # 3) HRRR → readable current
    current_hrrr = jsonify_current_conditions(closest_city, current_arr)

    # 4) Live Open-Meteo
    wx = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params=dict(
            latitude=lat, longitude=lon,
            current="weather_code,wind_direction_10m,temperature_2m,dew_point_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,precipitation",
            daily="weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max",
            temperature_unit="fahrenheit", wind_speed_unit="mph", timezone="auto"
        ),
        timeout=15
    )
    wx.raise_for_status()
    api = wx.json()
    current = api.get("current", {})

    # 5) Dial inputs (use HRRR first; fall back to API)
    h_temp = float(current_hrrr.get("current_temp", current.get("temperature_2m", 0.0)))
    h_dew  = float(current_hrrr.get("current_dew", current.get("dew_point_2m", 0.0)))
    h_wspd = float(current_hrrr.get("wind_speed", current.get("wind_speed_10m", 0.0)))
    wdir = current_hrrr.get("wind_direction", current.get("wind_direction_10m", 0.0))
    if isinstance(wdir, dict) and wdir:
        wind_degrees = float(next(iter(wdir.values())))
    else:
        wind_degrees = float(wdir) if isinstance(wdir, (int, float, str)) else 0.0

    temp_dial, dew_dial, wind_dial = create_wx_dial.create_dial(h_temp, h_dew, h_wspd, wind_degrees)

    response =  {
        "temp_dial": temp_dial,
        "dew_dial": dew_dial,
        "wind_dial": wind_dial,
        "closest_points_weather": closest_points,
        "closest_points_wx_data_hrrr": current_hrrr,
        "api_current": current
    }
    print(response)
    return response
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
# Takes the first input from the data array, which is a dict of the weather for the 5 closest locations to you with the first entry being the current location
# Takes a confusing current conditions input and
def jsonify_currentconditions(city_name, current_location_wx):
    # turn self.cityLocations[city_name] = [lat, lon, state, postal_code, temp, dew, wx_phenom, cloud_cover, prate, wind_speed, wind_direction] into json for readability and for ease of access when using this data
    # current_location_wx[6][0] gets the current weather code, which you need to convert to the text description and the url to the icon
    wx_description = wx_condition_to_url_map(current_location_wx[6][0])[0]
    wx_icon_url = wx_condition_to_url_map(current_location_wx[6][0])[1]
    current_conditions = {
        "city_name": city_name,
        "latitude": current_location_wx[0],
        "longitude": current_location_wx[1],
        "state": current_location_wx[2],
        "postal_code": current_location_wx[3],
        "current_temp": current_location_wx[4][0],
        "current_dew": current_location_wx[5][0],
        "wx_phenomena_description": wx_description,
        "wx_phenomena_url": wx_icon_url,
        "cloud_cover": current_location_wx[7][0],
        "prate": current_location_wx[8][0],
        "wind_speed": current_location_wx[9][0],
        "wind_direction": current_location_wx[10][0]
    }

    return current_conditions

# Takes in a list of integers that represent the weather condition (eg 0: sunny, 1: mostly sunny).
def wx_condition_to_url_map(location_wx_icon_num_int):
    open_meteo_weather_codes = {
        0: ["Clear sky", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0001_sunny.png"],
        1: ["Mainly clear", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0002_sunny_intervals.png"],
        2: ["Partly cloudy", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0043_mostly_cloudy.png"],
        3: ["Overcast", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0003_white_cloud.png"],
        45: ["Fog", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0007_fog.png"],
        48: ["Depositing rime fog", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0047_freezing_fog.png"],
        51: ["Light drizzle", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0048_drizzle.png"],
        53: ["Moderate drizzle", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0048_drizzle.png"],
        55: ["Dense drizzle", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0081_heavy_drizzle.png"],
        56: ["Light freezing drizzle", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0049_freezing_drizzle.png"],
        57: ["Dense freezing drizzle", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0049_freezing_drizzle.png"],
        61: ["Slight rain", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0017_cloudy_with_light_rain.png"],
        63: ["Moderate rain", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0017_cloudy_with_light_rain.png"],
        65: ["Heavy rain", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0051_extreme_rain.png"],
        66: ["Light freezing rain", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0049_freezing_drizzle.png"],
        67: ["Heavy freezing rain", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0050_freezing_rain.png"],
        71: ["Light snow", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0019_cloudy_with_light_snow.png"],
        73: ["Moderate snow", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0019_cloudy_with_light_snow.png"],
        75: ["Heavy snow", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0020_cloudy_with_heavy_snow.png"],
        77: ["Snow grains", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0053_blowing_snow.png"],
        80: ["Slight rain showers", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0009_light_rain_showers.png"],
        81: ["Moderate rain showers", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0009_light_rain_showers.png"],
        82: ["Heavy rain showers", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0010_heavy_rain_showers.png"],
        85: ["Light snow showers", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0011_light_snow_showers.png"],
        86: ["Heavy snow showers", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0012_heavy_snow_showers.png"],
        95: ["Thunderstorm", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0024_thunderstorms.png"],
        96: ["Thunderstorm with slight hail", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0059_thunderstorms_with_hail.png"],
        99: ["Thunderstorm with heavy hail", "https://www.pythonanywhere.com/user/tropicainnovations/files/home/tropicainnovations/mysite/static/icons/MAm-WeatherIcons-MS02e/icons/PNGs_256x256/wsymbol_0015_heavy_hail_showers.png"]
    }
    # Given the weather code, generated from the hrrr_dump.json file, return the associated weather condition with the url to the url in the static folder in array form.
    wx_description_url = open_meteo_weather_codes[int(location_wx_icon_num_int)]

    return wx_description_url

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
