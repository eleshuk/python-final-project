from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openmeteo_requests
import requests_cache
import requests
from retry_requests import retry
import geocoder 
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from temp_analysis.temp_analysis import run_full_analysis

def main():
    print("Welcome to this weather analysis tool. It will help you learn about the weather in your area")
    farm_data = get_farm_input()  # Get user location and start date for weather analysis
    location = locationData(farm_data)
    municipality = location.get_municipality()
    print(f"It looks like you're located in the municipality of {municipality}. Enjoy these details about the weather in your area:")
    
    weather = weatherData(farm_data)  # Fetch weather data
    daily_weather_df = weather.get_weather_data()  # Get DataFrame of weather data
    weather.export_weather_data(export=True)  # Optionally export the data
    
    # Precipitation data analysis
    precipitation_data_avg(daily_weather_df)
    precip_data = precipitation_data_avg(daily_weather_df)
    precipitation_quick_stats(precip_data)
    
    # Temperature data analysis
    run_full_analysis(daily_weather_df)

import geocoder 
def get_farm_input():
    """
    Collect and validate GPS coordinates from the user's IP, start date, and end date.
    Returns a dictionary with the validated inputs.
    """
    # Step 1: Retrieve GPS coordinates using geocoder
    print("Fetching GPS coordinates from your IP address...")
    g = geocoder.ip('me')
    if g.ok:
        # Extract latitude and longitude if the geocoder is successful
        lat, long = g.latlng
        print(f"Detected latitude: {lat}, longitude: {long}")
    else:
        # Raise an exception if geocoder fails to retrieve coordinates
        raise Exception("Unable to retrieve GPS coordinates from IP address.")

    # Step 2: Prompt user for the start date and validate input
    while True:
        try:
            start_date = input("Enter start date of weather analysis (YYYY-MM-DD): ")
            # Validate the date format
            datetime.strptime(start_date, "%Y-%m-%d")
            break
        except ValueError:
            # Inform the user about the invalid format and prompt again
            print("Invalid date format. Please use YYYY-MM-DD.")

    print("The end date for analysis will be today's date")

    # Step 4: Return the collected and validated inputs
    return {
        "latitude": lat,
        "longitude": long,
        "start_date": start_date
    }

# Get location data from Geo API
class locationData:
    def __init__(self, inputs):
        # Initialize instance attributes
        self.latitude = inputs['latitude']
        self.longitude = inputs['longitude']
        
        # Set up the GEO API client with caching and retries
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.base_url = "https://json.geoapi.pt/gps"

    # make api request fpr latitude and longitude
    def get_location_data(self):
        # Make the API request
        url = f"{self.base_url}/{self.latitude},{self.longitude}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}"
        
    # get freguesia name from json
    def get_municipality(self):
        result = self.get_location_data()['concelho']
        return result

# Get weather data from API
class weatherData:
    def __init__(self, inputs):
        # Initialize instance attributes
        self.latitude = inputs['latitude']
        self.longitude = inputs['longitude']
        self.start_date = inputs['start_date']
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
        
 
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}

        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["precipitation_sum"] = daily_precipitation_sum

        daily_dataframe = pd.DataFrame(data=daily_data)

        # # Format and clean the DataFrame
        daily_dataframe['Date'] = daily_dataframe['date'].dt.strftime('%Y-%m-%d')
        daily_dataframe = daily_dataframe.drop(columns=['date'])
        daily_dataframe.columns = ['TemperatureMax', 'TemperatureMin', 'Precipitation', 'Date']
        # Reorder columns
        daily_dataframe = daily_dataframe[['Date','TemperatureMax', 'TemperatureMin', 'Precipitation']]

        # # Drop rows with all NA values in specific columns
        columns_to_check = ['TemperatureMax', 'TemperatureMin', 'Precipitation']
        daily_dataframe = daily_dataframe.dropna(subset=columns_to_check, how='all')
        
        float32_columns = daily_dataframe.select_dtypes(include=['float32']).columns
        daily_dataframe[float32_columns] = daily_dataframe[float32_columns].astype('float64').round(1)
        daily_dataframe = daily_dataframe.reset_index(drop=True)

        return daily_dataframe
    
    # Option to output weather data as a .csv
    def export_weather_data(self, export=False):
        if export:
            weather_data = self.get_weather_data()
            # Output to CSV

            print("Please use the GUI to select a destination for your .csv download")
            
            # Hide the root tkinter window
            root = tk.Tk()
            root.withdraw()
            # Ask the user to select a directory
            output_path = filedialog.askdirectory(title="Select Output Directory")
            
            if output_path:
                output_dir = Path(output_path)
                print(f"Output path set to: {output_dir}")

                # Define the full file path (directory + file name)
                output_file = output_dir / "weather_data.csv"

                # Save the data to the specified file
                weather_data.to_csv(output_file, index=False)
                print(f"File saved to: {output_file}")
            else:
                print("No directory selected.")
        else:
            pass


# Analyze precipitation data
def precipitation_data_avg(data):
    # Convert the 'date' column to datetime
    data['Date'] = pd.to_datetime(data['Date'])
    # Option for rolling window
    date_range = data['Date'].max() - data['Date'].min()

    # Get the number of days from timedelta
    num_days = date_range.days
    # print("Date range is: " + str(num_days) + " days")

    if num_days <= 14:
        # print("Window is 3")
        rolling_average = data['Precipitation'].rolling(window=3, min_periods=1).mean()
    elif num_days > 14 and num_days <=60:
        # print("Window is 7")
        rolling_average = data['Precipitation'].rolling(window=7, min_periods=1).mean()
    elif num_days > 60:
        # print("Window is 30")
        rolling_average = data['Precipitation'].rolling(window=30, min_periods=1).mean()
    
    # ra_df = pd.DataFrame(rolling_average)
    data['Rolling_Average'] = rolling_average
    
    # Drop temperature related columns
    # Dropping specific columns
    columns_to_drop = ['TemperatureMax', 'TemperatureMin']
    df_precip = data.drop(columns=columns_to_drop)

    return df_precip

# Precipitation quickstats
def precipitation_quick_stats(data):
    # Calculate additional stats
    # Get max precipitation
    max_precipitation = data['Precipitation'].max()
    # Get min precipitation
    min_precipitation = data['Precipitation'].min()
    # Get date with max precip
    day_most_rain = data.loc[data['Precipitation'].idxmax(), 'Date']
    # get date with min precip
    day_least_rain = data.loc[data['Precipitation'].idxmin(), 'Date']
    # Return results as a dictionary
    stats =  {
        'max_precipitation': max_precipitation,
        'min_precipitation': min_precipitation,
        'day_most_rain': day_most_rain,
        'day_least_rain': day_least_rain
    }
    # Convert to df
    stats_df = pd.DataFrame([stats])
    print("Precipitation quick stats:")
    print(stats_df)


if __name__ == "__main__":
    main()
