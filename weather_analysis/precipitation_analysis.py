import pandas as pd

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

# Precipitation quickstats