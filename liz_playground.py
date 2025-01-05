# Estimate switch from summer to winter and vice versa
# Extract temperature and date
# def get_growing_seasons(weather_data):
#     dates = weather_data['Date']
#     temperatures = weather_data['TemperatureMax']
#     # Find peaks (summer peaks) and valley (winter valley)
#     peaks, _ = find_peaks(temperatures)          # Find summer peaks
#     valleys, _ = find_peaks(-temperatures)       # Find winter valleys (negative for inversion)

#     # Get peak and valley temperatures
#     summer_peaks = temperatures[peaks]
#     winter_valley = temperatures[valleys].min()  # Get the lowest valley

#     # Calculate the midpoint temperature
#     T_mid = (summer_peaks.max() + winter_valley) / 2
#     # Calculate whether the temperature is above the midpoint
#     above_mid = temperatures >= T_mid
#     # Detect where the above_mid condition changes (True -> False or False -> True)
#     above_mid_diff = above_mid.diff().fillna(0).astype(bool)  # Handle NaN and ensure boolean
#     # Find indices of transitions
#     transition_indices = above_mid_diff[above_mid_diff].index  # Indices where the condition changes
#     # Extract the corresponding dates for the transitions
#     transition_dates = dates.loc[transition_indices]

#     print(transition_dates)  # Display the transition dates


#     # Plot results
#     plt.figure(figsize=(10, 6))
#     plt.plot(dates, temperatures, label='Temperature')
#     plt.scatter(dates[peaks], summer_peaks, color='red', label='Summer Peaks')
#     plt.scatter(dates[valleys], temperatures[valleys], color='blue', label='Winter Valley')
#     plt.axhline(T_mid, color='green', linestyle='--', label=f'Midpoint Temp ({T_mid:.2f})')
#     plt.scatter(transition_dates, temperatures[transition_dates.index], color='purple', label='Transitions')
#     plt.legend()
#     plt.title('Temperature Over Time with Transitions')
#     plt.xlabel('Date')
#     plt.ylabel('Temperature (°C)')
#     plt.grid()
#     plt.show()