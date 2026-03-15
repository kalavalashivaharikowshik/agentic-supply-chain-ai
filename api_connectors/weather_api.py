import requests


class WeatherAPI:

    def __init__(self):
        self.api_url = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, latitude, longitude):

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True
        }

        response = requests.get(self.api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data["current_weather"]
        else:
            return None