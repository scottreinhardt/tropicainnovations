#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 12:44:42 2024

@author: scottreinhardt
"""

import requests
import re
import numpy as np
import pprint
import urllib
import xmltodict

class MOSScraper:
    #superDict = {}
    #superArr = []
    def __init__(self):
        self.superDict = {}
        #self.createStaticDict = DistanceFinder
        #def parse(self, html):
    #   self.results.append(html)

       # lat1 and lat2 are the users current corrdinates
        # lat2 and lon2 are the corrdinates of the airport
        # If the airport is within 100 miles of the users coordinates the method will return true, otherwise false.
        # returns a boolean
    def distanceFinder(self, lat1, lon1, lat2, lon2, distance):
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

    def findCoords(self, lat1, lon1, d):
        # find coordinates for basemap
        tc = 90
        pi = np.pi
        lat = np.arcsin(np.sin(lat1) * np.cos(d) + np.cos(lat1) * np.sin(d) * np.cos(tc))
        dlon = np.arctan2(np.sin(tc) * np.sin(d) * np.cos(lat1), np.cos(d) - np.sin(lat1) * np.sin(lat))
        lon = np.mod(lon1 - dlon + pi, 2 * pi) - pi



    def createStaticDict(self, distance):
        # Dictionary of every airport within a certain distance of a user or location
        #Problem: right now, the dictionary is not in the correct format
        # It writes it as {'KBDL': [41.93806, -72.6825], 'KGON': [41.3275, -72.04944]}
        # When Folium takes the data in as airport_data1 = [{'name': 'KBVY', 'lat': 42.58361, 'lon': -70.91639}]
        aptnamesUSA = {}
        compatibleaptnamesUSA = []

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
                    if self.distanceFinder(lat1, lon1, lat2, lon2, 250000):
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
            return compatibleaptnamesUSA

    def run(self):
        #aptnamesUSA = {}
        aptnamesUSA = self.createStaticDict(1000)
        """
        # Dictionary of every airport within a certain distance of a user or location
        #Problem: right now, the dictionary is not in the correct format
        # It writes it as {'KBDL': [41.93806, -72.6825], 'KGON': [41.3275, -72.04944]}
        # When Folium takes the data in as airport_data1 = [{'name': 'KBVY', 'lat': 42.58361, 'lon': -70.91639}]
        aptnamesUSA = {}
        compatibleaptnamesUSA = []

        # Scrape data for airports within x amount of miles and create the perminant dictionary here to run once.
        # https://w1.weather.gov/xml/current_obs/index.xml contains the data for all the airport data and lat and lon but it is in xml format
        url1 = 'https://w1.weather.gov/xml/current_obs/index.xml'
        response1 = urllib.request.urlopen(url1).read()
        data = xmltodict.parse(response1)
        modDict = data["wx_station_index"]
        metarr = []
        compatibleArr = []
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
                    if self.distanceFinder(lat1, lon1, lat2, lon2, 250000):
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
        #for key in aptnamesUSA:
        #self.createStaticDict(250000)
        """
        superArr = []
        # URL of the webpage
        url = "https://www.weather.gov/source/mdl/MOS/GFSMAV.t00z"

        # Send a GET request to fetch the webpage content
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the text content of the webpage
            content = response.text
            #print(content)
            # Define the regular expression pattern to find a newline followed by a 4-letter word at th top of each block of text
            ICAO = r'\b[A-Z]{4}\b'
            # Define the regular expression pattern to find everything after "TMP" to the end of the line
            rawHour = r'HR.*'
            rawTemp = r'TMP.*'
            rawDew = r'DPT.*'
            rawCloudConds = r'CLD.*'

            # Define the regular expression pattern to find each block of text
            pattern = r'([A-Z]{4}.*?)\n(?=[A-Z]{4}|$)'

            # Find all blocks
            matchesTest = re.findall(pattern, content, re.DOTALL)

            # Find all matches
            # returns a list of all of the airport ICAO codes
            matchesICAO = re.findall(ICAO, content)
            #superDict = {}
            #superArr = []
            #print(matchesICAO)

            # returns a list of list of all of the hours
            matchesHour = re.findall(rawHour, content)
            #print(matchesHour)
            #returns a list of lists of all of the temperatures for each ICAO
            matchesTemp = re.findall(rawTemp, content)
            #print(matchesTemp)
            matchesDew = re.findall(rawDew, content)
            matchesCloudConds = re.findall(rawCloudConds, content)

            """for i in range(0, len(matchesHour)):
                matchesHour[i] = float(matchesHour[i])
            for j in range(0, len(matchesTemp)):
                matchesTemp[j] = float(matchesTemp[j])
            for k in range(0, len(matchesDew)):
                matchesDew[k] = float(matchesDew[k])"""
            #len(matchesICAO)
            # Print the matches
            #superDict = {}
            matchHourCSVArr = []
            matchTempCSVArr = []
            matchDewCSVArr = []
            # total icao len = len(matchesICAO)
            finalarr = []
            for icao in range(0, 1000):
                key = icao
                #print(key)
                superArr = []
                for temp in matchesTemp:
                    newArr = []
                    newArrHour = []
                    tempArr = temp.split()[1:]
                    #hourArr =
                    #temp prints 'TMP  70 70 71 78 82 85 82 76 74 73 73 79 87 91 90 84 79 76 75 88 88'
                    #print(temp)
                    #print(tempArr)
                    for index in range(len(tempArr)):
                        #print(matchesTemp[index])
                        # tempArr[index] prints each element in temp individually
                        #print(tempArr[index])
                        # try to convert tempArr[index] as a float
                        if(float(tempArr[index]) < 200.0):
                            tempVal = float(tempArr[index])
                            #print(tempVal)
                            # Build the new temporary array with float values
                            newArr.append(tempVal)
                            #print(newArr)
                            #print(newArr)
                            # ceates an arrays of arrays
                        else:
                            None
                    superArr.append(newArr)


                for hour in matchesHour:
                    newArrHour = []
                    hourArr = hour.split()[1:]
                    for index in range(len(hourArr)):
                        try:
                            hourVal = float(hourArr[index])
                            newArrHour.append(hourVal)
                        except:
                            break
                    superArr.append(newArrHour)
                self.superDict[matchesICAO[icao]] = superArr[icao]

                #print(superArr)
                #superArr = [[float(element) for element in sublist] for sublist in superArr]
                #print(superArr)

                #print(superArr)
                #print(len(self.superDict))

                #print(matchesTemp[i])
                #for j in matchesTest:
                #    print(matchesICAO[i])
                #superDict = {}

                #matchHourCSVArr = matchesHour[i].split()[1:]
                #print(matchesHour[i])
                #print(matchHourCSVArr)
                #matchTempCSVArr = matchesTemp[i].split()[1:]
                #matchDewCSVArr = matchesDew[i].split()[1:]

                #for a in range(0, len(matchHourCSVArr)):
                #    matchHourCSVArr[a] = float(matchHourCSVArr[a])
                #for j in range(0, len(matchTempCSVArr)):
                #    matchTempCSVArr[j] = float(matchTempCSVArr[j])
                #for k in range(0, len(matchDewCSVArr)):
                #    matchDewCSVArr[k] = float(matchDewCSVArr[k])

            #superArr.append(matchHourCSVArr)
            #superArr.append(matchTempCSVArr)
            #superArr.append(matchDewCSVArr)
            #superArr.append(matchesCloudConds[i].split()[1:])
            #for p in range(0,2):
            #    superArr.append(matchHourCSVArr)
            #    superArr.append(matchTempCSVArr)
            #    superArr.append(matchDewCSVArr)
            #    print(matchesICAO[p])
                #self.superDict[matchesICAO[p]] = superArr
            #print(superDict)
            #self.parse(superDict)
            #return superDict

            # Split the content into blocks using double newlines as the separator
            #blocks = content.split('\n\n')

            # Output each block separately
            #for i, block in enumerate(blocks):
            #    print(f"Block {i+1}:\n{block}\n")
        else:
            print("Failed to fetch the webpage.")
        return self.superDict

  # lat1 and lat2 are the users current corrdinates
    # lat2 and lon2 are the corrdinates of the airport
    # If the airport is within 100 miles of the users coordinates the method will return true, otherwise false.
    # returns a boolean
    """
    def distanceFinder(self, lat1, lon1, lat2, lon2, distance):
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

    def findCoords(self, lat1, lon1, d):
        # find coordinates for basemap
        tc = 90
        pi = np.pi
        lat = np.arcsin(np.sin(lat1) * np.cos(d) + np.cos(lat1) * np.sin(d) * np.cos(tc))
        dlon = np.arctan2(np.sin(tc) * np.sin(d) * np.cos(lat1), np.cos(d) - np.sin(lat1) * np.sin(lat))
        lon = np.mod(lon1 - dlon + pi, 2 * pi) - pi



    def createStaticDict(self, distance):
        # This is a temporary fix to repopulate mod dict because the current obs website is down

        # Dictionary of every airport within a certain distance of a user or location
        #Problem: right now, the dictionary is not in the correct format
        # It writes it as {'KBDL': [41.93806, -72.6825], 'KGON': [41.3275, -72.04944]}
        # When Folium takes the data in as airport_data1 = [{'name': 'KBVY', 'lat': 42.58361, 'lon': -70.91639}]
        aptnamesUSA = {}
        compatibleaptnamesUSA = []

        # Scrape data for airports within x amount of miles and create the perminant dictionary here to run once.
        # https://w1.weather.gov/xml/current_obs/index.xml contains the data for all the airport data and lat and lon but it is in xml format
        url1 = 'https://w1.weather.gov/xml/current_obs/index.xml'
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
                print(modDict[tag])
                metarr.append(modDict[tag])
                for index in range(0, len(modDict[tag]) - 1):
                    # Each station has a "station_id", "state", "station_name", "latitude", "longitude", "html_url", "rss_url", and "xml_url"
                    keyICAO = modDict[tag][index]["station_id"]
                    print(keyICAO)

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
                    if self.distanceFinder(lat1, lon1, lat2, lon2, 1000000):
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
        return compatibleaptnamesUSA


    def fetch(self, url):
        return requests.get(url)

    def seperateTempsFromDews(self, rawData):
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

    def isWindDefined(self, metarText):
        if(re.search("KT", metarText)):
            return True
        else:
            return False

    def convertWind(self, windRaw, metarText):
        #print(metarText)
        #print(windRaw)
        # Is the wind defined already
        if(self.isWindDefined(metarText)):
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


    def isAuto(self, rawAuto):
        # If the 3rd position is AUTO return true
        if(rawAuto == "AUTO" or rawAuto == "COR"):
            return True
        else:
            return False

    def visibilityCheck(self, rawInput):
        # If SM or Statuate Miles is in the 4th position of arrayData, then it is displaying the visibility
        if(re.search("SM", rawInput)):
            return True
        else:
            return False

    def getVisibility(self, rawInput):
        # Return all numbers between the 0th position of the input to the end of firwst letter of the unit
        return rawInput[0:len(rawInput) - 2]

    # Check to see if weather conditions are specificed or not
    def weatherConditionCheck(self, rawInput):
        # A weather condition starts with '-'
        if(re.search("-", rawInput)):
            return True
        else:
            return False

    def getConditions(self, rawInput):
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
    def getConds(self, textMETAR):
        weatherConditions = ["FU VA", "HZ", "DU SA", "BLDU BLSA", "PO", "VCSS", "BR", "MIFG", "VCTS","VIRGA","VCSH", "TS", "SQ", "FC", "SS", "+SS",
                            "BLSN", "DRSN", "VCFG", "BCFG","PRFG", "FG", "FZFG", "-DZ", "DZ", "+DZ","-FZDZ", "FZDZ +FZDZ", "-DZRA","DZRA","-RA",
                            "RA", "+RA", "-FZRA", "FZRA +FZRA", "-RASN", "RASN +RASN", "-SN", "SN", "+SN","SG", "IC", "PE PL", "-SHRA", "SHRA +SHRA",
                            "-SHRASN", "SHRASN +SHRASN", "-SHSN", "SHSN +SHSN","-GR","GR", "TSRA", "TSGR", "+TSRA"]
        # Search through list 'weatherCpnditions' based on raw data METRARtoSTRING as input
        for i in weatherConditions:
            if ('+' in i):
                if (i in textMETAR):
                    return i
        else:
            return re.search(textMETAR, i)

    def cloudConds(self, textMETAR):
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

    def splitcloudHeights(self, rawInput):
        # If there are no cloud heights listed it is an error
        if(len(rawInput) == 0):
            return "Not Listed"
        elif(rawInput[0]):
            return "Clear Skies"
        else:
            return rawInput

    def getTempDew(self, textMETAR):
        #If temperature and dewpoint are both positive
        tempDewRaw = re.search(r'\d{2}\/\d{2}',textMETAR)
        # If the temperature is positive and the dewpoint is negative
        tempMDewRaw = re.search(r'\d{2}\/\w\d{2}', textMETAR)
        # If the temperature is negative and the dewpoint is positive
        MtempDewRaw = re.search(r'\w\d{2}\/\d{2}', textMETAR)
        # If the temprature and dewpoint are both negative
        MtempMDewRaw = re.search(r'\w\d{2}\/\w\d{2}', textMETAR)
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
            None
    def generate_random_temperature(self, airport, metDict):
        if airport in metDict:
            return airport

    def plot_airports(self, airport_data):
        # get all relevant airports will return an array of dictionarys
        #compatibleaptnamesUSA1 = createStaticDict(100)
        # Create a map centered around the first airport
        map_center = [airport_data[0]['lat'], airport_data[0]['lon']]
        m = folium.Map(location=map_center, zoom_start=5)
        #createStaticDict(1000)
        # Add markers for each airport
        aptnamesUSA = self.createStaticDict(750000)
        for airport in aptnamesUSA:
            temp = 0
            heat_map = []
            name = airport['name']
            lat = airport['lat']
            lon = airport['lon']
            #print(generate_random_temperature(name))
            if self.generate_random_temperature(name, metDict['name']):
                temp = metDict.get(name)
                #print(temp[-1][0])
                try:
                    if({round(((temp[4][0] * (9.0/5.0)) + 32.0),2)} > 70):
                        marker_text = f"{name}<br>Temperature: {round(((temp[4][0] * (9.0/5.0)) + 32.0),2)}°F<br>Dewpoint: {round(((temp[4][1] * (9.0/5.0)) + 32.0), 2)}°F"
                except:
                    market_text = f"No Data"
            else:
                #print(0)
                None
            #heat_map.append(temp)
            marker = folium.Marker(location=[lat, lon], popup=marker_text)
            marker.add_to(m)

        # Display the map
        return m
        """
        # Example airport data
        #airport_data = [{'name': 'John F. Kennedy International Airport', 'lat': 40.6413, 'lon': -73.7781},{'name': 'Los Angeles International Airport', 'lat': 33.9416, 'lon': -118.4085},{'name': 'London Heathrow Airport', 'lat': 51.4700, 'lon': -0.4543},{'name': 'Tokyo Haneda Airport', 'lat': 35.5494, 'lon': 139.7798}]

        # Plot the airports on a map
        #map_with_airports = self.plot_airports(airport_data)

        # Save the map as an HTML file
        #map_with_airports.save('/Users/scottreinhardt/flasktropica/templates/airport_map1.html')
    """

    def parse(self, html):
        self.results.append(html)

    def to_csv(self):
        with open('proxies.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(self.results)

    # This splits the dewpoint and the temperature
    def splitTempDew(self, rawInput, tempordew):
        if(tempordew == "T"):
            # Convert to Farenheit
            return (float(rawInput[0]) * (5.0 / 9.0) + 32.0)
        elif(tempordew == "D"):
            # Convert to Farenheit
            return (float(rawInput[1]) * (5.0/9.0) + 32.0)

    def splitWind(self, rawInput, indicator):
        if(indicator == "Direction"):
            return rawInput[0]
        elif(indicator == "Speed"):
            return rawInput[1]
        elif(indicator == "Gust"):
            return rawInput[3]

    # raw input is an array with cloud condition and height
    def splitcloudHeights(self, rawinput):
        # Can get inputs of ['FEW', 2800, 'FEW', 40000]
        for i in range(0, len(rawInput) - 2):
            return rawInput[i] + " Clouds at " + str(rawInput[i + 1]) + " Feet"

    # Check if a String is a Float Number in Python
    def generate_random_temperature(self, airport, metDict):
        #print(metDict)
        if airport in metDict:
            return airport

    def plot_airports1(self, airport_data, metDict):
        # Create a map centered around the first airport
        map_center = [airport_data[0]['lat'], airport_data[0]['lon']]
        m = folium.Map(location=map_center, zoom_start=5)
        #aptnamesUSA = self.createStaticDict(750000)
        # Add markers for each airport
        for icao, data in self.superDict.items():
            lat, lon, name, state, country = data
            temp = 0
            heat_map = []
            name = airport['name']
            lat = airport['lat']
            lon = airport['lon']
            #print(generate_random_temperature(name))
            if self.generate_random_temperature(name, metDict):
                temp = metDict.get(name)
                #print(temp[5][0])
                #print(name)
                #print(temp[-1])
                try:

                    folium.Circle(
                        location=(airport["lat"], airport["lon"]),
                        radius=10,  # Radius of the circle
                        color='blue',
                        fill=True,
                        fill_color='blue',
                        popup=f"{airport['name']}: {airport['temp']}°F",  # Displaying temperature in popup
                    ).add_to(m)
                    #circle_color = pick_color(str(float(metDict.get(name)[4][0] * (9.0/5.0)) + 32.0))
                    temperature = temp[5][0]
                    #print(temperature)
                    color1 = 'blue'
                    if(temperature >= 100.0):
                        color1 = 'pink'
                    elif(temperature >= 95.0 and temperature < 100.0):
                        color1 = 'darkpurple'
                    elif(temperature >= 90.0 and temperature < 95.0):
                        color1 = 'purple'
                    elif(temperature >= 85.0 and temperature < 90.0):
                        color1 = 'darkred'
                    elif(temperature >= 80.0 and temperature < 85.0):
                        color1 = 'red'
                    elif(temperature >= 75.0 and temperature < 80.0):
                        color1 = 'red'
                    elif(temperature >= 70.0 and temperature < 75.0):
                        color1 = 'orange'
                    elif(temperature >= 65.0 and temperature < 70.0):
                        color1 = 'yellow'
                    elif(temperature >= 60.0 and temperature < 65.0):
                        color1 = 'beige'
                    elif(temperature >= 55.0 and temperature < 60.0):
                        color1 = 'brown'
                    elif(temperature >= 50.0 and temperature < 55.0):
                        color1 = 'lightblue'
                    elif(temperature >= 45.0 and temperature < 50.0):
                        color1 = 'blue'
                    elif(temperature <= 45.0):
                        color1 = 'darkblue'
                    else:
                        color1 = 'black'
                    folium.Circle(
                        location=(airport["lat"], airport["lon"]),
                        radius=2000,  # Radius of the circle
                        color=color1,
                        fill=True,
                        opacity=1,
                        fill_color=color1,
                        popup=f"{airport['name']}: {metDict.get(name)}°F",  # Displaying temperature in popup
                        html='<div style="font-size: 30pt">%s</div>' % temperature,
                    ).add_to(m)
                    """
                    """
                    folium.map.Marker(
                        [airport["lat"], airport["lon"]],
                        icon=DivIcon(
                            icon_size=(150, 36),
                            icon_anchor=(0, 0),
                            html=f"{airport['name']}: {str(float(metDict.get(name)[4][0]))}°F",
                        )
                    ).add_to(m)
                     """
                     """
                    marker_text1 = f"{name}<br>Temperature: {round(((temp[4][0] * (9.0/5.0)) + 32.0),2)}°F<br>Dewpoint: {round(((temp[4][1] * (9.0/5.0)) + 32.0), 2)}°F"
                    #print(temp[4][1])
                except:
                    market_text1 = f"No Data"
            else:
                None
            #heat_map.append(temp)
            #marker = folium.Marker(location=[lat, lon], popup=marker_text)

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

        # Display the map
        return m

    #fsgd
    """
    """
    def read_data(self):
        from pyairports.airports import Airports
        airports = Airports()
        print(airports)
        aptnamesMA = {}
        v = 0
        url = ""
        text_to_add = ""
        for key in range(0,aptnamesMA):
            if(key == 0):
                text_to_add = aptNames[key]
                print(key)
            else:
                text_to_add = "%2" + key
            # Loop through all the airport ICAOs in aptNames and add them to the url
            url = "https://aviationweather.gov/cgi-bin/data/metar.php?ids="+text_to_add+"&hours=0&order=id%2C-obs&sep=true"
            v+=1
        final_request_url = url
        #print(final_request_url)
        from pyairports.airports import Airports
        airports = Airports()
        #print(airports)
        #url24HourHistory = "https://tgftp.nws.noaa.gov/weather/current/" + key['name'] + ".html"
        #r = requests.get(url, headers=header)
        response = urllib.request.urlopen(final_request_url).read()
        METRARtoSTRING = response.decode('UTF-8')
        #print(response)
    """
    #https://aviationweather.gov/data/cache/metars.cache.xml.gz
    """
    def process_data(self):
        superDict1 = {}
        with open('/Users/scottreinhardt/flasktropica/airports.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                icao = row['icao_code']
                if icao and row['latitude_deg'] and row['longitude_deg'] and self.distanceFinder(lat1, lon1, lat2, lon2, 1000000):  # Ensure the ICAO code and coordinates are not empty
                    try:
                        lat = float(row['latitude_deg'])
                        lon = float(row['longitude_deg'])
                        name = row['name']
                        #print(name)
                        state = row['iso_region'].split('-')[1] if '-' in row['iso_region'] else ''
                        country = row['iso_country']
                    except:
                        lat = float(0.0)
                        lon = float(0.0)
                        name = "name_not_found"
                        #print(name)
                        state = row['iso_region'].split('-')[1] if '-' in row['iso_region'] else ''
                        country = row['iso_country']
                    superDict1[icao] = [lat, lon, name, state, country]
        return superDict1
    """
    """
    def generate_map(self):
        # Center the map on the USA
        m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

        for icao, data in superDict.items():
            lat, lon = data
            folium.Marker(
                location=[lat, lon],
                popup=f"{name}, {state}, {country} ({icao})",
                icon=folium.Icon(icon='cloud')
            ).add_to(m)

        # Save the map to an HTML file
        m.save('templates/map.html')
    """
    """
    def run(self):
        # Define Central Point
        lat1 = 42.3656
        lon1 = -71.0096
        superDict1 = {}
        aptnamesUSA1 = {}
        with open('/Users/scottreinhardt/flasktropica/airports.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            lat = 0.0
            lon = 0.0
            name = ""
            for row in reader:
                #print(row)
                icao = row['ident']
                #print(icao)
                # and self.distanceFinder(lat1, lon1, float(row['latitude_deg']), float(row['longitude_deg']), 500000)
                if icao[0][0] =='K' and row['latitude_deg'] and row['longitude_deg'] and self.distanceFinder(lat1, lon1, float(row['latitude_deg']), float(row['longitude_deg']), 2500):  # Ensure the ICAO code and coordinates are not empty
                    try:
                        lat = float(row['latitude_deg'])
                        lon = float(row['longitude_deg'])
                        name = icao
                        #print(name)
                        #state = row['iso_region'].split('-')[1] if '-' in row['iso_region'] else ''
                        #country = row['iso_country']
                        superDict1[icao] = [lat, lon]
                    except:
                        lat = float(0.0)
                        lon = float(0.0)
                        name = "name_not_found"
                        #print(name)
                        #state = row['iso_region'].split('-')[1] if '-' in row['iso_region'] else ''
                        #country = row['iso_country']
                    #superDict1[icao] = [lat, lon]

        #print(self.read_data())
        #print(self.process_data)

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
                      "KBDL":[41.93806, 72.6825]}

        metDict = {}
        p = 0
        # average time for 1 airport to scrape
        avg = 0
        #aptnamesUSA is a list filled with mini dicts with one key for each station
        #aptnamesUSA = self.createStaticDict(1000000)
        aptnamesUSA1 = superDict1


        # Define blank dict to assign pruined down icaos to
        complatibleApts = {}
        # shorten dictionary
        lat1 = 42.3656
        lon1 = -71.0096
        # apply law of cosines to find airports 100 miles from current location
        # If it is within 100 miles put in dict otherwise it is out of range
        # The distance is measured in meters
        for key2 in suerDict1:
            if self.distanceFinder(lat1, lon1, lat2, lon2, 250000):
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
    """
    """
        text_to_add_arr = []
        counter = 0
        for key1 in superDict1:
            if(counter == 0):
                text_to_add_arr.append(key1)
                #print(key)
            elif(counter >= 1):
                text_to_add_arr.append("%2" + key1)
            counter = counter + 1
            # Loop through all the airport ICAOs in aptNames and add them to the url
        # change the text in the array and concatenate the strings inside into one big string
        text_to_add = ''.join(text_to_add_arr)
        url = "https://aviationweather.gov/cgi-bin/data/metar.php?ids="+text_to_add+"&hours=0&order=id%2C-obs&sep=true"
        final_request_url = url
        #response = urllib.request.urlopen(url).read()
        #print(response)
        print(superDict1.keys())
        print(final_request_url)
        for key in superDict1:
            # starts the timer
            start_time = time.time()
            metData = []
            #url = "https://w1.weather.gov/data/METAR/" + key['name'] + ".1.txt"

            #url = "https://aviationweather.gov/cgi-bin/data/metar.php?ids="KBOS%2C%2CKSYR%2CKBGR%2CKORH"&hours=0&order=id%2C-obs&sep=true
            #url = "https://aviationweather.gov/cgi-bin/data/metar.php?ids="+ str(icao) +"&hours=0&order=id%2C-obs&sep=true"
            #url24HourHistory = "https://tgftp.nws.noaa.gov/weather/current/" + key['name'] + ".html"
            #r = requests.get(url, headers=header)
            #response = urllib.request.urlopen(url).read()
            #print(response)
            #response11 = urllib.request.urlopen(url24HourHistory).read()
            #METRARtoSTRING1 = response11.decode('UTF-8')

            # Regular expression to find content inside parentheses
            #pattern = r'\(([^)]+)\)'

            # Find all matches
            #matches = re.findall(pattern, METRARtoSTRING1)
            #for match1 in matches:
            #    print(match1)
            #highPast6hours = matches[13]
            #lowPast6hours = matches[14]
            #highPast24Hours = matches[15]
            #lowPast24Hours = matches[16]
            #print(highPast24Hours)
            #print(lowPast24Hours)
            #print(highPast24Hours)
            #print(highPast24Hours)
            #arr24Hour = []
            # Print matches

            #for match in matches:
            #    try:
            #        arr24Hour.append(float(match))
            #        #print(float(match))

            #    except ValueError:
             #       None
            #highPast6hours = matches[0]
            #lowPast6hours = matches[1]
            #highPast24Hours = matches[2]
            #lowPast24Hours = matches[3]
            #subArr = []
            #for i in range(0,8):
            #    subArr.append(matches[i])

            #subarrays = []
            #for i in range(4, len(arr24Hour)):
            #    subarray = arr24Hour[i:i + 3]
            #    subarrays.append(subarray)

            #subarrays = split_into_subarrays(large_array)

            # Print the result
            #for subarray in arr24Hour:
            #    print(subarray)

            METRARtoSTRING = response.decode('UTF-8')
            # Find the start of the METAR
            METARstartpos = re.search('METAR', METRARtoSTRING)
            # Get rest of METAR
            data = METRARtoSTRING[METARstartpos.start():]
            arrayData = data.split(' ')
            metData.append(key['name'])
            #print(METRARtoSTRING)
            # Initialize variable
            WindDataArr = 0
            # Check 3rd digit for potential modifier
            if (not self.isAuto(arrayData[3])):
                metData.append(self.convertWind(arrayData[3], METRARtoSTRING))
            else:
                # perminantly shortens arrayData
                arrayData.pop(3)
                metData.append(self.convertWind(arrayData[3], METRARtoSTRING))

            visData = 0
            if(self.visibilityCheck(arrayData[4])):
                #Check to see if wind has variable direction over 60 degrees
                if(re.search(r'\d{3}\w\d{3}', arrayData[5])):
                    # If visibility is a field, return it
                    metData.append(self.getVisibility(arrayData[5]))
                else:
                    metData.append(self.getVisibility(arrayData[4]))
            else:
                # Insert No Visibility stated as none into the array
                metData.append(None)
            #self.mapster(airport_data, aptnamesUSA)
            metData.append(self.getConds(METRARtoSTRING))
            #print(cloudConds(METRARtoSTRING))
            metData.append(self.cloudConds(METRARtoSTRING))
            metData.append(self.getTempDew(METRARtoSTRING))
            metDict[key['name']] = metData
            #metData.append(highPast6hours)
            #metData.append(lowPast6hours)
            #metData.append(highPast24Hours)
            #metData.append(lowPast24Hours)
            # For testing purposes
            # Add i as key and metData as value to metDict
            #metDict['name'] = metData
            #print(metDict)
            # ends the timer
            end_time = time.time()
            total_time = end_time - start_time
            p = p + 1
            #avg = (avg + total_time) / p
            print("The Airport " + key['name'] + " has successfully been updated!")
            print("You are " + str((p / len(aptnamesUSA)) * 100) + "% complete! Now loading airport " + str(p) +" of " + str(len(aptnamesUSA)))
            print((total_time * len(aptnamesUSA)) - total_time)

            #print((avg * len(aptnamesUSA)))
            self.parse(metData)
            # Example airport data
            airport_data = [
                {'name': 'John F. Kennedy International Airport', 'lat': 40.6413, 'lon': -73.7781},
                {'name': 'Los Angeles International Airport', 'lat': 33.9416, 'lon': -118.4085},
                {'name': 'London Heathrow Airport', 'lat': 51.4700, 'lon': -0.4543},
                {'name': 'Tokyo Haneda Airport', 'lat': 35.5494, 'lon': 139.7798}
            ]

            # Plot the airports on a map
            map_with_airports = self.plot_airports(airport_data, metDict)

            # Save the map as an HTML file
            map_with_airports.save('airport_map2.html')
            webbrowser.open("airport_map2.html")
            #print(dynamicDict)
"""

if __name__ == "__main__":
    #scraper = MOSScraper()
    #scraper.run()
    #print(scraper.superDict)


