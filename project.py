from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openmeteo_requests
import requests_cache
import requests
from retry_requests import retry
import geocoder 
from location_data.location_data import locationData
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from weather_analysis.precipitation_analysis import precipitation_data_avg, precipitation_quick_stats
from temp_analysis.temp_analysis import run_full_analysis
# from plot_toggling.plot import run_weather_plot_viewer



def main():
    farm_data = get_farm_input()  # Collect user input
    weather = weatherData(farm_data)  # Fetch weather data
    daily_weather_df = weather.get_weather_data()  # Get DataFrame of weather data

    if daily_weather_df is None or daily_weather_df.empty:
        print("No weather data was retrieved. Please check your inputs or API connectivity.")
        return

    weather.export_weather_data(export=False)  # Optionally export the data

# Analyze temperature data
    run_full_analysis(daily_weather_df)

    # Precipitation data
    precipitation_data_avg(daily_weather_df)
    precip_data = precipitation_data_avg(daily_weather_df)
    precipitation_quick_stats(precip_data)
    location = locationData(farm_data)
    freguesia = location.get_freguesia()
    print(f"It looks like you're located in the freguesia of {freguesia}. Enjoy this weather plot of your area!")
    weather_data_plot(weather_df=daily_weather_df)

    # Location
    print("\n### Location Information ###")
    try:
        location = locationData(farm_data)
        freguesia = location.get_freguesia()
        if freguesia:
            print(f"It looks like you're located in the freguesia of {freguesia}. Enjoy this weather plot of your area!")
        else:
            print("Could not determine the freguesia for your location.")
    except Exception as e:
        print(f"Failed to retrieve location data: {e}")


    # # Adicionar interface gráfica para exibir os gráficos
    # print("\n### Launching Weather Plot Viewer ###")
    # try:
    #     run_weather_plot_viewer(daily_weather_df)
    # except Exception as e:
    #     print(f"Failed to launch weather plot viewer: {e}")

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
            start_date = input("Enter start date (YYYY-MM-DD): ")
            # Validate the date format
            datetime.strptime(start_date, "%Y-%m-%d")
            break
        except ValueError:
            # Inform the user about the invalid format and prompt again
            print("Invalid date format. Please use YYYY-MM-DD.")

    # Step 3: Prompt user for the end date and validate input
    # while True:
    #     try:
    #         end_date = input("Enter end date (YYYY-MM-DD): ")
    #         # Validate the date format
    #         datetime.strptime(end_date, "%Y-%m-%d")
    #         # Check if the end date is not earlier than the start date
    #         if end_date < start_date:
    #             raise ValueError("End date must not be earlier than start date.")
    #         break
    #     except ValueError as e:
    #         # Inform the user about the invalid input and prompt again
    #         print(f"Invalid input: {e}")

    # Step 4: Return the collected and validated inputs
    return {
        "latitude": lat,
        "longitude": long,
        "start_date": start_date
        # "end_date": end_date,
    }

# Get weather data from API
class weatherData:
    def __init__(self, inputs):
        # Initialize instance attributes
        self.latitude = inputs['latitude']
        self.longitude = inputs['longitude']
        # self.start_date = '2023-06-01'
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


'''
input: a dataframe of weather across a date range, for a specific location
output: plot of max temperature, and min temperature
'''
def weather_data_plot(weather_df):
    # create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(weather_df["Date"], weather_df["TemperatureMax"], label="TemperatureMax")
    ax.plot(weather_df["Date"], weather_df["TemperatureMin"], label="TemperatureMin")
    
    # Set the x-axis to display a limited number of dates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=20))
    
    # Rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    # customise and show the plot
    plt.xlabel("Date")
    plt.ylabel("Temperature (C)")
    plt.tight_layout()
    plt.show()
    return 'Plot successfully created'

if __name__ == "__main__":
    main()
