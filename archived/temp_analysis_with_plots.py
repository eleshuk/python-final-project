import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

class TemperatureAnalyzer:
    def __init__(self, weather_df):
        """
        Initialize the TemperatureAnalyzer with a DataFrame of weather data.
        """
        self.weather_df = weather_df

    def calculate_descriptive_statistics(self):
        """
        Calculate and print descriptive statistics for temperature data.
        """
        print("Descriptive Statistics:")
        stats = self.weather_df[['TemperatureMax', 'TemperatureMin']].describe()
        print(stats)
        return stats

    def calculate_daily_range(self):
        """
        Calculate the daily temperature range and add it to the DataFrame.
        """
        self.weather_df['DailyRange'] = self.weather_df['TemperatureMax'] - self.weather_df['TemperatureMin']
        return self.weather_df[['Date', 'DailyRange']]

    def detect_extreme_temperatures(self, threshold=35, heat=True):
    # def detect_extreme_temperatures(self, heatwave_threshold=35, cold_snap_threshold=5, heat=True):
        """
        Detect extreme temperature days (heatwaves and cold snaps).
        """
        
        if heat:
            extreme_days = self.weather_df[self.weather_df['TemperatureMax'] > threshold]
            print(f"Number of heatwave days (> {threshold}°C): {len(extreme_days)}")
        else:
            extreme_days = self.weather_df[self.weather_df['TemperatureMin'] < threshold]
            print(f"Number of cold snap days (< {threshold}°C): {len(extreme_days)}")
        
        return extreme_days

    # def plot_daily_range(self, figsize=(12, 6)):
    #     """
    #     Plot the daily temperature range.
    #     Parameters:
    #     - figsize (tuple): Size of the figure (width, height).
    #     """
    #     if 'DailyRange' not in self.weather_df:
    #         self.calculate_daily_range()

    #     plt.figure(figsize=figsize)
    #     plt.plot(self.weather_df['Date'], self.weather_df['DailyRange'], label="Daily Temperature Range", linestyle='-', marker='o')
    #     plt.xlabel("Date")
    #     plt.ylabel("Temperature Range (\u00B0C)")
    #     plt.title("Daily Temperature Range Over Time")
    #     plt.legend()
    #     plt.grid(True, linestyle='--', alpha=0.7)

    #     # Customize the x-axis date format
    #     plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    #     plt.xticks(rotation=45)

    #     plt.tight_layout()
    #     # plt.show()

    # def plot_temperature_trends(self, figsize=(12, 6)):
    #     """
    #     Plot max and min temperature trends over time.
    #     Parameters:
    #     - figsize (tuple): Size of the figure (width, height).
    #     """
    #     plt.figure(figsize=figsize)
    #     plt.plot(self.weather_df['Date'], self.weather_df['TemperatureMax'], label="Max Temperature", color="red", linestyle='-', marker='o')
    #     plt.plot(self.weather_df['Date'], self.weather_df['TemperatureMin'], label="Min Temperature", color="blue", linestyle='--', marker='x')
    #     plt.xlabel("Date")
    #     plt.ylabel("Temperature (\u00B0C)")
    #     plt.title("Temperature Trends Over Time")
    #     plt.legend()
    #     plt.grid(True, linestyle='--', alpha=0.7)

    #     # Customize the x-axis date format
    #     plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    #     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    #     plt.xticks(rotation=45)

    #     plt.tight_layout()
    #     # plt.show()


def run_full_analysis(daily_weather_df):
    """
    Perform a full temperature analysis, including descriptive statistics,
    daily range calculation, extreme temperature detection, and plotting.
    """
    print("\n### Running Full Temperature Analysis ###")
    try:
        analyzer = TemperatureAnalyzer(daily_weather_df)  # Initialize the analyzer

        # Descriptive statistics
        analyzer.calculate_descriptive_statistics()  # Apenas chamamos a função, sem redundância

        # Daily temperature range
        daily_range = analyzer.calculate_daily_range()
       
        print("\n### Extreme Temperatures ###")
        heatwave_days = analyzer.detect_extreme_temperatures(35, True)
        print("Heatwave Days:")
        if not heatwave_days.empty:
            print(heatwave_days)
        else:
            print("No heatwave days found.")
        
        cold_snap_days = analyzer.detect_extreme_temperatures(5, False)
        print("Cold Snap Days:")
        if not cold_snap_days.empty:
            print(cold_snap_days)
        else:
            print("No cold snap days found.")

    #     # Plot temperature trends
    #     analyzer.plot_temperature_trends()

    #     # Plot daily temperature range
    #     analyzer.plot_daily_range()
    except Exception as e:
        print(f"Failed to analyze temperature data: {e}")