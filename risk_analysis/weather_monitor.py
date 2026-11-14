"""Weather-based disruption monitoring for configured ports."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from api_connectors.weather_api import WeatherAPI
from app.settings import get_settings
from risk_analysis.risk_scorer import RiskScorer

# WMO weather codes that indicate severe conditions (thunderstorms, heavy snow/rain)
SEVERE_WEATHER_CODES = {65, 67, 75, 82, 86, 95, 96, 99}


class WeatherMonitor:
    def __init__(self, api: Optional[WeatherAPI] = None):
        self.api = api or WeatherAPI()
        self.scorer = RiskScorer()

    def check_weather_risk(self, latitude: float, longitude: float, location: str = "Unknown") -> Optional[Dict[str, Any]]:
        data = self.api.get_weather(latitude, longitude)
        if not data:
            return None
        windspeed = float(data.get("windspeed", 0) or 0)
        severity = self.scorer.score_wind(windspeed)
        code = int(data.get("weathercode", 0) or 0)
        if code in SEVERE_WEATHER_CODES:
            severity = max(severity, 65)
        return {
            "event_type": "Weather Disruption",
            "location": location,
            "severity_score": severity,
            "risk_level": self.scorer.calculate_risk(severity),
            "description": f"Wind {windspeed:.0f} km/h, weather code {code}, temp {data.get('temperature')}°C",
        }

    def check_all_ports(self, min_level: str = "MEDIUM") -> List[Dict[str, Any]]:
        """Return weather events at or above ``min_level`` across all configured ports."""
        order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        events = []
        for port in get_settings().ports:
            event = self.check_weather_risk(port["lat"], port["lon"], port["name"])
            if event and order.index(event["risk_level"]) >= order.index(min_level):
                events.append(event)
        return events
