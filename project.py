from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime

# def main():
#     farm_data = get_farm_input()
#     print("Collected inputs:", farm_data)

def get_farm_input():
    """
    Collect and validate latitude, longitude, start date, and end date from the user.
    Returns a dictionary with the validated inputs.
    """
    while True:
        try:
            lat = float(input("Enter latitude (between -90 and 90): "))
            if not -90 <= lat <= 90:
                raise ValueError("Latitude must be between -90 and 90.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    while True:
        try:
            long = float(input("Enter longitude (between -180 and 180): "))
            if not -180 <= long <= 180:
                raise ValueError("Longitude must be between -180 and 180.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    while True:
        try:
            start_date = input("Enter start date (YYYY-MM-DD): ")
            datetime.strptime(start_date, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    while True:
        try:
            end_date = input("Enter end date (YYYY-MM-DD): ")
            datetime.strptime(end_date, "%Y-%m-%d")
            if end_date < start_date:
                raise ValueError("End date must not be earlier than start date.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    return {
        "latitude": lat,
        "longitude": long,
        "start_date": start_date,
        "end_date": end_date,
    }

# Get weather data from API
# Get user inputs
user_inputs = get_farm_input()

def get_weather_data(inputs):
    # If inputs is going to be used multiple times throughout the code, then put it outside of get_weather_data
    # inputs = get_farm_input()
    lat = inputs['latitude']
    long = inputs['longitude']
    start_date = inputs['start_date']
    end_date = inputs['end_date']

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
    }
    # Make the API request
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
    
    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["TemperatureMax"] = daily_temperature_2m_max
    daily_data["TemperatureMin"] = daily_temperature_2m_min
    daily_data["Precipitation"] = daily_precipitation_sum
    
    daily_dataframe = pd.DataFrame(data = daily_data)
    # Convert date to date format (not datetime)
    daily_dataframe['Date'] = daily_dataframe['date'].dt.strftime('%Y-%m-%d')
    daily_dataframe = daily_dataframe.drop(columns=['date'])

    # print("collected API data")

    return daily_dataframe

'''
STILL NEEDS TESTING ONCE DF IS READY
input: a dataframe of weather across a date range, for a specific location
output: plot of max temperature, min temperature and precipitation
'''
# Get weather df to pass to this plot
# Leave outside of function for now since this data could be used in other functions
weather_df = get_weather_data(inputs = user_inputs)

def weather_data_plot(weather_df):
    # create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(weather_df["Date"], weather_df["TemperatureMax"], label="TemperatureMax")
    plt.plot(weather_df["Date"], weather_df["TemperatureMin"], label="TemperatureMin")
    # plt.plot(weather_df["Date"], weather_df["Precipitation"], label="Precipitation")
    
    # customise and show the plot
    plt.xlabel("Date")
    plt.ylabel("Temperature (C)")
    plt.xticks(rotation=45)
    plt.show()
    return 'Plot successfully created'

weather_data_plot(weather_df=weather_df)

# if __name__ == "__main__":
#     main()
