from api_connectors.weather_api import WeatherAPI


class WeatherMonitor:

    def check_weather_risk(self, latitude, longitude):

        weather = WeatherAPI()
        data = weather.get_weather(latitude, longitude)

        if not data:
            return None

        windspeed = data.get("windspeed", 0)

        risk_level = "LOW"

        if windspeed > 40:
            risk_level = "HIGH"
        elif windspeed > 20:
            risk_level = "MEDIUM"

        return {
            "event_type": "Weather Disruption",
            "severity_score": windspeed,
            "risk_level": risk_level
        }