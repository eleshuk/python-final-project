import pytest
from project import weatherData, get_farm_input, locationData, precipitation_data_avg
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys


@pytest.fixture
def default_values():
    """Fixture to provide default and boundary test values."""
    return {
        "valid_latlng": [37.7749, -122.4194],  # Default coordinates
        "boundary_latlng": [-90.0, 180.0],    # Boundary coordinates
        "start_date": "2023-01-01"          # Default start date
    }


@patch('geocoder.ip')
@patch('builtins.input')
def test_valid_input(mock_input, mock_geocoder, default_values):
    """Test user input with valid values."""
    mock_geocoder_instance = MagicMock()
    mock_geocoder_instance.latlng = default_values["valid_latlng"]
    mock_geocoder_instance.ok = True
    mock_geocoder.return_value = mock_geocoder_instance

    mock_input.side_effect = [default_values["start_date"]]
                            #   default_values["end_date"]]
    result = get_farm_input()

    assert result['latitude'] == default_values["valid_latlng"][0]
    assert result['longitude'] == default_values["valid_latlng"][1]
    assert result['start_date'] == default_values["start_date"]
    # assert result['end_date'] == default_values["end_date"]


@patch('geocoder.ip')
@patch('builtins.input')
def test_invalid_date_format(mock_input, mock_geocoder, default_values):
    """Test input with an invalid date format."""
    mock_geocoder_instance = MagicMock()
    mock_geocoder_instance.latlng = default_values["valid_latlng"]
    mock_geocoder_instance.ok = True
    mock_geocoder.return_value = mock_geocoder_instance

    mock_input.side_effect = ["invalid-date", default_values["start_date"]]
                            #   default_values["end_date"]]

    with patch('builtins.print') as mock_print:
        result = get_farm_input()

    assert "Invalid date format. Please use YYYY-MM-DD." in str(mock_print.call_args_list)
    assert result['start_date'] == default_values["start_date"]


@patch('geocoder.ip')
def test_geocoder_failure(mock_geocoder):
    """Test geocoder failure when fetching GPS coordinates."""
    mock_geocoder_instance = MagicMock()
    mock_geocoder_instance.ok = False
    mock_geocoder.return_value = mock_geocoder_instance

    with pytest.raises(Exception, match="Unable to retrieve GPS coordinates"):
        get_farm_input()


@patch('geocoder.ip')
@patch('builtins.input')
def test_boundary_coordinates(mock_input, mock_geocoder, default_values):
    """Test valid boundary GPS coordinates."""
    mock_geocoder_instance = MagicMock()
    mock_geocoder_instance.latlng = default_values["boundary_latlng"]
    mock_geocoder_instance.ok = True
    mock_geocoder.return_value = mock_geocoder_instance

    mock_input.side_effect = [default_values["start_date"]]
                            #   default_values["end_date"]]
    result = get_farm_input()

    assert result['latitude'] == default_values["boundary_latlng"][0]
    assert result['longitude'] == default_values["boundary_latlng"][1]

    
# User inputs to test API call
@pytest.fixture
def user_inputs():
    return {
        "latitude": 39.3999,
        "longitude": -8.2245,
        "start_date": "2025-01-01",
        "end_date": "2025-01-04",
    }

# Mock response from API call
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

# Mock and test API call
@patch("openmeteo_requests.Client")
def test_api_returns_expected_data(mock_client, mock_response):
    # Mocking the Daily data
    mock_daily = MagicMock()
    mock_daily.Time.return_value = pd.Timestamp("2025-01-01", tz="UTC")
    mock_daily.TimeEnd.return_value = pd.Timestamp("2025-01-04", tz="UTC")
    mock_daily.Interval.return_value = 86400

    # Correctly mock Variables to return a list of mocks, each returning the correct data
    mock_variables = [
        MagicMock(ValuesAsNumpy=lambda: mock_response["daily"]["temperature_2m_max"]),
        MagicMock(ValuesAsNumpy=lambda: mock_response["daily"]["temperature_2m_min"]),
        MagicMock(ValuesAsNumpy=lambda: mock_response["daily"]["precipitation_sum"]),
    ]
    mock_daily.Variables.return_value = mock_variables

    # Mocking the client instance
    mock_instance = mock_client.return_value
    mock_instance.weather_api.return_value = [MagicMock(Daily=lambda: mock_daily)]

    # Call the mocked API
    api_data = mock_instance.weather_api()
    daily_data = api_data[0].Daily()

    # Assertions
    assert daily_data.Time() == pd.Timestamp("2025-01-01", tz="UTC"), "Start date mismatch"
    assert daily_data.TimeEnd() == pd.Timestamp("2025-01-04", tz="UTC"), "End date mismatch"

    # Check temperature_2m_max
    assert daily_data.Variables()[0].ValuesAsNumpy() == mock_response["daily"]["temperature_2m_max"], \
        "Temperature max mismatch"

    # Check temperature_2m_min
    assert daily_data.Variables()[1].ValuesAsNumpy() == mock_response["daily"]["temperature_2m_min"], \
        "Temperature min mismatch"

    # Check precipitation_sum
    assert daily_data.Variables()[2].ValuesAsNumpy() == mock_response["daily"]["precipitation_sum"], \
        "Precipitation mismatch"

# Test data cleaning function
def test_data_cleaning(mock_response, user_inputs):
    # Use the mock response as input data for cleaning
    weather = weatherData(user_inputs)
    # Simulate raw data being set by the API
    weather.raw_data = mock_response["daily"]
    weather.raw_data = pd.DataFrame(data=weather.raw_data)
    weather.raw_data.columns = ['Date','TemperatureMax', 'TemperatureMin', 'Precipitation']

    # Clean data according to the project.py function
    cleaned_data = weather.get_weather_data()
    # Filter cleaned df to match the dates that we're testing
    cleaned_data = cleaned_data[(cleaned_data['Date'] >= mock_response["daily"]["time"][0]) & (cleaned_data['Date'] <= mock_response["daily"]["time"][3])]
    cleaned_data = cleaned_data.reset_index(drop=True)

    # Define the expected cleaned data as a DataFrame
    expected_data = pd.DataFrame([
        {"Date": "2025-01-01", "TemperatureMax": 13.5, "TemperatureMin": 4.0, "Precipitation": 0.0},
        {"Date": "2025-01-02", "TemperatureMax": 14.8, "TemperatureMin": 1.9, "Precipitation": 0.0},
        {"Date": "2025-01-03", "TemperatureMax": 14.6, "TemperatureMin": 3.4, "Precipitation": 0.0},
        {"Date": "2025-01-04", "TemperatureMax": 15.6, "TemperatureMin": 5.2, "Precipitation": 0.0},
    ])

    print(cleaned_data)
    print(expected_data)
    print(weather.raw_data)

    # Assert that cleaned data (from function) matches expected data
    assert cleaned_data.equals(expected_data), "Cleaned data does not match expected data"

    # If weather.raw_data (from mocked API call) is also expected to be a DataFrame
    assert pd.DataFrame(weather.raw_data).equals(expected_data), "Raw data does not match expected data"


# Test to check whether the export function is working properly
# Add the folder to sys.path
sys.path.append(str(Path(__file__).parent.parent / "python-final-project"))

# Test to check whether the export function is working properly
@patch("tkinter.filedialog.askdirectory")
@patch("project.weatherData.get_weather_data")  # Adjust module path
def test_export_weather_data_with_export_true(mock_get_weather_data, mock_askdirectory, user_inputs):
    # Mock askdirectory to return a specific directory
    mock_askdirectory.return_value = "/test/output/directory/"

    # Mock DataFrame
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_csv = MagicMock()

    # Mock get_weather_data to return the mocked DataFrame
    mock_get_weather_data.return_value = mock_df

    # Instantiate the weatherData class
    obj = weatherData(user_inputs)

    # Call the method
    obj.export_weather_data(export=True)

    # Debugging output
    print(f"askdirectory called: {mock_askdirectory.call_count}")
    print(f"get_weather_data called: {mock_get_weather_data.call_count}")
    print(f"to_csv calls: {mock_df.to_csv.call_args_list}")

    # Fix: Normalize the paths for comparison
    expected_path = str(Path("/test/output/directory/").resolve() / "weather_data.csv")
    actual_path = mock_df.to_csv.call_args[0][0]  # The first positional argument to to_csv

    print(f"Expected path: {expected_path}")
    print(f"Actual path: {actual_path}")

    # Ensure all mocks were called correctly
    mock_askdirectory.assert_called_once()
    mock_get_weather_data.assert_called_once()

    # Fix: Normalize both paths and compare
    assert Path(actual_path).resolve() == Path(expected_path).resolve(), \
        f"Path mismatch: {Path(actual_path).resolve()} != {Path(expected_path).resolve()}"

    # Check the 'index' argument
    assert 'index' in mock_df.to_csv.call_args[1], "Missing 'index' keyword argument in to_csv call"
    assert mock_df.to_csv.call_args[1]['index'] == False, f"Index value mismatch: {mock_df.to_csv.call_args[1]['index']} != False"

# Test for when export=False
@patch("project.pd.DataFrame.to_csv")  # Mock pandas DataFrame to_csv
@patch("project.weatherData.get_weather_data")  # Mock get_weather_data method
def test_export_weather_data_with_export_false(mock_get_weather_data, mock_to_csv, user_inputs):
    # Instantiate your class
    obj = weatherData(user_inputs)

    # Call the function with export=False
    obj.export_weather_data(export=False)

    # Assertions
    mock_get_weather_data.assert_not_called()  # Check get_weather_data is NOT called
    mock_to_csv.assert_not_called()  # Check to_csv is NOT called

# Test precipitation data output
def test_precipitation_data_avg():
    # Create sample test data
    data_10_days = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
        'Precipitation': [1.0, 2.0, 0.5, 1.2, 3.4, 2.1, 0.7, 1.5, 2.8, 3.0],
        'TemperatureMax': [30, 29, 28, 27, 26, 25, 24, 23, 22, 21],
        'TemperatureMin': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6],
    })
    
    data_45_days = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=45, freq='D'),
        'Precipitation': [1.0] * 45,
        'TemperatureMax': [30] * 45,
        'TemperatureMin': [15] * 45,
    })
    
    data_100_days = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'Precipitation': [0.5] * 100,
        'TemperatureMax': [25] * 100,
        'TemperatureMin': [10] * 100,
    })

    # Test for 10-day data (rolling window = 3)
    result_10_days = precipitation_data_avg(data_10_days)
    assert 'Rolling_Average' in result_10_days.columns
    assert len(result_10_days) == len(data_10_days)
    assert result_10_days['Rolling_Average'].iloc[2] == pytest.approx((1.0 + 2.0 + 0.5) / 3)
    assert 'TemperatureMax' not in result_10_days.columns
    assert 'TemperatureMin' not in result_10_days.columns

    # Test for 45-day data (rolling window = 7)
    result_45_days = precipitation_data_avg(data_45_days)
    assert len(result_45_days) == len(data_45_days)
    assert result_45_days['Rolling_Average'].iloc[6] == pytest.approx(1.0)  # Since all values are 1.0

    # Test for 100-day data (rolling window = 30)
    result_100_days = precipitation_data_avg(data_100_days)
    assert len(result_100_days) == len(data_100_days)
    assert result_100_days['Rolling_Average'].iloc[29] == pytest.approx(0.5)  # Since all values are 0.5

    # Test for correct handling of dropped columns
    assert 'TemperatureMax' not in result_45_days.columns
    assert 'TemperatureMin' not in result_45_days.columns
    assert 'TemperatureMax' not in result_100_days.columns
    assert 'TemperatureMin' not in result_100_days.columns

# test location api
@pytest.fixture
def sample_inputs():
    return {
        'latitude': 38.748406,
        'longitude': -9.102984
    }

@pytest.fixture
def location_mock_response():
    return {"lon":-9.102984,
            "lat":38.748406,
            "distrito":"Lisboa",
            "concelho":"Lisboa",
            "freguesia":"Marvila",
            "clima":
                {"data_medicao":"12/01/2025",
                 "hora_medicao":"14:00:00",
                 "temperatura_C":18,
                 "humidade_%":67,
                 "pressao_hPa":1030},
                 "altitude_m":36,
                 "perigo_incendio":"Nulo",
                 "perigo_inundacao":"Nulo / Informação Inexistente",
                 "uso":"Tecido edificado contínuo predominantemente vertical",
                 "SEC":"011",
                 "SS":"06",
                 "rua":"Rua Fernando Maurício",
                 "n_porta":"30",
                 "CP":"1950-449"}

class testLocationData:
    # test the locationDate class
    @patch('requests.get')
    def test_get_location_data(self, mock_get, sample_inputs, location_mock_response):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = location_mock_response

        location = locationData(sample_inputs)
        result = location.get_location_data()

        assert result == location_mock_response
        mock_get.assert_called_once_with(f"https://json.geoapi.pt/gps/{sample_inputs['latitude']},{sample_inputs['longitude']}")

    @patch('requests.get')
    def test_get_freguesia(self, mock_get, sample_inputs, location_mock_response):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = location_mock_response

        location = locationData(sample_inputs)
        result = location.get_freguesia()

        assert result == 'Marvila'

    @patch('requests.get')
    def test_get_location_data_error(self, mock_get, sample_inputs):
        mock_get.return_value.status_code = 404

        location = locationData(sample_inputs)
        result = location.get_location_data()

        assert result == "Error: 404"


if __name__ == "__main__":
    pytest.main([__file__])
