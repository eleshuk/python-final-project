import pytest
from project import weatherData, get_farm_input, weather_data_plot
import responses
import pandas as pd
import matplotlib.pyplot as plt
from unittest.mock import patch

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

def test_weather_data_plot_creates_figure(sample_weather_df, monkeypatch):
    mock_figure = None
    def mock_figure_creation(*args, **kwargs):
        nonlocal mock_figure
        mock_figure = plt.Figure(*args, **kwargs)
        return mock_figure

    monkeypatch.setattr(plt, 'figure', mock_figure_creation)
    monkeypatch.setattr(plt, 'show', lambda: None)

    weather_data_plot(sample_weather_df)
    assert mock_figure is not None
    # assert mock_figure.get_size_inches() == (12, 6)

if __name__ == "__main__":
    pytest.main()
