import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from herbie import Herbie
from herbie.toolbox import EasyMap, pc
import numpy as np
from datetime import datetime, timedelta
from herbie import HerbieLatest
from flask import Flask
from metpy.plots import colortables  # Import MetPy colortables
import json
from scipy.spatial import cKDTree
import requests

class HRRR_Temperature_Map:
    def __init__(self):
        self.station_url = 'https://aviationweather.gov/data/cache/stations.cache.json'
        self.url = 'https://aviationweather.gov/data/cache/metars.cache.csv'
        self.city_locatons = {}
        self.superDict = {}
        self.stations = []
        self.metars = []
        self.airportLocations = {}
        self.cityLocations = {}

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
                temp = {}
                dew = {}
                #priority = airport.get("priority")
                self.airportLocations[icao] = [lat, lon, elev, site, state, country, {}, {}]
    def read_json(self, file_path):
        try:
            with open(file_path, 'r') as file:
                city_data = json.load(file)
                for city in city_data:
                    city_name  = city.get("name")
                    country_name  = city.get("cou_name_en")
                    # coordinates is a jsonb array of {lat, lon}
                    coordinates = city.get("coordinates")
                    lat = coordinates.get("lat")
                    lon = coordinates.get("lon")
                    timezone = city.get("timezone")
                    population = city.get("population")
                    elevation = city.get("elevation")
                    temp = {}
                    dew = {}
                    self.cityLocations[city_name] = [lat, lon, country_name, population, elevation, timezone, {}, {}]
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
    def fetch_city_data(self):
        r = requests.get('https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/geonames-all-cities-with-a-population-1000/exports/csv?lang=en&timezone=America%2FNew_York&use_labels=true&delimiter=%3B')
        r_final = r.json()
        print(r)
    def get_forecast(self):
        model_arr = []
        model_arr_dew = []
        for hour in range(0, 17):
            H = HerbieLatest(model="hrrr", product="sfc", fxx=hour)
            ds = H.xarray("TMP:2 m")
            ds_dew = H.xarray("DPT:2 m")
            model_arr.append(ds)
            model_arr_dew.append(ds_dpt)
        #for hour in range(0, 384, 6):
        #H_GFS = HerbieLatest(model="gfs", fxx=hour_gfs)

        # Extract static grid info once
        lats = model_arr[0]['latitude'].values
        lons = model_arr[0]['longitude'].values
        tree = cKDTree(np.column_stack((lats.ravel(), lons.ravel())))

        # Precompute airport grid indices
        airport_indices = {}
        i = 0
        for icao, data in self.airportLocations.items():
            lat = data[0]
            lon = self.normalize_lon(data[1])
            _, idx = tree.query([lat, lon])
            y_idx, x_idx = np.unravel_index(idx, lats.shape)
            airport_indices[icao] = (y_idx, x_idx)
            i += 1
            total_steps = len(self.airportLocations) * len(model_arr)
            print(f"{(i / total_steps) * 100:.2f}%")


        j = 0
        # Extract data for all hours
        varname = list(model_arr[0].data_vars.keys())[0]

        for hour, ds in enumerate(model_arr):
            data_array = ds[varname]
            for icao, (y_idx, x_idx) in airport_indices.items():
                temp_kelvin = data_array.isel(y=y_idx, x=x_idx).values.item()
                temp_f = (temp_kelvin - 273.15) * 9/5 + 32
                self.airportLocations[icao][6][hour] = temp_f
                j+=1
                total_steps = len(self.airportLocations) * len(model_arr)
                print(f"{(j / total_steps) * 100:.2f}%")

        """
        model_arr = []
        for hour in range(0,17):
            # Load latest HRRR surface model
            H = HerbieLatest(model="hrrr", product="sfc", fxx=hour)
            ds = H.xarray("TMP:2 m")  # Loads the right field
            # Get the lat/lon arrays
            lats = ds['latitude'].values
            lons = ds['longitude'].values
            model_arr.append(ds)
        # Get the actual variable name from the dataset
        varname = list(ds.data_vars.keys())[0]
        i = 0

        for icao, data in self.airportLocations.items():
            for hour, ds in enumerate(model_arr):
                lats = ds['latitude'].values
                lons = ds['longitude'].values
                tree = cKDTree(np.column_stack((lats.ravel(), lons.ravel())))

                for icao, data in self.airportLocations.items():
                    airport_lat = data[0]
                    airport_lon = self.normalize_lon(data[1])

                    _, idx = tree.query([airport_lat, airport_lon])
                    y_idx, x_idx = np.unravel_index(idx, lats.shape)

                    temp_kelvin = ds[varname].isel(y=y_idx, x=x_idx).values.item()
                    temp_fahrenheit = (temp_kelvin - 273.15) * 9/5 + 32

                    data[6][hour] = temp_fahrenheit
                i += 1
                print(f"{(i / len(self.airportLocations)) * 100}%")
        """
        """
            for hour, item in enumerate(model_arr):
                airport_lat = data[0]  # lat
                airport_lon = self.normalize_lon(data[1])  # lon
                #print(airport_lat, airport_lon)
                #print(lats, lons)

                # Find the nearest x/y index
                dist_sq = (lats - airport_lat)**2 + (lons - airport_lon)**2
                #print(dist_sq)
                y_idx, x_idx = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)

                # Extract the value
                temp_kelvin = item[varname].isel(y=y_idx, x=x_idx).values.item()

                # Convert to Fahrenheit
                temp_fahrenheit = (temp_kelvin - 273.15) * 9/5 + 32
                # Get or create the temp dict
                temps_by_hour = data[6]  # index 6 is temp dict

                # Store the temperature for this hour
                temps_by_hour[hour] = temp_fahrenheit


                #print(f"{icao} 2m temperature: {temp_fahrenheit:.2f}°F for hour: {hour}")
                # This should give you the dictionary for each airport.
                # Want to put {icao: {hour: temp}}
                data[6][hour] = temp_fahrenheit
            i += 1
            #print(f"{(i / len(self.airportLocations)) * 100}%")
            """

    def get_forecast_fast(self):
        city_data = self.cityLocations
        airport_data = self.airportLocations
        model_arr = []
        model_arr_dew = []
        hours = range(0, 17)

        # Step 1: Download and store GRIB files for each forecast hour
        for hour in hours:
            H = HerbieLatest(model="hrrr", product="sfc", fxx=hour)
            ds = H.xarray("TMP:2 m")
            ds_dew = H.xarray("DPT:2 m")
            model_arr.append(ds)
            model_arr_dew.append(ds_dew)

        # Step 2: Get lat/lon grid once from first dataset
        lats = model_arr[0]['latitude'].values
        lons = model_arr[0]['longitude'].values

        # Step 3: Build KDTree and precompute nearest grid indices for each airport
        points = np.column_stack((lons.ravel(), lats.ravel()))
        tree = cKDTree(points)


        city_indices = {}
        for i, (name, data) in enumerate(city_data.items()):
            lat = data[0]
            lon = self.normalize_lon(data[1])
            _, idx = tree.query([self.normalize_lon(lon), lat])
            y_idx, x_idx = np.unravel_index(idx, lats.shape)
            city_indices[name] = (y_idx, x_idx)

            #print(f"[Indexing] {i + 1}/{len(city_data)} ({((i + 1) / len(city_data)) * 100:.2f}%)")

        # Step 4: Precompute variable name
        varname = list(model_arr[0].data_vars.keys())[0]
        var_dew = list(model_arr_dew[0].data_vars.keys())[0]

        # Step 5: For each hour, extract temperatures using NumPy indexing
        total_steps = len(hours) * len(city_data)
        step = 0

        for hour, ds in enumerate(model_arr):
            #data_array = ds[varname].data  # .data avoids xarray overhead
            #data_array_dpt = ds_dew["DPT:2 m"].data  # .data avoids xarray overhead
            #data_array_dpt = ds_dew["d2m"].data
            temp_data = model_arr[hour][varname].data
            dew_data = model_arr_dew[hour][var_dew].data

            for icao, (y_idx, x_idx) in city_indices.items():
                temp_k = temp_data[y_idx, x_idx]
                temp_f = round((temp_k - 273.15) * 9 / 5 + 32, 2)
                city_data[icao][6][hour] = temp_f

                # Handle dewpoints
                dew_k = dew_data[y_idx, x_idx]
                dew_f = round((dew_k - 273.15) * 9/5 + 32, 2)
                city_data[icao][7][hour] = dew_f
                step += 1
                """
                if step % 100 == 0 or step == total_steps:
                    print(f"[Extracting] {step}/{total_steps} ({(step / total_steps) * 100:.2f}%)")
                """

    def json_dump(self):
        with open('/home/tropicainnovations/mysite/static/hrrr_grib_json_dump/hrrr_dump.json', "w") as f:
            json.dump(self.cityLocations, f)
    def normalize_lon(self, lon):
        """Convert longitude to 0–360° east format"""
        return lon if lon >= 0 else 360 + lon

    def get_forecast_test(self):

        # Coordinates for KBOS (Boston Logan)
        kbos_lat = 42.3656
        lon = -71.0096
        kbos_lon = self.normalize_lon(lon)

        # Load latest HRRR surface model
        H = HerbieLatest(model="hrrr", product="sfc", fxx=0)
        ds = H.xarray("TMP:2 m")  # Loads the right field
        varname = list(ds.data_vars.keys())[0]
        data = ds[varname].values

        #print("Data shape:", data.shape)
        #print("Min:", np.min(data))
        #print("Max:", np.max(data))

        # Get the lat/lon arrays
        lats = ds['latitude'].values
        lons = ds['longitude'].values

        #print("Latitude range:", np.min(lats), np.max(lats))
        #print("Longitude range:", np.min(lons), np.max(lons))

        # Find the nearest x/y index to KBOS
        dist_sq = (lats - kbos_lat)**2 + (lons - kbos_lon)**2
        y_idx, x_idx = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)

        # Get the actual variable name from the dataset
        varname = list(ds.data_vars.keys())[0]

        # Extract the value at the closest grid point
        temp_kelvin = ds[varname].isel(y=y_idx, x=x_idx).values.item()

        # Convert to Fahrenheit
        temp_fahrenheit = (temp_kelvin - 273.15) * 9/5 + 32

        print(f"KBOS 2m temperature: {temp_fahrenheit:.2f}°F")





    def convert_units(self, SI_unit, data_to_convert):
        if SI_unit == "K":
            converted_unit = (data_to_convert - 273.15) * (9.0/5.0) + 32.0  # Convert Kelvin to Fahrenheit
            return converted_unit
        elif SI_unit == "m s**-1":
            converted_unit = data_to_convert * 2.23694  # Convert meters per second to miles per hour
            return converted_unit
        else:
            return data_to_convert  # Return unchanged data if no conversion is needed


    # This method allows you to dynamically assign individual colortables from matplotlib
    # Takes in the SI Unit from the variable and outputs a string colortable
    def find_colormap(self, long_name):
        # Temperature is measured in Kelvin (K)
        if(long_name == "2 metre temperature"):
            return "nipy_spectral"
        elif(long_name == "2 metre dewpoint temperature"):
            return "YlGn"
        elif(long_name == "2 metre relative humidity"):
            return "PuBu"
        elif(long_name == "Maximum/Composite radar reflectivity"):
            return "NWSReflectivityExpanded"
        elif(long_name == "Wind speed (gust)"):
            return "plasma"
        else:
            return "rainbow"

    # This method takes an SI unit such as 'K' for Kelvin and would return the full metric equivelant name
    # For example an input of 'K' (for Kelvin) would return the string 'Farenheit'
    # Used to represent the correct units when making the color table for labeling purposes
    # If a metric version is videly used such as decibels then an input of the abbreviated version (dB) would return the full name "decibeks"
    def metric_to_imperial_unit_name(self, SI_unit_name):
        #"K"(Kelvin)->"Farenheit"
        if(SI_unit_name == "K"):
            return "Fahrenheit"
        # "m s**-1" (meters/second) -> "miles/hour"
        elif(SI_unit_name == "m s**-1"):
            return "miles/hour"
        # "dB" (decibels) -> "decibels"
        elif(SI_unit_name == "dB"):
            return "decibels"
        # "Pa" (Pascals)
        elif(SI_unit_name == "Pa"):
            return "hectopascals"
        # "%" (%RH) -> "% Relative Humidity"
        elif(SI_unit_name == "%"):
            return "% Relative Humidity"


if __name__ == '__main__':
    HRRR_Temperature_Map = HRRR_Temperature_Map()
    HRRR_Temperature_Map.read_json('/home/tropicainnovations/mysite/static/geonames-all-cities-with-a-population-1000.json')
    #HRRR_Temperature_Map.fetch_city_data()
    #HRRR_Temperature_Map.fetch_airport_data()
    #HRRR_Temperature_Map.get_forecast()
    HRRR_Temperature_Map.get_forecast_fast()
    HRRR_Temperature_Map.json_dump()
    #HRRR_Temperature_Map.get_forecast_test()