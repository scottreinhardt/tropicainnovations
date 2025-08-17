from sklearn.neighbors import BallTree
import numpy as np
import json
import os


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


def find_closest_point(lat, lon):
    # Retrieve current latitude and longitude from the javascript
    current_lat = lat
    current_lon = lon

    file_name = '/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json'

    # load the json file containing all 147,000 cities (gfs_dump.json)
    with open(file_name) as f:
        data = json.load(f)

    # Convert to list of (lat, lon) and names
    locations = []
    names = []

    for city, info in data['cities'].items():
        # Append the [lat, lon] (info[0] and info[1]) as an item in the locations list
        locations.append([info[0], info[1]])
        # Append each city name to a list of city names (corrosponding to the index of the lat and lon in the locations array.)
        names.append(city)
    # This produces a dict like this:
    # {"valid_hrs_dt": {"4": "2025-08-08 17:00:00", "5": "2025-08-08 18:00:00", "6": "2025-08-08 19:00:00", "7": "2025-08-08 20:00:00", "8": "2025-08-08 21:00:00", "9": "2025-08-08 22:00:00", "10": "2025-08-08 23:00:00", "11": "2025-08-09 00:00:00", "12": "2025-08-09 01:00:00", "13": "2025-08-09 02:00:00", "14": "2025-08-09 03:00:00",
    hours = data["valid_hrs_dt"]
    hour_arr = []
    # Loop through all of the keys (hours in the dict)
    for hour in hours.values():
        # Append all of the hours into a static list
        hour_arr.append(hour)
    # Convert to radians for BallTree (uses haversine)
    locations_rad = np.radians(locations)
    your_point = np.radians([[current_lat, current_lon]])

    # Build BallTree
    tree = BallTree(locations_rad, metric='haversine')

    # Query for 5 nearest neighbors
    dists, indices = tree.query(your_point, k=6)

    # Keep track of the cities with the closest name
    closest_city_names = []

    # Convert distance from radians to kilometers
    earth_radius_km = 6371
    for i, idx in enumerate(indices[0]):
        dist_km = dists[0][i] * earth_radius_km
        closest_city_names.append(names[idx])
        #print(f"{names[idx]}: {dist_km:.2f} km")

    # Make a dictionary to hold the list of weather information from each closest city
    closest_cities_info = {}

    # Load the original complete dict with the cities (gfs_dump.json)
    original_data = data['cities']
    # loop through closest_city_data
    for city_name in closest_city_names:
        # Get the value from the city in the original dictionary containing the weather infomation
        city_info = original_data[city_name]
        closest_cities_info[city_name] = city_info

    #print(build_wx_response(lat, lon))
    return (hour_arr, closest_cities_info)

def build_wx_response(lat, lon):
    HRRR_PATH = "/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json"
    if not os.path.exists(HRRR_PATH):
        raise FileNotFoundError(f"HRRR file not found: {HRRR_PATH}")

    # (You load the file here but don't use city_data; fine to remove if unused)
    # with open(HRRR_PATH, 'r') as f:
    #     city_data = json.load(f)

    hour_arr, closest_points_data = find_closest_point(lat, lon)
    if not closest_points_data:
        raise ValueError("No closest cities found")

    first_city, first_city_wx = next(iter(closest_points_data.items()))
    current = jsonify_current_conditions(first_city, first_city_wx)
    hrrr_temp = float(current["current_temp"])
    hrrr_dew  = float(current["current_dew"])
    hrrr_wspd = float(current["wind_speed"])
    wind_degrees = current["wind_direction"]

    temp_dial, dew_dial, wind_dial = create_wx_dial.create_dial(
        hrrr_temp, hrrr_dew, hrrr_wspd, wind_degrees
    )
    closest_points_weather = jsonified_5_cities(closest_points_data, hour_arr)
    #print(five_cities_jsonified)
    closest_points_list = [{"city": name, "wx": wx} for name, wx in closest_points_data.items()]

    return {
        "temp_dial": temp_dial,
        "dew_dial": dew_dial,
        "wind_dial": wind_dial,
        "closest_points_weather": closest_points_weather,
        "closest_points_wx_data_hrrr": current,
    }
# Takes the first input from the data array, which is a dict of the weather for the 5 closest locations to you with the first entry being the current location
# Takes a confusing current conditions input and
def jsonify_current_conditions(city_name, current_location_wx):
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
"""
def jsonified_5_cities(closest_points_data, hour_arr):

    json_5_cities = {}
    temp_json = {}
    dew_json = {}
    wx_descriptions_json = {}
    wx_urls_json = {}
    cloud_cover_json = {}
    prate_json = {}
    wind_speed_json = {}
    wind_direction_description_json = {}
    wind_direction_degrees_json = {}

    for city, wx in closest_points_data.items():
        temp_json = {}
        for temp, hour in zip(wx[4], hour_arr):
            temp_json[hour] = temp
        for dew, hour in zip(wx[5], hour_arr):
            dew_json[hour] = dew
        for wx_phenom, hour in zip(wx[6], hour_arr):
            wx_description[hour] = wx_condition_to_url_map(wx_phenom)[0]
            wx_urls_json[hour] = wx_condition_to_url_map(wx_phenom)[1]
        for cloud_cover, hour in zip(wx[7], hour_arr):
            cloud_cover_json[hour] = cloud_cover
        for prate, hour in zip(wx[8], hour_arr):
            prate_json[hour] = prate
        for wind_speed, hour in zip(wx[9], hour_arr):
            wind_speed_json[hour] = wind_speed
        for wind_direction, hour in zip(wx[10], hour_arr):
            wind_direction_description_json[hour] = wind_direction
            wind_direction_degrees_json[hour] = wind_direction





        json_5_cities["city_name"] = city
        json_5_cities["state"] = wx[2]
        json_5_cities["latitude"] = wx[0]
        json_5_cities["longitude"] = wx[1]
        json_5_cities["zip_code"] = wx[3]
        json_5_cities["temp_arr"] = temp_json
        json_5_cities["dew_arr"] = dew_json
        json_5_cities["wx_phenom_description"] = wx_description_json
        json_5_cities["wx_phenom_description"] = wx_url_json
        json_5_cities["prate"] = prate_json
        json_5_cities["wind_speed"] = wind_speed_json
        json_5_cities["wind_direction"] = wx[9]
    return json_5_cities
    #closest_points_list = [{"city": name, "wx": wx} for name, wx in closest_points_data.items()]
"""
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
"""
if __name__ == "__main__":
    lat = 42.2110562502361
    lon = -70.76194745371187
    payload = build_wx_response(lat, lon)
    print(json.dumps(payload, indent=2))
"""


dict_locations = find_closest_point(42.2110562502361, -70.76194745371187)
"""
print(dict_locations)
for name, info in dict_locations.items():
    print(info)
"""

