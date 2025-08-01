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

class HRRR_Temperature_Map:
    def __init__(self):
        self.station_url = 'https://aviationweather.gov/data/cache/stations.cache.json'
        self.url = 'https://aviationweather.gov/data/cache/metars.cache.csv'
        self.superDict = {}
        self.stations = []
        self.metars = []
        self.airportLocations = {}
    # Read in airport information json file and populate airportLocations dictionary
    def fetch_airport_data(self):
        with open('/Users/scottreinhardt/flasktropica/static/metar_map/station_list/stations.cache.json') as airport_list:
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
                #priority = airport.get("priority")
                self.airportLocations[icao] = [lat, lon, elev, site, state, country, {}]

    def get_forecast(self):
        model_arr = []
        # Initialize HRRR datasets
        for hour in range(0,17):
            # Load latest HRRR surface model
            H = HerbieLatest(model="hrrr", product="sfc", fxx=hour)
            #H_GFS = HerbieLatest(model="gfs", fxx=hour)
            ds = H.xarray("TMP:2 m")  # Loads the right field
            f = H.file  # This is a FileDownloader object
            f.filter("TMP:2 m above ground").download(save_dir="/home/tropicainnovations/mysite/static/model_grib_files/")


            # Get the lat/lon arrays
            lats = ds['latitude'].values
            lons = ds['longitude'].values
            #ds.download(save_dir="/home/tropicainnovations/mysite/static/model_grib_files/")
            model_arr.append(ds)
            model_arr.append(ds_dpt)
        # Initialize GFS datasets count in increments of 6 hours
        #for hour_gfs in range(0, 383, 6):
        #    H_GFS = HerbieLatest(model="gfs", fxx=hour_gfs)
        #    H_GFS.download(save_dir="/home/tropicainnovations/mysite/static/model_grib_files/")
        # Get the actual variable name from the dataset
        #varname = list(ds.data_vars.keys())[0]
        """
        for icao, data in self.airportLocations.items():
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
    """
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
    #HRRR_Temperature_Map.fetch_airport_data()
    HRRR_Temperature_Map.get_forecast()
    #HRRR_Temperature_Map.get_forecast_test()