from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from project import weatherData, get_farm_input
from plotnine import ggplot, aes, geom_line, geom_point, geom_hline, theme_minimal, labs, ggtitle, scale_color_manual, element_text
import pandas as pd

def main():
    farm_data = get_farm_input()
    weather = weatherData(farm_data)
    weather_data = weather.get_weather_data()
    result = precipitation_data_avg(data=weather_data)
    print(result)

# Estimate switch from summer to winter and vice versa
# Extract temperature and date
def get_growing_seasons(weather_data):
    dates = weather_data['Date']
    temperatures = weather_data['TemperatureMax']
    # Find peaks (summer peaks) and valley (winter valley)
    peaks, _ = find_peaks(temperatures)          # Find summer peaks
    valleys, _ = find_peaks(-temperatures)       # Find winter valleys (negative for inversion)

    # Get peak and valley temperatures
    summer_peaks = temperatures[peaks]
    winter_valley = temperatures[valleys].min()  # Get the lowest valley

    # Calculate the midpoint temperature
    T_mid = (summer_peaks.max() + winter_valley) / 2
    # Calculate whether the temperature is above the midpoint
    above_mid = temperatures >= T_mid
    # Detect where the above_mid condition changes (True -> False or False -> True)
    above_mid_diff = above_mid.diff().fillna(0).astype(bool)  # Handle NaN and ensure boolean
    # Find indices of transitions
    transition_indices = above_mid_diff[above_mid_diff].index  # Indices where the condition changes
    # Extract the corresponding dates for the transitions
    transition_dates = dates.loc[transition_indices]

    print(transition_dates)  # Display the transition dates


    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(dates, temperatures, label='Temperature')
    plt.scatter(dates[peaks], summer_peaks, color='red', label='Summer Peaks')
    plt.scatter(dates[valleys], temperatures[valleys], color='blue', label='Winter Valley')
    plt.axhline(T_mid, color='green', linestyle='--', label=f'Midpoint Temp ({T_mid:.2f})')
    plt.scatter(transition_dates, temperatures[transition_dates.index], color='purple', label='Transitions')
    plt.legend()
    plt.title('Temperature Over Time with Transitions')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.grid()
    plt.show()


# get_growing_seasons(weather_data)


# Option to output weather data as a .csv
# def export_weather_data():
#     weather_data = weather.get_weather_data()
#     # Output to CSV
#     output_path = "/Users/eleshuk/Library/CloudStorage/GoogleDrive-eleshuk@gmail.com/.shortcut-targets-by-id/1XNkQR60z1T7WELqvqkvZchRrVWQpCzvs/data_science_project/03_python/data/weather_data.csv"
#     print(output_path)
#     weather_data.to_csv(output_path, index=False)


# Analyze precipitation data
def precipitation_data_avg(data):
    # Convert the 'date' column to datetime
    data['Date'] = pd.to_datetime(data['Date'])
    # Option for rolling window
    date_range = data['Date'].max() - data['Date'].min()

    # Get the number of days from timedelta
    num_days = date_range.days
    print("Date range is: " + str(num_days) + " days")

    if num_days <= 14:
        print("Window is 3")
        rolling_average = data['Precipitation'].rolling(window=3, min_periods=1).mean()
    elif num_days > 14 and num_days <=60:
        print("Window is 7")
        rolling_average = data['Precipitation'].rolling(window=7, min_periods=1).mean()
    elif num_days > 60:
        print("Window is 30")
        rolling_average = data['Precipitation'].rolling(window=30, min_periods=1).mean()
    
    # ra_df = pd.DataFrame(rolling_average)
    data['Rolling_Average'] = rolling_average
    
    # Drop temperature related columns
    # Dropping specific columns
    columns_to_drop = ['TemperatureMax', 'TemperatureMin']
    df_precip = data.drop(columns=columns_to_drop)

    return df_precip

def precipitation_quick_stats(data):
    # Calculate additional stats
    max_precipitation = data['Precipitation'].max()
    min_precipitation = data['Precipitation'].min()
    day_most_rain = data.loc[data['Precipitation'].idxmax(), 'Date']
    day_least_rain = data.loc[data['Precipitation'].idxmin(), 'Date']
        # Return results as a dictionary
    return {
        'max_precipitation': max_precipitation,
        'min_precipitation': min_precipitation,
        'day_most_rain': day_most_rain,
        'day_least_rain': day_least_rain
    }

if __name__ == "__main__":
    main()