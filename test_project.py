import pytest
from project_location import get_farm_input
from project import weatherData
import responses

def test_valid_inputs(monkeypatch):
    inputs = iter(["39.3999", "-8.2245", "2025-01-01", "2025-01-10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result == {
        "latitude": 39.3999,
        "longitude": -8.2245,
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
    }

def test_invalid_latitude(monkeypatch):
    inputs = iter(["100", "39.3999", "-8.2245", "2025-01-01", "2025-01-10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result["latitude"] == 39.3999

def test_invalid_longitude(monkeypatch):
    inputs = iter(["39.3999", "200", "-8.2245", "2025-01-01", "2025-01-10"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result["longitude"] == -8.2245

def test_invalid_dates(monkeypatch):
    inputs = iter(["39.3999", "-8.2245", "2025-01-10", "2025-01-01", "2025-01-15"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_farm_input()
    assert result["end_date"] == "2025-01-15"


# Test to ensure that API call didn't fail
@responses.activate
def test_pull_weather_data():
    user_inputs = {
            "latitude": 39.3999,
            "longitude": -8.2245,
            "start_date": "2025-01-01",
            "end_date": "2025-01-04",
        }
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast"
    # https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=39.3999&longitude=-8.2245&start_date=2025-01-01&end_date=2025-01-04&daily=temperature_2m_max,temperature_2m_min,precipitation_sum
    
    # Mock the API response (example Open-Meteo response structure)
    responses.add(
        responses.GET,
        url,
        json={
            "latitude": user_inputs["latitude"],
            "longitude": user_inputs["longitude"],
            "start_date": user_inputs["start_date"],
            "end_date": user_inputs["end_date"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
        },
        status=200
    )

    # Call the function with user inputs
    cleaned_data = weatherData.get_weather_data(user_inputs)

    # Expected cleaned data after processing
    expected_data = [
        {"date": "2025-01-01", "TemperatureMax": 13.5, "TemperatureMin": 4, "Precipitation": 0},
        {"date": "2025-01-02", "TemperatureMax": 14.8, "TemperatureMin": 1.9, "Precipitation": 0},
        {"date": "2025-01-03", "TemperatureMax": 14.6, "TemperatureMin": 3.4, "Precipitation": 0},
        {"date": "2025-01-04", "TemperatureMax": 15.6, "TemperatureMin": 5.2, "Precipitation": 0}
    ]

    # Assert the cleaned data matches the expected output
    assert cleaned_data == expected_data, "Data cleaning failed for Open-Meteo API response"
    assert all("Date" in item and "TemperatureMax" in item and "TemperatureMin" and "TemperatureMin" in item in item for item in cleaned_data)

