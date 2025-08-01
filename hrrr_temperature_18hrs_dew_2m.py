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

class HRRR_Temperature_Map:

    def create_map(self):
        # Initialize Flask app
        app = Flask(__name__)

        image_files = []
        # Get the current date
        current_date = datetime.utcnow()

        # Define the forecast hours to loop through
        for forecast_hour in range(1, 17):
            # Fetch the HRRR data for the given forecast hour
            H = HerbieLatest(
                model="hrrr",
                product="sfc",  # Surface data product
                fxx=forecast_hour  # Forecast hour (fxx=24 means 24 hours ahead)
            )

            inventory = H.inventory()
            #product_nums = [0, 8, 70, 73, 74]  # Specify the products to process
            product_nums = [73]
            # Loop through the products you're interested in
            for index, row in inventory.iterrows():
                if index in product_nums:
                    product = f"{row['search_this']}"
                    print(f"Processing: {product} for forecast hour {forecast_hour}")

                    try:
                        # Fetch data for the current product
                        ds = H.xarray(product)

                        # Extract the variable name from the dataset
                        variable_names = list(ds.data_vars.keys())[0]
                        variable_data = ds[variable_names]
                        # Loop through all of the different variable names
                        for var_name in ds.data_vars:
                            # Get the desired variable from the model
                            variable = ds[var_name]

                            # Get the unit of the model variable by taking the attributes of the variable and accessing its full description name
                            units = variable.attrs.get('units', 'No units specified')  # Safely access 'units'
                            # Get the long name of the model variable by taking the attributes of the variable and accessing its full description name
                            long_name = variable.attrs.get('long_name', 'No long name specified')  # Safely access 'long_name'

                            # Print the variable name, long name (title), and units
                            #print(f"Variable: {var_name}, Full Title: {long_name}, Units: {units}")
                            SI_unit = f"{units}"
                            long_name = f"{long_name}"

                            # Convertsd the abbreviation for the unit given by the model to the imperial full name equivelant, or if the unit is standard, returns the full name of the original unit
                            converted_unit_full_name = self.metric_to_imperial_unit_name(SI_unit)

                            # Converts the SI unit to the imperial equivelant or if SI is standard, it will return that standard unit
                            converted_unit = self.convert_units(units, variable_data)

                            # Colortable for the given unit
                            c_table = self.find_colormap(long_name)


                            try:
                                # If the color table is part of metpy's colortable library
                                cmap = colortables.get_colortable(c_table)
                            except:
                                # If the color table is part of matplotlib's color table library
                                cmap = c_table

                            us_extent = [-125.0, -66.0, 25.0, 50.0]  # lon_min, lon_max, lat_min, lat_max
                            northeast_extent = [-100.0, -66.0, 37.0, 50.0]  # lon_min, lon_max, lat_min, lat_max
                            southeast_extent = [-100.0, -66.0, 25.0, 37.0]  # lon_min, lon_max, lat_min, lat_max
                            northwest_extent = [-125.0, -100.0, 37.0, 50.0]  # lon_min, lon_max, lat_min, lat_max
                            southwest_extent = [-125.0, -100.0, 25.0, 37.0]  # lon_min, lon_max, lat_min, lat_max

                            # Define New England's geographic extent (approximate latitudes and longitudes)
                            new_england_extent = [-73.5, -66.5, 40.0, 47.5]  # [min_longitude, max_longitude, min_latitude, max_latitude]
                            regions = {
                                "us_extent": [-125.0, -66.0, 25.0, 50.0],
                                "new_england_extent": [-73.5, -66.5, 40.0, 47.5]
                            }

                            # Convert each region variable to its own string name
                            #new_england_extent_to_dict = dict()
                            #new_england_extent_as_string = f'us_extent_to_dict='.split('=')[0]

                            #us_extent_to_dict = dict()
                            #us_extent_as_string = f'us_extent_to_dict='.split('=')[0]
                            for region_name, region_extent in regions.items():
                                fig, ax = plt.subplots(figsize=(20, 16), subplot_kw={'projection': ccrs.PlateCarree()})

                                ax.set_extent(region_extent, crs=ccrs.PlateCarree())

                                # Add map features
                                ax.coastlines(resolution='10m')
                                ax.add_feature(cfeature.BORDERS, linestyle=':')
                                ax.add_feature(cfeature.STATES, edgecolor='black')

                                # Plot the data using pcolormesh
                                p = ax.pcolormesh(
                                    ds.longitude.values,
                                    ds.latitude.values,
                                    converted_unit,
                                    cmap=cmap,  # Choose an appropriate colormap
                                    transform=ccrs.PlateCarree(),
                                    shading="auto"
                                )

                                # Add a colorbar with larger font for tick marks and label
                                cbar = plt.colorbar(
                                    p,
                                    ax=ax,
                                    orientation="horizontal",
                                    pad=0.05,
                                    label=f"{long_name} ({converted_unit_full_name})"
                                )
                                cbar.ax.xaxis.label.set_size(26)  # Increase colorbar label size
                                cbar.ax.tick_params(labelsize=26)  # Increase colorbar tick label size

                                # Set the title with larger font size
                                ax.set_title(
                                    f"{long_name} - Forecast for {ds.valid_time.dt.strftime('%Y-%m-%d %H:%M UTC').item()}",
                                    fontsize=35
                                )

                                # Ensure the directory exists
                                output_dir = os.path.join(app.root_path, "static", "images", "hrrr")
                                os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

                                # Sanitize the product name for safe file naming
                                no_spaces_product = product.replace(" ", "_").replace(":", "_")

                                # Construct the file path to save the image in the static directory
                                file_path = os.path.join(output_dir, f"{no_spaces_product}_forecast_{forecast_hour}_{region_name}.png")

                                # Save the image
                                plt.savefig(file_path)
                                print(f"Image saved: {file_path}")

                                # Clear the figure to prevent duplicates in the next loop iteration
                                #plt.clf()  # Clear the current figure
                                # Alternatively, close the figure completely after saving
                                plt.clf()

                    # If there is an exception processing the product from the forecast mo0del, then throw an error
                    except Exception as e:
                        print(f"Error processing {product} for forecast hour {forecast_hour}: {e}")

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

    # convert a variable name into its own string representation
    # For an input of example new_england_extent would return 'new_england_extent_as_string'
    def var_name_to_string(self, var_name):
        return 0

    # This method takes an SI unit such as 'K' for Kelvin and would return the full metric equivelant name
    # For example an input of 'K' (for Kelvin) would return the string 'Farenheit'
    # Used to represent the correct units when making the color table for labeling purposes
    # If a metric version is videly used such as decibels then an input of the abbreviated version (dB) would return the full name "decibeks"
    def metric_to_imperial_unit_name(self, SI_unit_name):
        #"K"(Kelvin)->"Farenheit"
        if(SI_unit_name == "K"):
            return "Farenheit"
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
    HRRR_Temperature_Map.create_map()
