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
from datetime import datetime, timedelta
import xarray

class HRRR_Point_Forecast:
    def __init__(self):
        self.station_url = 'https://aviationweather.gov/data/cache/stations.cache.json'
        self.url = 'https://aviationweather.gov/data/cache/metars.cache.csv'
        self.city_locatons = {}
        self.superDict = {}
        self.stations = []
        self.metars = []
        self.airportLocations = {}
        self.cityLocations = {}
        # for valid hours to their respective datetime strings dictionary
        self.valid_hrs_dt = {}

    # This method reads in each parameter from the list of cities and stores them in a large array
    def read_json(self, file_path):
        try:
            with open(file_path, 'r') as file:
                city_data = json.load(file)
                # Loop over every city in the list of cities
                for city in city_data:
                    # Extract the city name
                    city_name  = city.get("name")
                    # Extract the country name
                    country_name  = city.get("cou_name_en")
                    # Extract the time zone
                    time_zone = city.get("timezone")
                    #zip_code  = city.get("zip_code")
                    # coordinates is a json array of {lat, lon}
                    # Extract the coordinates, which contain the lat and lon
                    coords = city.get("coordinates")
                    # Obtain the lat and lon from coords
                    lat = coords.get("lat")
                    lon = coords.get("lon")
                    # Initialize empty arrays to hold all of the variables you are looking for
                    temp = []
                    dew = []
                    #wind_speed = []
                    #wind_direction = []
                    wx_phenom = []
                    self.cityLocations[city_name] = [lat, lon, city_name, country_name, time_zone, temp, dew, wx_phenom]
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")

    # Converts the hour into UTC (zulu time)
    def hour_int_to_utc(self, int_hour):
        if int_hour == 0:
            return "00"
        elif int_hour == 6:
            return "06"
        else:
            return str(int_hour)

    def get_latest_hrrr_run(self):
        now = datetime.utcnow()

        if now.hour >= 22:
            current_run = 18
        elif now.hour >= 16:
            current_run = 12
        elif now.hour >= 10:
            current_run = 6
        elif now.hour >= 4:
            current_run = 0
        else:
            # If it's earlier than 03Z, use yesterday's 18Z run
            current_run = 18
            now = now - timedelta(days=1)
        current_date = now.date()
        formatted_run_hour = self.hour_int_to_utc(current_run)

        return [current_date, formatted_run_hour]

        #return now.replace(hour=current_run, minute=0, second=0, microsecond=0)

    def list_var_names(self):
        # Find the latest gfs run date and run hour using the get_layest_gfs_run() method
        run_params = self.get_latest_gfs_run()
        date = run_params[0]
        run_hour = run_params[1]
        H = Herbie(date=date, model="gfs", product="pgrb2.0p25",run=run_hour, fxx=6)
        inv = H.inventory()
        for item in inv["variable"]:
            print(item)
        #print(inv[inv["name"].str.contains("cloud|gust|vis|precip|snow|fog", case=False, na=False)])
    # Returns the number of hours ahead from the initialization time of the model time to no
    # If the model initialized at 12z and the current time is 18z, you would want to start at hour 6
    def starting_fxx(self, model_initialized_hour):
        # get current time in UTC
        now = datetime.utcnow()
        fxx = now.hour - model_initialized_hour
        # If now.hour < model_initialized_hour, then fxx will be negative so add 24 hours
        # For example if it is 00z and the model initialized at 18z
        if fxx < 0:
            fxx += 24
        return fxx

    def get_forecast_fast(self):
        city_data = self.cityLocations
        airport_data = self.airportLocations
        # Hours in total_hours that herbie can find the equaivelant file for
        valid_hours = []

        model_arr = []
        model_arr_dew = []
        model_arr_wind_u = []
        model_arr_wind_v = []
        model_arr_cc = []
        model_arr_vis = []
        model_arr_snow = []
        model_arr_rain_rate = []
        model_arr_rh = []
        model_arr_cape = []
        model_arr_refc = []
        #model_array_chance_preip = []
        #model_arr_total_precip = []
        #model_arr_total_precip_type = []
        time_step = 1

        latest_date, latest_run = self.get_latest_hrrr_run()
        formatted_date = str(latest_date) + " " + latest_run + ":00"

        starting_fxx = self.starting_fxx(int(latest_run))

        # first 36 hours from starting_fxx should have 1 hour time increment starting at current time
        #hours_1_hr_step = np.arange(starting_fxx, starting_fxx + 36, time_step)
        # All hours after 36 + new time increment to max range of GFS model (384 hours) should have a 6 or 12 hour time Step
        # A 6 hour time step results in an hours list of len 87 and a 12 hour time step after the 36 hours results in 65 total hours
        new_time_step = 3
        #hours_6_hr_step = np.arange(max(hours_1_hr_step) + new_time_step, 384, new_time_step)
        # Append the two hour arrays together
        #total_hours = np.append(hours_1_hr_step, hours_6_hr_step)
        total_hours = np.arange(starting_fxx, starting_fxx + 2, new_time_step)
        # Create valid hours dict with {{valid_hr:dt_valid_hr}}
        # total_hourts = [9, (9+6), (9+12), (9+18), ...]
        # formatted_date: str(latest_date) + " " + latest_run + ":00" or 2025-Apr-30 12:00
        # new_time_step = 12
        valid_hrs_dt = self.create_valid_hr_dict(total_hours, formatted_date, new_time_step)
        self.valid_hrs_dt = valid_hrs_dt
        skipped_files = 0
        # Step 1: Download and store GRIB files for each forecast hour
        for hour in total_hours:
            #H = HerbieLatest(model="hrrr", product="sfc", fxx=hour)
            # Herbie may not be anble to find the file for the current hour, so handle the case that it caan and cannot find it
            try:
                #H = Herbie(formatted_date, model="gfs", product="pgrb2.0p25",fxx=int(hour))
                #H = HerbieLatest(model="hrrr",product="sfc",fxx=forecast_hour)
                H = HerbieLatest(model="hrrr", product="sfc", fxx=int(hour))
                # If it cannot find more than 3 files in a row, assume the model has not finished rendering and skip the rest of the hours
                if H.grib is None:
                    skipped_files += 1
                    if skipped_files < 3:
                        print(f"Skipping F{hour}: No GRIB file found")
                        continue
                    else:
                        break
                ds = H.xarray("TMP:2 m")

                #ds = H.xarray(":TMP:2 m above")
                ds_dew = H.xarray("DPT:2 m")
                # Cloud Cover
                ds_cc = H.xarray("TCDC:entire atmosphere")
                #if isinstance(ds_cc, list):
                #    ds_cc = ds_cc[0]
                # Relative Humidity
                #ds_rh = H.xarray("RH:2 m above ground")
                # East to West Wind
                ds_u_wind = H.xarray("UGRD:10 m above ground")
                # North or South Wind
                ds_v_wind = H.xarray("VGRD:10 m above ground")
                wind = np.sqrt((ds_u_wind)**2 + (ds_v_wind)**2)
                # Chance of precipitation
                #ds_pop = H.xarray(":POZP:surface")
                # Accumulated Precipitation
                #ds_apcp = H.xarray(":APCP:surface")
                # Precipitation Rate
                ds_prate = H.xarray(":PRATE:surface")
                # Can also show precipitation type if the temperature is below 32ºF
                # This shows 1: Snow is occurring 0: Its not Snowing
                ds_snow = H.xarray(":CSNOW:surface")
                #ds_vis = H.xarray("VIS:surface")
                ds_rh = H.xarray("RH:2 m above ground")

                ds_cape = H.xarray("CAPE:surface")
                ds_refc = H.xarray("REFC:entire atmosphere")

                # Use CAPE, precipitation rate, and composite reflectivity to predict Thunderstorms in data
                model_arr_cape.append(ds_cape)
                model_arr_refc.append(ds_refc)

                model_arr.append(ds)
                model_arr_dew.append(ds_dew)
                model_arr_wind_u.append(ds_u_wind)
                model_arr_wind_v.append(ds_v_wind)
                model_arr_cc.append(ds_cc)
                model_arr_rh.append(ds_rh)
                model_arr_snow.append(ds_snow)
                #model_arr_wx_phenom.append(ds_wx)
                #model_array_chance_preip.append(ds_pop)
                #model_arr_total_precip.append(ds_apcp)
                model_arr_rain_rate.append(ds_prate)
                #model_arr_total_precip_type.append(ds_snow)
                valid_hours.append(hour)
            except Exception as e:
                print(f"Skipping F{hour}: {e}")
                continue


        lats_1d = ds['latitude'].values      # shape (721,)
        lons_1d = ds['longitude'].values     # shape (1440,)

        # Create 2D lat/lon grid just like HRRR format
        #lons, lats = np.meshgrid(lons_1d, lats_1d)  # shape (721, 1440)
        tree = cKDTree(np.column_stack((lons_1d.ravel(), lats_1d.ravel())))


        city_indices = {}
        for i, (name, data) in enumerate(city_data.items()):
            # Make sure to skip the first entry, which is just the valid hrs: datetime dictionary
            if not (isinstance(data, list) and isinstance(data[0], (int, float)) and isinstance(data[1], (int, float))):
                continue
            lat = data[0]
            lon = self.normalize_lon(data[1])
            _, idx = tree.query([self.normalize_lon(lon), lat])
            y_idx, x_idx = np.unravel_index(idx, lats_1d.shape)
            city_indices[name] = (y_idx, x_idx)

            #print(f"[Indexing] {i + 1}/{len(city_data)} ({((i + 1) / len(city_data)) * 100:.2f}%)")

        # Step 4: Precompute variable name for dewpoint and temperature
        varname = list(model_arr[0].data_vars.keys())[0]
        var_dew = list(model_arr_dew[0].data_vars.keys())[0]
        # See if rh data has been extracted from the model
        if model_arr_rh:
            # get the variable name for relative humidity
            var_rh = list(model_arr_rh[0].data_vars.keys())[0]
        else:
            print("Warning ⚠️: No relative humidity data")
            var_rh = None
        # see if visibility data has been extracted from the model
        """
        if model_arr_vis:
            # Get the variable name for bvisibility
            var_vis = list(model_arr_vis[0].data_vars.keys())[0]
        else:
            print("Warning: No visibility data found.")
            var_vis = None
        """

        # see if the u-component of the wind has been extracted from the model
        if model_arr_wind_u:
            # get the variable name for the u component of the wind
            var_wind_u = list(model_arr_wind_u[0].data_vars.keys())[0]
        else:
            print("Warning: No u-wind component data found.")
            var_wind_u = None

        # see if the v component of the wind has been extracted from the model
        if model_arr_wind_v:
            # get the variable name for the v component of the wind
            var_wind_v = list(model_arr_wind_v[0].data_vars.keys())[0]
        else:
            print("Warning: No v-wind component data found.")
            var_wind_v = None

        # See if the cloud cover data has been extracted from the model
        if model_arr_cc:
            # get the variable name for cloud cover
            var_cc = list(model_arr_cc[0].data_vars.keys())[0]
        else:
            print("Warning: No cloud cover data found.")
            var_cc = None

        if model_arr_cape:
            var_cape = list(model_arr_cape[0].data_vars.keys())[0]
        else:
            print("Warning: No u-wind component data found.")
            var_cape = None

        if model_arr_refc:
            var_refc= list(model_arr_refc[0].data_vars.keys())[0]
        else:
            print("Warning: No u-wind component data found.")
            var_refc = None


        #var_wx = list(model_arr_wx_phenom[0].data_vars.keys())[0]
        #var_pop = list(model_array_chance_preip[0].data_vars.keys())[0]
        #var_apcp = list(model_arr_total_precip[0].data_vars.keys())[0]
        if model_arr_rain_rate:
            var_prate = list(model_arr_rain_rate[0].data_vars.keys())[0]
        else:
            print("Warning: No precipitation rate component data found.")
            var_prate = None
        #var_snow = list(model_arr_total_precip_type[0].data_vars.keys())[0]
        var_snow = list(model_arr_snow[0].data_vars.keys())[0]
        #if isinstance(model_arr_cc[0], xarray.DataArray):
        # Just use it directly
        #    cc_data = model_arr_cc[0].data
        #else:
        #    var_cc = list(model_arr_cc[0].data_vars.keys())[0]
        #    cc_data = model_arr_cc[0][var_cc].data

        # Step 5: For each hour, extract temperatures using NumPy indexing
        total_steps = len(valid_hours) * len(city_data)
        step = 0
        #for hour, ds in enumerate(range(0, 12, 6)):
        # Add this BEFORE the for-loop over ds in zip(...)
        city_keys = list(city_indices.keys())
        y_indices = np.array([city_indices[c][0] for c in city_keys])
        x_indices = np.array([city_indices[c][1] for c in city_keys])

        for ds, ds_dew, ds_cc, ds_rh, ds_prate, ds_snow, ds_cape, ds_refc, hour in zip(
            model_arr, model_arr_dew, model_arr_cc, model_arr_rh,
            model_arr_rain_rate, model_arr_snow, model_arr_cape,
            model_arr_refc, valid_hours):

            # Extract raw NumPy arrays
            temp_data = ds[varname].data
            dew_data = ds_dew[var_dew].data
            cc_data = ds_cc[var_cc].data
            rh_data = ds_rh[var_rh].data
            prate_data = ds_prate[var_prate].data
            snow_data = ds_snow[var_snow].data
            cape_data = ds_cape[var_cape].data
            refc_data = ds_refc[var_refc].data

            # Vectorized slicing
            temp_f_all = ((temp_data[y_indices, x_indices] - 273.15) * 9/5) + 32
            dew_f_all = ((dew_data[y_indices, x_indices] - 273.15) * 9/5) + 32
            cloud_cover_all = cc_data[y_indices, x_indices].astype(int)
            snow_all = snow_data[y_indices, x_indices].astype(int)
            prate_all = prate_data[y_indices, x_indices].astype(int)
            rh_all = rh_data[y_indices, x_indices].astype(int)
            cape_all = cape_data[y_indices, x_indices].astype(int)
            refc_all = refc_data[y_indices, x_indices].astype(int)

            # Loop through each city — this part is still required
            for i, city in enumerate(city_keys):
                temp_f = round(temp_f_all[i], 1)
                dew_f = round(dew_f_all[i], 1)
                cloud_cover = cloud_cover_all[i]
                c_snow = snow_all[i]
                precipitation_rate = prate_all[i]
                rh = rh_all[i]
                cape = cape_all[i]
                refc = refc_all[i]

                city_data[city][5].append(temp_f)
                city_data[city][6].append(dew_f)
                wx_condition = self.compute_wx_condition(
                    cloud_cover, precipitation_rate, c_snow, temp_f, cape, refc, dew_f, rh
                )
                city_data[city][7].append(wx_condition)

        """
        for ds, ds_dew, ds_cc, ds_rh, ds_prate, ds_snow, ds_cape, ds_refc, hour in zip(model_arr, model_arr_dew, model_arr_cc, model_arr_rh, model_arr_rain_rate, model_arr_snow, model_arr_cape, model_arr_refc, valid_hours):
            temp_data = ds[varname].data
            dew_data = ds_dew[var_dew].data
            #wind_u_data = ds_u_wind[var_wind_u].data
            #wind_v_data = ds_v_wind[var_wind_v].data
            cc_data = ds_cc[var_cc].data

            rh_data = ds_rh[var_rh].data
            prate_data = ds_prate[var_prate].data
            snow_data = ds_snow[var_snow].data
            #vis_data = ds_vis[var_vis]
            cape_data = ds_cape[var_cape]
            refc_data = ds_refc[var_refc]
            #vis_data = ds_vis[var_vis]
            #ptype_data = ds_snow[var_snow].data
            for icao, (y_idx, x_idx) in city_indices.items():
                temp_k = temp_data[y_idx, x_idx]
                temp_f = round((temp_k - 273.15) * 9 / 5 + 32, 2)
                city_data[icao][5].append(temp_f)


                # Handle dewpoints
                dew_k = dew_data[y_idx, x_idx]
                dew_f = round((dew_k - 273.15) * 9/5 + 32, 2)
                city_data[icao][6].append(dew_f)

                # Handle Wind Speed
                #wind_u = wind_u_data[y_idx, x_idx]
                #wind_v = wind_v_data[y_idx, x_idx]
                #wind_magnitude = int(np.hypot(wind_u, wind_v))
                #city_data[icao][6].append(wind_magnitude)
                #wind_angle = int(self.compute_angle(wind_u, wind_v))
                #wind_heading_angle_dict = self.create_direction_angle_name_dict(wind_angle)
                #city_data[icao][7].append(wind_angle)

                # Handle Cloud Cover Data
                cloud_cover = int(cc_data[y_idx, x_idx])
                #city_data[icao][7].append(cloud_cover)

                # Handle Chance Snow
                c_snow = int(snow_data[y_idx, x_idx])
                #city_data[icao][9].append(c_snow)

                # Handle Visibility
                #visibility = int(vis_data[y_idx, x_idx])
                #city_data[icao][8].append(visibility)

                # Handle Precipitation rate
                precipitation_rate = int(prate_data[y_idx, x_idx])
                #city_data[icao][11].append(precipitation_rate)

                # Handle Relative Humidity
                rh = int(rh_data[y_idx, x_idx])
                #city_data[icao][10].append(humidity)

                # Handle CAPE
                cape = int(cape_data[y_idx, x_idx])

                # handle composite reflectivity
                refc = int(refc_data[y_idx, x_idx])

                # Calculate the weather phenomena
                wx_condition = self.compute_wx_condition(cloud_cover, precipitation_rate, c_snow, temp_f, cape, refc, dew_f, rh)
                city_data[icao][7].append(wx_condition)


                step += 1
                #if step % 100 == 0 or step == total_steps:
                #    print(f"[Extracting] {step}/{total_steps} ({(step / total_steps) * 100:.2f}%)")
        """
        # formatted_date = str(latest_date) + " " + latest_run + ":00"
        # starting_fxx = self.starting_fxx(int(latest_run))
        # valid_hours
        # pass in the starting hour, the
        #self.create_hour_datetime_dict(formatted_date, valid_hours)
        #self.valid_hours = valid_hours

        # {valid_hour[hour]: latest_date + (latest_run + valid_hours[hour]) + ":00"
        # if latest_run + valid_hours[hour] > 23, latest_day.day+=1
        # loop through list of hourhours in valid_hours array

        # add valid_hours list to the end of self.city_data dict

    # Takes in the cloud cover percentage, the precipitation rate, if it is snowing, and the visibility
    # Returns the number for the correct icon
    def compute_wx_condition(self, cloud_cover, prate, snow, temp, cape, refc, dew, rh):
        # Check for fog
        if (rh > 96 and prate == 0):
            # Foggy conditions
            return 45
            if temp <= 32:
                # Freezing fog
                return 48
        # If the precipitation rate is 0, then no wx_phenomena, only cloud cover
        if prate == 0:
            #cloudCoverTypes = {'CLR': 0.0, 'FEW': 0.25, 'SCT': 0.50, 'BKN': 0.75, 'OVC': 1.0, 'SKC': 0.00, 'CAVOK': 0.0}
            if cloud_cover >= 0 and cloud_cover < 0.25:
                # Clear
                return 0
            elif cloud_cover >= 0.25 and cloud_cover < 0.5:
                # Partly Cloudy
                return 1
            elif cloud_cover >= 0.5 and cloud_cover < 0.75:
                # Mostly Cloudy
                return 2
            elif cloud_cover >= 0.75 and cloud_cover <= 1:
                # Overcast
                return 3
        # Check to see if it is precipitating
        if prate > 0:
            # If the temp is at or below freezing and it is precipitating, then you have freezing rain
            if temp < 32:
                if prate < 0.5:
                    # Light Freezing Rain
                    return 66
                else:
                    # Heavy freezing rain
                    return 67
            # If the temperature is above freezing, then it is raining
            else:
                if prate < 0.5:
                    # Light Rain
                    return 61
                elif prate < 2.0:
                    # Moderate Rain
                    return 63
                else:
                    # Heavy Rain
                    return 65
        # If ex icon can not be identified, return Unknown icon
        return "Unknown"

    # Want to pass in the valid_hours array, the datee that the model is initialized, and the timestep
    def create_valid_hr_dict(self, valid_hrs, starting_dt_str, time_step):
        # total_hours = [9, 9+6, (9+12, (9+18), ...]
        # formatted_date: str(latest_date) + " " + latest_run + ":00" or 2025-Apr-30 12:00
        # define new dictionary valid_hr_dt
        valid_hrs_dt = {}
        # Check to make sure valid_hrs is not null
        try:
            # Convert starting_dt_str ("2025-04-21 00:00") into datetime object
            starting_dt = datetime.strptime(starting_dt_str, "%Y-%m-%d %H:%M")
            # assign old_dt to starting_dt
            #old_dt = starting_dt
            # valid_hrs = [9, 9+6, (9+12, (9+18), ...]
            # the first key of valid_hrs is the time difference between when the model initialized in utc and the current time (or the number of hours since the model has initialized)
            # Get the first key from valid_hrs
            # Add the number of hours since the model initialized to the time ththe model initialized
            # this represents a rough estimate of the current time you would have to increase the model to get a current representation in the model, as the model hours start when it initializes,initialized, not the time right now
            initial_offset = int(list(valid_hrs)[0])
            current_dt = starting_dt + timedelta(hours=initial_offset)
            hourIndex = 0
            for hr in valid_hrs:
                # Compute new date with timestep
                # new dt = old_datetime + time_step
                # Note that the new DT may be a completely different day,month,or even year
                # Takes in the original datetime and returns the new datetime, which is the original datetime + the timestep
                #new_dt = self.oldDT_to_newDT(starting_dt_plus_diff, time_step)
                new_dt = current_dt + timedelta(hours=int(hourIndex))
                #current_dt += timedelta(hours=time_step)
                # Append {hr: new_dt} to valid_hr_dt
                valid_hrs_dt[int(hr)] = str(new_dt)
                # Update old_dt to reflect the new_dt so that starting_datetime doesnt stay the same for every valid hour
                starting_dt = new_dt
                # increment hourIndex by 1
                hourIndex += 1
            # return the array of all the individual dictionaries of {int(hour): datetime_of_hour}
            return valid_hrs_dt
        except:
            # Case where valid hours has no elements in it
            return {}

    def oldDT_to_newDT(self, old_dt, time_step):
        future_datetime = old_dt + timedelta(hours=time_step)
        return future_datetime


    #def create_hour_datetime_dict
    def compute_angle(self, u, v):
        angle_rad = np.arctan2(v, u)  # Returns radians
        angle_deg = np.degrees(angle_rad)  # Converts to degrees
        if angle_deg < 0:
            angle_deg += 360
        return angle_deg
    def create_direction_angle_name_dict(self, angle):
        # Use an 8 point compass to return wind direction in N, NE, E, SE, S, SW, W, NW
        # return {compass_heading, angle}
        wind_compass = {}
        if (angle >= 337.5 and angle < 22.5) or angle == 0:
            wind_compass = {'North': angle}
        elif angle >= 22.5 and angle < 67.5:
            wind_compass = {'North East': angle}
        elif angle >= 67.5 and angle < 112.5:
            wind_compass = {'East': angle}
        elif angle >= 112.5 and angle < 157.5:
            wind_compass = {'South East': angle}
        elif angle >= 157.5 and angle < 202.5:
            wind_compass = {'South': angle}
        elif angle >= 202.5 and angle < 247.5:
            wind_compass = {'South West': angle}
        elif angle >= 247.5 and angle < 292.5:
            wind_compass = {'West': angle}
        elif angle >= 292.5 and angle < 337.5:
            wind_compass = {'North West': angle}
        return wind_compass
    """
    def json_dump(self):
        # /Users/scottreinhardt/flasktropica/static/gfs_dump/gfs_dump.json
        # /home/tropicainnovations/mysite/static/gfs_dump/gfs_dump.json
        with open('/home/tropicainnovations/mysite/static/gfs_dump/gfs_dump.json', "w") as f:
            json.dump(self.cityLocations, f)
    """

    import numpy as np
    import json

    def convert_to_native(self, obj):
        if isinstance(obj, dict):
            return {k: self.convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_native(i) for i in obj]
        elif isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        else:
            return obj
    """
    def json_dump(self):
        # Clean version of cityLocations (only real cities)
        safe_cityLocations = self.cityLocations

        # Clean version of valid_hrs_dt
        safe_valid_hrs_dt = {}
        for k, v in self.valid_hrs_dt.items():
            safe_valid_hrs_dt[int(k)] = v  # v already string

        # --- Build the output dict ---
        output = {
            "valid_hrs_dt": safe_valid_hrs_dt,   # <-- put valid_hrs_dt FIRST
            "cities": safe_cityLocations         # <-- put cities SECOND
        }

        with open('/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json', "w") as f:
            json.dump(output, f)
    """
    def json_dump(self):
        # Clean version of cityLocations (only real cities)
        safe_cityLocations = self.convert_to_native(self.cityLocations)

        # Clean version of valid_hrs_dt
        safe_valid_hrs_dt = {}
        for k, v in self.valid_hrs_dt.items():
            safe_valid_hrs_dt[int(k)] = v  # v already string

        # --- Build the output dict ---
        output = {
            "valid_hrs_dt": safe_valid_hrs_dt,   # <-- put valid_hrs_dt FIRST
            "cities": safe_cityLocations         # <-- put cities SECOND
        }

        with open('/home/tropicainnovations/mysite/static/hrrr_dump/hrrr_dump.json', "w") as f:
            json.dump(output, f)

    def normalize_lon(self, lon):
        """Convert longitude to 0–360° east format"""
        return lon if lon >= 0 else 360 + lon


    def get_temperature_at_point(self, ds, lat, lon):

        varname = list(ds.data_vars.keys())[0]
        data_k = ds[varname].values

        lats_1d = ds['latitude'].values      # shape (721,)
        lons_1d = ds['longitude'].values     # shape (1440,)

        # Create 2D lat/lon grid just like HRRR format
        lons, lats = np.meshgrid(lons_1d, lats_1d)  # shape (721, 1440)

        # Now everything behaves like HRRR
        tree = cKDTree(np.column_stack((lons.ravel(), lats.ravel())))
        _, idx = tree.query([lon, lat])
        y_idx, x_idx = np.unravel_index(idx, lats.shape)  # Now lats is 2D
        temp_k = data_k[y_idx, x_idx]
        temp_f = (temp_k - 273.15) * 9/5 + 32

        return temp_f

    def get_forecast_test(self):

        # Coordinates for KBOS (Boston Logan)
        kbos_lat = 42.3656
        lon = -71.0096
        kbos_lon = self.normalize_lon(lon)
        H = HerbieLatest(model="hrrr", product="sfc", fxx=0)
        H.download()
        inv = H.inventory()

        for i, row in inv.iterrows():
            var = row['variable']
            level = row['level']
            forecast = row['forecast_time']
            print(f"{i+1:>3}: {var:<6} | Level: {level:<20} | Forecast Hour: {forecast}")


        """
        # Load latest HRRR surface model
        #H = HerbieLatest(model="hrrr", product="sfc", fxx=0)

        # April 21, 2025 at 00Z GFS run
        H = Herbie("2025-04-21", model="gfs", product="pgrb2.0p25", fxx=0)
        H.download()
        inv = H.inventory()
        for item in inv:
            if "10 m above ground" in item:
                print(item)

        for hour in range(0,384,6):
            H = Herbie("2025-04-21", model="gfs", product="pgrb2.0p25", fxx=0)
            # Get 2m temperature field
            #ds = H.xarray(":TMP:2 m above")
            ds = H.xarray(":TMP:2 m above")

        #ds = H.xarray(":10 m above ground")
        #ds = H.xarray(filter_by="level", value=["10 m above ground", "2 m above ground", "surface"])

        #ds = H.xarray(filter_by="shortName", value="WIND")
        #ds = H.xarray(filter_by="shortName", value=["UGRD", "VGRD", "WIND"])
        #ds = H.xarray(":TMP:2 m above")
        #ds = H.xarray("WIND:10 m above ground")
        #ds = H.xarray("GUST:10 m above ground")
        ds = H.xarray("VGRD:10 m above ground")
        #ds = H.xarray("APCP:surface")
        #ds = H.xarray("RH:2 m above ground")
        #wind_speed = ds['WIND']

        varname = list(ds.data_vars.keys())[0]
        print("Variable name:", varname)
        print(ds[varname])
        varname = list(ds.data_vars.keys())[0]
        temp_k = ds[varname].values
        temp_f = (temp_k - 273.15) * 9/5 +32
        print(self.get_temperature_at_point(ds, kbos_lat, kbos_lon))

        print(f"GFS 00Z run (2025-04-21): 2m temperature sample (°F):\n{temp_f}")
        """


if __name__ == '__main__':
    HRRR_Point_Forecast = HRRR_Point_Forecast()
    # /home/tropicainnovations/mysite/static/geonames-all-cities-with-a-population-1000.json
    # /Users/scottreinhardt/flasktropica/static/geonames-all-cities-with-a-population-1000 (1).json
    HRRR_Point_Forecast.read_json('/home/tropicainnovations/mysite/static/geonames-all-cities-with-a-population-1000.json')
    HRRR_Point_Forecast.get_forecast_fast()
    HRRR_Point_Forecast.json_dump()
    #HRRR_Point_Forecast.get_forecast_test()
