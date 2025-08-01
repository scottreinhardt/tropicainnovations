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

class ProxyScraper:
    results = []
    def __init__(self):
        self.station_url = 'https://aviationweather.gov/data/cache/stations.cache.json'
        self.url = 'https://aviationweather.gov/data/cache/metars.cache.csv'
        self.superDict = {}
        self.stations = []
        self.metars = []
        self.airportLocations = {}


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
    # Read in airport information json file and populate airportLocations dictionary
    def fetch_airport_data(self):
        with open('/home/tropicainnovations/mysite/static/METAR_map/stations_list/stations.cache.json') as airport_list:
            list_of_airports = json.load(airport_list)
            for airport in list_of_airports:
                icao     = airport.get("icaoId")
                #iata     = airport.get("iataId")
                #faa      = airport.get("faaId")
                #wmo      = airport.get("wmoId")
                lat      = airport.get("lat")
                lon      = airport.get("lon")
                elev     = airport.get("elev")
                site     = airport.get("site")
                state    = airport.get("state")
                country  = airport.get("country")
                #priority = airport.get("priority")
                self.airportLocations[icao] = [lat, lon, elev, site, state, country]




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
                """
                # Also grab airport info from GitHub CSV
                airport_response = requests.get("https://raw.githubusercontent.com/ip2location/ip2location-iata-icao/master/iata-icao.csv")
                #airport_response = requests.get("")
                airport_response.raise_for_status()
                reader = csv.reader(airport_response.text.splitlines())
                next(reader)  # Skip header

                matched_info = None
                for row in reader:
                    if len(row) > 3 and row[3] == icao_input:
                        matched_info = row
                        break

                if matched_info:
                    country = matched_info[0]
                    state = matched_info[1]
                    name = matched_info[4] if len(matched_info) > 4 else "Unknown Airport"
                else:
                    country, state, name = "Unknown", "Unknown", "Unknown Airport"

                self.stations = [name]
                self.airportLocations = {
                    icao_input: [country, state, name]
                }

                print(f"✅ Loaded METAR for {icao_input}:")
                print(self.csv_data)
                """

            else:
                # Fetch real data from FAA site
                response = requests.get(self.url)
                response.raise_for_status()
                self.csv_data = response.text
                for tag in self.superDict:
                    if tag == "METAR":
                        print(tag)
                        #raw_text = metar.find('raw_text').text
                        observation_time = tag.find('observation_time')

                        icao = tag.find('station_id')
                        #print(icao)

                        lon = tag.find('longitude')
                        lat = tag.find('latitude')
                        #print(f"Number of valid airports: {regularcoord}, Number of invalid airports: {lat_lon_zerozero}")
                        temp_c = tag.find('temp_c')
                        dewpoint_c = tag.find('dewpoint_c')
                        wind_dir_degrees = tag.find('wind_dir_degrees')
                        wind_speed_kt = tag.find('wind_speed_kt')
                        altim_in_hg = tag.find('altim_in_hg')
        except Exception as e:
            print(f"Error loading {'test' if test_mode else 'live'} data: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
        print(self.scrapeLocation())

    def findLoction(self, icao):
        """
        # calling the Nominatim tool and create Nominatim class
        loc = Nominatim(user_agent="Geopy Library")

        # entering the location name
        getLoc = loc.geocode("İzmir")

        # printing address
        #print(getLoc.address)

        # printing latitude and longitude
        return [getLoc.latitude, getLoc.longitude]
        #print("Latitude = ", getLoc.latitude, "\n")
        #print("Longitude = ", getLoc.longitude)
        """
        for key, value in list(self.airportLocations.items()):
            if icao == key:
                return value

    # This method scrapes the national weather services free location api and retrieves the json location information gives lat and lo0n passed in
    def scrapeLocation(self):
        # URL of the CSV file
        csv_url = 'https://raw.githubusercontent.com/ip2location/ip2location-iata-icao/refs/heads/master/iata-icao.csv'

        # Fetch the CSV data from the URL
        response = requests.get(csv_url)
        response.raise_for_status()  # Ensure the request was successful

        # Decode the content into a string
        csv_data = response.content.decode('utf-8').splitlines()

        # Initialize the dictionary to hold ICAO as the key and other details as the value
        #icao_dict = {}

        # Use the csv reader to parse the CSV
        csv_reader = csv.reader(csv_data)

        # Skip the header row (if there's one)
        next(csv_reader, None)

        # Loop through each row in the CSV
        for row in csv_reader:
            icao = row[3]  # Assuming ICAO is the second column
            rest_of_row = row[:2] + row[4:5]  # Get the rest of the row excluding the ICAO
            self.airportLocations[icao] = rest_of_row
        #data = json.loads(url)
        # store the response of URL
        #response = urlopen(url)
        # storing the JSON response
        # from url in data
        #data_json = json.loads(response.read())
        #print(data_json)

    # This method takes in the METAR raw text as variable row
    def find_weather_condition(self, row):
        # Find weather condition
        wxPhenomena = { ' DZ ': ['Moderate Drizzle', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0048-drizzle_orig.png'],
                       ' -DZ ': ['Light Drizzle', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0048-drizzle_orig.png'],
                       ' +DZ ': ['Heavy Drizzle', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0081-heavy-drizzle_orig.png'],
                       ' FRDZ ':['Freezing Drizzle', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0049-freezing-drizzle_orig.png'],
                       ' -FRDZ ':['Light Freezing Drizzle', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0049-freezing-drizzle_orig.png'],
                       ' +FRDZ ':['Heavy Freezing Drizzle', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0083-heavy-freezing-drizzle_orig.png'],
                       ' RA ': ['Moderate Rain','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0034-cloudy-with-heavy-rain-night_orig.png'],
                       ' -RA ': ['Light Rain','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0017-cloudy-with-light-rain_orig.png'],
                       ' +RA ': ['Heavy Rain','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0051-extreme-rain_orig.png'],
                       ' SHRA ': ['Rain Showers', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0010-heavy-rain-showers_orig.png'],
                       ' -SHRA ': ['Light Rain Showers', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0009-light-rain-showers_orig.png'],
                       ' +SHRA ': ['Heavy Rain Showers', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0085-extreme-rain-showers_orig.png'],
                       'TSRA': ['Thunderstorm with Heavy Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0024-thunderstorms_orig.png'],
                       ' SN ': ['Moderate Snow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0020-cloudy-with-heavy-snow_orig.png'],
                       ' -SN ': ['Light Snow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0019-cloudy-with-light-snow_orig.png'],
                       ' +SN ': ['Heavy Snow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0052-extreme-snow_orig.png'],
                       ' DRSN ': ['Drifting snow, which is snow that remains below 8 feet (2 meters)', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0053-blowing-snow_orig.png'],
                       ' BLSN ': ['Blowing Snow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0053-blowing-snow_orig.png'],
                       ' SHSN ': ['Snow Showers', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0011-light-snow-showers_orig.png'],
                       ' -SHSN ': ['Light Snow Showers','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0011-light-snow-showers_orig.png'],
                       ' +SHSN ': ['Heavy Snow Showers','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0012-heavy-snow-showers_orig.png'],
                       ' PE ': ['Sleet','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0021-cloudy-with-sleet_orig.png'],
                       ' -PE ': ['Light Sleet','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0021-cloudy-with-sleet_orig.png'],
                       ' +PE ': ['Heavy Sleet', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0089-heavy-sleet_orig.png'],
                       ' SHPE ': ['Showers and precipitation, such as rain, snow, ice pellets, hail, or snow pellets.', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0021-cloudy-with-sleet_orig.png'],
                       ' TSPE ': ['Thunder Sleet', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0021-cloudy-with-sleet_orig.png'],
                       ' GR ': ['Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0023-cloudy-with-heavy-hail_orig.png'],
                       ' -GR ': ['Light Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0038-cloudy-with-light-hail-night_orig.png'],
                       ' +GR ': ['Heavy Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0023-cloudy-with-heavy-hail_orig.png'],
                       ' SHGR ': ['Thundershowers with Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0059-thunderstorms-with-hail_orig.png'],
                       ' TSGR ': ['Thunderstorm with Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0059-thunderstorms-with-hail_orig.png'],
                       ' GS ': ['Small Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0038-cloudy-with-light-hail-night_orig.png'],
                       ' SHGS ':['Thundershowers with Small Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0059-thunderstorms-with-hail_orig.png'],
                       ' TSGS ': ['Thunderstorm with Small Hail', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0059-thunderstorms-with-hail_orig.png'],
                       ' UP ': ['Unkown Precipitation', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0999-unknown_orig.png'],
                       ' TS ': ['Thunderstorm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0024-thunderstorms_orig.png'],
                       ' VCTS ': ['Thunderstorm in the Vicinity (5-10 Miles Away', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0024-thunderstorms_orig.png'],
                       ' TSRA ': ['Thunderstorm with Moderate Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0024-thunderstorms_orig.png'],
                       ' -TSRA ': ['Thunderstorm with Light Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0016-thundery-showers_orig.png'],
                       ' +TSRA ': ['Thunderstorm with Heavy Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0024-thunderstorms_orig.png'],
                       ' TSSN ': ['Thundersnow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0058-thunderstorms-with-snow_orig.png'],
                       ' - TSSN ': ['Light Thundersnow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0057-thundery-snow-showers_orig.png'],
                       ' +TSSN ': ['Heavy Thundersnow', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0058-thunderstorms-with-snow_orig.png'],
                       ' VCSH ': ['Showers in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0010-heavy-rain-showers_orig.png'],
                       ' SHPE ': ['Showers with Ice Pellets','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0013-sleet-showers_orig.png'],
                       ' -SHPE ': ['Showers with Ice Pellets','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0013-sleet-showers_orig.png'],
                       ' +SHPE ':['Showers with Ice Pellets','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0013-sleet-showers_orig.png'],
                       ' -FZRA ': ['Freeing Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0050-freezing-rain_orig.png'],
                       ' -FZRA ': ['Light Freeing Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0050-freezing-rain_orig.png'],
                       ' -FZRA ': ['Heavy Freeing Rain', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0050-freezing-rain_orig.png'],
                       ' FZFG': ['Freezing Fog', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0047-freezing-fog_orig.png'],
                       ' BR ': ['Mist', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0006-mist_orig.png'],
                       ' FG ': ['Fog','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0007-fog_orig.png'],
                       ' VCFG ': ['Fog in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0007-fog_orig.png'],
                       ' MIFG ': ['Shallow Fog Below 6 Feet', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0007-fog_orig.png'],
                       ' PRFG ': ['Partial Fog', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0007-fog_orig.png'],
                       ' BCFG ': ['Patches of Fog', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0007-fog_orig.png'],
                       ' FU ': ['Smoke', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0055-smoke_orig.png'],
                       ' VA ': ['Volcanic Ash', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0091-volcanic-ash_orig.png'],
                       ' DU ': ['Widespread Dust', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' DRDU ': ['Low Widespread Dust', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' BLDU ': ['Blowing Dust/ Dust Storm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' SA ': ['Sand', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' DRSA ': ['Low Sand Storm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' BLSA ': ['Blowing Sand/Sand Storm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' HZ ': ['Haze','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0005-hazy-sun_orig.png'],
                       ' VCBLSN ': ['Blowing Snow in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0053-blowing-snow_orig.png'],
                       ' BLDU ': ['Blowing Dust', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' VCBLSA ': ['Blowing Sand in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' VCBLD ': ['Blowing Dust in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' PO ': ['Dust Devil/Sand/Dust Whirls', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' VCPO ': ['Dust Devil in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' SQ ': ['Squalls (increase in wind speed of at least 16kts lasting for more than 1 minute)', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0060-windy_orig.png'],
                       ' FC ': ['Funnel Cloud', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0079-tornado_orig.png'],
                       ' FC ': ['Tornado (If Over Land), Waterspout (If Over Water)', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0079-tornado_orig.png'],
                       ' SS ': ['Sandstorm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0074-dust-sand-night_orig.png'],
                       ' +SS ': ['Heavy Sandstorm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' VCSS ': ['Sandstorm in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' DS ': ['Duststorm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' +DS ': ['Heavy Duststorm', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' VCDS ': ['Duststorm in the Vicinity', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0056-dust-sand_orig.png'],
                       ' CLR ': ['Clear Skies', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/32_orig.png'],
                       ' SKC ': ['Clear Skies', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/32_orig.png'],
                       ' CAVOK ': ['Clear Skies', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/32_orig.png']
                       }

        weather_condition = ''
        # Loop through all the weather conditions in the array and see if any are in the metar 'row'
        # If there is no weather _condition will return ''.
        for i in wxPhenomena:
            #print(i)
            # if weather condition exists in the row
            #print(str(i) + ' ' + str(row))
            if str(i) in row:
                weather_condition = wxPhenomena[i]
                #print(weather_condition)
                return weather_condition

    # Returns first level of clouds only not multiple layers
    # for each METAR input this method returns [cloudCoverTypeTextAbbreviaiton, integerHeightOfClouds *10]
    def cloudCoverType(self, row):
        # This regex will capture any sequence of 3 letters followed by 3 digits.
        # Note that this Regex does not account for when it is CLR or SKC and there are no cloud levels
        pattern = r'[A-Za-z]{3}\d{3}'
        # Finds all matchews to the above pattern in the METAR (all cloud cover types and their heights)
        # Returns all matching instances like OVC020 or OVC020, SCT200as an array
        # Check to see if metar costains CLR (for clear skies) or SKC (for completely clear). These keywords do not have 3 digits after them so it will return an empty list as if CLR or SKC are not reported at all
        if 'CLR' in row:
            matches = 'CLR'
        elif 'SKC' in row:
            matches = 'SKC'
        elif 'CAVOK' in row:
            matches = 'CAVOK'
        else:
            matches = re.findall(pattern, row)
        #print(f"matches: {matches}")
        #print(matches)
        # This dict holds cloud cover abbreviuations and the meaning of the key and the respective image as an array for the value
        cloudCoverType = {'CLR':['Clear Skies at or below 12000ft', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png'],
                          'FEW': ['Few Clouds', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0002-sunny-intervals_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0041-partly-cloudy-night_orig.png'],
                          'SCT':['Scattered Clouds', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0002-sunny-intervals_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0041-partly-cloudy-night_orig.png'],
                          'BKN': ['Broken Clouds', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0043-mostly-cloudy_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0044-mostly-cloudy-night_orig.png'],
                          'OVC': ['Overcast', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0004-black-low-cloud_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0004-black-low-cloud_orig.png'],
                          'SKC': ['Clear, no cloud levels reported at any height', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png'],
                          'CAVOK': ['Clear, no cloud levels reported at any height', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png']
        }
        # declare temporary array to store the abbreviation of the cloud condition as the 0th element and the cloud height * 1000 as the 1st element
        finalCloud = []
        # loop through every matching cloud cover report in the metar returned in the matches array
        # Multiple cloud heights can be reported
        for i in matches:
            if len(i) >= 6 and i[0:3] in cloudCoverType and i[3:6].isdigit():
                cloudHeight = str(int(self.checkForLeadingZeroes(i[3:6])) * 100) + ' ft'
                finalCloud.append([i[0:3], cloudHeight])
        # Must check for CLR edge cases with no cloud height (cloud height is 0)
        if matches == 'CLR':
            cloudHeight = 0
            finalCloud.append(['CLR', cloudHeight])
        # Must check for SKC edge cases with no cloud height (cloud height is 0)
        elif matches == 'SKC':
            cloudHeight = 0
            finalCloud.append(['SKC', cloudHeight])
        elif matches == 'CAVOK':
            cloudHeight = 0
            finalCloud.append(['CAVOK', cloudHeight])
        # If there are no matches for any cloud cover reported, append "no cloud cover reported" to the temporary array which will be the only element in that array
        # This code will still look to see if there is a weather phenomena
        if finalCloud == []:
            finalCloud.append(["No Cloud Cover Reported", 0])
        # return the temporary array
        return finalCloud

    # Helper method to check for edge cases for cloud heights reported as 020 with a leading 0.
    def checkForLeadingZeroes(self, cloudHeight):
        # Knock off leading 0 if there is one
        # Example: input: '020' would return '20'
        if cloudHeight[0] == '0':
            return cloudHeight[1:]
        else:
            # If there isd no leading 0, return the cloudHeight as is
            return cloudHeight

    # extracts and returns Zulu time from each METAR
    def present_time(self, metar):
        time = ""
        pattern = r'\d{6}Z'
        time_of_day_raw = re.search(pattern, metar)
        #print(time_of_day_raw.group(0)[2:])
        try:
            time = time_of_day_raw.group(0)[2:]
        except:
            # No time is indicated in metar
            time = None
        return None

    # pass in average wx phenomena from average_cloud_condition() method
    def retrieve_url_from_wx_phenomena(self, averageCloudCondition):
        cloudCoverType = {'CLR':['Clear Skies at or below 12000ft', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png'],
                          'CAVOK':['CAVOK', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png'],
                          'FEW': ['Few Clouds', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0002-sunny-intervals_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0041-partly-cloudy-night_orig.png'],
                          'SCT':['Scattered Clouds', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0002-sunny-intervals_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0041-partly-cloudy-night_orig.png'],
                          'BKN': ['Broken Clouds', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0043-mostly-cloudy_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0044-mostly-cloudy-night_orig.png'],
                          'OVC': ['Overcast', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0004-black-low-cloud_orig.png', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0004-black-low-cloud_orig.png'],
                          'SKC': ['Clear, no cloud levels reported aty any height', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png']}
        for i in cloudCoverType:
            if i == averageCloudCondition:
                #print(cloudCoverType[i])
                return cloudCoverType[i]
    # Returns the corresponding URL
    # This function determins which icon to give each weather condition for each metar
    # cloud_cover_type is the array of [cloud cover, cloud height * 1000] which is determined in the parse_data method
    # weather_condition is a string that is the extended form of a weather condition. This is also determined in parse_data
    def determine_wx_icon(self, weather_phenomena, cloud_cover_type):
        if weather_phenomena == '' and cloud_cover_type == []:
            return ['N/A', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0999-unknown_orig.png']
        elif weather_phenomena == '':
            #print(f"cloud_cover_type: {cloud_cover_type}")
            # Use the already-parsed cloud_cover_type list directly
            avgCloudCoverNumerical = self.average_cloud_condition(cloud_cover_type)
            #print(f"avgCloudCoverNumerical: {avgCloudCoverNumerical}")
            #print(f"self.cloud_cover_percentage_to_text(avgCloudCoverNumerical): {self.cloud_cover_percentage_to_text(avgCloudCoverNumerical)}")
            avgCloudCoverText = self.cloud_cover_percentage_to_text(avgCloudCoverNumerical)[0]
            #print(f"avgCloudCoverText: {avgCloudCoverText}")
            urlAndDescription = self.retrieve_url_from_wx_phenomena(avgCloudCoverText)
            #print(f"urlAndDescription: {urlAndDescription}")
            if urlAndDescription == []:
                urlAndDescription.append('No Cloud Conditions Reported')
            #print(urlAndDescription)
            return urlAndDescription
        else:
            return weather_phenomena


    # Used when there is more than one cloud height
    # Only dependant on cloud cover
    # cloudCoverType input can be [], [['SCT', 200]], OR [[SCT, 20000], ['OVC', 40000], [..,..],...]
    def average_cloud_condition(self, cloudCoverType):
        # Define the percentages of cloud cover types and then add them up and divide them by the total number of cloud layers
        cloudCoverTypes = {'CLR': 0.0, 'FEW': 0.25, 'SCT': 0.50, 'BKN': 0.75, 'OVC': 1.0, 'SKC': 0.00, 'CAVOK': 0.0}

        # CloudCover is reported as [] for no clouds and [[type1, height]] or [[type1, height1], [type2, height2], [..,..],...]
        if len(cloudCoverType) == 0:
            # No clouds and no layers
            return 0
        # An input of a cloudCoverType of array of length 1 would indicate 1 cloud level reported in the metar

        elif len(cloudCoverType) == 1 and isinstance(cloudCoverType[0], list):
            if cloudCoverType[0] is None or not isinstance(cloudCoverType[0], list):
                print("Invalid cloud cover data structure")
                return 0  # or some fallback
            for key, value in cloudCoverTypes.items():
                if key == cloudCoverType[0][0]:
                    return value

        # If cloudCoverType has more than one cloud level reported, you will need to loop through all of the inner cloud level arrays
        # if cloudCoverType = [['SCT', 2000], ['OVC', 40000]]
        # INdicates more than one cloud level reported in the METAR
        else:
            ccArr = []
            # For multiple cloud layers
            # Find out each cloud layer type by looping through the input arrays
            #print(f"cloudCoverType: {cloudCoverType}.")
            try:
                # loop through every avaliable cloud cover type
                for i in cloudCoverType:
                    #print(i)
                    cover = i[0]
                    # if the first cloud layer is overcast, automatically add 1 directly for overcast (cloud conditions are percentages in decimal form) 0.1 corrospons to 100% clouds.
                    if cover == 'OVC':
                        ccArr.clear()
                        ccArr.append(1)  # Add 1 directly for overcast
                        break;
                    # For each cloud height in the input check what cloud condition it matches
                    else:
                        if cover in cloudCoverTypes:
                            ccArr.append(cloudCoverTypes[cover])
            except Exception as e:
                print(f"⚠️ Error in average_cloud_condition loop: {e}")
                return 0
            # Ensure that ccArr is not empty to avoid division by zero
            #print(f"ccarr: {ccArr}")
            if ccArr:
                return (sum(ccArr) / len(ccArr))
            else:
                print("No valid cloud cover data found.")

    # Converts average cloud conditions from percentages to their text cloud condition text equivelant
    # returns the metar text for cloud conditions
    def cloud_cover_percentage_to_text(self, numerical_avg_cloud_cover):
        if numerical_avg_cloud_cover is None:
            return ['N/A', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0999-unknown_orig.png']
        elif numerical_avg_cloud_cover <= 0.125:
            # CLR conditions
            return ['CLR', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/32_orig.png']
        elif numerical_avg_cloud_cover > 0.125 and numerical_avg_cloud_cover <= 0.375:
            # FEW clouds
            return ['FEW', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/34_orig.png']
        elif numerical_avg_cloud_cover > 0.375 and numerical_avg_cloud_cover <= 0.625:
            # Scattered clouds
            return ['SCT', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/30_orig.png']
        elif numerical_avg_cloud_cover > 0.625 and numerical_avg_cloud_cover <= 0.875:
            # BKN cloud conditions
            return ['BKN', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/28_orig.png']
        elif numerical_avg_cloud_cover > 0.875 and numerical_avg_cloud_cover <= 1.0:
            return ['OVC', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/26_orig.png']

    def get_visibility(self, metar_text):
        # Initialize visibility variable to 0
        visibility = 0
        # Visibility can either be reported in SM or parameter
        # If visibility is reported in SM or Statuate Miles, it will be 2 digits followed by the chars 'SM'
        # Example EGLL 021220Z 23012KT 9999 FEW030 SCT045 18/11 Q1013 NOSIG
        # Case 1: Look for 4 digits
        vis_match_meters = re.search(r'\b\d{4}\b', metar_text)
        # If visibility is reported in meters, it will be reported as 4 digits
        #\b Ensures it does not match inside another word
        # Example: KBOS 021254Z 23008KT 10SM FEW050 22/14 A2992 RMK AO2 SLP134
        # Case 2: Look for 2 digits or 1 digit (if less than 10SM) followed by 'SM'
        # Matches fractions such as 3 1/2 SM or matches either 1 or 2 digits and then SM for Statate Miles
        vis_match_sm = re.search(r'\b(\d{1,2}\s)?\d/\dSM\b|\b\d{1,2}SM\b', metar_text)

        # When visibility is not the same in different directions and when the lowest visibility is different from the prevailing visibility and less than 1 500 m, less than 50% of the prevailing visibility and less than 5 000 m, the lowest visibility
        # observed should also be reported and, when possible its general direction in relation to the aerodrome reference point indicated by reference to one of the eight points of the compass.
        #The prevailing visibility is reported as 800 meters.
        #There is lower visibility reported in another direction: 3000NE.
        #The lowest visibility is less than: 1,500 m ✅
        #50% of 3,000 m = 1,500 m ✅
        #5,000 m ✅
        # The direction of the better visibility (NE) is included using compass reference.
        # Example: METAR EGLL 021120Z 26005KT 0800 3000NE R27L/0900U FG BKN003 08/07 Q1013
        # Look for 4 digits followed by a space and then 4 digits followed by the direction N, NE, E, SE, S, SW, W, NW
        # Note that this can be reported as meters or SM
        # Accounts for fractions of Statuate miles like 1 1/2
        # Note you will never have a case like 1 1/2SM 1 1/2NE
        vis_match_direction = re.search(r'\b((\d{1,2}\s)?\d/\d|\d{1,2})SM\b|\b\d{4}(N|NE|E|SE|S|SW|W|NW)?\b', metar_text)
        #vis_match = re.search(r'\b\d{2}SM\b', metar_text)
        #In some METARs, the visibility information can be replaced by a group of letters:
        #CAVOK = Clouds And Visibility OK
        #NSC = No Significant Clouds = no clouds below 5000 feet, no cumulonimbus (CB) or towering cumulus(TCU)
        #SKC = SKy Clear – no clouds
        if vis_match_meters:
            # Note that a visibility of 99999 means an unlimited visibility or greater than 10 SM
            visibility = vis_match_meters
        elif vis_match_sm:
            visibility = vis_match_sm
        elif "CAVOK" in metar_text:
            visibility = 10000  # or set visibility = 10_000
        else:
            # Visibility is curropted or Broken
            visibility = None

        return visibility

    # Helper function to turn 030 into 30⁰ and 03 to 3kts
    # Wind speed can be 30 or 03. 03 will become 3
    # Wind directions are 3 digits. 030 should become 30
    """
    def trim_leading_zeros(self, value):
        print(f"the value is: {value}")
        trimmed_value = 0
        if (value != '0' or value != '00' or value != '000') and (value is not None):
            if value[0] == '0':
                if value[1] == '0':
                    trimmed_value = value[2:]
                else:
                    trimmed_value = value[1:]
            elif value[0] != '0':
                trimmed_value = value
        elif value == '0' or value == '00' or value == '000':
            trimmed_value = 0
        else:
            trimmed_value = value
        print(f"the trimmed value is: {trimmed_value}")
        return trimmed_value
    """
    def trim_leading_zeros(self, value):

        if value is None:
            return None

        value = str(value).lstrip('0')  # Removes leading zeros

        if value == '':
            return 0
        return int(value)

    def get_wind_dir_speed_gust(self, metar_text):
        wind_match = re.search(r'\b(?P<dir>\d{3})(?P<speed>\d{2})(?P<gust>G\d{2})?KT\b', metar_text)
        if(wind_match):
            wind_dir = wind_match.group('dir')
            wind_speed = wind_match.group('speed')
            gust = wind_match.group('gust')
            #print(wind_dir, wind_speed, gust)
            # If gust is None, that means the wind gust is 0
            if gust is None:
                return wind_dir, wind_speed, 0
            else:
                # remove the leading 'G' from gust
                return wind_dir, wind_speed, gust[1:]
        else:
            return None, None, None

    def getTempDew(self, metar_text):
        match_primary = re.search(r'T(\d{4})(\d{4})', metar_text)
        # Search for the first valid temperature/dewpoint pair (ignores ///// and similar garbage)
        match_secondary = re.search(r'\b(M?\d{2})/(M?\d{2})\b', metar_text)
        if match_primary:
            temp, dew = match_primary.groups()
            temp_raw = match_primary.group(1)
            dew_raw = match_primary.group(2)
            temp_c = -int(temp_raw[1:]) / 10.0 if temp_raw[0] == '1' else int(temp_raw[1:]) / 10.0
            dew_c = -int(dew_raw[1:]) / 10.0 if dew_raw[0] == '1' else int(dew_raw[1:]) / 10.0
            temp_f = round((temp_c * 9.0 / 5.0) + 32.0, 2)
            dew_f = round((dew_c * 9.0 / 5.0) + 32.0, 2)
            return [temp_f,dew_f]
        elif(match_secondary):
            temp_str, dew_str = match_secondary.groups()
            # Convert to Celsius
            temp_c = -int(temp_str[1:]) if temp_str.startswith('M') else int(temp_str)
            dew_c = -int(dew_str[1:]) if dew_str.startswith('M') else int(dew_str)
            rh = 100 * (((math.exp((17.625 * float(dew_c)) / (243.04 + float(dew_c))) / (math.exp((17.625 * float(temp_c)) / (243.04 + float(temp_c)))))))
            heatIndex = 0.5 * ((round(((9.0/5.0)*float(temp_c))+32.0,2)) + 61.0 + (((round(((9.0/5.0)*float(temp_c))+32.0,2))-68.0)*1.2) + (rh * 0.094))
            return [round(((9.0/5.0)*float(temp_c))+32.0), round(((9.0/5.0)*float(dew_c))+32.0), round(rh), round(heatIndex)]
        else:
            return [-99999.0,-99999.0,-99999.0,-99999.0]

    # get the current pressure at the station
    def get_altimeter_setting(self, metar_text):
        # Altimeter setting can either be found with an A and then 4 digits (measured in inHg) or a Q followed by 4 digits (measured in HPa)
        # Reports the pressure at the station
        match_altimeter_imperial = re.search(r'A(\d{4})', metar_text)
        match_altimeter_international = re.search(r'Q(\d{4})', metar_text)
        if match_altimeter_imperial:
            #print(match_altimeter_imperial)
            altimeter_setting_raw = match_altimeter_imperial.group()
            altimeter_setting = float(altimeter_setting_raw[1:3] + '.' + altimeter_setting_raw[3:5])
            #print(altimeter_setting)
        elif match_altimeter_international:
            #print(match_altimeter_international)
            altimeter_setting_raw = match_altimeter_international.group()[1:]
            altimeter_setting = float(altimeter_setting_raw)
            #print(altimeter_setting)
        else:
            # Altimeter setting not reported
            altimeter_setting = None
        return altimeter_setting


    def parse_data(self):
        results = []
        #airports = Airports()
        try:
            # Using csv.reader to parse the CSV data
            reader = csv.reader(self.csv_data.splitlines())
            k = 0
            station_name = ""
            for row in reader:
                if row:  # Ensure the row is not empty
                    icao = row[0]
                    metar = row[0]
                    lat = 0.0
                    lon = 0.0
                    temp = 0.0
                    dew = 0.0
                    time = 0
                    is_daytime = False
                    #windkts = 0.0
                    #windgustkts = 0.0

                    icao_corrected = ""
                    tempDewRaw = ""
                    cloudCoverWxType = []  # Initialize as an empty list
                    weather_phenomena = ""
                    time_of_day = ""
                    urls = ""
                    try:
                        # Ensure row[0] is a string before passing to regex
                        if isinstance(row[0], list):
                            row_str = ' '.join(map(str, row[0]))  # Convert to string if needed
                        else:
                            row_str = str(row[0])
                        # Passes the METAR and array of derived METAR information into "getTempDew()"
                        # and the program extracts the temp and dew in degrees F and returns them as [temp, dew] for convience
                        #print(metar)
                        tempDewRaw = self.getTempDew(str(metar))
                        #visibility = self.get_visibility(str(metar))

                        # Parse the dat for wind direction, wind speed, and wind gust (if there are any)
                        wind_direction, wind_speed, wind_gust = self.get_wind_dir_speed_gust(str(metar))
                        direction = self.trim_leading_zeros(wind_direction)
                        speed = self.trim_leading_zeros(wind_speed)
                        gust = self.trim_leading_zeros(wind_gust)
                        # If there is a wind direction and gust reported, parse them
                        # If there is no wind gusts reported, gust will be equal to 0

                        visibility = self.get_visibility(str(metar))
                        match = self.get_visibility(str(metar))
                        if match:
                            if isinstance(visibility, int):
                                # the get_visibility() method returns either a match object for vis or 10000 for "CAVOK" or None if no visibility is found
                                # CAVOK has a visibility of 10000 meters
                                visibility = 10000
                            else:
                                # parse visibility match object
                                visibility = match.group(0)
                        else:
                            visibility = None  # or default value
                        #print(f"visibility: {visibility} for metar: {str(metar)}")

                        # Retrieve Current Pressure
                        altimeter_pressure = self.get_altimeter_setting(str(metar))
                        """
                        if altimeter_pressure:
                            print(f"Altimeter pressure is: {altimeter_pressure}")
                        else:
                            print(f"altimeter pressure is not reported")
                        """
                        """
                        if direction and speed:
                            print(f"Wind direction: {direction}, wind speed: {speed}, wind gust: {gust}, for metar {str(metar)}")
                        else:
                            print(f"No wind at metar {str(metar)}")
                        """

                        # Gets the ICAO code like "KBOS"
                        icao_pattern = re.search(r'\b[A-Z]{4}\b', str(metar))

                        try:
                            icao_corrected = icao_pattern.group()
                        except:
                            # for airport identifiers like K1DW that do not follow the traditional 4 uppercase letters, search from the list of all the stations and see if it matches a station.
                            print(f"{str(metar)} not in list looking though list of airports")
                        #cloudCoverWxType = self.cloudCoverType(str(row)) or []
                        cloudCoverWxType = self.cloudCoverType(str(metar)) or []
                        if not isinstance(cloudCoverWxType, list):
                            cloudCoverWxType = []
                        #print(cloudCoverWxType)
                        #print(f"Weather phenomena: {weather_phenomena}")
                        time_of_day = self.present_time(str(metar)) or ""

                        p = self.average_cloud_condition(cloudCoverWxType)
                        #print(p)
                        #print(self.cloud_cover_percentage_to_text(p))
                        #print(cloudCoverWxType)
                        try:
                            if not len(row):
                                print(f"Skipping row {row}. There are only {len(row)} elements")
                            else:
                                lat = float(row[3])
                                lon = float(row[4])
                                temp = float(row[5])
                                dew = float(row[6])
                                try:
                                    datetime_match = self.get_time(str(metar)).group()
                                    #print(f"datetime_match: {datetime_match}, lon: {lon}")
                                    local_time = self.get_local_hour_from_metar_zulu(datetime_match, lon)
                                    #print(datetime_match)
                                    utc_day = int(datetime_match[0:2])
                                    #print(utc_day)
                                    utc_hour = int(datetime_match[2:4])
                                    #print(utc_hour)
                                    utc_min = int(datetime_match[4:6])
                                    #print(utc_min)
                                    #print(f"year:2025, month: 3, day: {utc_day}, hour: {utc_hour}, min: {utc_min}")
                                    #print(f"lat: {lat}, lon: {lon}")
                                    #dt = datetime(2025, 3, 28, 17, 0, tzinfo=timezone.utc)
                                    # Get current date in UTC to infer year and month
                                    now_utc = datetime.now(timezone.utc)
                                    # Construct datetime with correct year/month/day/hour/minute
                                    dt_utc = datetime(now_utc.year, now_utc.month, utc_day, utc_hour, utc_min, 0, tzinfo=timezone.utc)
                                    #dt_utc = datetime(2025, 3, utc_day, utc_hour, utc_min, 0, tzinfo=timezone.utc)
                                    is_daytime = self.is_daytime(lat, lon, dt_utc)
                                    urls_raw = self.determine_wx_icon(weather_phenomena, cloudCoverWxType)
                                    urls = ""
                                    if not urls_raw:
                                        None
                                        #print(f"⚠️ urls_raw is None or empty for {icao} no weather or cloud condition reported")
                                    elif isinstance(urls_raw, list):
                                        if len(urls_raw) >= 3 and is_daytime in [True, False]:
                                            urls = urls_raw[1] if is_daytime else urls_raw[2]
                                        elif len(urls_raw) > 1:
                                            urls = urls_raw[1]  # fallback
                                        elif len(urls_raw) == 1:
                                            urls = urls_raw[0]
                                    elif isinstance(urls_raw, str):
                                        urls = urls_raw
                                    else:
                                        print(f"⚠️ Unexpected type for urls_raw: {type(urls_raw)} from {icao}")
                                    time_info = [is_daytime, local_time]
                                    #print(f"datetime match: {datetime_match}")
                                    #print(f"local time: {local_time}")
                                    #print(f"is daytime: {is_daytime}")
                                except:
                                    print("cannot extract")

                        except (IndexError, ValueError, TypeError):
                            print(f"Skipping {icao} due to missing or invalid lat/lon/temp/dew data.")
                            continue
                        try:
                            # if the station exists in the stations
                            station_name = self.stations[k]
                        except:
                            # if the station doesn't exist in the list of stations just add the ICAO to the list
                            station_name = icao_corrected

                    except Exception as e:
                        # Get traceback info
                        tb = traceback.extract_tb(sys.exc_info()[2])[-1]  # Last call in the traceback
                        filename, lineno, func, code = tb
                        print(f"Skipping {icao}: {e}")
                        print(f"  ↳ Error in file: {filename}, line {lineno}, in {func}")
                        print(f"  ↳ Code: {code}")

                        #print("No Data")
                    # Append new data to super dict
                    #print(float(lat), float(lon), tempDewRaw, icao_corrected, station_name, cloudCoverWxType, weather_phenomena, str(time_of_day), urls)
                    self.superDict[icao_corrected] = [float(lat), float(lon), tempDewRaw ,icao_corrected, station_name, cloudCoverWxType, weather_phenomena, direction, speed, gust, visibility, altimeter_pressure, time_of_day, urls, metar, is_daytime]
                    k += 1
            results.append(self.superDict)
            return results
        except Exception as e:
            print(f"Unexpected error: {e}")
            return results

    def get_local_hour_from_metar_zulu(self, zulu_time_str, lon):
        # Example input: "262353Z"

        utc_hour = int(zulu_time_str[2:4])
        #print(f"utc hour: {utc_hour}")
        utc_minute = int(zulu_time_str[4:6])
        offset = int(round(lon / 15.0))
        local_time = (utc_hour + offset) % 24
        local_time_full = str(local_time) + "" + str(utc_minute)
        #print(local_time_full)
        return local_time_full

    def to_metar_zulu_format(self, dt):
        # Assumes dt is a timezone-aware datetime in UTC
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        return f"{day:02d}{hour:02d}{minute:02d}Z"

    def is_daytime(self, lat, lon, dt_utc):
        try:
            observer = Observer(latitude=lat, longitude=lon)

            # Get sunrise and sunset times for today and tomorrow
            s_today = sun(observer, date=dt_utc.date(), tzinfo=timezone.utc)
            s_yesterday = sun(observer, date=dt_utc.date() - timedelta(days=1), tzinfo=timezone.utc)
            s_tomorrow = sun(observer, date=dt_utc.date() + timedelta(days=1), tzinfo=timezone.utc)

            sunrise = s_today['sunrise']
            sunset = s_today['sunset']

            # Fix the UTC "wraparound" issue: if sunset is earlier than sunrise, it's actually next day
            if sunset < sunrise:
                sunset = s_tomorrow['sunset']

            # Early-morning UTC case: use previous day's sunset
            if dt_utc < sunrise:
                sunset = s_yesterday['sunset']

            #print(f"UTC: {dt_utc}, Sunrise: {sunrise}, Sunset: {sunset}")
            return sunrise <= dt_utc <= sunset

        except Exception as e:
            #print(f"☀️ Error in is_daytime(): {e}")
            return False

    def getLatLon(self, row):
        lat = 0.0
        lon = 0.0
        try:
            lat = float(row[3])
            lon = -1 * float(row[4])
            return([lat, lon])
        except:
            None

    def get_time(self, metar_text):
        # Extract the time of day and the day of the month following the pattern DDHHMM followed by a Z for Zulu
        match = re.search(r'\b\d{6}Z\b', metar_text)
        #day_of_month = match[:1]
        #hour = match[2:3]
        #minutes = match[4:5]
        return(match)
    """
    # extracts the dewpoint and the temperature and convertts them to degrees F and returns them in an array
    def getTempDew(self, textMETAR):
        #Airports from the United States have this code at ththe end of the METAR which is more reliable than matching based on a '/'
        # Note only US based airports use this format for their METARS
        # If this code isn't found then it should go back to the original way of finding the temperature and dewpoint based on the slash
        match = re.search(r'T(\d{4})(\d{4})', textMETAR)
        #If temperature and dewpoint are both positive
        tempDewRaw = re.search(r'\d{2}\/\d{2}',textMETAR)
        # If the temperature is positive and the dewpoint is negative
        tempMDewRaw = re.search(r'\d{2}\/\w\d{2}', textMETAR)
        # If the temperature is negative and the dewpoint is positive
        MtempDewRaw = re.search(r'\w\d{2}\/\d{2}', textMETAR)
        # If the temprature and dewpoint are both negative
        MtempMDewRaw = re.search(r'\w\d{2}\/\w\d{2}', textMETAR)

        # Finds the temperature and dewpoint based on the first instance of a slash
        textMETAR = "METAR KBVY 211853Z 30018G28KT 10SM OVC060 05/M02 A2946 RMK AO2 PK WND 32035/1840 SLP973 T00501022"

        regex_match = re.search(r'\b(M?\d{2})/(M?\d{2})\b', textMETAR)

        if match:
            temp, dew = match.groups()
            match_secondary = re.search(r'\b(M?\d{2})/(M?\d{2})\b', textMETAR)
            temp_raw = match.group(1)
            dew_raw = match.group(2)
            temp_c = -int(temp_raw[1:]) / 10.0 if temp_raw[0] == '1' else int(temp_raw[1:]) / 10.0
            dew_c = -int(dew_raw[1:]) / 10.0 if dew_raw[0] == '1' else int(dew_raw[1:]) / 10.0
            print(temp_c, dew_c)
            temp_f = round((temp_c * 9.0 / 5.0) + 32.0, 2)
            dew_f = round((dew_c * 9.0 / 5.0) + 32.0, 2)
            return [temp_f,dew_f]
        else:
            if(tempDewRaw):
                temp = tempDewRaw.group()[0:2]
                dew = tempDewRaw.group()[3:]
                rh = 100 * (((math.exp((17.625 * float(dew)) / (243.04 + float(dew))) / (math.exp((17.625 * float(temp)) / (243.04 + float(temp)))))))
                heatIndex = 0.5 * ((round(((9.0/5.0)*float(temp))+32.0,2)) + 61.0 + (((round(((9.0/5.0)*float(temp))+32.0,2))-68.0)*1.2) + (rh * 0.094))
                return [round(((9.0/5.0)*float(temp))+32.0,2), round(((9.0/5.0)*float(dew))+32.0,2), round(rh, 2), round(heatIndex, 2)]
            if(tempMDewRaw):
                temp = tempMDewRaw.group()[0:2]
                dew = tempMDewRaw.group()[4:]
                rh = 100 * (((math.exp((17.625 * float(dew)) / (243.04 + float(dew))) / (math.exp((17.625 * float(temp)) / (243.04 + float(temp)))))))
                heatIndex = 0.5 * ((round(((9.0/5.0)*float(temp))+32.0,2)) + 61.0 + (((round(((9.0/5.0)*float(temp))+32.0,2))-68.0)*1.2) + (rh * 0.094))
                return [round(((9.0/5.0)*float(temp))+32.0,2), round(((9.0/5.0)*float(dew))+32.0,2), round(rh, 2), round(heatIndex, 2)]
            if(MtempDewRaw):
                temp = MtempDewRaw.group()[1:3]
                dew = MtempDewRaw.group()[4:]
                rh = 100 * (((math.exp((17.625 * float(dew)) / (243.04 + float(dew))) / (math.exp((17.625 * float(temp)) / (243.04 + float(temp)))))))
                heatIndex = 0.5 * ((round(((9.0/5.0)*float(temp))+32.0,2)) + 61.0 + (((round(((9.0/5.0)*float(temp))+32.0,2))-68.0)*1.2) + (rh * 0.094))
                return [round(((9.0/5.0)*float(temp))+32.0,2), round(((9.0/5.0)*float(dew))+32.0,2), round(rh, 2), round(heatIndex, 2)]
            if (MtempMDewRaw):
                # M01/M04
                temp = MtempMDewRaw.group()[1:3]
                dew = MtempMDewRaw.group()[4:]
                rh = 100 * (((math.exp((17.625 * float(dew)) / (243.04 + float(dew))) / (math.exp((17.625 * float(temp)) / (243.04 + float(temp)))))))
                heatIndex = 0.5 * ((round(((9.0/5.0)*float(temp))+32.0,2)) + 61.0 + (((round(((9.0/5.0)*float(temp))+32.0,2))-68.0)*1.2) + (rh * 0.094))
                return [round(((9.0/5.0)*float(temp))+32.0,2), round(((9.0/5.0)*float(dew))+32.0,2), round(rh, 2), round(heatIndex, 2)]
            else:
                # Else no temperature data was reported
                return [-99999.0,-99999.0,-99999.0,-99999.0]

    """
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

    def generate_thermometer_svg(self, temp_f, wind_direction):
        import random  # if not already imported
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

    def generate_direction_ticks(self, cx=125, cy=125, radius=100, tick_length=10):
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
        x3 = 15 + cx + radius / 2
        y3 = cy + 10

        # Position for West text marker
        x4 = cx - (radius / 2) - 15
        y4 = cy + 10
        svg_parts.append(f'<text x="{x1}" y="{y1}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">S</text>')
        svg_parts.append(f'<text x="{x2}" y="{y2}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">N</text>')
        svg_parts.append(f'<text x="{x3}" y="{y3}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">E</text>')
        svg_parts.append(f'<text x="{x4}" y="{y4}" text-anchor="middle" class="gauge-label" font-size="30" fill="#333" font-family="Arial">W</text>')

        svg_parts.append(f'<g transform="rotate({wind_dir}, {cx}, {cy})"><rect x="{cx-5}" y="{cy}" width="4" height="{radius/2}"/></g>')
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
        """
        for i, (label, color) in enumerate(categories):
            start = start_angle + i * segment_angle
            end = start + segment_angle
            path_b = self.describe_arc(cx, cy, radius + 30, start, end)
            svg_parts.append(f'<path d="{path_b}" stroke="{color}" stroke-width="20" fill="none" stroke-linecap="butt" />')
        """
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
        #svg_parts.append(self.generate_feels_like())
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

    def describe_smaller_arc(self, cx, cy, radius, start_angle, end_angle):
        start_pt = self.polar_to_cartesian(cx, cy, radius, end_angle)
        end_pt = self.polar_to_cartesian(cx,cy, radius, start_angle)
        large_arc = 1 if (end_angle - start_angle) > 180 else 0
        return f'M {start_pt[0]}, {start_pt[1]} A {radius}, {radius} 0 {large_arc}, 0 {end_pt[0]}, {end_pt[1]}'
    # Pass in current temperature and get the temperature category below that temperature, the current temperature category,Category, and the temperature Category above that
    def dynamic_feels_like_category(self, temperature):
        feels_like_categories = [
            {"label": "Life-Threatening Cold", "range": "-40° to -20°", "color": "#4B0082"},
            {"label": "Extreme Cold", "range": "-20° to 0°", "color": "#1E90FF"},
            {"label": "Very Cold", "range": "0° to 20°", "color": "#00BFFF"},
            {"label": "Cold", "range": "20° to 32°", "color": "#87CEEB"},
            {"label": "Chilly", "range": "32° to 45°", "color": "#ADD8E6"},
            {"label": "Cool", "range": "45° to 55°", "color": "#90EE90"},
            {"label": "Comfortable", "range": "55° to 70°", "color": "#2ECC71"},
            {"label": "Warm", "range": "70° to 80°", "color": "#FFD700"},
            {"label": "Hot", "range": "80° to 90°", "color": "#FFA500"},
            {"label": "Very Hot", "range": "90° to 100°", "color": "#FF4500"},
            {"label": "Dangerous Heat", "range": "100° to 110°", "color": "#FF0000"},
            {"label": "Extreme Heat", "range": "110° to 120°", "color": "#8B0000"},
        ]

    def generate_feels_like(self):
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

        categories = []
        """
        if parameter == "temperature":
            categories = temperature_categories
        elif parameter == "dewpoint":
            categories = dewpoint_categories
        """
        svg_parts = []
        svg_width = 450
        x_start = 5
        y_base = 10
        rectangle_length = 100
        space_btwn_categories = 10
        max_per_row = 5

        for i, cat in enumerate(temperature_categories):
            col = i % max_per_row
            row = i // max_per_row
            x = x_start + col * (rectangle_length)
            y = y_base + row * 50

            box = f'''
            <rect x="{x}" y="{y}" width="{rectangle_length}" height="30" rx="4" ry="4" fill="{cat['color']}"/>
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

    # takes in a parameter string if you want to generate a temperature or dewpoint legend (type string)
    # inputs will be "temperature" or "dewpoint"
    def generate_legend(self, parameter):
        temperature_categories = [
            {"label": "Extreme Cold", "range": "-40° to -10°", "color": "#4B0082"},
            {"label": "Cold", "range": "20° to 40°", "color": "#00BFFF"},
            {"label": "Comfortable", "range": "50° to 70°", "color": "#2ECC71"}
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
        rectangle_length = 50
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

        for icao, data in self.superDict.items():
            try:
                lat, lon, temp_c, icao_corrected, station_name, cloudCoverWxType, weather_phenomena, direction, speed, gust, visibility, altimeter_pressure, time, urls, metar, is_daytime = data
                #print(lat, lon, temp_c, icao_corrected, station_name, cloudCoverWxType, weather_phenomena, direction, speed, gust, visibility, altimeter_pressure, time, urls, metar, is_daytime)
                #print(cloudCoverWxType)
                #print(metar)
                #print(lat, lon, temp_c, icao_corrected, station_name)

                # Check if temperature is missing or invalid
                """
                if temp_c[0] == -99999.0 or math.isnan(temp_c[0]):
                    #print(f"⚠️ Skipping {icao} due to bad temperature:", temp_c)
                    continue
                """
                # Ensure temp_c is a valid list or tuple with at least two numeric elements
                if (not isinstance(temp_c, (list, tuple)) or len(temp_c) < 2 or temp_c[0] in (None, -99999.0) or
                not isinstance(temp_c[0], (int, float)) or math.isnan(temp_c[0])
                ):
                    print(f"⚠️ Skipping {icao} due to bad temperature: {temp_c}")
                    continue
                # Skip if cloud cover or URLs are malformed
                if urls is None or (isinstance(urls, list) and len(urls) < 2):
                    print(f"⚠️ Skipping {icao} due to bad URL:", urls)
                    continue


                temperature = temp_c[0]
                dewpoint = temp_c[1]
                cloudCoverWxType = cloudCoverWxType or []
                #cloudCoverWxType1 = cloudCoverWxType
                wx_phenomena = weather_phenomena or ""
                cloudCoverWxTypeccArr = []
                ccAbbrvToFullName = {'CAVOK': 'Clear Skies', 'SKC': 'Clear Skies', 'CLR': 'Clear Skies at or below 12,000 ft', 'FEW': 'Few Clouds', 'SCT': 'Scattered Clouds', 'BKN': 'Broken Clouds', 'OVC': 'Overcast'}
                # cloudCoverWxType input can be [], [['SCT', 200]], OR [[SCT, 20000], ['OVC', 40000], [..,..],...]
                if isinstance(weather_phenomena, list) and len(weather_phenomena) > 0:
                    wx_phenomena = weather_phenomena[0]
                    #print(f"wx_phenomena: {wx_phenomena}")
                else:
                    wx_phenomena = "None"
                    #print(f"wx_phenomena: None!")
                if cloudCoverWxType == ["No Cloud Cover Reported"]:
                    #print("No Cloud Cover Reported")
                    cloudCoverWxTypeccArr.append("No Cloud Cover Reported")
                else:
                    #print(cloudCoverWxType)
                    # Need to covert cloud cover abbreaviations in array to their full name
                    ccArr = []
                    # For multiple cloud layers
                    # Find out each cloud layer type by looping through the input arrays
                    """
                    for i in cloudCoverWxType:
                        print(f"i {i}")
                        # For each cloud height in the input check what cloud condition it matches
                        for metarCCAbbrev, ccFullName in ccAbbrvToFullName.items():
                            # Define an array to collect cloud cover types
                            if i[0] == metarCCAbbrev:
                                if i[0] == 'CLR' or i[0] == 'SKC':
                                    ccArr.append([ccFullName + ' at ' + str(0)])
                                else:
                                    ccArr.append([ccFullName + ' at ' + i[1]])
                    """
                    for i in cloudCoverWxType:
                        if not i or not isinstance(i, list) or len(i) < 2:
                            continue  # Skip invalid entries
                        for metarCCAbbrev, ccFullName in ccAbbrvToFullName.items():
                            if i[0] == metarCCAbbrev:
                                if i[0] in ('CLR', 'SKC', 'CAVOK'):
                                    ccArr.append([f"{ccFullName} at 0"])
                                else:
                                    ccArr.append([f"{ccFullName} at {i[1]}"])
                    # Ensure that ccArr is not empty to avoid division by zero
                    if ccArr:
                        cloudCoverWxTypeccArr = ccArr
                        #print(cloudCoverWxTypeccArr)
                    else:
                        #print("No valid cloud cover data found.")
                        None
                #urls = self.determine_wx_icon(weather_phenomena, cloudCoverWxType)
                #print(lat, lon, temperature, dewpoint, icao_corrected, station_name)
                #print('urls')
                #print(urls)
                if temperature is None or not isinstance(temperature, (int, float)):
                    continue
                if dewpoint == -99999.0 or not isinstance(dewpoint, (int, float)) or math.isnan(dewpoint):
                    print(f"⚠️ Invalid dewpoint for {icao_corrected}: {dewpoint}")

                color1 = self.get_color(temperature)
                gradient_css_temperture = self.get_gradient_window(temperature)
                gradient_css_dewpoint = self.get_gradient_window(dewpoint)
                #color1 = self.get_color(temperature)
                gradient_id = f"arcGradient_{icao_corrected}"
                """
                categories = [
                    ("Dangerously Cold", "#000000"),
                    ("Extreme Cold", "#800000"),
                    ("Frigid", "#A52A2A"),
                    ("Bitter Cold", "#DC143C"),
                    ("Very Cold", "#C71585"),
                    ("Cold", "#9932CC"),
                    ("Chilly", "#8A2BE2"),
                    ("Cool", "#0000FF"),
                    ("Mild", "#1E90FF"),
                    ("Comfortable", "#00FF00"),
                    ("Pleasant", "#7FFF00"),
                    ("Warm", "#FFD700"),
                    ("Hot", "#FFA500"),
                    ("Very Hot", "#FF6347"),
                    ("Scorching", "#FF0000"),
                    ("Danger Zone", "#800000")
                ]
                """
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
                svg_dial_temperature = self.create_svg_dial(round(temperature), temperature_categories)
                svg_dial_dewpoint = self.create_svg_dial(round(dewpoint), dewpoint_categories)
                if speed:
                    svg_dial_wind = self.create_svg_dial_wind(speed, wind_categories, direction)

                svg_thermometer = f"""
                    <svg width="50" height="100" viewBox="0 0 200 300" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                      <defs>
                        <!-- Temperature gradient -->
                        <linearGradient id="thermoGradient" x1="0%" y1="100%" x2="0%" y2="0%">
                          <stop offset="0%" stop-color="blue" />
                          <stop offset="50%" stop-color="yellow" />
                          <stop offset="100%" stop-color="red" />
                        </linearGradient>
                      </defs>

                      <!-- Removed background rect for transparency -->
                      <!-- <rect width="200" height="300" fill="white" /> -->

                      <!-- Outer thermometer shell (white fill inside, black border) -->
                      <path
                        d="
                          M85,30
                          a15,15 0 0 1 30,0
                          v150
                          a35,35 0 1 1 -30,0
                          v-150
                          z"
                        fill="white"
                        stroke="black"
                        stroke-width="4"
                      />

                      <!-- Dynamic stem fill -->
                      <!-- This should be updated dynamically using the Python function -->
                      <rect x="90" y="88" width="20" height="96" fill="url(#thermoGradient)" />

                      <!-- Inner fill shape (tube + smaller, centered bulb) -->
                      <path
                        d="
                          M90,40
                          a10,10 0 0 1 20,0
                          v144
                          a30,30 0 1 1 -20,0
                          v-144
                          z"
                        fill="url(#thermoGradient)"
                      />

                      <!-- Tick marks for every 10°F -->
                      <g stroke="black" stroke-width="2" stroke-linecap="round">
                        <line x1="93" y1="184" x2="107" y2="184" />
                        <line x1="93" y1="175" x2="107" y2="175" />
                        <line x1="93" y1="166" x2="107" y2="166" />
                        <line x1="93" y1="157" x2="107" y2="157" />
                        <line x1="93" y1="148" x2="107" y2="148" />
                        <line x1="93" y1="139" x2="107" y2="139" />
                        <line x1="93" y1="130" x2="107" y2="130" />
                        <line x1="93" y1="121" x2="107" y2="121" />
                        <line x1="93" y1="112" x2="107" y2="112" />
                        <line x1="93" y1="103" x2="107" y2="103" />
                        <line x1="93" y1="94" x2="107" y2="94" />
                        <line x1="93" y1="85" x2="107" y2="85" />
                        <line x1="93" y1="76" x2="107" y2="76" />
                        <line x1="93" y1="67" x2="107" y2="67" />
                        <line x1="93" y1="58" x2="107" y2="58" />
                        <line x1="93" y1="49" x2="107" y2="49" />
                        <line x1="93" y1="40" x2="107" y2="40" />
                      </g>
                    </svg>
                """
                svg_html = f"""
                    <svg viewBox="0 0 200 200" width="100" height="100">
                        <circle cx="100" cy="100" r="80" fill="#FFFFFF" />
                        <!-- Triangle pointer at top center -->
                        <polygon points="100,10 95,25 105,25" fill={self.get_color(temperature)} />
                        <!--<img src="{urls}" style="width: 50px; height: 50px; margin-right: 4px;">-->

                        <text x="100" y="105" text-anchor="middle" fill= {self.get_color(temperature)} font-size="32px" font-family="Arial">
                            {temperature}
                        </text>
                        <defs>
                            <linearGradient id="{gradient_id}" x1="0" y1="100" x2="200" y2="100" gradientUnits="userSpaceOnUse">
                               {self.generate_svg_stops(temperature)}
                            </linearGradient>
                        </defs>
                        <path d="M 51.44 151.44 A 70 70 0 1 1 148.56 151.44"
                            fill="none" stroke="url(#{gradient_id})" stroke-width="20" stroke-linecap="butt" />
                        <h3>{temperature}</h3>
                    </svg>
                """
                value = round((temperature / 120) * 100)  # Map temp to a percentage (example logic)
                label = "Good" if temperature < 90 else "Hot"
                dial_gauge = f"""
                    <svg width="250" height="200" viewBox="0 0 250 200">
                      <!-- Arcs -->
                      <path id="redArc" stroke="#f44336" stroke-width="20" fill="none" stroke-linecap="round"/>
                      <path id="yellowArc" stroke="#ffeb3b" stroke-width="20" fill="none" stroke-linecap="round"/>
                      <path id="greenArc" stroke="#4caf50" stroke-width="20" fill="none" stroke-linecap="round"/>

                      <!-- Knob -->
                      <circle id="knob" cx="0" cy="0" r="7" fill="white" stroke="#ccc" stroke-width="3" />

                      <!-- Text -->
                      <text x="125" y="125" text-anchor="middle" class="gauge-text">{value}%</text>
                      <text x="125" y="150" text-anchor="middle" class="gauge-label">{label}</text>

                      <script type="text/javascript">
                        const centerX = 125;
                        const centerY = 125;
                        const radius = 95;

                        const polarToCartesian = (cx, cy, r, angleDeg) => {{
                          const rad = (angleDeg - 90) * Math.PI / 180;
                          return {{
                            x: cx + r * Math.cos(rad),
                            y: cy + r * Math.sin(rad)
                          }};
                        }};

                        const describeArc = (x, y, r, startAngle, endAngle) => {{
                          const start = polarToCartesian(x, y, r, endAngle);
                          const end = polarToCartesian(x, y, r, startAngle);
                          const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

                          return [
                            "M", start.x, start.y,
                            "A", r, r, 0, largeArcFlag, 0, end.x, end.y
                          ].join(" ");
                        }};

                        const segments = [
                          {{ id: "redArc", start: -135, end: -45 }},
                          {{ id: "yellowArc", start: -35, end: 35 }},
                          {{ id: "greenArc", start: 45, end: 135 }}
                        ];

                        segments.forEach(seg => {{
                          const path = document.getElementById(seg.id);
                          path.setAttribute("d", describeArc(centerX, centerY, radius, seg.start, seg.end));
                        }});

                        const value = {value};
                        const angle = (value / 100) * 270 - 135;
                        const knobPos = polarToCartesian(centerX, centerY, radius, angle);
                        const knob = document.getElementById("knob");
                        knob.setAttribute("cx", knobPos.x);
                        knob.setAttribute("cy", knobPos.y);
                      </script>
                    </svg>
                    """

                html_dial_gague = """
                <style>
                      .gauge-text {
                        font-size: 2em;
                        font-weight: bold;
                      }
                      .gauge-label {
                        font-size: 1.2em;
                        fill: #333;
                      }
                    </style>

                    <svg width="250" height="200" viewBox="0 0 250 200">
                      <path id="redArc" stroke="#f44336" stroke-width="20" fill="none" stroke-linecap="round"/>
                      <path id="yellowArc" stroke="#ffeb3b" stroke-width="20" fill="none" stroke-linecap="round"/>
                      <path id="greenArc" stroke="#4caf50" stroke-width="20" fill="none" stroke-linecap="round"/>
                      <circle id="knob" cx="0" cy="0" r="7" fill="white" stroke="#ccc" stroke-width="3" />
                      <text x="125" y="125" text-anchor="middle" class="gauge-text">58%</text>
                      <text x="125" y="150" text-anchor="middle" class="gauge-label">Good</text>
                    </svg>

                    <script>
                      const centerX = 125;
                      const centerY = 125;
                      const radius = 95;

                      const polarToCartesian = (cx, cy, r, angleDeg) => {
                        const rad = (angleDeg - 90) * Math.PI / 180;
                        return {
                          x: cx + r * Math.cos(rad),
                          y: cy + r * Math.sin(rad)
                        };
                      };

                      const describeArc = (x, y, r, startAngle, endAngle) => {
                        const start = polarToCartesian(x, y, r, endAngle);
                        const end = polarToCartesian(x, y, r, startAngle);
                        const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
                        return ["M", start.x, start.y, "A", r, r, 0, largeArcFlag, 0, end.x, end.y].join(" ");
                      };

                      const segments = [
                        { id: "redArc", start: -135, end: -45 },
                        { id: "yellowArc", start: -35, end: 35 },
                        { id: "greenArc", start: 45, end: 135 }
                      ];

                      segments.forEach(seg => {
                        const path = document.getElementById(seg.id);
                        path.setAttribute("d", describeArc(centerX, centerY, radius, seg.start, seg.end));
                      });

                      const value = 58;
                      const angle = (value / 100) * 270 - 135;
                      const knobPos = polarToCartesian(centerX, centerY, radius, angle);
                      const knob = document.getElementById("knob");
                      knob.setAttribute("cx", knobPos.x);
                      knob.setAttribute("cy", knobPos.y);
                    </script>
                """
                # Associate ICAO with actual airport name (returns an array of country code, region of country, and airport name)
                #airport_name = self.findLoction(icao_corrected)
                airport_info = self.findLoction(icao_corrected)
                airport_display_name = airport_info[2] if airport_info else "Unknown Airport"


                folium.Marker(
                    location=[lat, lon],
                    #icon=folium.DivIcon(html=f""" <img src={urls} width="1px"><div style="font-family: comic sans; font-size: 20px; text-shadow: black 0px 0px 2px; color: {color1}">{temperature}</div>"""),
                    # {self.generate_thermometer_svg(temperature, direction)}
                    icon=folium.DivIcon(html=f"""
                        {self.generate_thermometer_svg(temperature, dewpoint)}
                        <img src = "{urls}" height = "50px" width="50px">
                    """),
                    popup=folium.Popup(html=f"""
                        <h2 style="text-align: center;">{icao_corrected} : {airport_display_name}</h2>
                        <p>Is it Daytime: {is_daytime}</p>
                        <img src="{urls}" width="300px">
                        <h3>Weather Phenomena: {wx_phenomena}</h3>
                        <h3>Cloud Cover: {cloudCoverWxTypeccArr}</h3>
                        <h3> Wind Direction: {direction} deg from North, Wind Speed: {speed} kts, Wind Gust: {gust} kts </h3>
                        <h3>Visibility: {visibility} </h3>
                        <h3>Current Pressure: {altimeter_pressure}</h3>
                        <p>Temperature: {temperature} degrees F</p>
                        {svg_dial_temperature}
                        {self.generate_feels_like()}
                        {svg_dial_dewpoint}
                        {svg_dial_wind}
                        {self.generate_legend("temperature")}
                        {self.generate_legend("dewpoint")}

                        <div style="width: 100%; height: 15px; background: {gradient_css_temperture}; border-radius: 5px; position: relative;">
                            <div style="position: absolute; left: 50%; top: -5px; width: 3px; height: 25px; background: black;"></div>
                        </div>

                        <p>Dewpoint: {dewpoint} degrees F</p>
                        <div style="width: 100%; height: 15px; background: {gradient_css_dewpoint}; border-radius: 5px; position: relative;">
                            <div style="position: absolute; left: 50%; top: -5px; width: 3px; height: 25px; background: black;"></div>

                        </div>


                        <p>Location: ({lat}, {lon})</p>
                        <p>METAR: {metar}</p>
                        <a href="https://api.weather.gov/points/{lat},{lon}">Learn More!</a>
                    """, max_width=300)
                    ).add_to(m)
            except Exception as e:
                print(f"🔥 Skipping {icao} due to error: {e}")
                """
                tb = traceback.extract_tb(sys.exc_info()[2])[-1]
                filename, lineno, func, text = tb
                print(f"🔥 Skipping {icao} due to error on line {lineno}: {e}")
                print(f"  ↳ In file: {filename}, function: {func}")
                print(f"  ↳ Code: {text}")
                """


        from folium import raster_layers
        #image_url = 'https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif'
        raster_layers.ImageOverlay('https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif',
                    [[-119.564209,38.503915],[-114.060059,41.211203]],
                    opacity=0.8,
                   ).add_to(m)
        folium.LayerControl().add_to(m1)

        from folium import raster_layers
        file_path = "/home/tropicainnovations/mysite/static/METAR_map/airport_metar_map.html"
        # Write the file

        # Save the image
        #plt.savefig(file_path)
        #print(f"HTML file saved: {file_path}")
        m.save("airport_metar_map.html")
        m.save(file_path)


if __name__ == '__main__':
    scraper = ProxyScraper()
    # Populate global airport info dictionary
    scraper.fetch_airport_data()
    #scraper.fetch_data(True, "CYLK")
    scraper.fetch_data(True, "KBOS")

    #scraper.fetch_data(False, "KRYY")
    scraper.export_to_json()
    scraper.parse_data()
    scraper.generate_map()