"""Maps raw signals to 0-100 severity scores and risk levels."""

from __future__ import annotations

from app.settings import get_settings


class RiskScorer:
    def __init__(self):
        settings = get_settings()
        t = settings.get("risk.thresholds", {}) or {}
        self.critical = t.get("critical", 80)
        self.high = t.get("high", 50)
        self.medium = t.get("medium", 20)
        self.max_wind = settings.get("risk.max_wind_speed_kmh", 90)

    def calculate_risk(self, severity: float) -> str:
        severity = float(severity or 0)
        if severity >= self.critical:
            return "CRITICAL"
        if severity >= self.high:
            return "HIGH"
        if severity >= self.medium:
            return "MEDIUM"
        return "LOW"

    def score_wind(self, windspeed_kmh: float) -> int:
        """Convert wind speed (km/h) into a 0-100 severity score."""
        return int(max(0, min(100, round(float(windspeed_kmh or 0) / self.max_wind * 100))))
