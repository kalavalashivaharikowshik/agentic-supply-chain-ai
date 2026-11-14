"""Open-Meteo weather client (free, no API key required)."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from app.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherAPI:
    api_url = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout
        self.enabled = get_settings().enable_external_apis

    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Return current weather (temperature, windspeed km/h, weathercode) or None."""
        if not self.enabled:
            return None
        params = {"latitude": latitude, "longitude": longitude, "current_weather": True}
        try:
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("current_weather")
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Weather API unavailable: %s", exc)
            return None
