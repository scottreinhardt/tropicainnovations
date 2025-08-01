import requests
from bs4 import BeautifulSoup
import re
import urllib
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.interpolate
import xml.etree.ElementTree as ET
import xmltodict
import time

header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36","X-Requested-With": "XMLHttpRequest"}

# Ask for zip code, choose city, or randomize (pick a random town anywhere in the us
#zipcode = input("Please Enbter Your Zip Code")
# define whole us dictionary containing all airports and coordinates within 100 miles
# calculate the distance between lat1 lon1 and lat2 lon2

# Dictionary of every airport within a certain distance of a user or location
#Problem: right now, the dictionary is not in the correct format
# It writes it as {'KBDL': [41.93806, -72.6825], 'KGON': [41.3275, -72.04944]}
# When Folium takes the data in as airport_data1 = [{'name': 'KBVY', 'lat': 42.58361, 'lon': -70.91639}]
aptnamesUSA = {}
compatibleaptnamesUSA = []
# lat1 and lat2 are the users current coordinates
# lat2 and lon2 are the coordinates of the airport
# If the airport is within 100 miles of the users coordinates the method will return true, otherwise false.
# returns a boolean
def distanceFinder(lat1, lon1, lat2, lon2, distance):
    pi = np.pi
    R = 6371e3 # metres
    φ1 = lat1 * pi / 180 # φ, λ in radians
    φ2 = float(lat2) * pi / 180
    Δφ = (lat2 - lat1) * pi / 180
    Δλ = (lon2 - lon1) * pi / 180
    a = np.sin(Δφ / 2) * np.sin(Δφ / 2) + np.cos(φ1) * np.cos(φ2) * np.sin(Δλ / 2) * np.sin(Δλ / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = R * c # in metres
    # If the distance is 100 or less miles return the distance otherwiae return false
    if d <= distance:
        return d
    else:
        return False

def findCoords(lat1, lon1, d):
    # find coordinates for basemap
    tc = 90
    pi = np.pi
    lat = np.arcsin(np.sin(lat1) * np.cos(d) + np.cos(lat1) * np.sin(d) * np.cos(tc))
    dlon = np.arctan2(np.sin(tc) * np.sin(d) * np.cos(lat1), np.cos(d) - np.sin(lat1) * np.sin(lat))
    lon = np.mod(lon1 - dlon + pi, 2 * pi) - pi

# Creates a dynamic (or static if no disatance is used) dictionary of airports with lats and lons within a certain distance
# Input: Airports In a 365 degree area DISTANCE areas wide will be includede in the dict but none others
# This is to shorten the time needed to render the current conditions

# Also inside this method I will be creating a new dictionary for all US airports so that Folium can read it as ChatGPT wrote the dictionary there in a different format

def createStaticDict(distance):
    # Scrape data for airports within x amount of miles and create the perminant dictionary here to run once.
    # https://w1.weather.gov/xml/current_obs/index.xml contains the data for all the airport data and lat and lon but it is in xml format
    url1 = 'https://w1.weather.gov/xml/current_obs/index.xml'
    #mytree = ET.parse(url1)
    #root = tree.getroot()
    response1 = urllib.request.urlopen(url1).read()
    data = xmltodict.parse(response1)
    modDict = data["wx_station_index"]
    metarr = []
    compatibleArr = []
    #print(modDict[0])
    for tag in modDict:
        # Heres an example of what station looks like
        # 'station': [{'station_id': 'CWAV', 'state': 'AB', 'station_name': 'Sundre', 'latitude': '51.76667', 'longitude': '-114.68333',
        # [
        #     {'name': 'KBVY', 'lat': 42.58361, 'lon': -70.91639},
        if tag == 'station':
            #print(modDict[tag])
            metarr.append(modDict[tag])
            for index in range(0, len(modDict[tag]) - 1):
                # Each station has a "station_id", "state", "station_name", "latitude", "longitude", "html_url", "rss_url", and "xml_url"
                keyICAO = modDict[tag][index]["station_id"]
                #modDict[tag][0]["state"]
                #print(modDict[tag][0]["latitude"])


                # This is the lat and lon from where you want to get airport data from x miles out
                lat2 = float(modDict[tag][index]["latitude"])
                lon2 = float(modDict[tag][index]["longitude"])

                # Have user enter current location in lat and lon
                #lat1 = float(input("Please enter current latitude"))
                #lon1 = float(input("Please enter current longitude"))
                # This is the original latitude anbd longitude from where you want to start.
                lat1 = 42.3656
                lon1 = -71.0096
                # apply law of cosines to find airports 100 miles from current location
                # If it is within 100 miles put in dict otherwise it is out of range
                # The distance is measured in meters
                if distanceFinder(lat1, lon1, lat2, lon2, 400000):
                    #each airport gets its own dict with name lat and lon
                    # This is the standard step of building the normal dictionary
                    aptnamesUSA[keyICAO] = [lat2, lon2]
                    # MiniDict is defined
                    miniDict = {}
                    # Build the mini dictionary
                    miniDict["name"] = keyICAO
                    miniDict["lat"] = lat2
                    miniDict["lon"] = lon2
                    compatibleaptnamesUSA.append(miniDict)
    #print(aptnamesUSA)
    print(compatibleaptnamesUSA)

def createCompatibleDict(distance):
    None
def coordDist(dist):
    None

    #ETRARtoSTRING1 = response1.decode('UTF-8')
    #print(METRARtoSTRING1)
print(createStaticDict(1000))


"""
The goal of this method is to create a dynamic list of airport codes to run based on how far away they want
"""
dynamicDict = {}
def createDynamicDict():
    # for every key in aptnamesUSA (which is every airport code in the US),
    for key in aptnamesUSA:
        lat1 = aptnamesUSA[key][0]
        lat2 = aptnamesUSA[key][1]


# Create a list of airports in new england
aptnamesMA = {"KBVY" : [42.58361, 70.91639], "KBOS":[42.36056, 71.01056], "KCQX":[41.6875, 69.99333],
              "KCEF":[42.2, 72.53333], "KFIT":[42.55194, 71.75583], "KHYA":[41.67194, 70.26972],
              "KBED":[42.46811, 71.29463], "KLWM":[42.7126, 71.12553], "KGHG":[42.0983, 70.6722],
              "KMVY":[41.39298, 70.61588], "KACK":[41.25389, 70.05972], "KEWB":[41.67528, 70.95694],
              "KAQW":[42.69731, 73.16955], "KOWD":[42.19083, 71.17389], "KORE":[42.57, 72.28693],
              "KFMH":[41.65, 70.51667], "KPSF":[42.42691, 73.28897], "KPYM":[41.90861, 70.72806],
              "KPVC":[42.07436, 70.21816], "KBAF":[42.15972, 72.71278], "KORH":[42.27056, 71.87306],
              "KBDR":[41.16421, 73.12663], "KSNC":[41.38389, 72.50583], "KDXR":[41.37167, 73.48444],
              "KGON":[41.3275, 72.04944], "KHFD":[41.735, 72.65167],"KMMK":[41.50972, 72.82778],
              "KHVN":[41.26389, 72.88722], "KOXC":[41.48333, 73.13333], "KIJD":[41.74194, 72.18361],
              "KBDL":[41.93806, 72.6825], "PADK":[51.87778, 176.64583], "PAUT":[54.1446, 165.6041],
              "PAFM":[67.1, 157.85], "PAKP":[68.13361, 151.74333]}

weatherConditions = ["FU VA", "HZ", "DU SA", "BLDU BLSA", "PO", "VCSS", "BR", "MIFG", "VCTS","VIRGA","VCSH", "TS", "SQ", "FC", "SS", "+SS",
                     "BLSN", "DRSN", "VCFG", "BCFG","PRFG", "FG", "FZFG", "-DZ", "DZ", "+DZ","-FZDZ", "FZDZ +FZDZ", "-DZRA","DZRA","-RA",
                     "RA", "+RA", "-FZRA", "FZRA +FZRA", "-RASN", "RASN +RASN", "-SN", "SN", "+SN","SG", "IC", "PE PL", "-SHRA", "SHRA +SHRA",
                     "-SHRASN", "SHRASN +SHRASN", "-SHSN", "SHSN +SHSN","-GR","GR", "TSRA", "TSGR", "+TSRA"]


def seperateTempsFromDews(rawData):
    # Organize Temperature Data
    temp = float(rawData[0][1:])


    # Organize Dewpoint Data
    # If the dewpoint has an M it is negative
    if(rawData[1][0] == 'M'):
        dwpt = -1.0 * float(rawData[1][1:])
    # For regular non negative dewpoints
    else:
        dwpt = float(rawData[1][:])

    tempConvert = temp * (9.0/5.0) + 32.0
    dewConvert = dwpt * (9.0/5.0) + 32.0
    return [tempConvert, dewConvert]

def isWindDefined(metarText):
    if(re.search("KT", metarText)):
        return True
    else:
        return False

def convertWind(windRaw, metarText):
    #print(metarText)
    #print(windRaw)
    # Is the wind defined already
    if(isWindDefined(metarText)):
        # Check to see if the wind direction is variable meaning the wind speed is too low or the wind direction is all over the palce
        if(not (re.search("VRB", windRaw))):
            # If the wind direciton is NOT variable it is a normal reading
            # First three digits indiucate the direction from which the wind is blowing in relation to true North
            windAngle = windRaw[0:3]
            # The windspeed can be 2 to 3 digits
            # It starts at the end of the wind direction and ends at either "G" or "KT"
            # First check to see if there is a wind gust
            if(re.search("G", windRaw)):
                # Get everything between G and KT
                # KT is always the last thing in windRaw
                startGustPos = re.search("G", windRaw).start() + 1
                windGust = windRaw[startGustPos:len(windRaw) - 2]
                windSpeed = windRaw[3:startGustPos - 1]
                # This means there is a wind angle, wind speed, and a wind gust in the METAR
                return [float(windAngle), float(windSpeed), float(windGust)]
            # Otherwise there is no wind gust
            else:
                # Extract the wind speed
                # Get everything between end od windDir (position 2 in rawWind) and end of rawWind - 3 to strip off the KT
                windSpeed = windRaw[3:len(windRaw) - 2]
                # Return 0 for WindGusts
                try:
                    return [float(windAngle), float(windSpeed), 0]
                except:
                    return [-999999999999, -999999999999, -999999999999]
        else:
            windSpeedRaw = re.search(r'VRB(.*?)KT', windRaw).group()
            # Search to see if there are gusts with a variable wind direction
            #gust = re.search(r'G', windSpeedRaw)
            if re.search(r'G', windSpeedRaw):
                # example VRB05G01KT
                windSpeed = windSpeedRaw[3:4]
                windGust = windSpeedRaw[6:7]
                return ["VRB", float(windSpeed), float(windGust)]
            # else there is no wind gust with a variable wind direction
            else:
                windSpeed = windSpeedRaw[3:len(windSpeedRaw) - 2]
                return ["VRB", float(windSpeed), 0]
    else:
        # If the wind field is not defined
        return [-999999999999, -999999999999, -999999999999]

def isAuto(rawAuto):
    # If the 3rd position is AUTO return true
    if(rawAuto == "AUTO" or rawAuto == "COR"):
        return True
    else:
        return False

def visibilityCheck(rawInput):
    # If SM or Statuate Miles is in the 4th position of arrayData, then it is displaying the visibility
    if(re.search("SM", rawInput)):
        return True
    else:
        return False

def getVisibility(rawInput):
    # Return all numbers between the 0th position of the input to the end of firwst letter of the unit
    return rawInput[0:len(rawInput) - 2]

# Check to see if weather conditions are specificed or not
def weatherConsitionCheck(rawInput):
    # A weather condition starts with '-'
    if(re.search("-", rawInput)):
        return True
    else:
        return False

def getConditions(rawInput):
    # Pass in position 4 and 5 of the original array data
    # Test position 5 to see if it is sky conditions or not
    # If it is, then there is no second cindition
    if(re.match(rawInput[1], r'\w\w\w\d\d\d')):
        # No second condition
        return [rawInput[0], None]
    else:
        return [rawInput[0], rawInput[1]]

# This is the correct version of getting the conditions
# Paraemter textMETAR, is the raw output of the metar converted to text
def getConds(textMETAR):
    # Search through list 'weatherCpnditions' based on raw data METRARtoSTRING as input
    for i in weatherConditions:
        if ('+' in i):
            if (i in textMETAR):
                return i
    else:
        return re.search(textMETAR, i)

def cloudConds(textMETAR):
        conds = ["CLR", "FEW", "SCT", "BKN", "OVC"]
        cloudConds = []
        # Loop through all the conditions
        for i in conds:
            if(i in textMETAR):
                # Search through the METAR to see if you find an element in conds.
                cloudData = re.search(i, textMETAR)
                # This finds multiple instances of a word, useful for finding 2 conditions that are the same in  a METAR
                cloudData1 = re.findall(i, textMETAR)
                potentialCondition = re.compile(i)
                # This will find the starting and ending instances of all the occurences of the current cond (i) in the METAR. Only applies if the same condition is found twice
                duplicateConditions = [[m.group(), m.start(), m.end()] for m in potentialCondition.finditer(textMETAR)]
                #print(duplicateConditions)
                # If there are no clear skies
                if(not (re.search(i, textMETAR).group() == "CLR")):
                    #print("The cloud celing is " + re.search(i, textMETAR).group())
                    # If there are duplicate cloud layers, you will need to loop through each one
                    for j in duplicateConditions:
                        # Find the where the word ends
                        cloudCond = j[0]
                        # Get the height of the cloud layer Note it might be ///
                        try:
                            cloudCeiling = textMETAR[j[2]:int(j[2]) + 3]

                            # If there is no data for the cloud ceiling, replace that data with 0 meaning no data

                            #print("The cloud ceiling is " + cloudData1)
                            cloudConds.append(cloudCond)
                            # Cloud celing measurements are given in hundreds of feet
                            cloudConds.append(int(cloudCeiling) * 100)
                        except:
                            None
                else:
                    cloudConds.append("CLR")
            else:
                None
        return cloudConds

#date is YYYYMMDD
def generateRadarURL(ICAO, date, closestsite):
    url = "https://weather.ral.ucar.edu/radar/displayRad.php?icao="+ ICAO + "&prod = BREF&bkgr=gray&endDate=20230128&endTime=-1&duration = 0"

def getTempDew(textMETAR):
    #If temperature and dewpoint are both positive
    tempDewRaw = re.search(r'\d{2}\/\d{2}(.*?)',textMETAR)
    # If the temperature is positive and the dewpoint is negative
    tempMDewRaw = re.search(r'\d{2}\/\w\d{2}', textMETAR)
    # If the temperature is negative and the dewpoint is positive
    MtempDewRaw = re.search(r'M\d{2}\/\d{2}', textMETAR)
    # If the temprature and dewpoint are both negative
    MtempMDewRaw = re.search(r'M\d{2}/M\d{2}', textMETAR)
    if(tempDewRaw):
        temp = tempDewRaw.group()[0:2]
        dew = tempDewRaw.group()[3:]
        return [float(temp), float(dew)]
    elif(tempMDewRaw):
        temp = tempMDewRaw.group()[0:2]
        dew = tempMDewRaw.group()[4:]
        return [float(temp), -1 * float(dew)]
    elif(MtempDewRaw):
        temp = MtempDewRaw.group()[1:3]
        dew = MtempDewRaw.group()[4:]
        return [-1 * float(temp), float(dew)]
    elif (MtempMDewRaw):
        # M01/M04
        temp = MtempMDewRaw.group()[1:3]
        dew = MtempMDewRaw.group()[4:]
        print(temp, dew)
        return [-1.0 * float(temp), -1.0 * float(dew)]
    else:
        # Else no temperature data was reported
        None


metDict = {}
p = 0
# average time for 1 airport to scrape
avg = 0
for key in aptnamesUSA:
    # starts the timer
    start_time = time.time()
    metData = []
    url = "https://w1.weather.gov/data/METAR/" + key + ".1.txt"
    #r = requests.get(url, headers=header)
    response = urllib.request.urlopen(url).read()
    METRARtoSTRING = response.decode('UTF-8')
    # Find the start of the METAR
    METARstartpos = re.search('METAR', METRARtoSTRING)
    # Get rest of METAR
    data = METRARtoSTRING[METARstartpos.start():]
    arrayData = data.split(' ')
    #print(METRARtoSTRING)
    # Initialize variable
    WindDataArr = 0
    # Check 3rd digit for potential modifier
    if (not isAuto(arrayData[3])):
        metData.append(convertWind(arrayData[3], METRARtoSTRING))
    else:
        # perminantly shortens arrayData
        arrayData.pop(3)
        metData.append(convertWind(arrayData[3], METRARtoSTRING))

    visData = 0
    if(visibilityCheck(arrayData[4])):
        #Check to see if wind has variable direction over 60 degrees
        if(re.search(r'\d{3}\w\d{3}', arrayData[5])):
            # If visibility is a field, return it
            metData.append(getVisibility(arrayData[5]))
        else:
            metData.append(getVisibility(arrayData[4]))
    else:
        # Insert No Visibility stated as none into the array
        metData.append(None)

    """
    # Check if weather conditions are specific
    if(weatherConsitionCheck(arrayData[5])):
        # Extract Weather Conditions
        # Note that position
        metData.append(getConditions([arrayData[5], arrayData[6]]))
    else:
        # No weather condition is specified
        metData.append(None)
    """
    metData.append(getConds(METRARtoSTRING))
    #print(cloudConds(METRARtoSTRING))
    metData.append(cloudConds(METRARtoSTRING))
    metData.append(getTempDew(METRARtoSTRING))
    # For testing purposes
    # Add i as key and metData as value to metDict
    metDict[key] = metData
    # ends the timer
    end_time = time.time()
    total_time = end_time - start_time
    p = p + 1
    #avg = (avg + total_time) / p
    print("The Airport " + key + " has successfully been updated!")
    print("You are " + str((p / len(aptnamesUSA)) * 100) + "% complete! Now loading airport " + str(p) +" of " + str(len(aptnamesUSA)))
    print((total_time * len(aptnamesUSA)) - total_time)

    #print((avg * len(aptnamesUSA)))

#print(temps)
import folium
from folium.features import DivIcon
import random
def generate_random_temperature(airport):
    #print(metDict)
    if airport in metDict:
        return airport

# This breaks each circle color down into a color gradient to represent the temperature
# returns the hex code for the color the circle will be

# dark blue represents temperatures 26-29
# light blue represents 0C
# yellow reprents 60 degrees
def pick_color(data):
    # generate a single color table
    if(data < 45 and data >= 41):
        return #00A36C
    elif(data < 40 and data >= 36):
        return #5F9EA0
    elif(data < 35 and data >= 33):
        return  #7393B3
    elif(data < 32 and data >= 30):
        return #ADD8E6
    elif(data < 29 and data >= 25):
        return #00008B
    elif(data < 24 and data >= 20):
        return #0000FF
    elif(data < 15 and data >= 19):
        return #5D3FD3
    elif(data < 10 and data >= 14):
        return #5D3FD3
    elif (data < 10 and data >= 14):
        return #CCCCFF
    else:
        return #0437F2
def plot_airports(airport_data):
    # Create a map centered around the first airport
    map_center = [airport_data[0]['lat'], airport_data[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=5)

    # Add markers for each airport
    for airport in compatibleaptnamesUSA:
        temp = 0
        heat_map = []
        name = airport['name']
        lat = airport['lat']
        lon = airport['lon']
        #print(generate_random_temperature(name))
        if generate_random_temperature(name):
            temp = metDict.get(name)
            print(name)
            print(temp[-1])
            try:
                """
                folium.Circle(
                    location=(airport["lat"], airport["lon"]),
                    radius=10,  # Radius of the circle
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    popup=f"{airport['name']}: {airport['temp']}°F",  # Displaying temperature in popup
                ).add_to(m)"""
                #circle_color = pick_color(str(float(metDict.get(name)[4][0] * (9.0/5.0)) + 32.0))
                folium.Circle(
                    location=(airport["lat"], airport["lon"]),
                    radius=500,  # Radius of the circle
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    #popup=f"{airport['name']}: {metDict.get(name)}°F",  # Displaying temperature in popup
                ).add_to(m)

                folium.map.Marker(
                    [airport["lat"], airport["lon"]],
                    icon=DivIcon(
                        icon_size=(150, 36),
                        icon_anchor=(0, 0),
                        html='<a href="https://w1.weather.gov/data/METAR/KBOS.1.txt"><div style="font-size: 16pt">%s</div>' % f"{airport['name']}: {str(float(metDict.get(name)[4][0]))}°F",
                    )
                ).add_to(m)

                marker_text1 = f"{name}<br>Temperature: {round(((temp[4][0] * (9.0/5.0)) + 32.0),2)}°F<br>Dewpoint: {round(((temp[4][1] * (9.0/5.0)) + 32.0), 2)}°F"
                print(temp[4][1])
            except:
                market_text1 = f"No Data"
        else:
            None
        #heat_map.append(temp)
        #marker = folium.Marker(location=[lat, lon], popup=marker_text)
        """
        folium.Circle(
            location=(airport["lat"], airport["lon"]),
            radius=100,  # Radius of the circle
            color='blue',
            fill=True,
            fill_color='blue',
            popup=f"{airport['name']}: {metDict.get(name)}°F",  # Displaying temperature in popup
        ).add_to(m)

        folium.map.Marker(
            [airport["lat"], airport["lon"]],
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(0, 0),
                html='<div style="font-size: 12pt">%s</div>' % "airport",
            )
        ).add_to(m)
        #marker.add_to(m)
        """
    # Display the map
    return m

# Example airport data
airport_data = [
    {'name': 'John F. Kennedy International Airport', 'lat': 40.6413, 'lon': -73.7781},
    {'name': 'Los Angeles International Airport', 'lat': 33.9416, 'lon': -118.4085},
    {'name': 'London Heathrow Airport', 'lat': 51.4700, 'lon': -0.4543},
    {'name': 'Tokyo Haneda Airport', 'lat': 35.5494, 'lon': 139.7798}
]

# Plot the airports on a map
map_with_airports = plot_airports(airport_data)

# Save the map as an HTML file
map_with_airports.save('airport_map2.html')
#print(dynamicDict)
"""
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

# Load the GRIB data into an xarray Dataset
data = xr.open_dataset("gfs_data.grib", engine='cfgrib')

# Extract the temperature data
temperature = data.t2m.squeeze()

# Define the map extent for New England
latitude_min = 38.0
latitude_max = 46.0
longitude_min = -75.0
longitude_max = -70.0

# Create a Cartopy projection for the map
projection = ccrs.PlateCarree()

# Create a plot of the temperature data
fig, ax = plt.subplots(subplot_kw={'projection': projection})
temperature.plot.imshow(ax=ax, transform=ccrs.PlateCarree(),
                        extent=(longitude_min, longitude_max, latitude_min, latitude_max),
                        origin='upper', cmap='hot')
ax.coastlines()
ax.set_extent([longitude_min, longitude_max, latitude_min, latitude_max], crs=ccrs.PlateCarree())

# Display the plot
plt.show()

# scrape airport codes
# Define the table name and columns
table_name = "Current Conditions"
columns = ["Location STRING", "Wind Direction FLOAT", "Wind Speed FLOAT", "Wind Gust FLOAT", "Visibility FLOAT", "Weather Conditions STRING", "Cloud Conditions STRING", "Temperature FLOAT", "Dewpoint FLOAT"]

# Generate the CREATE TABLE statement
create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"

# Generate the INSERT INTO statements for 10 airports
insert_sql = []
for i in metDict:
    Location = "Location"
    Wind_Direction = i * 5
    Wind_Speed = i * 1000
    Wing_Gust = 1000
    Visibility = 1000
    Weather_Conditions = "Weather Conditions"
    Cloud_Conditions = "Cloud Connditions"
    Temperature = 1000
    Dewpoint = 1000
    values = f"{Location}, {Wind_Direction}, {Wind_Speed}, {Wing_Gust}, {Visibility}, {Weather_Conditions}, {Cloud_Conditions}, {Temperature}, {Dewpoint}"
    insert_sql.append(f"INSERT INTO {table_name} VALUES ({values})")

# Print the generated SQL code
print(create_table_sql)
print("\n".join(insert_sql))
# metdata key = airport code value = metar decoded
"""
"""
import folium

def plot_airports(airport_data):
    # Create a map centered around the first airport
    map_center = [airport_data[0]['lat'], airport_data[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=5)

    # Add markers for each airport
    for airport in airport_data:
        name = airport['name']
        lat = airport['lat']
        lon = airport['lon']
        marker = folium.Marker(location=[lat, lon], popup=name)
        marker.add_to(m)

    # Display the map
    return m

# Example airport data
airport_data = [
    {'name': 'John F. Kennedy International Airport', 'lat': 40.6413, 'lon': -73.7781},
    {'name': 'Los Angeles International Airport', 'lat': 33.9416, 'lon': -118.4085},
    {'name': 'London Heathrow Airport', 'lat': 51.4700, 'lon': -0.4543},
    {'name': 'Tokyo Haneda Airport', 'lat': 35.5494, 'lon': 139.7798}
]

# Plot the airports on a map
map_with_airports = plot_airports(airport_data)

# Save the map as an HTML file
map_with_airports.save('airport_map.html')
"""

"""
import folium
import requests

def get_temperature(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=YOUR_API_KEY"
    response = requests.get(url)
    data = response.json()
    if 'main' in data and 'temp' in data['main']:
        temperature = data['main']['temp']
        # Convert temperature from Kelvin to Celsius
        temperature = temperature - 273.15
        return temperature
    else:
        return None

def plot_airports_with_temperature(airport_data):
    # Create a map centered around the first airport
    map_center = [airport_data[0]['lat'], airport_data[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=5)

    # Add markers for each airport with temperature information
    for airport in airport_data:
        name = airport['name']
        lat = airport['lat']
        lon = airport['lon']
        temperature = get_temperature(lat, lon)
        if temperature is not None:
            marker_text = f"{name}<br>Temperature: {temperature:.2f}°C"
        else:
            marker_text = f"{name}<br>Temperature: N/A"
        marker = folium.Marker(location=[lat, lon], popup=marker_text)
        marker.add_to(m)

    # Display the map
    return m

# Example airport data
airport_data = [
    {'name': 'John F. Kennedy International Airport', 'lat': 40.6413, 'lon': -73.7781},
    {'name': 'Los Angeles International Airport', 'lat': 33.9416, 'lon': -118.4085},
    {'name': 'London Heathrow Airport', 'lat': 51.4700, 'lon': -0.4543},
    {'name': 'Tokyo Haneda Airport', 'lat': 35.5494, 'lon': 139.7798}
]
aptnamesMA1 = {"KBVY" : [42.58361, 70.91639], "KBOS":[42.36056, 71.01056], "KCQX":[41.6875, 69.99333],
              "KCEF":[42.2, 72.53333], "KFIT":[42.55194, 71.75583], "KHYA":[41.67194, 70.26972],
              "KBED":[42.46811, 71.29463], "KLWM":[42.7126, 71.12553], "KGHG":[42.0983, 70.6722],
              "KMVY":[41.39298, 70.61588], "KACK":[41.25389, 70.05972], "KEWB":[41.67528, 70.95694],
              "KAQW":[42.69731, 73.16955], "KOWD":[42.19083, 71.17389], "KORE":[42.57, 72.28693],
              "KFMH":[41.65, 70.51667], "KPSF":[42.42691, 73.28897], "KPYM":[41.90861, 70.72806],
              "KPVC":[42.07436, 70.21816], "KBAF":[42.15972, 72.71278], "KORH":[42.27056, 71.87306],
              "KBDR":[41.16421, 73.12663], "KSNC":[41.38389, 72.50583], "KDXR":[41.37167, 73.48444],
              "KGON":[41.3275, 72.04944], "KHFD":[41.735, 72.65167],"KMMK":[41.50972, 72.82778],
              "KHVN":[41.26389, 72.88722], "KOXC":[41.48333, 73.13333], "KIJD":[41.74194, 72.18361],
              "KBDL":[41.93806, 72.6825], "PADK":[51.87778, 176.64583], "PAUT":[54.1446, 165.6041],
              "PAFM":[67.1, 157.85], "PAKP":[68.13361, 151.74333]}

# Plot the airports on a map with temperature data
map_with_temperature = plot_airports_with_temperature(airport_data)

# Save the map as an HTML file
map_with_temperature.save('airport_temperature_map.html')
"""

"""
import folium
import random
from folium.plugins import HeatMap

def generate_random_temperature():
    # Generate a random temperature value between -10 and 40 degrees Celsius
    return random.uniform(-10, 40)

def plot_airports_with_temperature(airport_data):
    # Create a map centered around the first airport
    map_center = [airport_data[0]['lat'], airport_data[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=5)

    # Prepare data for the heatmap
    heat_data = []
    for airport in airport_data:
        lat = airport['lat']
        lon = airport['lon']
        temperature = generate_random_temperature()
        heat_data.append([lat, lon, temperature])

    # Create heatmap layer
    HeatMap(heat_data).add_to(m)

    # Display the map
    return m

# Example airport data
airport_data = [
    {'name': 'John F. Kennedy International Airport', 'lat': 40.6413, 'lon': -73.7781},
    {'name': 'Los Angeles International Airport', 'lat': 33.9416, 'lon': -118.4085},
    {'name': 'London Heathrow Airport', 'lat': 51.4700, 'lon': -0.4543},
    {'name': 'Tokyo Haneda Airport', 'lat': 35.5494, 'lon': 139.7798}
]

# Plot the airports on a heatmap with random temperature data
map_with_temperature = plot_airports_with_temperature(airport_data)

# Save the map as an HTML file
map_with_temperature.save('airport_temperature_heatmap.html')
"""

"""
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
# create new figure, axes instances.
fig=plt.figure()
ax=fig.add_axes([0.1,0.1,0.8,0.8])
# setup mercator map projection.
m = Basemap(llcrnrlon=-74.,llcrnrlat=40.71,urcrnrlon=-69.70,urcrnrlat=43.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='i',projection='merc',\
            lat_0=40.,lon_0=-20.,lat_ts=20.)
m.drawcoastlines()
#m.fillcontinents()
m.drawcountries(linewidth=0.25)
m.drawstates(linewidth=0.25)
#m.etopo(scale=1, alpha=1)

plt.text(42.3601, -71.0589, 'Boston',fontsize=12,fontweight='bold',color='k')
# draw parallels
m.drawparallels(np.arange(10,90,20),labels=[1,1,0,1])
# draw meridians
m.drawmeridians(np.arange(-180,180,30),labels=[1,1,0,1])

xs = []
ys = []
zs = []
for k in aptnamesUSA:
    #xs = []
    #ys = []
    lat = aptnamesUSA[k][0]
    lon = -1.0 * aptnamesUSA[k][1]
    xs.append(lat)
    ys.append(lon)
for u in metDict:
    # each u is every ICAO
    # ICAO, Dir, Speed, Gust, Visibility, WxConditions, Cloud Heights, Temperature, Dewpoint
    zs1 = metDict[u]
    zs2 = zs1[len(zs1)-1][0]
    zs.append(zs2)

# [41.2333, 43.344, ... ]
xs = np.array(xs)
ys = np.array(ys)
z = np.array(zs)
print(len(xs))
print(len(ys))
print(len(zs))
# x = x + np.random.normal(scale=1e-8, size=x.shape)
# y = y + np.random.normal(scale=1e-8, size=y.shape)

rescale = lambda x: (x - x.min()) / (x.max() - x.min())
# xs = rescale(x)
# ys = rescale(y)

# Set up a regular grid of interpolation points
xi = np.linspace(xs.min(), xs.max(), num=150)
print(xi)
yi = np.linspace(ys.min(), ys.max(), num=150)
print(yi)
x0, y0 = np.meshgrid(xi, yi)
print(x0)
# Interpolate
rbf = scipy.interpolate.Rbf(xs, ys, z, function='linear')
print(rbf)
zi = rbf(xi, yi)
plt.show()
plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower',
           extent=[xs.min(), xs.max(), ys.min(), ys.max()])

#map.contour(x0, y0, zs)
# plt.scatter(xs, ys, c=z)
plt.colorbar()

plt.show()
"""

"""
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

def draw_new_england_map():
    # Set the size of the figure
    plt.figure(figsize=(8, 10))

    # Define the projection, size, and the area of the map
    m = Basemap(projection='merc', llcrnrlat=40.5, urcrnrlat=47.5, llcrnrlon=-74, urcrnrlon=-66, resolution='f')

    # Draw coastlines and country boundaries
    m.drawcoastlines()
    m.drawcountries()

    # Draw states boundaries
    m.drawstates()

    # Draw map boundary
    m.drawmapboundary(fill_color='white')

    # Show the plot
    plt.title("Tropica Innovations Snow Depth Map")
    plt.show()

# Call the function to draw the map
draw_new_england_map()

import requests
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

# Define the URL to fetch alert data for New Hampshire
url = 'https://api.weather.gov/alerts/active?area=MA'

# Fetch alert data from the API
response = requests.get(url)
data = response.json()

# Find the first severe thunderstorm warning polygon
severe_thunderstorm_polygon = None
for alert in data['features']:
    if alert['properties']['event'] == 'Winter Storm Warning':
        polygon_coords = alert['geometry']['coordinates'][0]
        polygon = Polygon(polygon_coords)
        if polygon.is_valid:
            severe_thunderstorm_polygon = polygon
            break

if severe_thunderstorm_polygon:
    # Create a Basemap object for New Hampshire
    m1 = Basemap(
        projection='merc',
        llcrnrlat=42.697,
        urcrnrlat=45.305,
        llcrnrlon=-72.557,
        urcrnrlon=-70.603,
        resolution='i'
    )
    m = Basemap(
        projection='merc',  # Mercator projection
        llcrnrlat=41.0,  # Lower-left corner latitude
        urcrnrlat=45.0,  # Upper-right corner latitude
        llcrnrlon=-73.0,  # Lower-left corner longitude
        urcrnrlon=-69.0,  # Upper-right corner longitude
        resolution='i'  # Intermediate resolution (you can adjust as needed)
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
    plt.fill(x, y, 'y', alpha=0.5)

    # Set plot title and show the map
    plt.title('Winter Storm Warnings for New England')
    plt.show()
else:
    print('No severe thunderstorm warnings found in New Hampshire.')"""