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

    def fetch_data(self, test_mode, icao_input):
        try:
            """
            if test_mode:
                # Load one example METAR for testing
                self.csv_data = 'KRYY 261649Z 33010G16KT 10SM CLR 17/01 A3025 RMK AO2 SLPNO T01700010 $,KRYY,2025-03-26T16:49:00Z,34.0146,-84.5964,17,1,330,10,16,10+,30.25,,,,TRUE,TRUE,,,,,,CLR,,,,,,,,VFR,,,,,,,,,,,,METAR,306'
                self.stations = ["Marietta/Cobb Cnty"]
                self.airportLocations = {
                    "KUNV": ["US", "PA", "State College/Univ Park Arpt"]
                }
            """
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
                airport_response = requests.get("https://raw.githubusercontent.com/ip2location/ip2location-iata-icao/master/iata-icao.csv")
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
                       ' SKC ': ['Clear Skies', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/32_orig.png']}

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
                          'SKC': ['Clear, no cloud levels reported at any height', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png']}
        # declare temporary array to store the abbreviation of the cloud condition as the 0th element and the cloud height * 1000 as the 1st element
        finalCloud = []
        # loop through every matching cloud cover report in the metar returned in the matches array
        """
        for i in matches:
            # Take the first 3 characters of i or SCT020 for example, which would be SCT
            # If the first 3 characters is a key in the cloudCoverType dict, seperate the abbreviation from the cloud height and put them in the temporary array as seperate elements
            if i[0:3] in cloudCoverType:
                #print(i)
                #finalCloudHeight = int(self.checkForLeadingZeroes(i[3:7])) * 1000
                # Edge case: check to see if you get a leading zero as the cloud height (will result in having 0 as a cloud height after converted and multiplied)
                cloudHeight = str(int(self.checkForLeadingZeroes(i[3:7]))) + ' ft'
                # Covert the cloud height to an integer and multiply by 1000 to get the cloud height
                finalCloud.append([i[0:3], cloudHeight])
        """
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
        pattern = r'\d{6}Z'
        time_of_day_raw = re.search(pattern, metar)
        #print(time_of_day_raw.group(0)[2:])
        return time_of_day_raw.group(0)[2:]

    # pass in average wx phenomena from average_cloud_condition() method
    def retrieve_url_from_wx_phenomena(self, averageCloudCondition):
        cloudCoverType = {'CLR':['Clear Skies at or below 12000ft', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0001-sunny_orig.png','https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/wsymbol-0008-clear-sky-night_orig.png'],
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
    """
    def determine_wx_icon(self, weather_phenomena, cloud_cover_type):
        if weather_phenomena == '' and cloud_cover_type == []:
            # No need for time of day, return N/A icon
            return ['N/A', 'https://tropicainnovations.weebly.com/uploads/3/6/0/1/3601755/44_orig.png']
        # of there is no weather phenomena
        elif weather_phenomena == '':
            # Only use cloud cover averages and time of day
            # No time input, so only return the icon for cloud cover only
            print(cloud_cover_type)
            #extractCloudCoverType = self.cloudCoverType(cloud_cover_type)
            #print(extractCloudCoverType)
            avgCloudCoverNumerical = self.average_cloud_condition(extractCloudCoverType)
            # returns an array of the abbreviation of the avg cloud conditions along with the associated icon url
            avgCloudCoverText = self.cloud_cover_percentage_to_text(avgCloudCoverNumerical)[0]
            #print(avgCloudCoverText)
            # Prints [] if no cloud cover reported, and the average cloudcover condition as a string as well as the associated url to that cloud cover icon
            urlAndDescription = self.retrieve_url_from_wx_phenomena(avgCloudCoverText)
            if urlAndDescription == []:
                urlAndDescription.append('No Cloud Conditions Reported')
                #None
            #print(urlAndDescription)
            #return the average cloud condition url to the icon
            return urlAndDescription
        else:
            # Only return weather phenomena
            return weather_phenomena
            # Go through every weather condition that you want to use here
            # Will use both weather_phenomena and cloud_cover_type but not time_of_day
    """
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
        cloudCoverTypes = {'CLR': 0.0, 'FEW': 0.25, 'SCT': 0.50, 'BKN': 0.75, 'OVC': 1.0, 'SKC': 0.00}

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
                """
        elif len(cloudCoverType) == 1:
            # Only one cloud layer is given, return the percentage of cloud cover specified
            # Loop through the different cloud cover keys and values in the average_cloud_condition dict
            for key, value in cloudCoverTypes.items():
                # If the current key that you are on in the for loop matches the double array input, return the value of the key
                # Example, if key is currently 'FEW' and cloudCover = [['FEW', 2000]], cloudCoverType[0][0] of [['FEW', 2000]] is 'FEW'
                # 'FEW''s value in the dict is 0.25, so return 0.25

                #if key == cloudCoverType[0][0]:
                #    return value

                if len(cloudCoverType) == 1 and isinstance(cloudCoverType[0], list):
                    for key, value in cloudCoverTypes.items():
                        if key == cloudCoverType[0][0]:
                            return value
        """

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
                        """
                        # loop through all of the cloudCoverTypes again
                        for metar_cloud_cover, percentage_cloud_cover in cloudCoverTypes.items():
                            # Define an array to collect cloud cover types
                            print(f"hello {metar_cloud_cover}, {percentage_cloud_cover}")
                            # if one of the cloud cover types in cloudCoverTypes matches the cloud cover type from i in i[0]
                            if i[0] == metar_cloud_cover:
                                print(metar_cloud_cover, percentage_cloud_cover)
                                ccArr.append(percentage_cloud_cover)
                        """
            except Exception as e:
                print(f"⚠️ Error in average_cloud_condition loop: {e}")
                return 0
            # Ensure that ccArr is not empty to avoid division by zero
            print(f"ccarr: {ccArr}")
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

                        # Gets the ICAO code like "KBOS"
                        icao_pattern = re.search(r'\b[A-Z]{4}\b', str(metar))
                        icao_corrected = icao_pattern.group()
                        #cloudCoverWxType = self.cloudCoverType(str(row)) or []
                        cloudCoverWxType = self.cloudCoverType(str(metar)) or []
                        if not isinstance(cloudCoverWxType, list):
                            cloudCoverWxType = []
                        #print(cloudCoverWxType)
                        #print(f"Weather phenomena: {weather_phenomena}")
                        #urls = self.determine_wx_icon(weather_phenomena, metar)
                        #urls = self.determine_wx_icon(weather_phenomena, cloudCoverWxType)
                        #print(f"urls: {urls}")
                        #time_of_day = self.present_time(str(metar)) or ""

                        #p = self.average_cloud_condition(cloudCoverWxType)
                        #print(urls)
                        """
                        if urls == []:
                            urls = urls
                        else:
                            urls = urls[1]
                        """
                        #if urls and isinstance(urls, list) and len(urls) > 1:
                        #    urls = urls[1]
                        #else:
                        #    urls = ""
                        #urls_raw = self.determine_wx_icon(weather_phenomena, metar)
                        # Default to empty string if urls_raw is None or not a list
                        urls_raw = self.determine_wx_icon(weather_phenomena, cloudCoverWxType)
                        #print(f"urls: {urls_raw}")
                        urls = ""
                        if not urls_raw:
                            print(f"⚠️ urls_raw is None or empty for {icao}")
                        elif isinstance(urls_raw, list):
                            if len(urls_raw) > 1 and isinstance(urls_raw[1], str):
                                urls = urls_raw[1]
                            elif len(urls_raw) == 1 and isinstance(urls_raw[0], str):
                                urls = urls_raw[0]
                        elif isinstance(urls_raw, str):
                            urls = urls_raw
                        else:
                            print(f"⚠️ Unexpected type for urls_raw: {type(urls_raw)} from {icao}")


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
                                """
                                try:
                                    datetime_match = self.get_time(str(metar)).group()
                                    print(f"datetime_match: {datetime_match}, lon: {lon}")
                                    local_time = self.get_local_hour_from_metar_zulu(datetime_match, lon)
                                    print(datetime_match)
                                    utc_day = int(datetime_match[0:2])
                                    print(utc_day)
                                    utc_hour = int(datetime_match[2:4])
                                    print(utc_hour)
                                    utc_min = int(datetime_match[4:5])
                                    print(utc_min)
                                    print(f"year:2025, month: 3, day: {utc_day}, hour: {utc_hour}, min: {utc_min}")
                                    dt_utc = datetime(2025, 3, utc_day, utc_hour, utc_min, 0, tzinfo=timezone.utc)
                                    is_daytime = self.is_daytime(lat, lon, dt_utc)
                                    print(f"datetime match: {datetime_match}")
                                    print(f"local time: {local_time}")
                                    print(f"is daytime: {is_daytime}")
                                except:
                                    print("cannot extract")
                                """

                            print(lat, lon, temp, dew)
                        except (IndexError, ValueError, TypeError):
                            print(f"Skipping {icao} due to missing or invalid lat/lon/temp/dew data.")
                            continue
                        #print(lat, lon, temp, dew)
                        station_name = self.stations[k]
                    except Exception as e:
                        # No Data Recorded, don't do anything
                        print(f"Skipping {icao}: {e}")

                        #print("No Data")
                    # Append new data to super dict
                    #print(float(lat), float(lon), tempDewRaw, icao_corrected, station_name, cloudCoverWxType, weather_phenomena, str(time_of_day), urls)
                    self.superDict[icao_corrected] = [float(lat), float(lon), tempDewRaw ,icao_corrected, station_name, cloudCoverWxType, weather_phenomena, time_of_day, urls, metar]
                    k += 1
            results.append(self.superDict)
            return results
        except Exception as e:
            print(f"Unexpected error: {e}")
            return results
    from datetime import datetime, timedelta

    def get_local_hour_from_metar_zulu(self, zulu_time_str, lon):
        # Example input: "262353Z"

        utc_hour = int(zulu_time_str[2:4])
        utc_minute = int(zulu_time_str[4:6])
        offset = int(round(lon / 15.0))  # crude but decent
        local_time = (utc_hour + offset) % 24
        local_time_full = str(local_time) + "" + str(utc_minute)
        print(local_time_full)
        return local_time_full

    from astral import LocationInfo
    from astral.sun import sun
    from datetime import datetime, timezone

    from astral import Observer
    from astral.sun import sun

    def is_daytime(self, lat, lon, dt_utc):
        observer = Observer(latitude=lat, longitude=lon)
        print(f"observer = {observer}")
        s = sun(observer, date=dt_utc.date(), tzinfo=timezone.utc)

        sunrise = s['sunrise']
        sunset = s['sunset']

        return sunrise <= dt_utc <= sunset

    """
    def parse_data(self):
    results = []
    try:
        reader = csv.reader(self.csv_data.splitlines())
        k = 0
        for row in reader:
            if row is None or len(row) == 0:
                print(f"Skipping empty row: {k}")
                continue  # Skip empty rows

            icao = row[0]
            lat, lon, temp, dew = 0.0, 0.0, 0.0, 0.0  # Default values
            try:
                lat = float(row[3])
                lon = float(row[4])
                temp = float(row[5])
                dew = float(row[6])
            except (IndexError, ValueError, TypeError):
                print(f"Skipping {icao} due to missing or invalid lat/lon/temp/dew data.")
                continue

            cloudCoverWxType = self.cloudCoverType(str(row)) or []
            weather_phenomena = self.find_weather_condition(str(row)) or ""
            urls = self.determine_wx_icon(weather_phenomena, cloudCoverWxType)

            if isinstance(urls, list) and len(urls) > 1:
                urls = urls[1]
            else:
                urls = ""

            self.superDict[icao] = [float(lat), float(lon), temp, dew, icao, cloudCoverWxType, weather_phenomena, "", urls]
            k += 1

        results.append(self.superDict)
        return results
    except Exception as e:
        print(f"Unexpected error: {e}")
        return results
    """

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
            print(temp_c, dew_c)
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
            return [round(((9.0/5.0)*float(temp_c))+32.0,2), round(((9.0/5.0)*float(dew_c))+32.0,2), round(rh, 2), round(heatIndex, 2)]
        else:
            return [-99999.0,-99999.0,-99999.0,-99999.0]
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

    def generate_map(self):
        #data = json.loads('https://aviationweather.gov/data/cache/stations.cache.json')
        #for item in data:
        #    print(item)
        # Center the map on the USA
        m = folium.Map(location=[37.0902, -95.7129], zoom_start=8)
        m1 = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

        for icao, data in self.superDict.items():
            try:
                lat, lon, temp_c, icao_corrected, station_name, cloudCoverWxType, weather_phenomena, time, urls, metar = data
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
                if (
                not isinstance(temp_c, (list, tuple)) or
                len(temp_c) < 2 or
                temp_c[0] in (None, -99999.0) or
                not isinstance(temp_c[0], (int, float)) or
                math.isnan(temp_c[0])
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
                ccAbbrvToFullName = {'SKC': 'Clear Skies', 'CLR': 'Clear Skies at or below 12,000 ft', 'FEW': 'Few Clouds', 'SCT': 'Scattered Clouds', 'BKN': 'Broken Clouds', 'OVC': 'Overcast'}
                # cloudCoverWxType input can be [], [['SCT', 200]], OR [[SCT, 20000], ['OVC', 40000], [..,..],...]
                if isinstance(weather_phenomena, list) and len(weather_phenomena) > 0:
                    wx_phenomena = weather_phenomena[0]
                else:
                    wx_phenomena = "None"
                if cloudCoverWxType == ["No Cloud Cover Reported"]:
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
                                if i[0] in ('CLR', 'SKC'):
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
                color1 = self.get_color(temperature)
                #color1 = self.get_color(temperature)

                # Associatre ICAO with actual airport name (returns an array of country code, region of country, and airport name)
                airport_name = self.findLoction(icao_corrected)

                folium.Marker(
                    location=[lat, lon],
                    #icon=folium.DivIcon(html=f""" <img src={urls} width="1px"><div style="font-family: comic sans; font-size: 20px; text-shadow: black 0px 0px 2px; color: {color1}">{temperature}</div>"""),
                        icon=folium.DivIcon(html=f"""
                        <div style="display: flex; align-items: center;">
                            <img src="{urls}" style="width: 50px; height: 50px; margin-right: 4px;">
                            <br>
                            <div style="font-family: Comic Sans MS, Comic Sans; font-size: 20px; text-shadow: black 0px 0px 2px; color: {color1};">
                                {temperature}
                            </div>
                        </div>
                        """),
                    popup=folium.Popup(html=f"""
                        <h2 style="text-align: center;">{icao_corrected} : {airport_name}</h2>
                        <img src={urls} width="300px">
                        <h2 style="text-align: center;">Weather Phenomena: {wx_phenomena}</h3>
                        <h2 style="text-align: center;">Cloud Cover: {cloudCoverWxTypeccArr}</h3>
                        <p>Temperature: {temperature}&deg;F</p>F</p>
                        <input type="range" min="-5" max="120" value={temperature} class="slider" id="myRange">
                        <p>Dewpoint: {dewpoint}&deg;F</p>
                        <input type="range" min="-5" max="120" value={dewpoint} class="slider" id="myRange">
                        <p>Location: ({lat}, {lon})</p>
                        <p>METAR: {metar}</p>
                        <a href="https://api.weather.gov/points/{lat},{lon}">Learn More!</a>
                    """, max_width=300)
                    ).add_to(m)
            except Exception as e:
                print(f"🔥 Skipping {icao} due to error: {e}")


        from folium import raster_layers
        #image_url = 'https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif'
        raster_layers.ImageOverlay('https://mesonet.agron.iastate.edu/data/gis/images/4326/USCOMP/n0r_anim_large.gif',
                    [[-119.564209,38.503915],[-114.060059,41.211203]],
                    opacity=0.8,
                   ).add_to(m)
        folium.LayerControl().add_to(m1)

        from folium import raster_layers

        # Ensure the directory exists
        #output_dir = os.path.join(app.root_path, "static", "METAR_map")
        #os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Sanitize the product name for safe file naming
        #no_spaces_product = product.replace(" ", "_").replace(":", "_")

        # Construct the file path to save the image in the static directory
        #file_path = os.path.join(output_dir, f"airport_metar_map.html")
        file_path = "/home/tropicainnovations/mysite/static/METAR_map/airport_metar_map.html"
        # Write the file

        # Save the image
        #plt.savefig(file_path)
        #print(f"HTML file saved: {file_path}")
        m.save("airport_metar_map.html")
        m.save(file_path)


if __name__ == '__main__':
    scraper = ProxyScraper()
    #scraper.fetch_data(True, "KDUB")
    scraper.fetch_data(False, "KRYY")
    scraper.parse_data()
    scraper.generate_map()
