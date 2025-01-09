from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
import openmeteo_requests
import requests_cache
from retry_requests import retry


def main():
    farm_data = get_farm_input()
    print("Collected inputs:", farm_data)
    weather = weatherData(farm_data) 
    daily_weather_df = weather.get_weather_data()
    weather_data_plot(weather_df=daily_weather_df)

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
class weatherData:
    def __init__(self, inputs):
        # Initialize instance attributes
        self.latitude = inputs['latitude']
        self.longitude = inputs['longitude']
        self.start_date = '2023-06-01'
        self.end_date = date.today()
        
        # Set up the Open-Meteo API client with caching and retries
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=self.retry_session)
        self.url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    def get_weather_data(self):
        # Prepare request parameters
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
        }
        
        # Make the API request
        responses = self.client.weather_api(self.url, params=params)
        response = responses[0]

        # Process daily data
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
        
        # Create a DataFrame with the processed data
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), utc=True),  # No unit="s" needed for ISO strings
                end=pd.to_datetime(daily.TimeEnd(), utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ),
            "TemperatureMax": daily_temperature_2m_max,
            "TemperatureMin": daily_temperature_2m_min,
            "Precipitation": daily_precipitation_sum
        }
        daily_dataframe = pd.DataFrame(data=daily_data)

        # Format and clean the DataFrame
        daily_dataframe['Date'] = daily_dataframe['date'].dt.strftime('%Y-%m-%d')
        daily_dataframe = daily_dataframe.drop(columns=['date'])

        # Drop rows with all NA values in specific columns
        columns_to_check = ['TemperatureMax', 'TemperatureMin', 'Precipitation']
        daily_dataframe = daily_dataframe.dropna(subset=columns_to_check, how='all')
        
        return daily_dataframe

'''
input: a dataframe of weather across a date range, for a specific location
output: plot of max temperature, min temperature and precipitation
'''

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


if __name__ == "__main__":
    main()
