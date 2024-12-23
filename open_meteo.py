import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


def get_weather(latitude: list, longitude: list, forecast_days=7):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "surface_pressure", "visibility", "wind_speed_10m"],
        "forecast_days": forecast_days
    }
    responses = openmeteo.weather_api(url, params=params)

    all_df = []
    for i in range(len(longitude)):

        response = responses[i]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
        hourly_surface_pressure = hourly.Variables(3).ValuesAsNumpy()
        hourly_visibility = hourly.Variables(4).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left")
        }
        hourly_data["temperature"] = hourly_temperature_2m
        hourly_data["relative_humidity"] = hourly_relative_humidity_2m
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["surface_pressure"] = hourly_surface_pressure
        hourly_data["visibility"] = hourly_visibility
        hourly_data["wind_speed"] = hourly_wind_speed_10m

        all_df.append(pd.DataFrame(data = hourly_data))

    return all_df


if __name__ == '__main__':
    df = get_weather([10, 15], [10, 15], 16)
    print(df)
