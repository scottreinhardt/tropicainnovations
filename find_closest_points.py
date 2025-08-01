from sklearn.neighbors import BallTree
import numpy as np
import json


def find_closest_point(lat, lon):
    # Retrieve current latitude and longitude from the javascript
    current_lat = lat
    current_lon = lon

    file_name = '/home/tropicainnovations/mysite/static/gfs_dump/gfs_dump.json'

    # load the json file containing all 147,000 cities (gfs_dump.json)
    with open(file_name) as f:
        data = json.load(f)

    # Convert to list of (lat, lon) and names
    locations = []
    names = []
    for city, info in data['cities'].items():
        # Append the [lat, lon] (info[0] and info[1]) as an item in the locations list
        locations.append([info[0], info[1]])
        # Append each city name to a list of city names (corrosponding to the index of the lat and lon in the locations array.)
        names.append(city)

    # Convert to radians for BallTree (uses haversine)
    locations_rad = np.radians(locations)
    your_point = np.radians([[current_lat, current_lon]])

    # Build BallTree
    tree = BallTree(locations_rad, metric='haversine')

    # Query for 5 nearest neighbors
    dists, indices = tree.query(your_point, k=5)

    # Keep track of the cities with the closest name
    closest_city_names = []

    # Convert distance from radians to kilometers
    earth_radius_km = 6371
    for i, idx in enumerate(indices[0]):
        dist_km = dists[0][i] * earth_radius_km
        closest_city_names.append(names[idx])
        #print(f"{names[idx]}: {dist_km:.2f} km")

    # Make a dictionary to hold the list of weather information from each closest city
    closest_cities_info = {}

    # Load the original complete dict with the cities (gfs_dump.json)
    original_data = data['cities']
    # loop through closest_city_data
    for city_name in closest_city_names:
        # Get the value from the city in the original dictionary containing the weather infomation
        city_info = original_data[city_name]
        closest_cities_info[city_name] = city_info
    return closest_cities_info

dict_locations = find_closest_point(0.0, 0.0)
for name, info in dict_locations.items():
    print(info)
