
import requests_cache
import requests
from retry_requests import retry

# Get location data from Geo API
class locationData:
    def __init__(self, inputs):
        # Initialize instance attributes
        self.latitude = inputs['latitude']
        self.longitude = inputs['longitude']
        
        # Set up the GEO API client with caching and retries
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.base_url = "https://json.geoapi.pt/gps"

    # make api request fpr latitude and longitude
    def get_location_data(self):
        # Make the API request
        url = f"{self.base_url}/{self.latitude},{self.longitude}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}"
        
    # get freguesia name from json
    def get_freguesia(self):
        result = self.get_location_data()['freguesia']
        return result