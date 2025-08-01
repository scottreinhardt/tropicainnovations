import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from openmeteo_sdk.Variable import Variable
"""
def get_weather_data(lat, lon):
    try:
        # Setup the Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "wind_speed_10m", "wind_direction_10m"],
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature",
                        "is_day", "precipitation", "rain", "showers", "surface_pressure",
                        "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        print(response)
        # Process hourly forecast
        hourly = response.Hourly()
        hourly_temperature_2m_f = hourly.Variables(0).ValuesAsNumpy()

        # Process current weather
        current = response.Current()
        print(current)
        current_weather_vars = {var.Variable(): var for var in map(lambda i: current.Variables(i), range(current.VariablesLength()))}
        print(current_weather_vars)
        current_weather = {
            "temperature": current_weather_vars.get(Variable.temperature, None).Value() if current_weather_vars.get(Variable.temperature) else None,
            "relative_humidity": current_weather_vars.get(Variable.relative_humidity, None).Value() if current_weather_vars.get(Variable.relative_humidity) else None,
            "apparent_temperature": current_weather_vars.get(Variable.apparent_temperature, None).Value() if current_weather_vars.get(Variable.apparent_temperature) else None,
            "is_day": current_weather_vars.get(Variable.is_day, None).Value() if current_weather_vars.get(Variable.is_day) else None,
            "precipitation": current_weather_vars.get(Variable.precipitation, None).Value() if current_weather_vars.get(Variable.precipitation) else None,
            "rain": current_weather_vars.get(Variable.rain, None).Value() if current_weather_vars.get(Variable.rain) else None,
            "showers": current_weather_vars.get(Variable.showers, None).Value() if current_weather_vars.get(Variable.showers) else None,
            "surface_pressure": current_weather_vars.get(Variable.surface_pressure, None).Value() if current_weather_vars.get(Variable.surface_pressure) else None,
            "wind_speed_10m": current_weather_vars.get(Variable.wind_speed, None).Value() if current_weather_vars.get(Variable.wind_speed) else None,
            "wind_direction_10m": current_weather_vars.get(Variable.wind_direction, None).Value() if current_weather_vars.get(Variable.wind_direction) else None,
            "wind_gusts_10m": current_weather_vars.get(Variable.wind_gusts, None).Value() if current_weather_vars.get(Variable.wind_gusts) else None,
            "time": current.Time(),
            "latitude": response.Latitude(),
            "longitude": response.Longitude(),
            "elevation": response.Elevation()
        }
        print(current_weather)

        # Create hourly data
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly_temperature_2m_f
        }
        print(hourly_data)
"""



"""
import pandas as pd
import requests_cache
from openmeteo_requests import Client, Hourly, Daily, Current, Variable
from retry_requests import retry

def get_weather_data(lat, lon):
    try:
        # Setup the Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = Client(session=retry_session)

        # API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "wind_speed_10m", "wind_direction_10m"],
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature",
                        "is_day", "precipitation", "rain", "showers", "surface_pressure",
                        "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        print(response)
        # Process hourly forecast
        hourly = response.Hourly()
        hourly_temperature_2m_f = hourly.Variables(0).ValuesAsNumpy()

        # Process current weather
        current = response.Current()
        print(current)
        current_weather_vars = {var.Variable(): var for var in map(lambda i: current.Variables(i), range(current.VariablesLength()))}
        print(current_weather_vars)

        current_weather = {}
        for key, var in current_weather_vars.items():
            if var is not None:
                try:
                    value = var.Value()
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except ValueError:
                            pass #If it cannot be converted leave as string.
                    current_weather[key] = value
                except (ValueError, TypeError) as e:
                    print(f"Error processing {key}: {e}")
                    current_weather[key] = None
            else:
                current_weather[key] = None

        print(current_weather)

        # Create hourly data
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly_temperature_2m_f
        }
        print(hourly_data)
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        current_weather.update(hourly_data)
        print(current_weather)

        return current_weather
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
"""

def get_weather_data(lat, lon):
    try:
        # Setup the Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation", "wind_speed_10m", "wind_direction_10m"],
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature",
                        "is_day", "precipitation", "rain", "showers", "surface_pressure",
                        "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        #print(response)
        # Process hourly forecast
        hourly = response.Hourly()
        hourly_temperature_2m_f = hourly.Variables(0).ValuesAsNumpy()

        # Process current weather
        current = response.Current()
        #print(current)
        current_weather_vars = {var.Variable(): var for var in map(lambda i: current.Variables(i), range(current.VariablesLength()))}
        #print(current_weather_vars)
        """
        current_weather = {
            "temperature": current_weather_vars.get(Variable.temperature, None).Value() if current_weather_vars.get(Variable.temperature) else None,
            "relative_humidity": current_weather_vars.get(Variable.relative_humidity, None).Value() if current_weather_vars.get(Variable.relative_humidity) else None,
            "apparent_temperature": current_weather_vars.get(Variable.apparent_temperature, None).Value() if current_weather_vars.get(Variable.apparent_temperature) else None,
            "is_day": current_weather_vars.get(Variable.is_day, None).Value() if current_weather_vars.get(Variable.is_day) else None,
            "precipitation": current_weather_vars.get(Variable.precipitation, None).Value() if current_weather_vars.get(Variable.precipitation) else None,
            "rain": current_weather_vars.get(Variable.rain, None).Value() if current_weather_vars.get(Variable.rain) else None,
            "showers": current_weather_vars.get(Variable.showers, None).Value() if current_weather_vars.get(Variable.showers) else None,
            "surface_pressure": current_weather_vars.get(Variable.surface_pressure, None).Value() if current_weather_vars.get(Variable.surface_pressure) else None,
            "wind_speed_10m": current_weather_vars.get(Variable.wind_speed, None).Value() if current_weather_vars.get(Variable.wind_speed) else None,
            "wind_direction_10m": current_weather_vars.get(Variable.wind_direction, None).Value() if current_weather_vars.get(Variable.wind_direction) else None,
            "wind_gusts_10m": current_weather_vars.get(Variable.wind_gusts, None).Value() if current_weather_vars.get(Variable.wind_gusts) else None,
            "time": current.Time(),
            "latitude": response.Latitude(),
            "longitude": response.Longitude(),
            "elevation": response.Elevation()
        }
        """
        current_weather = {
            key: (var.Value() if var is not None else None)
            for key, var in current_weather_vars.items()
        }

        #print(current_weather)

        # Create hourly data
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly_temperature_2m_f
        }
        #print(hourly_data)
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        # Combine current and hourly weather data
        """
        weather_data = {
            "current_weather": current_weather,
            "hourly_forecast": hourly_dataframe.to_json(orient='records', date_format='iso')
        }
        """

        current_weather.update(hourly_data)
        print(current_weather)

        return current_weather
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#get_weather_data(42.1968, -70.7687)
"""
def get_weather_data(lat, lon):
    try:
        # Setup the Open-Meteo API client
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "current": ["temperature_2m", "relative_humidity_2m"],
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)
        # Process the response
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m_f = hourly.Variables(0).ValuesAsNumpy()
        #print(hourly_temperature_2m_f)
        current = response.Current()
        current_variables = list(map(lambda i: current.Variables(i), range(0, current.VariablesLength())))

        current_temperature_2m = next(filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, current_variables))
        current_relative_humidity_2m = next(filter(lambda x: x.Variable() == Variable.relative_humidity and x.Altitude() == 2, current_variables))

        # Create a lookup dictionary for current weather variables
        current_weather_vars = {var.Variable(): var for var in current_variables}
        current_weather = {
            "temperature": current_temperature_2m.Value(),
            "relative_humidity": current_relative_humidity_2m.Value(),
            "time": current.Time(),
            "latitude": response.Latitude(),
            "longitude": response.Longitude(),
            "elevation": response.Elevation()
        }
        #print(current_weather)
        # ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "rain", "showers", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"]
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        hourly_data["temperature_2m"] = hourly_temperature_2m_f
        hourly_dataframe = pd.DataFrame(data=hourly_data)

        print("Hourly data processed:", hourly_dataframe.head())
        #print("Weather JSON:", weather_json)
        # Combine current and hourly weather data
        weather_json = hourly_dataframe.to_json(orient='records', date_format='iso')
        weather_data = {
            "current_weather": current_weather,
            "hourly_forecast": weather_json
        }
        #print(weather_data)
        return weather_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
"""
#get_weather_data(42.1968,-70.7687)
