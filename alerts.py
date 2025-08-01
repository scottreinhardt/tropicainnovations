import requests
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

class Alerts:
    def run():
        # Define the URL to fetch alert data for New Hampshire
        url = 'https://api.weather.gov/alerts/active?area=NH'

        # Fetch alert data from the API
        response = requests.get(url)
        data = response.json()

        # Find the first severe thunderstorm warning polygon
        severe_thunderstorm_polygon = None
        for alert in data['features']:
            if alert['properties']['event'] == 'Severe Thunderstorm Warning':
                polygon_coords = alert['geometry']['coordinates'][0]
                polygon = Polygon(polygon_coords)
                if polygon.is_valid:
                    severe_thunderstorm_polygon = polygon
                    break

        if severe_thunderstorm_polygon:
            # Create a Basemap object for New Hampshire
            m = Basemap(
                projection='merc',
                llcrnrlat=42.697,
                urcrnrlat=45.305,
                llcrnrlon=-72.557,
                urcrnrlon=-70.603,
                resolution='i'
            )

            # Get the exterior coordinates of the polygon
            x, y = m(*severe_thunderstorm_polygon.exterior.xy)

            # Create a figure and plot the polygon
            plt.figure(figsize=(10, 8))
            m.drawcoastlines()
            m.drawcountries()
            m.drawstates()
            m.drawparallels(np.arange(40., 46., 1.), labels=[1, 0, 0, 0])
            m.drawmeridians(np.arange(-74., -68., 1.), labels=[0, 0, 0, 1])

            # Plot the polygon
            plt.fill(x, y, 'r', alpha=0.5)

            # Set plot title and show the map
            plt.title('Severe Thunderstorm Warning in New Hampshire')
            plt.show()
        else:
            print('No severe thunderstorm warnings found in New Hampshire.')

    if __name__ == '__main__':
        alert_map = Alerts()
        alert_map.run()
