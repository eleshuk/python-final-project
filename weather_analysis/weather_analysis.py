import pandas as pd

# Calculations based on weather data
class weatherAnalysis:
    def __init__(self, inputs):
        self.max_temps = inputs["TemperatureMax"]
        self.min_temps = inputs["TemperatureMin"]
        self.dry_season_start = ""
        self.wet_season_start = ""

    def average_max_temp(self):
        return self.max_temps
    
    def average_min_temp(self):
        return "min"
    
    def total_precip(self):
        return "precip"

    def wet_season_precip(self):
        return "precip"
    
    def dry_season_precip(self):
        # if date range insufficient, return nothing
        return "precip"
    


# this is only for testing, remove once methods are called from project.py, or it will not work
inputs = pd.DataFrame([
        {"Date": "2025-01-01", "TemperatureMax": 13.5, "TemperatureMin": 4.0, "Precipitation": 0.0},
        {"Date": "2025-01-02", "TemperatureMax": 14.8, "TemperatureMin": 1.9, "Precipitation": 0.0},
        {"Date": "2025-01-03", "TemperatureMax": 14.6, "TemperatureMin": 3.4, "Precipitation": 0.0},
        {"Date": "2025-01-04", "TemperatureMax": 15.6, "TemperatureMin": 5.2, "Precipitation": 0.0},
    ])
weather = weatherAnalysis(inputs)
print(weather.average_max_temp())