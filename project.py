from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

def main():
    farm_data = get_farm_input()
    print("Collected inputs:", farm_data)

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

'''
STILL NEEDS TESTING ONCE DF IS READY
input: a dataframe of weather across a date range, for a specific location
output: plot of max temperature, min temperature and precipitation
'''
def weather_data_plot(weather_df):
    # create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(weather_df["Date"], weather_df["TemperatureMax"], label="TemperatureMax")
    plt.plot(weather_df["Date"], weather_df["TemperatureMin"], label="TemperatureMin")
    plt.plot(weather_df["Date"], weather_df["Precipitation"], label="Precipitation")
    
    # customise and show the plot
    plt.xlabel("Date")
    plt.ylabel("Temperature")
    plt.xticks(rotation=45)
    plt.show()
    return 'Plot successfully created'

if __name__ == "__main__":
    main()
