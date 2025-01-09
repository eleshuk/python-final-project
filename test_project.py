import pytest
from project import weatherData, get_farm_input, weather_data_plot
import responses
import pandas as pd
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
import requests

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
# @responses.activate
# def test_pull_weather_data():
#     user_inputs = {
#             "latitude": 39.3999,
#             "longitude": -8.2245,
#             "start_date": "2025-01-01",
#             "end_date": "2025-01-04",
#         }
#     url = (
#         "https://historical-forecast-api.open-meteo.com/v1/forecast"
#         f"?latitude={user_inputs['latitude']}&longitude={user_inputs['longitude']}"
#         f"&start_date={user_inputs['start_date']}&end_date={user_inputs['end_date']}"
#         "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
#     )
#     # https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=39.3999&longitude=-8.2245&start_date=2025-01-01&end_date=2025-01-04&daily=temperature_2m_max,temperature_2m_min,precipitation_sum
    
#     # Mock the API response (example Open-Meteo response structure)
#     responses.add(
#         responses.GET,
#         url,
#         json={
#             "latitude": user_inputs["latitude"],
#             "longitude": user_inputs["longitude"],
#             "daily": {
#                 "time": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"],
#                 "temperature_2m_max": [13.5, 14.8, 14.6, 15.6],
#                 "temperature_2m_min": [4, 1.9, 3.4, 5.2],
#                 "precipitation_sum": [0, 0, 0, 0],
#             }
#         },
#         status=200
#     )
#     # Simulate making the request
#     response = requests.get(url).json()

#     # Access the latitude field from the mocked response
#     latitude = response["latitude"]
#     print(f"Latitude: {latitude}")

#     # Call the function with user inputs
#     cleaned_data = weatherData.get_weather_data(user_inputs)

#     # Expected cleaned data after processing
#     expected_data = [
#         {"date": "2025-01-01", "TemperatureMax": 13.5, "TemperatureMin": 4, "Precipitation": 0},
#         {"date": "2025-01-02", "TemperatureMax": 14.8, "TemperatureMin": 1.9, "Precipitation": 0},
#         {"date": "2025-01-03", "TemperatureMax": 14.6, "TemperatureMin": 3.4, "Precipitation": 0},
#         {"date": "2025-01-04", "TemperatureMax": 15.6, "TemperatureMin": 5.2, "Precipitation": 0}
#     ]

#     # Assert the cleaned data matches the expected output
#     assert cleaned_data == expected_data, "Data cleaning failed for Open-Meteo API response"
#     assert all("Date" in item and "TemperatureMax" in item and "TemperatureMin" and "Precipitation" in item in item for item in cleaned_data)

    
@pytest.fixture
def user_inputs():
    return {
        "latitude": 39.3999,
        "longitude": -8.2245,
        "start_date": "2025-01-01",
        "end_date": "2025-01-04",
    }


@pytest.fixture
def mock_response():
    return {
        "latitude": 39.3999,
        "longitude": -8.2245,
        "daily": {
            "time": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"],  # ISO date strings
            "temperature_2m_max": [13.5, 14.8, 14.6, 15.6],
            "temperature_2m_min": [4.0, 1.9, 3.4, 5.2],
            "precipitation_sum": [0.0, 0.0, 0.0, 0.0],
        },
    }


@patch("openmeteo_requests.Client")
def test_pull_weather_data(mock_client, user_inputs, mock_response):
    # Mock the behavior of response.Daily() and related methods
    mock_daily = MagicMock()

    # Mock Time, TimeEnd, and Interval to match the test date range
    mock_daily.Time.return_value = "2025-01-01"  # Start date
    mock_daily.TimeEnd.return_value = "2025-01-04"  # End date
    mock_daily.Interval.return_value = 86400  # 1 day in seconds

    # Mock Variables and ValuesAsNumpy
    mock_daily.Variables.side_effect = [
        MagicMock(ValuesAsNumpy=lambda: mock_response["daily"]["temperature_2m_max"]),
        MagicMock(ValuesAsNumpy=lambda: mock_response["daily"]["temperature_2m_min"]),
        MagicMock(ValuesAsNumpy=lambda: mock_response["daily"]["precipitation_sum"]),
    ]

    # Mock weather_api response
    mock_instance = mock_client.return_value
    mock_instance.weather_api.return_value = [MagicMock(Daily=lambda: mock_daily)]

    # Instantiate weatherData and call get_weather_data
    weather = weatherData(user_inputs)
    cleaned_data = weather.get_weather_data()

    print(cleaned_data)

    # Expected data
    expected_data = [
        {"Date": "2025-01-01", "TemperatureMax": 13.5, "TemperatureMin": 4.0, "Precipitation": 0.0},
        {"Date": "2025-01-02", "TemperatureMax": 14.8, "TemperatureMin": 1.9, "Precipitation": 0.0},
        {"Date": "2025-01-03", "TemperatureMax": 14.6, "TemperatureMin": 3.4, "Precipitation": 0.0},
        {"Date": "2025-01-04", "TemperatureMax": 15.6, "TemperatureMin": 5.2, "Precipitation": 0.0},
    ]
    print(expected_data)

    # Assert the output matches the expected data
    assert cleaned_data == expected_data

# Test API failure
@responses.activate
def test_pull_weather_data_api_failure(user_inputs):
    url = (
        "https://historical-forecast-api.open-meteo.com/v1/forecast"
        f"?latitude={user_inputs['latitude']}&longitude={user_inputs['longitude']}"
        f"&start_date={user_inputs['start_date']}&end_date={user_inputs['end_date']}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    )
    responses.add(
        responses.GET,
        url,
        json={"error": "Invalid request"},
        status=400
    )

    response = requests.get(url)
    assert response.status_code == 400, "Expected failure for invalid API request"


# Tests to ensure temperature data plot is functioning as expected
@pytest.fixture
def sample_weather_df():
    return pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=5),
        'TemperatureMax': [10, 12, 15, 11, 13],
        'TemperatureMin': [5, 6, 8, 7, 6],
        'Precipitation': [0, 0.5, 1, 0.2, 0]
    })

def test_weather_data_plot(sample_weather_df):
    with patch('matplotlib.pyplot.show'):
        result = weather_data_plot(sample_weather_df)
    assert result == 'Plot successfully created'

def test_weather_data_plot_empty_dataframe():
    empty_df = pd.DataFrame(columns=['Date', 'TemperatureMax', 'TemperatureMin', 'Precipitation'])
    with patch('matplotlib.pyplot.show'):
        result = weather_data_plot(empty_df)
    assert result == 'Plot successfully created'

def test_weather_data_plot_exception_handling():
    invalid_df = pd.DataFrame({'InvalidColumn': [1, 2, 3]})
    with pytest.raises(KeyError):
        weather_data_plot(invalid_df)

if __name__ == "__main__":
    pytest.main()
