
""""import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from herbie import Herbie
from herbie import HerbieLatest
import numpy as np
from datetime import datetime
from flask import Flask
from metpy.plots import colortables

class HRRR_Temperature_Map:

    def __init__(self):
        self.cached_ds = {}  # Cache datasets to reduce fetch frequency
        self.regions = {
            "us_extent": [-125.0, -66.0, 25.0, 50.0],
            "new_england_extent": [-73.5, -66.5, 40.0, 47.5]
        }

    def create_map(self):
        # Initialize Flask app
        app = Flask(__name__)
        current_date = datetime.utcnow()

        forecast_hours = range(1, 17)
        product_nums = [0, 8, 70, 73, 74]  # Focus on core products

        for forecast_hour in forecast_hours:
            ds = self.fetch_data(forecast_hour, product_nums)
            if ds:
                self.generate_plots(ds, forecast_hour, app)

    def fetch_data(self, forecast_hour, product_nums):
        try:
            H = HerbieLatest(model="hrrr", product="sfc", fxx=forecast_hour)
            inventory = H.inventory()
            data_sets = {}

            for index, row in inventory.iterrows():
                if index in product_nums:
                    product = f"{row['search_this']}"
                    ds = H.xarray(product)
                    data_sets[product] = ds
                    print(f"Fetched: {product} for hour {forecast_hour}")
            return data_sets

        except Exception as e:
            print(f"Error fetching data for hour {forecast_hour}: {e}")
            return None

    def generate_plots(self, data_sets, forecast_hour, app):
        for product, ds in data_sets.items():
            variable_names = list(ds.data_vars.keys())[0]
            variable_data = ds[variable_names]

            for region_name, region_extent in self.regions.items():
                # Separate plotting into a function to minimize repetition
                self.plot_region(ds, variable_data, product, forecast_hour, region_name, region_extent, app)

    def plot_region(self, ds, variable_data, product, forecast_hour, region_name, region_extent, app):
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent(region_extent, crs=ccrs.PlateCarree())
        ax.coastlines(resolution='50m')
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.STATES, edgecolor='gray')

        p = ax.pcolormesh(
            ds.longitude,
            ds.latitude,
            variable_data,
            cmap=self.get_colormap(ds),
            transform=ccrs.PlateCarree(),
            shading="auto"
        )

        cbar = plt.colorbar(p, ax=ax, orientation="horizontal", pad=0.05, label=f"{product}")
        cbar.ax.tick_params(labelsize=12)

        ax.set_title(f"{product} - {forecast_hour}-hr Forecast", fontsize=14)

        output_dir = os.path.join(app.root_path, "static", "images", "hrrr")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{product.replace(':', '_')}_forecast_{forecast_hour}_{region_name}.png")
        plt.savefig(file_path)
        plt.close(fig)
        print(f"Saved: {file_path}")

    def convert_units(self, SI_unit, data_to_convert):
        if SI_unit == "K":
            return (data_to_convert - 273.15) * (9.0/5.0) + 32.0
        elif SI_unit == "m s**-1":
            return data_to_convert * 2.23694
        return data_to_convert

    def get_colormap(self, ds):
        long_name = ds[list(ds.data_vars.keys())[0]].attrs.get("long_name", "default")
        colormaps = {
            "2 metre temperature": "coolwarm",
            "2 metre dewpoint temperature": "YlGn",
            "2 metre relative humidity": "PuBu",
            "Maximum/Composite radar reflectivity": "rainbow",
            "Wind speed (gust)": "plasma"
        }
        return colormaps.get(long_name, "rainbow")

if __name__ == '__main__':
    map_creator = HRRR_Temperature_Map()
    map_creator.create_map()"""

import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from herbie import HerbieLatest
from flask import Flask
from metpy.plots import colortables
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from datetime import datetime
import io

class HRRR_Temperature_Map:

    def __init__(self):
        # Regions for maps to be displayed
        self.regions = {
            "us_extent": [-125.0, -66.0, 25.0, 50.0],
            "new_england_extent": [-73.5, -66.5, 40.0, 47.5]
        }
        self.executor = ThreadPoolExecutor(max_workers=4)  # Allow 4 images to save simultaneously


    def create_map(self):
        app = Flask(__name__)
        forecast_hours = range(1, 8)
        # If you were to list every item in H.inventory() you want to find the producst that you want from the HRRR model. The numbers really represent their respective variables. Dynamically this looks like row['search this']
        product_nums = [0, 8, 70, 73, 74]

        # For every forecast hour in forecast_hours
        for forecast_hour in forecast_hours:
            # Fetch the data for that forecast_hour and desired product
            ds = self.fetch_data(forecast_hour, product_nums)
            if ds:
                # If that data exists, use it to generate a map
                self.generate_plots(ds, forecast_hour, app)

        self.executor.shutdown(wait=True)  # Wait for all threads to finish

    # Fetch forecast model data using Herbie
    def fetch_data(self, forecast_hour, product_nums):
        try:
            # Use HerbieLatest to get the latest model from the HRRR model
            H = HerbieLatest(model="hrrr", product="sfc", fxx=forecast_hour)
            # This gets the inventory from each forecast model
            # Inventory items such as ":REFC:entire atmosphere:1 hour fcst" or " :VIS:surface:1 hour fcst"
            inventory = H.inventory()
            #This makes searching through inventory lists much easier
            # fOR EVERY INDEX, ROW in H.inventory(), if the current index is in the list of desired products, then create an entry with the text of the desired index as they key and store that as an array using xarray for the value.
            # data_sets will look like "{':REFC:entire atmosphere:4 hour fcst': <xarray.Dataset>}" where <xarray.Dataset> is the corrosponding output for the slescted item from H.inventory()
            # You can get the variable name from this
            data_sets = {row['search_this']: H.xarray(row['search_this']) for index, row in inventory.iterrows() if index in product_nums}
            return data_sets
        except Exception as e:
            print(f"Error fetching data for hour {forecast_hour}: {e}")
            return None

    # variables:
    # data_sets: the data for each desired item in key value pairs in a list. Ex "{':REFC:entire atmosphere:4 hour fcst': <xarray.Dataset>}"
    #forecast_hour is the forecast hour (0,17) from when the model was produced. Ex 1 means 1 hour from the start time of the forecast model
    def generate_plots(self, data_sets, forecast_hour, app):
        for product, ds in data_sets.items():
            variable_name = list(ds.data_vars.keys())[0]
            variable_data = ds[variable_name]

            for region_name, region_extent in self.regions.items():
                fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
                ax.set_extent(region_extent, crs=ccrs.PlateCarree())
                ax.coastlines(resolution='50m')
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                ax.add_feature(cfeature.STATES, edgecolor='black')

                # Plot the data using pcolormesh
                cmap = self.get_colormap(ds)
                p = ax.pcolormesh(
                    ds.longitude, ds.latitude, variable_data, cmap=cmap,
                    transform=ccrs.PlateCarree(), shading="auto"
                )
                plt.colorbar(p, ax=ax, orientation="horizontal", pad=0.05, label=f"{product}")

                # Prepare to save asynchronously
                sanitized_product = product.replace(":", "_").replace(" ", "_")
                output_dir = os.path.join(app.root_path, "static", "images", "hrrr")
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, f"{sanitized_product}_forecast_{forecast_hour}_{region_name}.png")

                # Submit to thread pool for asynchronous saving
                self.executor.submit(self.save_figure, fig, file_path)

    def save_figure(self, fig, file_path):
        """Asynchronous saving of the figure."""
        fig.savefig(file_path, dpi=72)  # Adjust dpi to 72 for faster saving
        fig.clf()  # Clear the figure to free up memory
        print(f"Image saved: {file_path}")

    def get_colormap(self, ds):
        long_name = ds[list(ds.data_vars.keys())[0]].attrs.get("long_name", "default")
        colormaps = {
            "2 metre temperature": "coolwarm",
            "2 metre dewpoint temperature": "YlGn",
            "2 metre relative humidity": "PuBu",
            "Maximum/Composite radar reflectivity": "rainbow",
            "Wind speed (gust)": "plasma"
        }
        return colormaps.get(long_name, "rainbow")

if __name__ == '__main__':
    map_creator = HRRR_Temperature_Map()
    map_creator.create_map()