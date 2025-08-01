import requests
import csv
import re
import urllib
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import folium
import time
import xmltodict
import math
import io
from geopy.geocoders import Nominatim
import requests
import csv
import io
import json
import os

from datetime import datetime, timezone, timedelta
from astral import Observer
from astral.sun import sun
from astral import LocationInfo

import traceback
import sys
import math

import random

class ProxyScraper:
    results = []
    def __init__(self):
        self.station_url = 'https://aviationweather.gov/data/cache/stations.cache.json'
        self.url = 'https://aviationweather.gov/data/cache/metars.cache.csv'
        self.superDict = {}
        self.stations = []
        self.metars = []
        self.airportLocations = {}
        self.cityInfo = {}

    def read_json(self, file_path):
        try:
            with open(file_path, 'r') as file:
                city_data = json.load(file)
                return city_data
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")

    def fetch_station_data(self):
        try:
            #data = json.loads('https://aviationweather.gov/data/cache/stations.cache.json')
            response = requests.get(self.station_url)
            response.raise_for_status()
            data = response.json()

            # Correctly parse stations from the JSON
            for station_id, station_info in data.items():
                self.stations.append(station_info['site'])
            #for item in data:
            #    print(item["site"])
            #response = requests.get(self.station_url)
            #response.raise_for_status()
            #data = response.json()['stations']
            #self.stations = [station['site'] for station in data.values()]
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def fetch_data(self, test_mode, icao_input):
        try:
            if test_mode:
                # Fetch all METARs from the FAA CSV
                response = requests.get("https://aviationweather.gov/data/cache/metars.cache.csv")
                response.raise_for_status()
                all_metars = response.text.splitlines()

                # Find the line that starts with the desired ICAO
                matching_line = next((line for line in all_metars if line.startswith(icao_input)), None)
                if not matching_line:
                    print(f"❌ No METAR found for {icao_input}")
                    return

                self.csv_data = matching_line  # Use this line as the only row to parse

                # Also grab airport info from GitHub CSV
                #airport_response = requests.get("https://raw.githubusercontent.com/ip2location/ip2location-iata-icao/master/iata-icao.csv")
                with open('/home/tropicainnovations/mysite/static/gfs_dump/gfs_dump.json') as cities:
                    city_data = json.load(cities)
                    #print(list_of_airports)
                    """
                    for city_info in city_data:
                        city_name = city_info.get("city")
                        lat = city_info.get("lat")
                        lon = city_info.get("lon")
                        country = city_info.get("country")
                        population = city_info.get("population")
                        elevation = city_info.get("elevation")
                        timezone = city_info.get("timezone")
                        temp_dict = city_info.get("temperature_dict", {})
                        dewpoint_dict = city_info.get("dewpoint_dict", {})
                        cc_dict = city_info.get("cc_dict", {})

                        self.cityInfo[city_name] = [lat, lon, elevation, city_name, elevation, country, temp_dict, dewpoint_dict, cc_dict]
                    """
                    for city_name, city_info in city_data.items():
                        lat = city_info[0]
                        lon = city_info[1]
                        country = city_info[2]
                        population = city_info[3]
                        elevation = city_info[4]  # May be None
                        timezone = city_info[5]
                        temp_dict = city_info[6]
                        dewpoint_dict = city_info[7]
                        cc_dict = city_info[8]

                        self.cityInfo[city_name] = [lat, lon, elevation, city_name, "", country, temp_dict, dewpoint_dict, cc_dict]
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    def get_color(self, temperature):
        if temperature >= 115.0:
            return '#FF69B4'  # Hot Pink
        if temperature >= 110.0:
            return '#400000'  # Really Dark Red
        elif temperature >= 105.0:
            return '#800000'  # Dark Red
        if temperature >= 100.0:
            return '#FF0000'  # Red
        elif temperature >= 95.0:
            return '#FF4500'  # OrangeRed
        elif temperature >= 90.0:
            return '#FF6347'  # Tomato
        elif temperature >= 85.0:
            return '#FF8C00'  # DarkOrange
        elif temperature >= 80.0:
            return '#FFA500'  # Orange
        elif temperature >= 75.0:
            return '#FFD700'  # Gold
        elif temperature >= 70.0:
            return '#FFFF00'  # Yellow
        elif temperature >= 65.0:
            return '#ADFF2F'  # GreenYellow
        elif temperature >= 60.0:
            return '#7FFF00'  # Chartreuse
        elif temperature >= 55.0:
            return '#00FF00'  # Lime
        elif temperature >= 50.0:
            return '#32CD32'  # LimeGreen
        elif temperature >= 45.0:
            return '#00FA9A'  # MediumSpringGreen
        elif temperature >= 40.0:
            return '#00FFFF'  # Cyan
        elif temperature >= 35.0:
            return '#1E90FF'  # DodgerBlue
        elif temperature >= 30.0:
            return '#0000FF'  # Blue
        elif temperature >= 25.0:
            return '#8A2BE2'  # BlueViolet
        elif temperature >= 20.0:
            return '#9400D3'  # DarkViolet
        elif temperature >= 15.0:
            return '#9932CC'  # DarkOrchid
        elif temperature >= 10.0:
            return '#8B008B'  # DarkMagenta
        elif temperature >= 5.0:
            return '#FF00FF'  # Magenta
        elif temperature >= 0.0:
            return '#FF1493'  # DeepPink
        elif temperature >= -5.0:
            return '#FF69B4'  # HotPink
        elif temperature >= -10.0:
            return '#DB7093'  # PaleVioletRed
        elif temperature >= -15.0:
            return '#C71585'  # MediumVioletRed
        elif temperature >= -20.0:
            return '#DC143C'  # Crimson
        elif temperature >= -25.0:
            return '#B22222'  # FireBrick
        elif temperature >= -30.0:
            return '#A52A2A'  # Brown
        elif temperature >= -35.0:
            return '#800000'  # Maroon
        elif temperature >= -40.0:
            return '#000000'  # Black
        else:
            return '#000000'  # Default to Black


    def get_gradient_window(self, temp_f):
        temp_min = max(-40, temp_f - 10)
        temp_max = min(115, temp_f + 10)
        total_range = temp_max - temp_min

        color_steps = {
            115: '#FF69B4', 110: '#400000', 105: '#800000',
            100: '#FF0000', 95: '#FF4500', 90: '#FF6347',
            85: '#FF8C00', 80: '#FFA500', 75: '#FFD700',
            70: '#FFFF00', 65: '#ADFF2F', 60: '#7FFF00',
            55: '#00FF00', 50: '#32CD32', 45: '#00FA9A',
            40: '#00FFFF', 35: '#1E90FF', 30: '#0000FF',
            25: '#8A2BE2', 20: '#9400D3', 15: '#9932CC',
            10: '#8B008B', 5: '#FF00FF', 0: '#FF1493',
            -5: '#FF69B4', -10: '#DB7093', -15: '#C71585',
            -20: '#DC143C', -25: '#B22222', -30: '#A52A2A',
            -35: '#800000', -40: '#000000'
        }

        sorted_temps = sorted(color_steps.keys(), reverse=True)

        gradient_stops = []
        for t in sorted_temps:
            if temp_min <= t <= temp_max:
                pct = round(((t - temp_min) / total_range) * 100, 1)
                gradient_stops.append(f"{color_steps[t]} {pct}%")

        if not gradient_stops:
            return "linear-gradient(to right, #000000 0%, #FFFFFF 100%)"

        return "linear-gradient(to right, " + ", ".join(reversed(gradient_stops)) + ")"

    def get_gradient_window_map(self, temp_f):
        temp_min = max(-40, temp_f - 10)
        temp_max = min(115, temp_f + 10)
        total_range = temp_max - temp_min

        color_steps = {
            115: '#FF69B4', 110: '#400000', 105: '#800000',
            100: '#FF0000', 95: '#FF4500', 90: '#FF6347',
            85: '#FF8C00', 80: '#FFA500', 75: '#FFD700',
            70: '#FFFF00', 65: '#ADFF2F', 60: '#7FFF00',
            55: '#00FF00', 50: '#32CD32', 45: '#00FA9A',
            40: '#00FFFF', 35: '#1E90FF', 30: '#0000FF',
            25: '#8A2BE2', 20: '#9400D3', 15: '#9932CC',
            10: '#8B008B', 5: '#FF00FF', 0: '#FF1493',
            -5: '#FF69B4', -10: '#DB7093', -15: '#C71585',
            -20: '#DC143C', -25: '#B22222', -30: '#A52A2A',
            -35: '#800000', -40: '#000000'
        }

        sorted_temps = sorted(color_steps.keys())
        gradient_map = {}

        for t in sorted_temps:
            if temp_min <= t <= temp_max:
                pct = round(((t - temp_min) / total_range) * 100, 1)
                gradient_map[f"{pct}%"] = color_steps[t]

        return gradient_map

    def get_conic_gradient_arc(self, temp_f):
        temp_min = max(-40, temp_f - 10)
        temp_max = min(115, temp_f + 10)
        total_range = temp_max - temp_min

        color_steps = {
            115: '#FF69B4', 110: '#400000', 105: '#800000',
            100: '#FF0000', 95: '#FF4500', 90: '#FF6347',
            85: '#FF8C00', 80: '#FFA500', 75: '#FFD700',
            70: '#FFFF00', 65: '#ADFF2F', 60: '#7FFF00',
            55: '#00FF00', 50: '#32CD32', 45: '#00FA9A',
            40: '#00FFFF', 35: '#1E90FF', 30: '#0000FF',
            25: '#8A2BE2', 20: '#9400D3', 15: '#9932CC',
            10: '#8B008B', 5: '#FF00FF', 0: '#FF1493',
            -5: '#FF69B4', -10: '#DB7093', -15: '#C71585',
            -20: '#DC143C', -25: '#B22222', -30: '#A52A2A',
            -35: '#800000', -40: '#000000'
        }

        def get_thermometer_svg_values(self, temp_f):
            """
            Given a temperature in Fahrenheit (-40°F to 120°F),
            returns the height and y-position for the fluid in the thermometer SVG,
            and the tick y-position closest to the temperature.
            """

            # Clamp temperature between -40 and 120
            temp_f = max(-40, min(120, temp_f))

            # Define scale
            min_temp = -40
            max_temp = 120
            tube_top_y = 40
            tube_height = 144

            # Convert temperature to percentage (0 to 1)
            percent = (temp_f - min_temp) / (max_temp - min_temp)

            # Calculate fluid fill height and y position
            fluid_height = percent * tube_height
            fluid_y = tube_top_y + (tube_height - fluid_height)

            # Find closest tick mark y-coordinate
            # Each 10°F step = 9px
            tick_index = round((temp_f - min_temp) / 10)
            tick_y = 184 - (tick_index * 9)

            return {
                "temperature": temp_f,
                "fluid_y": round(fluid_y, 2),
                "fluid_height": round(fluid_height, 2),
                "nearest_tick_y": tick_y
            }


        sorted_temps = sorted(color_steps.keys())
        gradient_stops = []
        for t in sorted_temps:
            if temp_min <= t <= temp_max:
                # Map temp range to 180 degrees instead of full circle
                degrees = ((t - temp_min) / total_range) * 180
                gradient_stops.append(f"{color_steps[t]} {round(degrees, 1)}deg")

        return "conic-gradient(" + ", ".join(gradient_stops) + ")"

    def get_thermometer_svg_values(self, temp_f):
        min_temp = 0
        max_temp = 120
        tube_top_y = 40
        tube_height = 144

        percent = (temp_f - min_temp) / (max_temp - min_temp)
        fluid_height = percent * tube_height
        fluid_y = tube_top_y + (tube_height - fluid_height)

        return {
            "fluid_y": round(fluid_y, 2),
            "fluid_height": round(fluid_height, 2),
        }

    def generate_thermometer_svg(self, temp_f):
        gradient_id = f"thermoGradient_{int(temp_f)}_{random.randint(0, 99999)}"
        vals = self.get_thermometer_svg_values(temp_f)
        fluid_y = vals['fluid_y']
        fluid_height = vals['fluid_height']
        #print(f"the temperature is: {temp_f}, the y is: {vals['fluid_y']}, the height is: {vals['fluid_height']}")
        #<!--<svg width="200" height="200" viewBox="-200 -200 600 600" xmlns="http://www.w3.org/2000/svg">-->

        return f"""
            <svg width="200" height="200" viewBox="-200 -200 600 600" xmlns="http://www.w3.org/2000/svg">

            <defs>
                <linearGradient id={gradient_id} x1="0" y1="240" x2="0" y2="40" gradientUnits="userSpaceOnUse">
                  {self.generate_svg_stops(temp_f)}
                </linearGradient>
            </defs>
            <!-- Rotate around the center of the bulb, which is defined at cx = 100 and cy = 212 -->
            <path d="M85,30 a15,15 0 0 1 30,0 v150 a35,35 0 1 1 -30,0 v-150 z"
                fill="white" stroke="black" stroke-width="4" />

            <rect x="90" y="{fluid_y}" width="20" height="{fluid_height}" fill="url(#{gradient_id})" />


            <!-- Bulb only -->
            <circle cx="100" cy="212" r="30" fill="url(#{gradient_id})" />
            <text x="100" y="225" text-anchor="middle" fill="white" font-size="40" font-family="Arial">
                {int(temp_f)}
            </text>
            </svg>
    """

    # Generates a list of html stop offsets in percentages and stop colors in hexadecimal
    def generate_svg_stops(self, temp):
        gradient_map = self.get_gradient_window_map(temp)
        stops = []

        for offset, color in gradient_map.items():
            stops.append(f'<stop offset="{offset}" stop-color="{color}" />')

        return "\n".join(stops)

    def prettify_location(self, lat, lon):
        url = f'https://api.weather.gov/points/{lat},{lon}'
        response = requests.get(url)
        json_data = response.json()

        # Extract 'properties'
        properties = json_data.get('properties', {})

        # Fetch city and state from 'relativeLocation' link
        if 'relativeLocation' in properties:
            relative_location_url = properties['relativeLocation']['properties']['city']
            city = properties['relativeLocation']['properties']['city']
            state = properties['relativeLocation']['properties']['state']

            return city, state
        else:
            return None, None

        return properties

    def export_to_json(self, filename="metar_data.json"):
        station_list = []

        for icao, data in self.superDict.items():
            try:
                lat, lon, temp_c, icao_corrected, station_name, cloudCoverWxType, weather_phenomena, direction, speed, gust, visibility, altimeter_pressure, time, urls, metar, is_daytime = data

                station_list.append({
                    "icao": icao,
                    "name": station_name,
                    "lat": lat,
                    "lon": lon,
                    "temp": temp_c[0],
                    "dew": temp_c[1],
                    "wind_dir": direction,
                    "wind_speed": speed,
                    "gust": gust,
                    "visibility": visibility,
                    "clouds": [f"{cc[0]} at {cc[1]}" if isinstance(cc, list) else cc for cc in cloudCoverWxType],
                    "weather_icon": urls,
                    "svg": self.generate_thermometer_svg(temp_dew[0], wind_dir),
                    "is_daytime": is_daytime,
                    "metar": raw_metar
                })

            except Exception as e:
                print(f"⚠️ Error converting {icao} to JSON: {e}")

        with open(filename, "w") as f:
            #print(station_list)
            json.dump({"stations": station_list}, f, indent=2)
    """
    def generate_direction_ticks(self, cx=125, cy=125, radius=110, tick_length=10):
        ticks_svg = []
        for i in range(8):
            angle_deg = i * 45
            angle_rad = math.radians(angle_deg)

            x1 = cx + ((radius/2) - tick_length) * math.cos(angle_rad)
            y1 = cy + ((radius/2) - tick_length) * math.sin(angle_rad)
            x2 = cx + (radius/2) * math.cos(angle_rad)
            y2 = cy + (radius/2) * math.sin(angle_rad)

            ticks_svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="black" stroke-width="2"/>')

        return "\n".join(ticks_svg)

    def create_svg_dial_wind(self, value, categories, wind_dir):
        cx, cy, radius = 125, 125, 95
        total_angle = 270
        start_angle = -225
        # segment_angle = total_angle / len(categories)

        gap = 5  # degrees of empty space between each segment
        n = len(categories)
        segment_angle = (total_angle - gap * (n - 1)) / n
        svg_parts = [f'<svg width="250" height="400" viewBox="0 0 250 200">']
        # Draw each arc
        for i, (label, color) in enumerate(categories):
            start = start_angle + i * (segment_angle + gap)
            end = start + segment_angle
            path_d = self.describe_arc(cx, cy, radius, start, end)
            svg_parts.append(f'<path d="{path_d}" stroke="{color}" stroke-width="20" fill="none" stroke-linecap="butt" />')

        # Knob
        knob_angle = (value / 100) * total_angle + start_angle
        #const angle = (value / 100) * 270 - 135;
        knob_x, knob_y = self.polar_to_cartesian(cx, cy, radius, knob_angle)
        #svg_parts.append(f'<circle cx="{knob_x}" cy="{knob_y}" r="7" fill="white" stroke="#ccc" stroke-width="3"/>')
        # Replace the knob (circle) part with this triangle
        pointer_length = 20
        pointer_width = 20
        angle_rad = math.radians(knob_angle)

        # Triangle tip (at arc edge)
        tip_x = knob_x
        tip_y = knob_y

        # Base of triangle (move backward along the angle)
        base_center_x = cx + (radius - pointer_length) * math.cos(angle_rad)
        base_center_y = cy + (radius - pointer_length) * math.sin(angle_rad)

        # Compute the two base corners perpendicular to the angle
        perp_angle = angle_rad + math.pi / 2
        corner1_x = base_center_x + (pointer_width / 2) * math.cos(perp_angle)
        corner1_y = base_center_y + (pointer_width / 2) * math.sin(perp_angle)
        corner2_x = base_center_x - (pointer_width / 2) * math.cos(perp_angle)
        corner2_y = base_center_y - (pointer_width / 2) * math.sin(perp_angle)

        # Draw triangle instead of knob
        svg_parts.append(
            f'<polygon points="{tip_x},{tip_y} {corner1_x},{corner1_y} {corner2_x},{corner2_y}" '
            f'fill="white" stroke="#ccc" stroke-width="2"/>'
        )
        svg_parts.append(self.generate_direction_ticks())
        #print(value, total_angle, start_angle)
        #print(int((value/100)*len(categories)))
        # Text
        #print(categories[int((value/100)*len(categories))][0])
        # Clamp value between 0 and 100
        clamped_value = max(0, min(value, 100))
        # Where the knob should point based on the input value, which is a percentage (0 to 100).
        index = int((clamped_value / 100) * len(categories))
        # If categories[int((value/100)*len(categories))][0] produces an index into the categories array than that is actually bigger than its length
        if index >= len(categories):
            index = len(categories) - 1
        label = categories[index][0]
        #svg_parts.append(f'<text x="{cx}" y="125" text-anchor="middle" class="gauge-text" font-size="40" font-family="Arial" weight = "bold">{value}⁰F</text>')
        #svg_parts.append(f'<text x="{cx}" y="150" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">{label}</text>')
        svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius/2}" fill="white" stroke="#ccc" stroke-width="3"/>')

        # Position for South text marker
        x1 = cx
        y1 = 25 + cy + radius / 2

        # Position for North text marker
        x2 = cx
        y2 = cy - (radius / 2)

        # Position for East text marker
        x3 = 10 + cx + radius / 2
        y3 = cy

        # Position for West text marker
        x4 = cx - (radius / 2) - 10
        y4 = cy
        svg_parts.append(f'<text x="{x1}" y="{y1}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">S</text>')
        svg_parts.append(f'<text x="{x2}" y="{y2}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">N</text>')
        svg_parts.append(f'<text x="{x3}" y="{y3}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">E</text>')
        svg_parts.append(f'<text x="{x4}" y="{y4}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">W</text>')

        svg_parts.append(f'<g transform="rotate({wind_dir}, {cx}, {cy})"><rect x="{cx-5}" y="{cy}" width="10" height="{radius/2}"/></g>')
        svg_parts.append('</svg>')

        return ''.join(svg_parts)

    def create_svg_dial(self, value, categories):
        cx, cy, radius = 125, 125, 95
        total_angle = 270
        start_angle = -225
        segment_angle = total_angle / len(categories)

        svg_parts = [f'<svg width="250" height="400" viewBox="0 0 250 200">']
        # Draw each arc
        for i, (label, color) in enumerate(categories):
            start = start_angle + i * segment_angle
            end = start + segment_angle
            path_d = self.describe_arc(cx, cy, radius, start, end)
            svg_parts.append(f'<path d="{path_d}" stroke="{color}" stroke-width="20" fill="none" stroke-linecap="butt" />')

        # Knob
        knob_angle = (value / 100) * total_angle + start_angle
        #const angle = (value / 100) * 270 - 135;
        knob_x, knob_y = self.polar_to_cartesian(cx, cy, radius, knob_angle)
        #svg_parts.append(f'<circle cx="{knob_x}" cy="{knob_y}" r="7" fill="white" stroke="#ccc" stroke-width="3"/>')
        # Replace the knob (circle) part with this triangle
        pointer_length = 20
        pointer_width = 20
        angle_rad = math.radians(knob_angle)

        # Triangle tip (at arc edge)
        tip_x = knob_x
        tip_y = knob_y

        # Base of triangle (move backward along the angle)
        base_center_x = cx + (radius - pointer_length) * math.cos(angle_rad)
        base_center_y = cy + (radius - pointer_length) * math.sin(angle_rad)

        # Compute the two base corners perpendicular to the angle
        perp_angle = angle_rad + math.pi / 2
        corner1_x = base_center_x + (pointer_width / 2) * math.cos(perp_angle)
        corner1_y = base_center_y + (pointer_width / 2) * math.sin(perp_angle)
        corner2_x = base_center_x - (pointer_width / 2) * math.cos(perp_angle)
        corner2_y = base_center_y - (pointer_width / 2) * math.sin(perp_angle)

        # Draw triangle instead of knob
        svg_parts.append(
            f'<polygon points="{tip_x},{tip_y} {corner1_x},{corner1_y} {corner2_x},{corner2_y}" '
            f'fill="white" stroke="#ccc" stroke-width="2"/>'
        )
        #print(value, total_angle, start_angle)
        #print(int((value/100)*len(categories)))
        # Text
        #print(categories[int((value/100)*len(categories))][0])
        # Clamp value between 0 and 100
        clamped_value = max(0, min(value, 100))
        # Where the knob should point based on the input value, which is a percentage (0 to 100).
        index = int((clamped_value / 100) * len(categories))
        # If categories[int((value/100)*len(categories))][0] produces an index into the categories array than that is actually bigger than its length
        if index >= len(categories):
            index = len(categories) - 1
        label = categories[index][0]
        svg_parts.append(f'<text x="{cx}" y="125" text-anchor="middle" class="gauge-text" font-size="40" font-family="Arial" weight = "bold">{value}⁰F</text>')
        svg_parts.append(f'<text x="{cx}" y="150" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">{label}</text>')
        svg_parts.append('</svg>')

        return ''.join(svg_parts)
    """
    def create_svg_dials(self, values_dict, categories):
        """Create multiple SVG temperature dials side-by-side from a dictionary {hour: temp}"""

        svg_parts = ['<svg width="{}" height="250" viewBox="0 0 {} 250">'.format(140*len(values_dict), 140*len(values_dict))]

        for i, (hour, value) in enumerate(values_dict.items()):
            cx = 70 + i * 140  # center x for this dial
            cy = 100           # center y
            radius = 50
            total_angle = 270
            start_angle = -225
            segment_angle = total_angle / len(categories)

            # Draw arcs
            for j, (label, color) in enumerate(categories):
                start = start_angle + j * segment_angle
                end = start + segment_angle
                path_d = self.describe_arc(cx, cy, radius, start, end)
                svg_parts.append(f'<path d="{path_d}" stroke="{color}" stroke-width="10" fill="none" stroke-linecap="butt" />')

            # Knob (arrow/pointer)
            clamped_value = max(0, min(value, 100))
            knob_angle = (clamped_value / 100) * total_angle + start_angle
            knob_x, knob_y = self.polar_to_cartesian(cx, cy, radius, knob_angle)

            pointer_length = 12
            pointer_width = 10
            angle_rad = math.radians(knob_angle)
            tip_x = knob_x
            tip_y = knob_y
            base_center_x = cx + (radius - pointer_length) * math.cos(angle_rad)
            base_center_y = cy + (radius - pointer_length) * math.sin(angle_rad)
            perp_angle = angle_rad + math.pi/2
            corner1_x = base_center_x + (pointer_width/2) * math.cos(perp_angle)
            corner1_y = base_center_y + (pointer_width/2) * math.sin(perp_angle)
            corner2_x = base_center_x - (pointer_width/2) * math.cos(perp_angle)
            corner2_y = base_center_y - (pointer_width/2) * math.sin(perp_angle)

            svg_parts.append(
                f'<polygon points="{tip_x},{tip_y} {corner1_x},{corner1_y} {corner2_x},{corner2_y}" '
                f'fill="white" stroke="#ccc" stroke-width="1.5"/>'
            )

            # Labels: Temperature and Hour
            index = int((clamped_value / 100) * len(categories))
            if index >= len(categories):
                index = len(categories) - 1
            label = categories[index][0]

            svg_parts.append(f'<text x="{cx}" y="95" text-anchor="middle" font-size="18" font-family="Arial">{value}°F</text>')
            svg_parts.append(f'<text x="{cx}" y="120" text-anchor="middle" font-size="14" font-family="Arial" fill="#333">{label}</text>')
            svg_parts.append(f'<text x="{cx}" y="145" text-anchor="middle" font-size="12" font-family="Arial" fill="#555">Hour {hour}</text>')

        svg_parts.append('</svg>')
        return ''.join(svg_parts)

    def polar_to_cartesian(self, cx, cy, r, angle_deg):
        rad = math.radians(angle_deg)
        return (cx + r * math.cos(rad), cy + r * math.sin(rad))

    def describe_arc(self, cx, cy, radius, start_angle, end_angle):
        start_pt = self.polar_to_cartesian(cx, cy, radius, end_angle)
        end_pt = self.polar_to_cartesian(cx, cy, radius, start_angle)
        large_arc = 1 if (end_angle - start_angle) > 180 else 0
        return f'M {start_pt[0]},{start_pt[1]} A {radius},{radius} 0 {large_arc},0 {end_pt[0]},{end_pt[1]}'

    # takes in a parameter string if you want to generate a temperature or dewpoint legend (type string)
    # inputs will be "temperature" or "dewpoint"
    def generate_legend(self, parameter):
        temperature_categories = [
            {"label": "Extreme Cold", "range": "-40° to -10°", "color": "#4B0082"},
            {"label": "Very Cold", "range": "-10° to 20°", "color": "#1E90FF"},
            {"label": "Cold", "range": "20° to 40°", "color": "#00BFFF"},
            {"label": "Cool", "range": "40° to 50°", "color": "#87CEEB"},
            {"label": "Comfortable", "range": "50° to 70°", "color": "#2ECC71"},
            {"label": "Warm", "range": "70° to 90°", "color": "#FFA500"},
            {"label": "Hot", "range": "90° to 110°", "color": "#FF4500"},
            {"label": "Extreme Heat", "range": "110° to 120°", "color": "#8B0000"},
        ]

        dewpoint_categories = [
            {"label": "Extremely Dry", "range": "< -30°F", "color": "#eeeeee"},
            {"label": "Painfully Dry", "range": "-30° to -20°F", "color": "#dddddd"},
            {"label": "Very Dry", "range": "-20° to -10°F", "color": "#cccccc"},
            {"label": "Crisp & Dry", "range": "-10° to 0°F", "color": "#bbbbbb"},
            {"label": "Frigid Dry Air", "range": "0° to 10°F", "color": "#aaaaaa"},
            {"label": "Cold & Dry", "range": "10° to 20°F", "color": "#999999"},
            {"label": "Cool & Dry", "range": "20° to 30°F", "color": "#888888"},
            {"label": "Neutral", "range": "30° to 40°F", "color": "#77aadd"},
            {"label": "Comfortable", "range": "40° to 50°F", "color": "#66c2ff"},
            {"label": "Slightly Humid", "range": "50° to 55°F", "color": "#4db8ff"},
            {"label": "Noticeably Humid", "range": "55° to 60°F", "color": "#33aaff"},
            {"label": "Humid", "range": "60° to 65°F", "color": "#1a99ff"},
            {"label": "Very Humid", "range": "65° to 70°F", "color": "#0088ff"},
            {"label": "Oppressive", "range": "70° to 75°F", "color": "#0077e6"},
            {"label": "Tropical & Stifling", "range": "75° to 80°F", "color": "#0055aa"},
            {"label": "Saturated & Dangerous", "range": "> 80°F", "color": "#003366"}
        ]
        # initialize empty categories list out side of if statement
        categories = []
        if parameter == "temperature":
            categories = temperature_categories
        elif parameter == "dewpoint":
            categories = dewpoint_categories

        svg_parts = []
        svg_width = 450
        x_start = 5
        y_base = 10
        rectangle_length = 40
        space_btwn_categories = 10
        max_per_row = 5
        #total_row_width = max_per_row * rectangle_length + (max_per_row - 1) * space_btwn_categories
        # the center point
        #x_start = (svg_width - total_row_width) / 2
        for i, cat in enumerate(categories):
            col = i % max_per_row
            # this is the same as taking the floor of i / max_per_row
            row = i // max_per_row
            x = x_start + col * (rectangle_length + space_btwn_categories)
            # increase y
            y = y_base + row * 50

            box = f'''
            <rect x="{x}" y="{y}" width="{rectangle_length}" height="15" rx="4" ry="4" fill="{cat['color']}"/>
            <text x="{x + rectangle_length / 2}" y="{y + 25}" font-size="8" text-anchor="middle" fill="black">{cat['label']}</text>
            <text x="{x + rectangle_length / 2}" y="{y + 35}" font-size="7" text-anchor="middle" fill="black">{cat['range']}</text>
            '''
            svg_parts.append(box)

        final_svg = f'''
        <svg width="450" height="100" xmlns="http://www.w3.org/2000/svg">
          {''.join(svg_parts)}
        </svg>
        '''
        return final_svg

    def generate_map(self):
        #data = json.loads('https://aviationweather.gov/data/cache/stations.cache.json')
        #for item in data:
        #    print(item)
        # Center the map on the USA
        m = folium.Map(location=[42.3555, -71.0565], zoom_start=8)
        m1 = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

        for city_name, data in self.cityInfo.items():
            try:
                lat, lon, country_name, population, elevation, timezone, temperature_dict, dewpoint_dict, cc_dict = data
                # loop through
                #color1 = self.get_color(temperature)
                #gradient_css_temperture = self.get_gradient_window(temperature)
                #gradient_css_dewpoint = self.get_gradient_window(dewpoint)
                #color1 = self.get_color(temperature)
                gradient_id = f"arcGradient_{city_name}"

                temperature_categories = [
                    ("Extreme Cold (Frostbite Risk)", "#4B0082"),     # -40 to -10°F — Deep indigo (dangerously cold)
                    ("Very Cold", "#1E90FF"),                         # -10 to 20°F — Dodger blue (very cold, but manageable)
                    ("Cold", "#00BFFF"),                              # 20 to 40°F — Deep sky blue (chilly, jacket weather)
                    ("Cool", "#87CEEB"),                              # 40 to 50°F — Light blue (mildly cool, light layer)
                    ("Comfortable", "#2ECC71"),                       # 50 to 70°F — Soft green (ideal weather)
                    ("Mildly Warm", "#F4D03F"),                       # 70 to 80°F — Golden yellow (sunny, pleasant)
                    ("Warm", "#FFA500"),                              # 80 to 90°F — Orange (hot, caution in prolonged exposure)
                    ("Hot", "#FF4500"),                               # 90 to 100°F — Orange-red (very hot, dehydration risk)
                    ("Very Hot (Heat Exhaustion Risk)", "#FF0000"),   # 100 to 110°F — Red (danger of heat stress)
                    ("Extreme Heat (Heat Stroke Risk)", "#8B0000")    # 110 to 120°F — Dark red (life-threatening)
                ]

                dewpoint_categories = [
                    ("< -30°F: Extremely dry, arid cold (desert-like in winter)", "#eeeeee"),
                    ("-30°F to -20°F: Painfully dry, lips and skin crack quickly", "#dddddd"),
                    ("-20°F to -10°F: Very dry, nose and throat sting", "#cccccc"),
                    ("-10°F to 0°F: Crisp dry cold, no moisture in the air", "#bbbbbb"),
                    ("0°F to 10°F: Dry and frigid, static electricity increases", "#aaaaaa"),
                    ("10°F to 20°F: Cold and dry, some nose and skin irritation", "#999999"),
                    ("20°F to 30°F: Cool and dry, fairly comfortable in winter", "#888888"),
                    ("30°F to 40°F: Neutral—slightly dry but not uncomfortable", "#77aadd"),
                    ("40°F to 50°F: Comfortable, fresh-feeling air", "#66c2ff"),
                    ("50°F to 55°F: Slightly humid, still pleasant for most", "#4db8ff"),
                    ("55°F to 60°F: Noticeably humid, some will feel sticky", "#33aaff"),
                    ("60°F to 65°F: Humid—sweat won’t evaporate as well", "#1a99ff"),
                    ("65°F to 70°F: Very humid, muggy and oppressive", "#0088ff"),
                    ("70°F to 75°F: Oppressive humidity—uncomfortable for all", "#0077e6"),
                    ("75°F to 80°F: Extremely humid, tropical and stifling", "#0055aa"),
                    ("> 80°F: Saturated air—dangerous heat stress zone", "#003366")
                ]

                wind_categories = [
                    ("Light", "#88C0D0"),
                    ("Moderate", "#EBCB8B"),
                    ("Extreme", "#BF616A"),
                ]
                #svg_dial_temperatures = self.create_svg_dials(temperature_dict, temperature_categories)
                first_hour, first_temp = next(iter(temperature_dict.items()))


                folium.Marker(
                    location=[lat, lon],
                    #icon=folium.DivIcon(html=f""" <img src={urls} width="1px"><div style="font-family: comic sans; font-size: 20px; text-shadow: black 0px 0px 2px; color: {color1}">{temperature}</div>"""),
                    # {self.generate_thermometer_svg(temperature, direction)}
                    icon=folium.DivIcon(html=f"""
                        {self.generate_thermometer_svg(first_temp)}
                    """),
                    popup=folium.Popup(html=f"""
                        <h2 style="text-align: center;">{city_name}</h2>
                    """, max_width=300)
                    ).add_to(m)
            except Exception as e:
                #print(f"🔥 Skipping {city_name} due to error: {e}")
                print(e)
                None

        from folium import raster_layers
        #image_url = 'https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif'
        raster_layers.ImageOverlay('https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif',
                    [[-119.564209,38.503915],[-114.060059,41.211203]],
                    opacity=0.8,
                   ).add_to(m)
        folium.LayerControl().add_to(m1)

        from folium import raster_layers
        m.save("static/model_maps/model_map.html")

        # Ensure the directory exists
        #output_dir = os.path.join(app.root_path, "static", "METAR_map")
        #os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Sanitize the product name for safe file naming
        #no_spaces_product = product.replace(" ", "_").replace(":", "_")

        # Construct the file path to save the image in the static directory
        #file_path = os.path.join(output_dir, f"airport_metar_map.html")


if __name__ == '__main__':
    scraper = ProxyScraper()
    scraper.fetch_data(True, "KBOS")
    scraper.generate_map()