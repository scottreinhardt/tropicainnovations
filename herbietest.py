import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from herbie import Herbie
from herbie.toolbox import EasyMap, pc
import numpy as np
from datetime import datetime, timedelta

# Get the current date
current_date = datetime.utcnow()

# Define the forecast for tomorrow night (~24 hours in the future)
forecast_hour = 24  # Forecast hour for tomorrow night
forecast_date = current_date.strftime('%Y-%m-%d')

# Fetch the HRRR data for tomorrow night
H = Herbie(
    forecast_date,  # Use the current date
    model="hrrr",
    product="sfc",  # Surface data product
    fxx=forecast_hour  # Forecast hour (fxx=24 means 24 hours ahead)
)

# Fetch the temperature data from the model
ds = H.xarray("TMP:2 m above ground")  # Temperature at 2 meters above ground level

# Convert temperature from Kelvin to Celsius
temperature_celsius = ds.t2m - 273.15

# Define the map projection and area (New England region)
new_england_extent = [-73.5, -66.9, 40.0, 46.5]  # lon_min, lon_max, lat_min, lat_max

# Create the plot with Cartopy
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# Add map features (like borders, coastlines, states)
ax.set_extent(new_england_extent, crs=ccrs.PlateCarree())
ax.coastlines(resolution='50m')
ax.add_feature(cfeature.BORDERS, linestyle=':')  # Corrected to use cfeature
ax.add_feature(cfeature.STATES, edgecolor='gray')  # Corrected to use cfeature

# Plot the temperature data using a rainbow colormap
temp_plot = ax.pcolormesh(
    ds.longitude,
    ds.latitude,
    temperature_celsius,
    cmap="rainbow",  # Using the rainbow colormap
    transform=pc,  # Projection conversion tool from Herbie
    shading="auto",
)

# Add a colorbar
cbar = plt.colorbar(temp_plot, ax=ax, orientation="horizontal", pad=0.05, shrink=0.8)
cbar.set_label('Temperature (°C)')

# Add titles
ax.set_title(f"HRRR 2m Temperature - New England\nValid: {ds.valid_time.dt.strftime('%Y-%m-%d %H:%M UTC').item()}", loc="left")
ax.set_title(ds.t2m.GRIB_name, loc="right")

# Save the plot to a file or display it
plt.savefig("new_england_temperature_tomorrow_night.png")
plt.show()


