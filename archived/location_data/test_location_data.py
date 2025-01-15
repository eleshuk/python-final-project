import pytest
from location_data import locationData
from unittest.mock import patch

@pytest.fixture
def sample_inputs():
    return {
        'latitude': 38.748406,
        'longitude': -9.102984
    }

@pytest.fixture
def mock_response():
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

class TestLocationData:

    @patch('requests.get')
    def test_get_location_data(self, mock_get, sample_inputs, mock_response):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        location = locationData(sample_inputs)
        result = location.get_location_data()

        assert result == mock_response
        mock_get.assert_called_once_with(f"https://json.geoapi.pt/gps/{sample_inputs['latitude']},{sample_inputs['longitude']}")

    @patch('requests.get')
    def test_get_freguesia(self, mock_get, sample_inputs, mock_response):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

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